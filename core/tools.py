# -*- coding: utf-8 -*-
"""
MCP 工具定义和处理函数
"""

from typing import Dict, Any, List
from datetime import datetime
from .executor import get_executor
from .metadata import get_metadata


# MCP 工具定义
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


# 工具处理函数

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
        lines = [f"✅ 查询成功！共 {len(res['data'])} 行"]
        columns = res.get("columns", [])
        data = res.get("data", [])

        if columns and data:
            col_widths = [len(str(col)) for col in columns]
            for row in data:
                for i, col in enumerate(columns):
                    col_widths[i] = max(col_widths[i], len(str(row.get(col, ""))))

            header = " | ".join(str(col).ljust(col_widths[i]) for i, col in enumerate(columns))
            separator = "-+-".join("-" * w for w in col_widths)

            lines.append(header)
            lines.append(separator)
            for row in data:
                row_str = " | ".join(str(row.get(col, "")).ljust(col_widths[i]) for i, col in enumerate(columns))
                lines.append(row_str)

        lines.append(f"\n执行时间: {res.get('execution_time', 0):.3f}s")

        return {"content": [{"type": "text", "text": "\n".join(lines)}]}
    else:
        return {
            "content": [{
                "type": "text",
                "text": f"✅ 执行成功！影响行数: {res.get('row_count', 0)}"
            }]
        }


def handle_list_schemas() -> Dict:
    """处理 list_schemas 工具"""
    schemas = get_metadata().list_schemas()
    if schemas:
        lines = ["✅ 所有 Schema（用户）:"]
        for s in schemas:
            lines.append(f"  - {s}")
        return {"content": [{"type": "text", "text": "\n".join(lines)}]}
    return {"content": [{"type": "text", "text": "⚠️ 未找到 Schema"}]}


def handle_list_tables(args: Dict) -> Dict:
    """处理 list_tables 工具"""
    schema = args.get("schema")
    tables = get_metadata().list_tables(schema if schema else None)

    if tables:
        lines = [f"✅ 找到 {len(tables)} 个表:"]
        for t in tables:
            lines.append(f"  - {t['owner']}.{t['name']}")
        return {"content": [{"type": "text", "text": "\n".join(lines)}]}
    return {"content": [{"type": "text", "text": "⚠️ 未找到表"}]}


def handle_describe_table(args: Dict) -> Dict:
    """处理 describe_table 工具"""
    table_name = args.get("table_name", "")
    schema = args.get("schema")
    columns = get_metadata().describe_table(table_name, schema if schema else None)

    if columns:
        lines = [f"✅ 表 {schema + '.' if schema else ''}{table_name} 的结构:"]
        lines.append(f"{'列名':<30} {'类型':<20} {'长度':<10} {'可空':<10}")
        lines.append("-" * 70)
        for col in columns:
            nullable = "是" if col['nullable'] else "否"
            lines.append(f"{col['name']:<30} {col['data_type']:<20} {str(col['length']):<10} {nullable:<10}")
        return {"content": [{"type": "text", "text": "\n".join(lines)}]}
    return {"content": [{"type": "text", "text": f"⚠️ 未找到表 '{table_name}' 的结构"}]}


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
当前时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"""
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


# 工具路由表
TOOL_HANDLERS = {
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


def handle_tool_call(tool_name: str, args: Dict) -> Dict:
    """
    处理工具调用

    Args:
        tool_name: 工具名称
        args: 工具参数

    Returns:
        工具执行结果
    """
    handler = TOOL_HANDLERS.get(tool_name)
    if handler:
        try:
            if args:
                return handler(args)
            else:
                return handler()
        except Exception as e:
            return {
                "content": [{"type": "text", "text": f"❌ 工具执行错误: {str(e)}"}],
                "isError": True
            }
    else:
        return {
            "content": [{"type": "text", "text": f"❌ 未知工具: {tool_name}"}],
            "isError": True
        }
