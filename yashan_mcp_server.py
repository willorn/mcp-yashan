#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
崖山数据库 MCP Server Pro - YashanDB MCP Server Professional Edition

专业的崖山数据库 MCP 服务器，提供完整的数据库操作能力。
支持多种运行模式：stdio、sse、http

特性：
- 连接池管理
- SQL 执行和查询
- 数据库元数据获取
- 事务支持
- 性能监控
- 完善的错误处理

作者：AI Assistant
版本：2.0.0
"""

from mcp.server.fastmcp import FastMCP
import json
import datetime
import os
import sys
import logging
import time
from typing import Optional, List, Dict, Any, Tuple, Union
from contextlib import contextmanager
from dataclasses import dataclass, asdict
from functools import wraps
from starlette.requests import Request
from starlette.responses import JSONResponse

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

# 加载 .env 文件
_load_env_file()

# ============================================================
# 日志配置
# ============================================================

def setup_logging():
    """配置日志"""
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    logging.basicConfig(
        level=getattr(logging, log_level, logging.INFO),
        format=log_format,
        handlers=[
            logging.StreamHandler(sys.stderr),
            logging.FileHandler(
                os.path.join(os.path.dirname(__file__), 'yashan_mcp.log'),
                encoding='utf-8'
            )
        ]
    )
    return logging.getLogger("yashan_mcp")

logger = setup_logging()


def _to_display_str(value: Any) -> str:
    """将 JDBC 返回值安全转换为可展示字符串"""
    return "" if value is None else str(value)

# ============================================================
# 数据模型
# ============================================================

@dataclass
class DatabaseConfig:
    """数据库配置"""
    driver_class: str
    jdbc_url: str
    username: str
    password: str
    jvm_lib: str = ""
    
    @classmethod
    def from_env(cls) -> 'DatabaseConfig':
        """从环境变量创建配置"""
        host = os.getenv("DB_HOST", "localhost")
        port = os.getenv("DB_PORT", "1688")
        db_name = os.getenv("DB_NAME", "yashandb")
        
        jdbc_url = os.getenv("DB_JDBC_URL")
        if not jdbc_url:
            jdbc_url = f"jdbc:yasdb://{host}:{port}/{db_name}?failover=on&failoverType=session&failoverMethod=basic&failoverRetries=5&failoverDelay=1"
        
        return cls(
            driver_class=os.getenv("DB_DRIVER_CLASS", "com.yashandb.jdbc.Driver"),
            jdbc_url=jdbc_url,
            username=os.getenv("DB_USER", ""),
            password=os.getenv("DB_PASSWORD", ""),
            jvm_lib=os.getenv("JVM_LIB", "")
        )

@dataclass
class SQLResult:
    """SQL 执行结果"""
    success: bool
    data: Optional[List[Dict]] = None
    columns: Optional[List[str]] = None
    row_count: int = 0
    execution_time: float = 0.0
    error: Optional[str] = None
    sql_type: str = ""

@dataclass
class TableInfo:
    """表信息"""
    name: str
    owner: str
    table_type: str = "TABLE"
    comment: str = ""

@dataclass
class ColumnInfo:
    """列信息"""
    name: str
    data_type: str
    length: int
    nullable: bool
    default: Optional[str]
    comment: str = ""
    is_primary_key: bool = False
    is_foreign_key: bool = False

# ============================================================
# 性能监控装饰器
# ============================================================

def monitor_performance(func):
    """性能监控装饰器"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            logger.info(f"{func.__name__} 执行成功，耗时: {execution_time:.3f}s")
            return result
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"{func.__name__} 执行失败，耗时: {execution_time:.3f}s, 错误: {e}")
            raise
    return wrapper

# ============================================================
# 数据库连接管理
# ============================================================

class ConnectionPool:
    """数据库连接池"""
    
    def __init__(self, config: DatabaseConfig, max_connections: int = 5):
        self.config = config
        self.max_connections = max_connections
        self._connections = []
        self._in_use = set()
        self._jvm_started = False
        self._initialize_jvm()
        
    def _initialize_jvm(self):
        """初始化 JVM"""
        if self._jvm_started:
            return
            
        try:
            import jpype
            if not jpype.isJVMStarted():
                jvm_path = self._get_jvm_path()
                if not jvm_path:
                    raise RuntimeError("找不到 JVM！请安装 JDK 17+ 或设置 JVM_LIB 环境变量")
                
                jdbc_driver_path = os.path.join(
                    os.path.dirname(__file__), 
                    "yashandb-jdbc-1.7.19-21.jar"
                )
                
                jpype.startJVM(
                    jvm_path,
                    f"-Djava.class.path={jdbc_driver_path}",
                    ignoreUnrecognized=True
                )
                logger.info(f"JVM 启动成功: {jvm_path}")
            self._jvm_started = True
        except Exception as e:
            logger.error(f"JVM 启动失败: {e}")
            raise
    
    def _get_jvm_path(self) -> str:
        """获取 JVM 路径"""
        if self.config.jvm_lib:
            return self.config.jvm_lib
            
        import platform
        system = platform.system()
        
        # 常见 JVM 路径
        common_paths = []
        
        if system == "Darwin":  # macOS
            common_paths = [
                "/Users/tianyi/Library/Java/JavaVirtualMachines/graalvm-jdk-21.0.7/Contents/Home/lib/server/libjvm.dylib",
                "/Users/tianyi/Library/Java/JavaVirtualMachines/corretto-17.0.17/Contents/Home/lib/server/libjvm.dylib",
                "/Users/tianyi/Library/Java/JavaVirtualMachines/corretto-17.0.15/Contents/Home/lib/server/libjvm.dylib",
                "/Library/Java/JavaVirtualMachines/temurin-17.jdk/Contents/Home/lib/server/libjvm.dylib",
                "/Library/Java/JavaVirtualMachines/jdk-17.jdk/Contents/Home/lib/server/libjvm.dylib",
            ]
        elif system == "Linux":
            common_paths = [
                "/usr/lib/jvm/java-17-openjdk/lib/server/libjvm.so",
                "/usr/lib/jvm/java-17-temurin/lib/server/libjvm.so",
            ]
        elif system == "Windows":
            common_paths = [
                "C:\\Program Files\\Java\\jdk-17\\bin\\server\\jvm.dll",
            ]
        
        for path in common_paths:
            if os.path.exists(path):
                return path
        
        # 尝试使用 jpype 获取默认路径
        try:
            import jpype
            default_path = jpype.getDefaultJVMPath()
            if default_path and os.path.exists(default_path):
                return default_path
        except:
            pass
        
        return None
    
    @contextmanager
    def get_connection(self):
        """获取连接上下文管理器"""
        import jaydebeapi
        
        conn = None
        try:
            conn = jaydebeapi.connect(
                self.config.driver_class,
                self.config.jdbc_url,
                [self.config.username, self.config.password],
                os.path.join(os.path.dirname(__file__), "yashandb-jdbc-1.7.19-21.jar")
            )
            logger.debug("数据库连接已创建")
            yield conn
        finally:
            if conn:
                try:
                    conn.close()
                    logger.debug("数据库连接已关闭")
                except:
                    pass

# 全局连接池
_db_pool = None

def get_pool() -> ConnectionPool:
    """获取连接池"""
    global _db_pool
    if _db_pool is None:
        config = DatabaseConfig.from_env()
        _db_pool = ConnectionPool(config)
    return _db_pool

# ============================================================
# SQL 执行引擎
# ============================================================

class SQLEngine:
    """SQL 执行引擎"""
    
    # SQL 类型识别
    SQL_TYPES = {
        'SELECT': 'QUERY',
        'WITH': 'QUERY',
        'EXPLAIN': 'QUERY',
        'INSERT': 'DML',
        'UPDATE': 'DML',
        'DELETE': 'DML',
        'MERGE': 'DML',
        'CREATE': 'DDL',
        'ALTER': 'DDL',
        'DROP': 'DDL',
        'TRUNCATE': 'DDL',
        'GRANT': 'DCL',
        'REVOKE': 'DCL',
        'COMMIT': 'TCL',
        'ROLLBACK': 'TCL',
        'SAVEPOINT': 'TCL',
    }
    
    @classmethod
    def get_sql_type(cls, sql: str) -> str:
        """获取 SQL 类型"""
        first_word = sql.strip().split()[0].upper() if sql.strip() else ''
        return cls.SQL_TYPES.get(first_word, 'UNKNOWN')
    
    @classmethod
    def _can_manage_transactions(cls, conn) -> bool:
        """仅在连接未启用 auto-commit 时手动提交/回滚"""
        try:
            return not conn.jconn.getAutoCommit()
        except Exception:
            return False

    @classmethod
    @monitor_performance
    def execute(cls, sql: str, max_rows: int = 1000) -> SQLResult:
        """执行 SQL"""
        start_time = time.time()
        sql_type = cls.get_sql_type(sql)
        conn = None
        
        try:
            with get_pool().get_connection() as conn:
                cursor = conn.cursor()
                try:
                    cursor.execute(sql)
                    
                    if sql_type == 'QUERY':
                        # 查询操作
                        columns = [desc[0] for desc in cursor.description] if cursor.description else []
                        rows = cursor.fetchmany(max_rows)
                        data = []
                        for row in rows:
                            row_dict = {}
                            for i, col in enumerate(columns):
                                value = row[i]
                                # 处理特殊类型
                                if isinstance(value, datetime.datetime):
                                    value = value.isoformat()
                                elif isinstance(value, bytes):
                                    value = value.decode('utf-8', errors='replace')
                                row_dict[col] = value
                            data.append(row_dict)
                        
                        return SQLResult(
                            success=True,
                            data=data,
                            columns=columns,
                            row_count=len(data),
                            execution_time=time.time() - start_time,
                            sql_type=sql_type
                        )
                    else:
                        # DML/DDL 操作
                        if sql_type in {'DML', 'DDL', 'TCL'} and cls._can_manage_transactions(conn):
                            conn.commit()
                        row_count = cursor.rowcount if hasattr(cursor, 'rowcount') else 0
                        return SQLResult(
                            success=True,
                            row_count=row_count,
                            execution_time=time.time() - start_time,
                            sql_type=sql_type
                        )
                        
                finally:
                    cursor.close()
                    
        except Exception as e:
            if conn and sql_type in {'DML', 'DDL', 'TCL'} and cls._can_manage_transactions(conn):
                try:
                    conn.rollback()
                except Exception:
                    pass
            logger.error(f"SQL 执行失败: {sql[:100]}... 错误: {e}")
            return SQLResult(
                success=False,
                error=str(e),
                execution_time=time.time() - start_time,
                sql_type=sql_type
            )

# ============================================================
# 元数据管理
# ============================================================

class MetadataManager:
    """元数据管理器"""
    
    @staticmethod
    @monitor_performance
    def list_schemas() -> List[str]:
        """列出所有 Schema"""
        sql = """
            SELECT USERNAME FROM ALL_USERS 
            WHERE USERNAME NOT IN ('SYS', 'SYSTEM', 'PUBLIC')
            ORDER BY USERNAME
        """
        result = SQLEngine.execute(sql)
        if result.success and result.data:
            return [row['USERNAME'] for row in result.data]
        return []
    
    @staticmethod
    @monitor_performance
    def list_tables(schema: str = None) -> List[TableInfo]:
        """列出表"""
        if schema:
            sql = """
                SELECT TABLE_NAME, OWNER
                FROM ALL_TABLES
                WHERE OWNER = '{}'
                ORDER BY TABLE_NAME
            """.format(schema.upper())
        else:
            sql = """
                SELECT TABLE_NAME, OWNER
                FROM ALL_TABLES
                ORDER BY OWNER, TABLE_NAME
            """
        
        result = SQLEngine.execute(sql)
        tables = []
        if result.success and result.data:
            for row in result.data:
                tables.append(TableInfo(
                    name=row.get('TABLE_NAME', ''),
                    owner=row.get('OWNER', ''),
                    table_type='TABLE',
                    comment=''
                ))
        return tables
    
    @staticmethod
    @monitor_performance
    def describe_table(table_name: str, schema: str = None) -> List[ColumnInfo]:
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
        
        result = SQLEngine.execute(sql)
        columns = []
        if result.success and result.data:
            for row in result.data:
                columns.append(ColumnInfo(
                    name=row.get('COLUMN_NAME', ''),
                    data_type=row.get('DATA_TYPE', ''),
                    length=row.get('DATA_LENGTH', 0),
                    nullable=row.get('NULLABLE', 'Y') == 'Y',
                    default=row.get('DATA_DEFAULT'),
                    comment=''
                ))
        return columns
    
    @staticmethod
    @monitor_performance
    def search_tables(pattern: str, schema: str = None) -> List[TableInfo]:
        """搜索表"""
        schema_filter = f"AND OWNER = '{schema.upper()}'" if schema else ""
        
        sql = f"""
            SELECT TABLE_NAME, OWNER
            FROM ALL_TABLES
            WHERE TABLE_NAME LIKE '%{pattern.upper()}%' 
            {schema_filter}
            ORDER BY OWNER, TABLE_NAME
        """
        
        result = SQLEngine.execute(sql)
        tables = []
        if result.success and result.data:
            for row in result.data:
                tables.append(TableInfo(
                    name=row.get('TABLE_NAME', ''),
                    owner=row.get('OWNER', ''),
                    comment=''
                ))
        return tables
    
    @staticmethod
    @monitor_performance
    def get_table_indexes(table_name: str, schema: str = None) -> List[Dict]:
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
        
        result = SQLEngine.execute(sql)
        return result.data if result.success else []
    
    @staticmethod
    @monitor_performance
    def get_table_count(table_name: str, schema: str = None) -> int:
        """获取表行数"""
        full_table = f"{schema.upper()}.{table_name.upper()}" if schema else table_name.upper()
        sql = f"SELECT COUNT(*) as count FROM {full_table}"
        
        result = SQLEngine.execute(sql)
        if result.success and result.data:
            return result.data[0].get('COUNT', 0)
        return 0

# ============================================================
# MCP 服务器初始化
# ============================================================

mcp = FastMCP("YashanDB MCP Server Pro")


class BearerAuthMiddleware:
    """为 MCP 入口提供可选 Bearer Token 鉴权"""

    def __init__(self, app, token: str, protected_prefixes: List[str]):
        self.app = app
        self.token = token
        self.protected_prefixes = tuple(protected_prefixes)

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http" or not self.token:
            await self.app(scope, receive, send)
            return

        request = Request(scope, receive=receive)
        if request.url.path.startswith(self.protected_prefixes):
            auth_header = request.headers.get("authorization", "")
            expected = f"Bearer {self.token}"
            if auth_header != expected:
                response = JSONResponse(
                    {"error": "Unauthorized", "message": "Missing or invalid bearer token"},
                    status_code=401,
                )
                await response(scope, receive, send)
                return
        await self.app(scope, receive, send)


class HealthcheckApp:
    """在现有 ASGI 应用前增加健康检查入口"""

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http" and scope.get("path") == "/healthz":
            response = JSONResponse({"ok": True, "service": "yashan-mcp"})
            await response(scope, receive, send)
            return
        await self.app(scope, receive, send)


def create_http_app(auth_token: str):
    """创建带健康检查和鉴权的 HTTP MCP 应用"""
    http_app = mcp.streamable_http_app()
    if auth_token:
        http_app = BearerAuthMiddleware(http_app, auth_token, ["/mcp"])
    return HealthcheckApp(http_app)


def create_sse_app(auth_token: str):
    """创建带健康检查和鉴权的 SSE MCP 应用"""
    sse_app = mcp.sse_app()
    if auth_token:
        sse_app = BearerAuthMiddleware(sse_app, auth_token, ["/sse", "/messages"])
    return HealthcheckApp(sse_app)

# ============================================================
# MCP 工具定义
# ============================================================

@mcp.tool()
def test_connection() -> str:
    """测试数据库连接"""
    try:
        config = DatabaseConfig.from_env()
        sql = "SELECT USER FROM DUAL"
        result = SQLEngine.execute(sql)
        
        if result.success:
            return f"""✅ 崖山数据库连接正常！
主机：{config.jdbc_url.split('//')[1].split('/')[0]}
用户：{config.username}
当前会话用户：{result.data[0].get('USER', 'N/A') if result.data else 'N/A'}
数据库：{config.jdbc_url.split('/')[-1].split('?')[0]}
驱动：JayDeBeApi + YashanDB JDBC"""
        else:
            return f"❌ 连接失败: {result.error}"
    except Exception as e:
        logger.error(f"连接测试失败: {e}")
        return f"❌ 连接失败: {str(e)}"

@mcp.tool()
def run_sql(sql_query: str, max_rows: int = 100) -> str:
    """
    执行 SQL 查询
    
    参数:
        sql_query: SQL 语句
        max_rows: 最大返回行数（默认 100）
    """
    try:
        result = SQLEngine.execute(sql_query, max_rows)
        
        if not result.success:
            return "❌ SQL 执行失败\n错误信息：" + str(result.error)
        
        if result.sql_type == 'QUERY':
            # 格式化查询结果
            if not result.data:
                return "✅ 查询成功，但没有返回任何数据。"
            
            # 构建表格
            lines = []
            lines.append("✅ 查询成功！共 " + str(result.row_count) + " 行")
            
            # 表头
            headers = result.columns
            col_widths = [max(len(str(row.get(col, ''))) for row in result.data + [{col: col}]) for col in headers]
            
            # 分隔线
            sep_line = '├' + '┼'.join('─' * (w + 2) for w in col_widths) + '┤'
            top_line = '┌' + '┬'.join('─' * (w + 2) for w in col_widths) + '┐'
            bottom_line = '└' + '┴'.join('─' * (w + 2) for w in col_widths) + '┘'
            
            lines.append(top_line)
            header_row = '│' + '│'.join(" " + str(col).ljust(col_widths[i]) + " " for i, col in enumerate(headers)) + '│'
            lines.append(header_row)
            lines.append(sep_line)
            
            # 数据行
            for row in result.data:
                data_row = '│' + '│'.join(" " + str(row.get(col, '')).ljust(col_widths[i]) + " " for i, col in enumerate(headers)) + '│'
                lines.append(data_row)
            
            lines.append(bottom_line)
            lines.append("\n执行时间: " + str(round(result.execution_time, 3)) + "s")
            
            return '\n'.join(lines)
        else:
            return "✅ 执行成功\n影响行数: " + str(result.row_count) + "\n执行时间: " + str(round(result.execution_time, 3)) + "s"
            
    except Exception as e:
        logger.error("SQL 执行异常: " + str(e))
        return "❌ SQL 执行异常: " + str(e)

@mcp.tool()
def list_schemas() -> str:
    """列出所有 Schema（用户）"""
    try:
        schemas = MetadataManager.list_schemas()
        if schemas:
            return "✅ Schema 列表:\n" + '\n'.join(f"  - {s}" for s in schemas)
        return "⚠️ 未找到任何 Schema"
    except Exception as e:
        return f"❌ 查询失败: {str(e)}"

@mcp.tool()
def list_tables(schema: str = "") -> str:
    """
    列出表
    
    参数:
        schema: 可选，指定 Schema 名
    """
    try:
        tables = MetadataManager.list_tables(schema if schema else None)
        if tables:
            lines = [f"✅ 共找到 {len(tables)} 个表:"]
            for t in tables:
                comment = f" - {t.comment}" if t.comment else ""
                lines.append(f"  - {t.owner}.{t.name}{comment}")
            return '\n'.join(lines)
        return f"⚠️ 在 Schema '{schema}' 下未找到任何表" if schema else "⚠️ 未找到任何表"
    except Exception as e:
        return f"❌ 查询失败: {str(e)}"

@mcp.tool()
def describe_table(table_name: str, schema: str = "") -> str:
    """
    查看表结构
    
    参数:
        table_name: 表名
        schema: 可选，指定 Schema 名
    """
    try:
        columns = MetadataManager.describe_table(table_name, schema if schema else None)
        if columns:
            lines = [f"✅ 表 {schema + '.' if schema else ''}{table_name} 的结构:", ""]
            lines.append(f"{'列名':<30} {'类型':<20} {'长度':<10} {'可空':<8} {'默认值':<20}")
            lines.append("-" * 90)
            for col in columns:
                nullable = "是" if col.nullable else "否"
                name = _to_display_str(col.name)
                data_type = _to_display_str(col.data_type)
                length = _to_display_str(col.length)
                default = _to_display_str(col.default)
                lines.append(
                    f"{name:<30} {data_type:<20} {length:<10} {nullable:<8} {default:<20}"
                )
                if col.comment:
                    lines.append(f"  注释: {_to_display_str(col.comment)}")
            return '\n'.join(lines)
        return f"⚠️ 在 Schema '{schema}' 下未找到表 '{table_name}'" if schema else f"⚠️ 未找到表 '{table_name}'"
    except Exception as e:
        return f"❌ 查询失败: {str(e)}"

@mcp.tool()
def search_tables(pattern: str, schema: str = "") -> str:
    """
    搜索表
    
    参数:
        pattern: 表名关键字（支持模糊搜索）
        schema: 可选，限定在某个 Schema 下搜索
    """
    try:
        tables = MetadataManager.search_tables(pattern, schema if schema else None)
        if tables:
            lines = [f"✅ 找到 {len(tables)} 个匹配 '{pattern}' 的表:"]
            for t in tables:
                comment = f" - {t.comment}" if t.comment else ""
                lines.append(f"  - {t.owner}.{t.name}{comment}")
            return '\n'.join(lines)
        return f"⚠️ 未找到包含 '{pattern}' 的表"
    except Exception as e:
        return f"❌ 查询失败: {str(e)}"

@mcp.tool()
def get_table_indexes(table_name: str, schema: str = "") -> str:
    """
    查看表索引
    
    参数:
        table_name: 表名
        schema: 可选，指定 Schema
    """
    try:
        schema_filter = f"AND OWNER = '{schema.upper()}'" if schema else ""
        sql = f"""SELECT INDEX_NAME, INDEX_TYPE, UNIQUENESS 
                 FROM ALL_INDEXES 
                 WHERE TABLE_NAME = '{table_name.upper()}' {schema_filter}
                 ORDER BY INDEX_NAME"""
        result = run_sql(sql, max_rows=50)
        return result
    except Exception as e:
        return f"❌ 查询失败: {str(e)}"

@mcp.tool()
def get_table_count(table_name: str, schema: str = "") -> str:
    """
    快速获取表行数
    
    参数:
        table_name: 表名
        schema: 可选，指定 Schema
    """
    try:
        count = MetadataManager.get_table_count(table_name, schema if schema else None)
        full_name = f"{schema}.{table_name}" if schema else table_name
        return f"✅ 表 {full_name} 的行数: {count}"
    except Exception as e:
        return f"❌ 查询失败: {str(e)}"

@mcp.tool()
def get_database_info() -> str:
    """获取数据库信息"""
    try:
        config = DatabaseConfig.from_env()
        host_port = config.jdbc_url.split('//')[1].split('/')[0] if '//' in config.jdbc_url else 'unknown'
        db_name = config.jdbc_url.split('/')[-1].split('?')[0] if '/' in config.jdbc_url else 'unknown'
        
        return f"""📊 崖山数据库环境信息
{'='*50}
连接地址：{host_port}
数据库名：{db_name}
用户名：{config.username}
驱动类：{config.driver_class}
当前时间：{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"""
    except Exception as e:
        return f"❌ 获取信息失败: {str(e)}"

@mcp.tool()
def explain_sql(sql_query: str) -> str:
    """
    获取 SQL 执行计划
    
    参数:
        sql_query: SQL 语句
    """
    try:
        explain_statement = f"EXPLAIN {sql_query}"
        result = SQLEngine.execute(explain_statement, max_rows=200)
        
        if result.success and result.data:
            lines = ["✅ SQL 执行计划:"]
            for row in result.data:
                plan_line = _to_display_str(row.get("PLAN_DESCRIPTION", ""))
                if plan_line:
                    lines.append(plan_line)
            return '\n'.join(lines)
        return "⚠️ 无法获取执行计划"
    except Exception as e:
        return f"❌ 获取执行计划失败: {str(e)}"

# ============================================================
# 主程序入口
# ============================================================

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="崖山数据库 MCP Server Pro")
    parser.add_argument("--mode", choices=["stdio", "http", "sse"], default="http",
                       help="运行模式：http（默认）、stdio、sse")
    parser.add_argument("--host", default="0.0.0.0", help="HTTP/SSE 模式监听地址")
    parser.add_argument("--port", type=int, default=8080, help="HTTP/SSE 模式监听端口")
    parser.add_argument(
        "--auth-token",
        default=os.getenv("MCP_AUTH_TOKEN", ""),
        help="可选 Bearer Token；也可通过 MCP_AUTH_TOKEN 环境变量设置",
    )
    parser.add_argument("--log-level", choices=["DEBUG", "INFO", "WARNING", "ERROR"], 
                       default="INFO", help="日志级别")
    args = parser.parse_args()
    
    # 设置日志级别
    logging.getLogger("yashan_mcp").setLevel(getattr(logging, args.log_level))
    
    # 预热连接池
    logger.info("正在初始化连接池...")
    get_pool()

    config = DatabaseConfig.from_env()
    logger.info("YashanDB MCP Server 启动中")
    logger.info("数据库: %s", config.jdbc_url)
    logger.info("模式: %s", args.mode)
    
    if args.mode == "stdio":
        mcp.run()
    elif args.mode == "http":
        import uvicorn
        if args.auth_token:
            logger.info("HTTP MCP 鉴权已启用")
        logger.info("HTTP MCP 监听地址: http://%s:%s/mcp", args.host, args.port)
        logger.info("健康检查地址: http://%s:%s/healthz", args.host, args.port)
        uvicorn.run(create_http_app(args.auth_token), host=args.host, port=args.port)
    elif args.mode == "sse":
        import uvicorn
        if args.auth_token:
            logger.info("SSE MCP 鉴权已启用")
        logger.info("SSE MCP 入口: http://%s:%s/sse", args.host, args.port)
        logger.info("健康检查地址: http://%s:%s/healthz", args.host, args.port)
        uvicorn.run(create_sse_app(args.auth_token), host=args.host, port=args.port)
