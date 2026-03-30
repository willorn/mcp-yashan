#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
崖山数据库 MCP SSE Server - 跨平台实现
使用 Java 子进程调用 JDBC 驱动，支持 Windows 和 Mac

保留的 MCP 能力：
- test_connection: 测试数据库连接
- run_sql: 执行 SQL 查询
- list_schemas: 列出所有 Schema（用户）
- list_tables: 列出表
- describe_table: 查看表结构
- search_tables: 搜索表
- get_table_indexes: 查看表索引
- get_table_count: 快速获取表行数
- get_database_info: 获取数据库信息
- explain_sql: 获取 SQL 执行计划
"""

import json
import subprocess
import os
import sys
import logging
import asyncio
from typing import Dict, Any, List, Optional
from urllib.parse import urlparse

from starlette.applications import Starlette
from starlette.routing import Route, Mount
from starlette.responses import Response, StreamingResponse, JSONResponse
from starlette.requests import Request
from starlette.middleware.cors import CORSMiddleware

# ============================================================
# 配置加载
# ============================================================

def _load_env_file():
    """加载 .env 文件"""
    env_file = os.path.join(os.path.dirname(__file__), ".env")
    if os.path.exists(env_file):
        with open(env_file, "r", encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    os.environ.setdefault(key.strip(), value.strip())

_load_env_file()

# ============================================================
# 日志配置
# ============================================================

logger = logging.getLogger("yashan_mcp")
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO").upper(),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stderr),
        logging.FileHandler(
            os.path.join(os.path.dirname(__file__), 'yashan_mcp.log'),
            encoding='utf-8'
        )
    ]
)

# ============================================================
# Java SQL 执行器 - 跨平台实现
# ============================================================

JAVA_TEMPLATE = '''
import java.sql.*;
public class TempSqlExecutor {{
    public static void main(String[] args) throws Exception {{
        String jdbcUrl = "{jdbc_url}";
        String user = "{username}";
        String password = "{password}";
        String sql = args[0];
        int maxRows = Integer.parseInt(args[1]);

        long startTime = System.currentTimeMillis();

        try {{
            Class.forName("com.yashandb.jdbc.Driver");
            Connection conn = DriverManager.getConnection(jdbcUrl, user, password);
            Statement stmt = conn.createStatement();
            stmt.setMaxRows(maxRows);
            boolean isResultSet = stmt.execute(sql);

            if (isResultSet) {{
                ResultSet rs = stmt.getResultSet();
                ResultSetMetaData metaData = rs.getMetaData();
                int columnCount = metaData.getColumnCount();

                System.out.println("COLUMNS:" + columnCount);
                for (int i = 1; i <= columnCount; i++) {{
                    System.out.println("COL:" + metaData.getColumnName(i));
                }}

                int rowCount = 0;
                while (rs.next() && rowCount < maxRows) {{
                    System.out.print("ROW:");
                    for (int i = 1; i <= columnCount; i++) {{
                        if (i > 1) System.out.print("|");
                        Object value = rs.getObject(i);
                        System.out.print(value != null ? value.toString().replace("\\n", " ").replace("\\r", " ").replace("\\t", " ") : "NULL");
                    }}
                    System.out.println();
                    rowCount++;
                }}
                System.out.println("ROW_COUNT:" + rowCount);
                rs.close();
            }} else {{
                int updateCount = stmt.getUpdateCount();
                System.out.println("UPDATE_COUNT:" + updateCount);
            }}

            stmt.close();
            conn.close();
            System.out.println("SUCCESS:true");
        }} catch (Exception e) {{
            System.out.println("SUCCESS:false");
            System.out.println("ERROR:" + e.getMessage());
        }}

        System.out.println("EXEC_TIME:" + (System.currentTimeMillis() - startTime));
    }}
}}
'''


class JavaSqlExecutor:
    """Java SQL 执行器 - 跨平台"""
    
    def __init__(self):
        self.config = {
            "host": os.getenv("DB_HOST", "localhost"),
            "port": os.getenv("DB_PORT", "1688"),
            "db_name": os.getenv("DB_NAME", "yashandb"),
            "username": os.getenv("DB_USER", ""),
            "password": os.getenv("DB_PASSWORD", ""),
        }
        self.jdbc_url = os.getenv("DB_JDBC_URL", 
            f"jdbc:yasdb://{self.config['host']}:{self.config['port']}/{self.config['db_name']}?failover=on")
        self.jar_path = os.path.join(os.path.dirname(__file__), "yashandb-jdbc-1.7.19-21.jar")
        self.java_cmd = self._find_java()
        
    def _find_java(self) -> str:
        """查找 Java 可执行文件（跨平台）"""
        # 1. 检查 JAVA_HOME
        java_home = os.getenv("JAVA_HOME")
        if java_home:
            # Windows
            java_exe = os.path.join(java_home, "bin", "java.exe")
            if os.path.exists(java_exe):
                return java_exe
            # Mac/Linux
            java_exe = os.path.join(java_home, "bin", "java")
            if os.path.exists(java_exe):
                return java_exe
        
        # 2. 检查 PATH
        return "java"
    
    def execute(self, sql: str, max_rows: int = 1000) -> Dict[str, Any]:
        """执行 SQL"""
        temp_dir = os.path.dirname(__file__)
        temp_java = os.path.join(temp_dir, "TempSqlExecutor.java")
        temp_class = os.path.join(temp_dir, "TempSqlExecutor.class")
        
        # 转义字符串
        safe_jdbc_url = self.jdbc_url.replace("\\", "\\\\")
        safe_username = self.config['username'].replace("\\", "\\\\")
        safe_password = self.config['password'].replace("\\", "\\\\")
        
        java_code = JAVA_TEMPLATE.format(
            jdbc_url=safe_jdbc_url,
            username=safe_username,
            password=safe_password
        )
        
        try:
            # 写入 Java 文件
            with open(temp_java, "w", encoding="utf-8") as f:
                f.write(java_code)
            
            # 编译
            javac_cmd = self._get_javac_cmd()
            compile_result = subprocess.run(
                [javac_cmd, "-cp", self.jar_path, temp_java], 
                capture_output=True, timeout=30, cwd=temp_dir
            )
            
            if compile_result.returncode != 0:
                return {
                    "success": False, 
                    "error": f"编译失败: {compile_result.stderr.decode('utf-8', errors='ignore')}"
                }
            
            # 执行
            classpath_sep = ";" if os.name == "nt" else ":"
            result = subprocess.run(
                [self.java_cmd, "-cp", f"{self.jar_path}{classpath_sep}{temp_dir}", "TempSqlExecutor", sql, str(max_rows)],
                capture_output=True, text=True, timeout=60, cwd=temp_dir
            )
            
            return self._parse_output(result.stdout)
            
        except Exception as e:
            logger.error(f"SQL 执行错误: {e}")
            return {"success": False, "error": str(e)}
        finally:
            # 清理临时文件
            for f in [temp_java, temp_class]:
                try:
                    if os.path.exists(f):
                        os.remove(f)
                except:
                    pass
    
    def _get_javac_cmd(self) -> str:
        """获取 javac 命令"""
        javac_cmd = self.java_cmd.replace("java.exe", "javac.exe").replace("java", "javac")
        if javac_cmd == "javac":
            return "javac"
        if os.path.exists(javac_cmd):
            return javac_cmd
        return "javac"
    
    def _parse_output(self, output: str) -> Dict[str, Any]:
        """解析 Java 输出"""
        result = {
            "success": False, 
            "columns": [], 
            "data": [], 
            "row_count": 0, 
            "execution_time": 0,
            "error": None
        }
        
        for line in output.strip().split("\n"):
            line = line.strip()
            if line.startswith("SUCCESS:"):
                result["success"] = line.split(":")[1].lower() == "true"
            elif line.startswith("ERROR:"):
                result["error"] = line[6:]
            elif line.startswith("COLUMNS:"):
                pass
            elif line.startswith("COL:"):
                result["columns"].append(line[4:])
            elif line.startswith("ROW:"):
                row_data = line[4:].split("|")
                row_dict = {}
                for i, col in enumerate(result["columns"]):
                    if i < len(row_data):
                        row_dict[col] = None if row_data[i] == "NULL" else row_data[i]
                result["data"].append(row_dict)
            elif line.startswith("ROW_COUNT:") or line.startswith("UPDATE_COUNT:"):
                result["row_count"] = int(line.split(":")[1])
            elif line.startswith("EXEC_TIME:"):
                result["execution_time"] = float(line.split(":")[1]) / 1000.0
        
        return result


# ============================================================
# 元数据管理器
# ============================================================

class MetadataManager:
    """元数据管理器"""
    
    def __init__(self, executor: JavaSqlExecutor):
        self.executor = executor
    
    def list_schemas(self) -> List[str]:
        """列出所有 Schema"""
        sql = """
            SELECT USERNAME FROM ALL_USERS 
            WHERE USERNAME NOT IN ('SYS', 'SYSTEM', 'PUBLIC')
            ORDER BY USERNAME
        """
        result = self.executor.execute(sql)
        if result.get("success") and result.get("data"):
            return [row.get('USERNAME', '') for row in result["data"]]
        return []
    
    def list_tables(self, schema: str = None) -> List[Dict]:
        """列出表"""
        if schema:
            sql = f"""
                SELECT TABLE_NAME, OWNER
                FROM ALL_TABLES
                WHERE OWNER = '{schema.upper()}'
                ORDER BY TABLE_NAME
            """
        else:
            sql = """
                SELECT TABLE_NAME, OWNER
                FROM ALL_TABLES
                ORDER BY OWNER, TABLE_NAME
            """
        
        result = self.executor.execute(sql, max_rows=1000)
        tables = []
        if result.get("success") and result.get("data"):
            for row in result["data"]:
                tables.append({
                    "name": row.get('TABLE_NAME', ''),
                    "owner": row.get('OWNER', '')
                })
        return tables
    
    def describe_table(self, table_name: str, schema: str = None) -> List[Dict]:
        """获取表结构"""
        schema_filter = f"AND OWNER = '{schema.upper()}'" if schema else ""
        
        sql = f"""
            SELECT 
                COLUMN_NAME,
                DATA_TYPE,
                DATA_LENGTH,
                NULLABLE,
                DATA_DEFAULT
            FROM ALL_TAB_COLUMNS
            WHERE TABLE_NAME = '{table_name.upper()}' {schema_filter}
            ORDER BY COLUMN_ID
        """
        
        result = self.executor.execute(sql)
        columns = []
        if result.get("success") and result.get("data"):
            for row in result["data"]:
                columns.append({
                    "name": row.get('COLUMN_NAME', ''),
                    "data_type": row.get('DATA_TYPE', ''),
                    "length": row.get('DATA_LENGTH', 0),
                    "nullable": row.get('NULLABLE', 'Y') == 'Y',
                    "default": row.get('DATA_DEFAULT')
                })
        return columns
    
    def search_tables(self, pattern: str, schema: str = None) -> List[Dict]:
        """搜索表"""
        schema_filter = f"AND OWNER = '{schema.upper()}'" if schema else ""
        
        sql = f"""
            SELECT TABLE_NAME, OWNER
            FROM ALL_TABLES
            WHERE TABLE_NAME LIKE '%{pattern.upper()}%' 
            {schema_filter}
            ORDER BY OWNER, TABLE_NAME
        """
        
        result = self.executor.execute(sql, max_rows=200)
        tables = []
        if result.get("success") and result.get("data"):
            for row in result["data"]:
                tables.append({
                    "name": row.get('TABLE_NAME', ''),
                    "owner": row.get('OWNER', '')
                })
        return tables
    
    def get_table_indexes(self, table_name: str, schema: str = None) -> List[Dict]:
        """获取表索引"""
        schema_filter = f"AND TABLE_OWNER = '{schema.upper()}'" if schema else ""
        
        sql = f"""
            SELECT 
                INDEX_NAME,
                INDEX_TYPE,
                UNIQUENESS,
                TABLE_NAME,
                TABLE_OWNER
            FROM ALL_INDEXES
            WHERE TABLE_NAME = '{table_name.upper()}' {schema_filter}
            ORDER BY INDEX_NAME
        """
        
        result = self.executor.execute(sql)
        return result.get("data", []) if result.get("success") else []
    
    def get_table_count(self, table_name: str, schema: str = None) -> int:
        """获取表行数"""
        full_table = f"{schema.upper()}.{table_name.upper()}" if schema else table_name.upper()
        sql = f"SELECT COUNT(*) as count FROM {full_table}"
        
        result = self.executor.execute(sql)
        if result.get("success") and result.get("data"):
            return result["data"][0].get('COUNT', 0)
        return 0


# ============================================================
# MCP SSE 服务器
# ============================================================

executor = None
metadata = None
clients = {}

def get_executor() -> JavaSqlExecutor:
    """获取执行器（单例）"""
    global executor
    if executor is None:
        executor = JavaSqlExecutor()
    return executor

def get_metadata() -> MetadataManager:
    """获取元数据管理器（单例）"""
    global metadata
    if metadata is None:
        metadata = MetadataManager(get_executor())
    return metadata


# ============================================================
# MCP 工具定义
# ============================================================

TOOLS = [
    {
        "name": "test_connection",
        "description": "测试数据库连接",
        "inputSchema": {"type": "object", "properties": {}}
    },
    {
        "name": "run_sql",
        "description": "执行 SQL 查询",
        "inputSchema": {
            "type": "object",
            "properties": {
                "sql_query": {"type": "string", "description": "SQL 语句"},
                "max_rows": {"type": "integer", "description": "最大返回行数", "default": 100}
            },
            "required": ["sql_query"]
        }
    },
    {
        "name": "list_schemas",
        "description": "列出所有 Schema（用户）",
        "inputSchema": {"type": "object", "properties": {}}
    },
    {
        "name": "list_tables",
        "description": "列出表",
        "inputSchema": {
            "type": "object",
            "properties": {
                "schema": {"type": "string", "description": "可选，指定 Schema 名"}
            }
        }
    },
    {
        "name": "describe_table",
        "description": "查看表结构",
        "inputSchema": {
            "type": "object",
            "properties": {
                "table_name": {"type": "string", "description": "表名"},
                "schema": {"type": "string", "description": "可选，指定 Schema 名"}
            },
            "required": ["table_name"]
        }
    },
    {
        "name": "search_tables",
        "description": "搜索表",
        "inputSchema": {
            "type": "object",
            "properties": {
                "pattern": {"type": "string", "description": "表名关键字（支持模糊搜索）"},
                "schema": {"type": "string", "description": "可选，限定在某个 Schema 下搜索"}
            },
            "required": ["pattern"]
        }
    },
    {
        "name": "get_table_indexes",
        "description": "查看表索引",
        "inputSchema": {
            "type": "object",
            "properties": {
                "table_name": {"type": "string", "description": "表名"},
                "schema": {"type": "string", "description": "可选，指定 Schema"}
            },
            "required": ["table_name"]
        }
    },
    {
        "name": "get_table_count",
        "description": "快速获取表行数",
        "inputSchema": {
            "type": "object",
            "properties": {
                "table_name": {"type": "string", "description": "表名"},
                "schema": {"type": "string", "description": "可选，指定 Schema"}
            },
            "required": ["table_name"]
        }
    },
    {
        "name": "get_database_info",
        "description": "获取数据库信息",
        "inputSchema": {"type": "object", "properties": {}}
    },
    {
        "name": "explain_sql",
        "description": "获取 SQL 执行计划",
        "inputSchema": {
            "type": "object",
            "properties": {
                "sql_query": {"type": "string", "description": "SQL 语句"}
            },
            "required": ["sql_query"]
        }
    }
]


# ============================================================
# 工具处理函数
# ============================================================

def handle_test_connection() -> Dict:
    """处理 test_connection 工具"""
    res = get_executor().execute("SELECT USER FROM DUAL")
    if res.get("success"):
        user = res.get("data", [{}])[0].get("USER", "N/A")
        config = get_executor().config
        return {
            "content": [{
                "type": "text",
                "text": f"""✅ 崖山数据库连接正常！
主机：{config['host']}:{config['port']}
用户：{config['username']}
当前会话用户：{user}
数据库：{config['db_name']}"""
            }]
        }
    else:
        return {
            "content": [{
                "type": "text",
                "text": f"❌ 连接失败: {res.get('error', '未知错误')}"
            }],
            "isError": True
        }


def handle_run_sql(args: Dict) -> Dict:
    """处理 run_sql 工具"""
    sql = args.get("sql_query", "")
    max_rows = args.get("max_rows", 100)
    res = get_executor().execute(sql, max_rows)
    
    if not res.get("success"):
        return {
            "content": [{
                "type": "text",
                "text": f"❌ SQL 执行失败: {res.get('error', '未知错误')}"
            }],
            "isError": True
        }
    
    if res.get("data") is not None:
        # 查询结果
        lines = [f"✅ 查询成功！共 {len(res['data'])} 行"]
        columns = res.get("columns", [])
        data = res.get("data", [])
        
        if columns and data:
            # 计算列宽
            col_widths = [len(str(col)) for col in columns]
            for row in data:
                for i, col in enumerate(columns):
                    col_widths[i] = max(col_widths[i], len(str(row.get(col, ""))))
            
            # 表头
            header = " | ".join(str(col).ljust(col_widths[i]) for i, col in enumerate(columns))
            separator = "-+-".join("-" * w for w in col_widths)
            
            lines.append(header)
            lines.append(separator)
            for row in data:
                row_str = " | ".join(str(row.get(col, "")).ljust(col_widths[i]) for i, col in enumerate(columns))
                lines.append(row_str)
        
        lines.append(f"\n执行时间：{res.get('execution_time', 0):.3f}s")
        return {"content": [{"type": "text", "text": "\n".join(lines)}]}
    else:
        # DML/DDL 结果
        return {
            "content": [{
                "type": "text",
                "text": f"✅ 执行成功，影响 {res.get('row_count', 0)} 行\n执行时间：{res.get('execution_time', 0):.3f}s"
            }]
        }


def handle_list_schemas() -> Dict:
    """处理 list_schemas 工具"""
    schemas = get_metadata().list_schemas()
    if schemas:
        lines = [f"✅ 共找到 {len(schemas)} 个 Schema:"]
        for s in schemas:
            lines.append(f"  - {s}")
        return {"content": [{"type": "text", "text": "\n".join(lines)}]}
    return {"content": [{"type": "text", "text": "⚠️ 未找到任何 Schema"}]}


def handle_list_tables(args: Dict) -> Dict:
    """处理 list_tables 工具"""
    schema = args.get("schema")
    tables = get_metadata().list_tables(schema if schema else None)
    if tables:
        lines = [f"✅ 共找到 {len(tables)} 个表:"]
        for t in tables:
            lines.append(f"  - {t['owner']}.{t['name']}")
        return {"content": [{"type": "text", "text": "\n".join(lines)}]}
    schema_msg = f"在 Schema '{schema}' 下" if schema else ""
    return {"content": [{"type": "text", "text": f"⚠️ {schema_msg}未找到任何表"}]}


def handle_describe_table(args: Dict) -> Dict:
    """处理 describe_table 工具"""
    table_name = args.get("table_name", "")
    schema = args.get("schema")
    columns = get_metadata().describe_table(table_name, schema if schema else None)
    
    if columns:
        lines = [f"✅ 表 {schema + '.' if schema else ''}{table_name} 的结构:", ""]
        lines.append(f"{'列名':<30} {'类型':<20} {'长度':<10} {'可空':<8} {'默认值':<20}")
        lines.append("-" * 90)
        for col in columns:
            nullable = "是" if col["nullable"] else "否"
            default = str(col["default"]) if col["default"] else ""
            lines.append(
                f"{col['name']:<30} {col['data_type']:<20} {str(col['length']):<10} {nullable:<8} {default:<20}"
            )
        return {"content": [{"type": "text", "text": "\n".join(lines)}]}
    
    schema_msg = f"在 Schema '{schema}' 下" if schema else ""
    return {"content": [{"type": "text", "text": f"⚠️ {schema_msg}未找到表 '{table_name}'"}]}


def handle_search_tables(args: Dict) -> Dict:
    """处理 search_tables 工具"""
    pattern = args.get("pattern", "")
    schema = args.get("schema")
    tables = get_metadata().search_tables(pattern, schema if schema else None)
    
    if tables:
        lines = [f"✅ 找到 {len(tables)} 个匹配 '{pattern}' 的表:"]
        for t in tables:
            lines.append(f"  - {t['owner']}.{t['name']}")
        return {"content": [{"type": "text", "text": "\n".join(lines)}]}
    return {"content": [{"type": "text", "text": f"⚠️ 未找到包含 '{pattern}' 的表"}]}


def handle_get_table_indexes(args: Dict) -> Dict:
    """处理 get_table_indexes 工具"""
    table_name = args.get("table_name", "")
    schema = args.get("schema")
    indexes = get_metadata().get_table_indexes(table_name, schema if schema else None)
    
    if indexes:
        lines = [f"✅ 表 {schema + '.' if schema else ''}{table_name} 的索引:"]
        for idx in indexes:
            unique = "唯一" if idx.get('UNIQUENESS') == 'UNIQUE' else "非唯一"
            lines.append(f"  - {idx.get('INDEX_NAME')} ({idx.get('INDEX_TYPE')}, {unique})")
        return {"content": [{"type": "text", "text": "\n".join(lines)}]}
    return {"content": [{"type": "text", "text": f"⚠️ 未找到表 '{table_name}' 的索引"}]}


def handle_get_table_count(args: Dict) -> Dict:
    """处理 get_table_count 工具"""
    table_name = args.get("table_name", "")
    schema = args.get("schema")
    count = get_metadata().get_table_count(table_name, schema if schema else None)
    full_name = f"{schema}.{table_name}" if schema else table_name
    return {"content": [{"type": "text", "text": f"✅ 表 {full_name} 的行数: {count}"}]}


def handle_get_database_info() -> Dict:
    """处理 get_database_info 工具"""
    config = get_executor().config
    return {
        "content": [{
            "type": "text",
            "text": f"""📊 崖山数据库环境信息
{'='*50}
主机：{config['host']}:{config['port']}
数据库：{config['db_name']}
用户名：{config['username']}
驱动：YashanDB JDBC
当前时间：{__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"""
        }]
    }


def handle_explain_sql(args: Dict) -> Dict:
    """处理 explain_sql 工具"""
    sql_query = args.get("sql_query", "")
    explain_sql = f"EXPLAIN {sql_query}"
    res = get_executor().execute(explain_sql, max_rows=200)
    
    if res.get("success") and res.get("data"):
        lines = ["✅ SQL 执行计划:"]
        for row in res["data"]:
            plan_line = row.get("PLAN_DESCRIPTION", "")
            if plan_line:
                lines.append(plan_line)
        return {"content": [{"type": "text", "text": "\n".join(lines)}]}
    return {"content": [{"type": "text", "text": "⚠️ 无法获取执行计划"}]}


# ============================================================
# SSE 端点
# ============================================================

async def sse_endpoint(request: Request):
    """SSE 连接端点"""
    client_id = id(request)
    clients[client_id] = {"queue": asyncio.Queue()}
    
    async def event_generator():
        try:
            # 发送 endpoint 事件
            yield f"event: endpoint\ndata: /messages?sessionId={client_id}\n\n"
            
            # 等待并转发消息
            while True:
                try:
                    message = await asyncio.wait_for(
                        clients[client_id]["queue"].get(), 
                        timeout=30.0
                    )
                    yield f"event: message\ndata: {json.dumps(message)}\n\n"
                except asyncio.TimeoutError:
                    # 发送心跳
                    yield ": ping\n\n"
        except Exception as e:
            logger.error(f"SSE 流错误：{e}")
        finally:
            clients.pop(client_id, None)
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


async def messages_endpoint(request: Request):
    """消息处理端点（POST）"""
    if request.method == "POST":
        try:
            session_id = int(request.query_params.get("sessionId", 0))
            body = await request.json()
            
            # 处理 MCP 消息
            method = body.get("method", "")
            params = body.get("params", {})
            msg_id = body.get("id")
            
            result = None
            error = None
            
            if method == "initialize":
                result = {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {"tools": {}},
                    "serverInfo": {"name": "yashan-mcp-sse", "version": "2.0.0"}
                }
            elif method == "tools/list":
                result = {"tools": TOOLS}
            elif method == "tools/call":
                tool_name = params.get("name", "")
                args = params.get("arguments", {})
                
                # 工具路由
                handlers = {
                    "test_connection": handle_test_connection,
                    "run_sql": handle_run_sql,
                    "list_schemas": handle_list_schemas,
                    "list_tables": handle_list_tables,
                    "describe_table": handle_describe_table,
                    "search_tables": handle_search_tables,
                    "get_table_indexes": handle_get_table_indexes,
                    "get_table_count": handle_get_table_count,
                    "get_database_info": handle_get_database_info,
                    "explain_sql": handle_explain_sql,
                }
                
                handler = handlers.get(tool_name)
                if handler:
                    try:
                        if args:
                            result = handler(args)
                        else:
                            result = handler()
                    except Exception as e:
                        logger.error(f"工具执行错误 {tool_name}: {e}")
                        error = str(e)
                else:
                    error = f"未知工具：{tool_name}"
            
            # 构建响应
            if error:
                response = {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "error": {"code": -32600, "message": str(error)}
                }
            else:
                response = {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "result": result
                }
            
            # 将响应放入队列
            if session_id in clients:
                await clients[session_id]["queue"].put(response)
            
            return JSONResponse({"status": "ok"})
            
        except Exception as e:
            logger.error(f"消息处理错误：{e}")
            return JSONResponse({"status": "error", "message": str(e)}, status_code=500)
    
    return JSONResponse({"error": "Method not allowed"}, status_code=405)


async def health_check(request: Request):
    """健康检查"""
    return JSONResponse({"ok": True, "service": "yashan-mcp-sse"})


# 创建路由
routes = [
    Route("/sse", endpoint=sse_endpoint, methods=["GET"]),
    Mount("/messages", routes=[
        Route("/", endpoint=messages_endpoint, methods=["POST"]),
    ]),
    Route("/healthz", endpoint=health_check, methods=["GET"]),
]

app = Starlette(routes=routes)
app = CORSMiddleware(
    app=app,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================
# 启动入口
# ============================================================

if __name__ == "__main__":
    import argparse
    import uvicorn

    parser = argparse.ArgumentParser(description="崖山数据库 MCP SSE Server")
    parser.add_argument("--host", default="0.0.0.0", help="监听地址")
    parser.add_argument("--port", type=int, default=8080, help="监听端口")
    args = parser.parse_args()

    logger.info("正在初始化...")
    get_executor()

    config = get_executor().config
    logger.info(f"数据库：{config['host']}:{config['port']}/{config['db_name']}")
    logger.info(f"SSE MCP 监听：http://{args.host}:{args.port}/sse")
    logger.info(f"消息端点：http://{args.host}:{args.port}/messages")
    logger.info(f"健康检查：http://{args.host}:{args.port}/healthz")

    uvicorn.run(app, host=args.host, port=args.port, forwarded_allow_ips="*")
