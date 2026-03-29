#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
崖山数据库 MCP Server - Yashan DB Helper

这是一个连接到崖山数据库的 MCP 服务器，
向 AI（如 Claude、Cursor 等）暴露数据库查询工具，
让 AI 能够自然语言执行 SQL 查询崖山数据库中的数据。

使用 JayDeBeApi + JDBC 驱动连接崖山数据库。

优化版：支持多 Schema 自动降级、模糊搜索表、增强元数据查询
"""

from mcp.server.fastmcp import FastMCP
import json
import datetime
import os
from typing import Optional, List, Dict, Any

# ============================================================
# 配置部分
# ============================================================

# JDBC 驱动路径
JDBC_DRIVER_PATH = os.path.join(os.path.dirname(__file__), "yashandb-jdbc-1.7.19-21.jar")

# 崖山数据库 JDBC URL（支持环境变量覆盖）
JDBC_URL = os.getenv("DB_JDBC_URL", "jdbc:yasdb://localhost:1688/yashandb?failover=on&failoverType=session&failoverMethod=basic&failoverRetries=5&failoverDelay=1")

# 数据库连接配置（支持环境变量覆盖）
DATABASE_CONFIG = {
    "driver_class": "com.yashandb.jdbc.Driver",
    "jdbc_url": JDBC_URL,
    "username": os.getenv("DB_USER", "your_username"),
    "password": os.getenv("DB_PASSWORD", "your_password"),
    "jvm_lib": os.getenv("JVM_LIB", ""),  # 自动检测
}

# 常用 Schema 列表（用于快速切换和搜索）
KNOWN_SCHEMAS = [
    "***REMOVED***",
    "***REMOVED***",
    "SZ_NCIS_BILL",
    "SZ_NCIS_SEARCH",
    "SZ_NCIS_ORDER",
]

# ============================================================
# 数据库连接
# ============================================================

db_connection = None
_jvm_started = False

def _get_jvm_path():
    """自动检测 JVM 路径"""
    if DATABASE_CONFIG["jvm_lib"]:
        return DATABASE_CONFIG["jvm_lib"]

    import platform
    system = platform.system()

    # 常见 JVM 路径
    common_paths = []

    if system == "Darwin":  # macOS
        common_paths = [
            "/Library/Java/JavaVirtualMachines/temurin-17.jdk/Contents/Home/lib/server/libjvm.dylib",
            "/Library/Java/JavaVirtualMachines/jdk-17.jdk/Contents/Home/lib/server/libjvm.dylib",
            "/Library/Java/JavaVirtualMachines/corretto-17.jdk/Contents/Home/lib/server/libjvm.dylib",
            "/Library/Java/JavaVirtualMachines/graalvm-jdk-21.0.7/Contents/Home/lib/server/libjvm.dylib",
        ]
    elif system == "Linux":
        common_paths = [
            "/usr/lib/jvm/java-17-openjdk/lib/server/libjvm.so",
            "/usr/lib/jvm/java-17-temurin/lib/server/libjvm.so",
            "/usr/lib/jvm/default-java/lib/server/libjvm.so",
        ]
    elif system == "Windows":
        common_paths = [
            "C:\\Program Files\\Java\\jdk-17\\bin\\server\\jvm.dll",
            "C:\\Program Files\\Eclipse Adoptium\\jdk-17\\bin\\server\\jvm.dll",
        ]

    import os
    for path in common_paths:
        if os.path.exists(path):
            return path

    # 尝试使用默认路径
    default_path = jpype.getDefaultJVMPath()
    if default_path and os.path.exists(default_path):
        return default_path

    return None

def _ensure_jvm():
    """确保 JVM 已启动"""
    global _jvm_started
    if not _jvm_started:
        import jpype
        if not jpype.isJVMStarted():
            jvm_path = _get_jvm_path()
            if not jvm_path:
                raise RuntimeError("找不到 JVM！请安装 JDK 17+ 或设置 JVM_LIB 环境变量")
            print(f"[✓] 使用 JVM: {jvm_path}")
            jpype.startJVM(
                jvm_path,
                f"-Djava.class.path={JDBC_DRIVER_PATH}",
                ignoreUnrecognized=True
            )
            print("[✓] JVM 启动成功")
        _jvm_started = True

def get_connection():
    """获取崖山数据库连接"""
    global db_connection

    if db_connection is not None:
        try:
            cursor = db_connection.cursor()
            cursor.execute("SELECT 1 FROM DUAL")
            cursor.fetchone()
            cursor.close()
            return db_connection
        except Exception:
            db_connection = None

    try:
        _ensure_jvm()
        import jaydebeapi

        db_connection = jaydebeapi.connect(
            DATABASE_CONFIG["driver_class"],
            DATABASE_CONFIG["jdbc_url"],
            [DATABASE_CONFIG["username"], DATABASE_CONFIG["password"]],
            JDBC_DRIVER_PATH
        )
        print("[✓] 已通过 JDBC 驱动连接到崖山数据库")
        return db_connection
    except Exception as e:
        print(f"[!] JDBC 连接失败: {e}")
        return None


def close_connection():
    """关闭数据库连接"""
    global db_connection, _jvm_started
    if db_connection:
        try:
            db_connection.close()
        except Exception:
            pass
        db_connection = None

    if _jvm_started:
        try:
            import jpype
            jpype.shutdownJVM()
            _jvm_started = False
        except Exception:
            pass


# ============================================================
# SQL 执行
# ============================================================

def _execute_sql(sql: str, max_rows: int = 1000) -> Dict[str, Any]:
    """执行 SQL 并返回结果"""
    conn = get_connection()
    if conn is None:
        return {
            "success": False,
            "error": "无法连接到崖山数据库",
            "sql": sql,
        }

    try:
        cursor = conn.cursor()
        cursor.execute(sql)

        if cursor.description:
            columns = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()
            result = {
                "success": True,
                "columns": columns,
                "rows": [list(row) for row in rows],
                "row_count": len(rows),
                "sql": sql,
                "truncated": len(rows) >= max_rows,
            }
        else:
            result = {
                "success": True,
                "columns": [],
                "rows": [],
                "row_count": 0,
                "message": "执行成功，无返回数据",
                "sql": sql,
            }

        cursor.close()
        return result

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "sql": sql,
        }


def _format_result(result: Dict, show_sql: bool = True) -> str:
    """将查询结果格式化为易读的文本"""
    if not result.get("success"):
        error = result.get("error", "未知错误")
        return f"❌ SQL 执行失败\n错误信息：{error}"

    columns = result.get("columns", [])
    rows = result.get("rows", [])
    row_count = result.get("row_count", 0)
    truncated = result.get("truncated", False)
    sql = result.get("sql", "")

    if not rows:
        return f"✅ 执行成功\n查询成功，但没有返回任何数据。"

    lines = []
    if show_sql:
        lines.append(f"✅ 查询成功！共 {row_count} 行" + ("（结果已截断）" if truncated else ""))
    else:
        lines.append(f"✅ 共 {row_count} 行" + ("（结果已截断）" if truncated else ""))

    # 计算列宽
    col_widths = [len(str(col)) for col in columns]
    for row in rows:
        for i, val in enumerate(row):
            col_widths[i] = max(col_widths[i], min(len(str(val)), 50))

    # 格式化表格
    header_line = "│ " + " │ ".join(str(col).ljust(col_widths[i]) for i, col in enumerate(columns)) + " │"
    separator = "├" + "┼".join("─" * (w + 2) for w in col_widths) + "┤"

    lines.append(separator)
    lines.append(header_line)
    lines.append(separator.replace("┼", "┬").replace("─", "─"))

    for row in rows:
        row_line = "│ " + " │ ".join(str(val)[:col_widths[i]].ljust(col_widths[i]) for i, val in enumerate(row)) + " │"
        lines.append(row_line)

    lines.append(separator.replace("┼", "┴").replace("─", "─"))

    return "\n".join(lines)


# ============================================================
# MCP 工具
# ============================================================

mcp = FastMCP("Yashan DB Helper")


@mcp.tool()
def test_connection() -> str:
    """
    测试崖山数据库连接是否正常。

    Returns:
        连接状态信息
    """
    conn = get_connection()
    if conn:
        # 获取一些基本信息
        user_result = _execute_sql("SELECT USER FROM DUAL")
        user = user_result.get("rows", [[""]])[0][0] if user_result.get("success") else "未知"

        return f"✅ 崖山数据库连接正常！\n" \
               f"主机：***REMOVED***:1688\n" \
               f"用户：{DATABASE_CONFIG['username']}\n" \
               f"当前会话用户：{user}\n" \
               f"数据库：yashandb\n" \
               f"驱动：JayDeBeApi + YashanDB JDBC"
    else:
        return "❌ 无法连接到崖山数据库"


@mcp.tool()
def list_schemas() -> str:
    """
    列出数据库中所有的 Schema（用户/Owner）。

    Returns:
        Schema 列表
    """
    result = _execute_sql("SELECT DISTINCT OWNER FROM ALL_TABLES ORDER BY OWNER")
    return _format_result(result)


@mcp.tool()
def list_tables(schema: str = "") -> str:
    """
    列出崖山数据库中的表。

    Args:
        schema: 可选，指定 Schema 名（如 ***REMOVED***）。不指定时列出当前用户下的表。

    Returns:
        表列表
    """
    if schema:
        sql = f"SELECT TABLE_NAME, OWNER FROM ALL_TABLES WHERE OWNER = '{schema.upper()}' ORDER BY TABLE_NAME"
    else:
        sql = "SELECT TABLE_NAME FROM USER_TABLES ORDER BY TABLE_NAME"

    result = _execute_sql(sql)
    return _format_result(result)


@mcp.tool()
def search_tables(pattern: str, schema: str = "") -> str:
    """
    搜索表名包含指定关键字的表。

    Args:
        pattern: 表名关键字（支持模糊搜索，不区分大小写）
        schema: 可选，限定在某个 Schema 下搜索

    Returns:
        匹配的表列表
    """
    pattern_upper = pattern.upper()
    if schema:
        sql = f"SELECT TABLE_NAME, OWNER FROM ALL_TABLES WHERE TABLE_NAME LIKE '%{pattern_upper}%' AND OWNER = '{schema.upper()}' ORDER BY OWNER, TABLE_NAME"
    else:
        sql = f"SELECT TABLE_NAME, OWNER FROM ALL_TABLES WHERE TABLE_NAME LIKE '%{pattern_upper}%' ORDER BY OWNER, TABLE_NAME"

    result = _execute_sql(sql)
    return _format_result(result)


@mcp.tool()
def describe_table(table_name: str, schema: str = "") -> str:
    """
    查看崖山数据库中指定表的详细结构。

    包含列名、数据类型、是否可空、默认值、字段注释、主键、外键等信息。
    支持自动降级：如果当前用户下找不到，会自动尝试 ALL_TAB_COLUMNS。

    Args:
        table_name: 要查看的表名
        schema: 可选，指定 Schema 名（如 ***REMOVED***）

    Returns:
        表结构信息
    """
    table_upper = table_name.upper()

    # 如果指定了 schema，直接查询
    if schema:
        schema_upper = schema.upper()
        sql = f"""
            SELECT
                COLUMN_NAME,
                DATA_TYPE,
                DATA_LENGTH,
                DATA_PRECISION,
                DATA_SCALE,
                NULLABLE,
                DATA_DEFAULT,
                COLUMN_ID
            FROM ALL_TAB_COLUMNS
            WHERE TABLE_NAME = '{table_upper}' AND OWNER = '{schema_upper}'
            ORDER BY COLUMN_ID
        """
        result = _execute_sql(sql)
        if result.get("success") and result.get("rows"):
            return _format_describe_result(result, table_name, schema_upper)
        else:
            return f"❌ 在 Schema {schema_upper} 下未找到表 {table_upper}"

    # 1. 先尝试 USER_TAB_COLUMNS（当前用户）
    sql = f"""
        SELECT
            COLUMN_NAME,
            DATA_TYPE,
            DATA_LENGTH,
            DATA_PRECISION,
            DATA_SCALE,
            NULLABLE,
            DATA_DEFAULT,
            COLUMN_ID
        FROM USER_TAB_COLUMNS
        WHERE TABLE_NAME = '{table_upper}'
        ORDER BY COLUMN_ID
    """
    result = _execute_sql(sql)

    if result.get("success") and result.get("rows"):
        return _format_describe_result(result, table_name, "当前用户")

    # 2. 降级：尝试 ALL_TAB_COLUMNS
    sql = f"""
        SELECT
            ATC.COLUMN_NAME,
            ATC.DATA_TYPE,
            ATC.DATA_LENGTH,
            ATC.DATA_PRECISION,
            ATC.DATA_SCALE,
            ATC.NULLABLE,
            ATC.DATA_DEFAULT,
            ATC.COLUMN_ID,
            ATC.OWNER
        FROM ALL_TAB_COLUMNS ATC
        WHERE ATC.TABLE_NAME = '{table_upper}'
        ORDER BY ATC.OWNER, ATC.COLUMN_ID
    """
    result = _execute_sql(sql)

    if result.get("success") and result.get("rows"):
        # 提取 owner 列
        columns = result.get("columns", [])
        rows = result.get("rows", [])

        # 检查是否有 OWNER 列
        if "OWNER" in columns:
            owner_idx = columns.index("OWNER")
            owners = set(row[owner_idx] for row in rows)
            if len(owners) == 1:
                # 只有一个 owner，直接返回
                rows = [row[:owner_idx] + row[owner_idx+1:] for row in rows]  # 移除 OWNER 列
                result["columns"] = [c for c in columns if c != "OWNER"]
                result["rows"] = rows
                return _format_describe_result(result, table_name, list(owners)[0])
            else:
                # 多个 owner，列出所有可能的 schema
                return f"❌ 表 {table_upper} 在多个 Schema 下存在，请指定 schema：\n" + \
                       "\n".join(f"  - {o}" for o in sorted(owners)) + \
                       f"\n\n使用方式：describe_table(\"{table_name}\", schema=\"SCHEMA_NAME\")"

        return _format_describe_result(result, table_name, "ALL_TAB_COLUMNS")

    # 3. 搜索相似的表名
    search_result = _execute_sql(
        f"SELECT TABLE_NAME, OWNER FROM ALL_TABLES WHERE TABLE_NAME LIKE '%{table_upper}%' ORDER BY OWNER, TABLE_NAME"
    )

    if search_result.get("success") and search_result.get("rows"):
        matches = search_result.get("rows")
        return f"❌ 表 {table_upper} 不存在。\n\n你是不是想找这些表？\n" + \
               _format_result(search_result) + \
               f"\n\n使用方式：describe_table(\"表名\", schema=\"SCHEMA_NAME\")"

    return f"❌ 未找到表 {table_upper}"


def _format_describe_result(result: Dict, table_name: str, schema: str) -> str:
    """格式化表结构查询结果"""
    columns = result.get("columns", [])
    rows = result.get("rows", [])

    if not rows:
        return f"❌ 表 {table_name} 没有列信息"

    lines = [
        f"📋 表结构：{table_name}",
        f"   Schema：{schema}",
        "=" * 80,
        ""
    ]

    # 表头
    lines.append(f"{'序号':<4} {'列名':<30} {'类型':<20} {'可空':<6} {'默认值'}")
    lines.append("-" * 80)

    for row in rows:
        col_name = str(row[0])
        data_type = str(row[1]) if row[1] else ""
        data_length = str(row[2]) if row[2] else ""
        nullable = "否" if row[5] == "N" else "是"
        default = str(row[6])[:20] if row[6] else ""

        # 格式化类型
        if row[3]:  # DATA_PRECISION
            type_str = f"{data_type}({row[3]}"
            if row[4]:
                type_str += f",{row[4]}"
            type_str += ")"
        elif data_length and data_length != "0":
            type_str = f"{data_type}({data_length})"
        else:
            type_str = data_type

        col_id = str(row[7]) if len(row) > 7 else ""
        lines.append(f"{col_id:<4} {col_name:<30} {type_str:<20} {nullable:<6} {default}")

    lines.append("-" * 80)
    lines.append("")

    # 查询主键信息
    pk_result = _execute_sql(
        f"SELECT CC.COLUMN_NAME FROM ALL_CONS_COLUMNS CC "
        f"JOIN ALL_CONSTRAINTS C ON CC.CONSTRAINT_NAME = C.CONSTRAINT_NAME "
        f"WHERE C.TABLE_NAME = '{table_name.upper()}' AND C.CONSTRAINT_TYPE = 'P' AND CC.OWNER = '{schema}'"
    )

    if pk_result.get("success") and pk_result.get("rows"):
        pk_cols = [str(row[0]) for row in pk_result.get("rows", [])]
        lines.append(f"🔑 主键：{', '.join(pk_cols)}")
    else:
        lines.append("🔑 主键：无")

    lines.append("")
    lines.append(f"💡 提示：使用 search_tables(\"{table_name}\") 可以搜索包含该关键字的所有表")

    return "\n".join(lines)


@mcp.tool()
def get_table_indexes(table_name: str, schema: str = "") -> str:
    """
    查看表的索引信息。

    Args:
        table_name: 表名
        schema: 可选，指定 Schema

    Returns:
        索引信息
    """
    if schema:
        sql = f"""
            SELECT
                UIC.INDEX_NAME,
                UIC.COLUMN_NAME,
                CASE WHEN I.UNIQUENESS = 'UNIQUE' THEN '是' ELSE '否' END AS 是否唯一,
                I.INDEX_TYPE
            FROM USER_IND_COLUMNS UIC
            JOIN USER_INDEXES I ON UIC.INDEX_NAME = I.INDEX_NAME
            WHERE UIC.TABLE_NAME = '{table_name.upper()}' AND UIC.TABLE_OWNER = '{schema.upper()}'
            ORDER BY UIC.INDEX_NAME, UIC.COLUMN_POSITION
        """
    else:
        sql = f"""
            SELECT
                INDEX_NAME,
                COLUMN_NAME,
                COLUMN_POSITION,
                UNIQUENESS,
                INDEX_TYPE
            FROM USER_IND_COLUMNS
            WHERE TABLE_NAME = '{table_name.upper()}'
            ORDER BY INDEX_NAME, COLUMN_POSITION
        """

    result = _execute_sql(sql)
    return _format_result(result)


@mcp.tool()
def get_table_count(table_name: str, schema: str = "") -> str:
    """
    快速获取表的行数。

    Args:
        table_name: 表名
        schema: 可选，指定 Schema

    Returns:
        表的行数
    """
    if schema:
        sql = f"SELECT COUNT(*) FROM \"{schema.upper()}\".\"{table_name.upper()}\""
    else:
        sql = f"SELECT COUNT(*) FROM \"{table_name.upper()}\""

    result = _execute_sql(sql)
    if result.get("success") and result.get("rows"):
        count = result.get("rows", [[0]])[0][0]
        return f"📊 表 {schema + '.' if schema else ''}{table_name} 共有 {count:,} 行数据"
    return _format_result(result)


@mcp.tool()
def run_sql(sql_query: str, max_rows: int = 100) -> str:
    """
    在崖山数据库中执行 SQL 查询语句。

    这是最核心的工具。当你需要查询崖山数据库中的数据时，使用这个工具。

    Args:
        sql_query: 要执行的完整 SQL 语句
        max_rows: 最大返回行数，默认 100 行

    Returns:
        格式化的查询结果
    """
    print(f"[SQL 执行] {sql_query}")

    result = _execute_sql(sql_query, max_rows=max_rows)
    return _format_result(result)


@mcp.tool()
def get_database_info() -> str:
    """
    获取崖山数据库的基本信息。

    Returns:
        数据库信息
    """
    version_result = _execute_sql("SELECT * FROM V$VERSION WHERE ROWNUM <= 3")
    user_result = _execute_sql("SELECT USER FROM DUAL")
    schema_result = _execute_sql("SELECT DISTINCT OWNER FROM ALL_TABLES ORDER BY OWNER")

    info_lines = [
        "📊 崖山数据库环境信息",
        "=" * 50,
    ]

    if version_result.get("success") and version_result.get("rows"):
        versions = [row[0] for row in version_result.get("rows", [])]
        info_lines.append(f"数据库版本：{versions[0] if versions else '未知'}")

    if user_result.get("success") and user_result.get("rows"):
        info_lines.append(f"当前用户：{user_result['rows'][0][0]}")

    if schema_result.get("success") and schema_result.get("rows"):
        schemas = [row[0] for row in schema_result.get("rows", [])]
        info_lines.append(f"可用 Schema：{', '.join(schemas)}")

    info_lines.extend([
        f"连接地址：***REMOVED***:1688",
        f"查询时间：{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
    ])

    return "\n".join(info_lines)


# ============================================================
# 启动服务器
# ============================================================

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="崖山数据库 MCP Server")
    parser.add_argument("--mode", choices=["stdio", "http", "sse"], default="stdio",
                       help="运行模式：stdio（默认，本地CLI）, http（HTTP API）, sse（Server-Sent Events）")
    parser.add_argument("--host", default="0.0.0.0", help="HTTP 模式监听地址")
    parser.add_argument("--port", type=int, default=8080, help="HTTP 模式监听端口")
    args = parser.parse_args()

    print("=" * 60)
    print("       崖山数据库 MCP Server  - Yashan DB Helper")
    print("=" * 60)
    print(f"数据库地址：***REMOVED***:1688")
    print(f"数据库用户：{DATABASE_CONFIG['username']}")
    print(f"数据库名  ：yashandb")
    print(f"运行模式  ：{args.mode}")
    print("-" * 60)

    # 预热数据库连接
    print("\n正在连接崖山数据库...")
    get_connection()

    if args.mode == "stdio":
        print("\n✅ 服务器已就绪，等待 AI 客户端连接（stdio 模式）...\n")
        try:
            mcp.run()
        finally:
            close_connection()

    elif args.mode == "http":
        print(f"\n✅ 服务器已就绪，HTTP API 监听 {args.host}:{args.port} ...\n")
        import uvicorn
        try:
            uvicorn.run(mcp.streamable_http_app(), host=args.host, port=args.port)
        finally:
            close_connection()

    elif args.mode == "sse":
        print(f"\n✅ 服务器已就绪，SSE 监听 {args.host}:{args.port} ...\n")
        import uvicorn
        try:
            uvicorn.run(mcp.sse_app(), host=args.host, port=args.port)
        finally:
            close_connection()
