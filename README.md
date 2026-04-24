# 崖山数据库 MCP SSE Server

一个用于连接崖山数据库（YashanDB）的 MCP（Model Context Protocol）SSE 服务器，让 AI 助手能够自然语言查询崖山数据库。

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

## 特性

- 🔌 **完整的数据库操作**：支持查询、插入、更新、删除等所有 SQL 操作
- 🤖 **MCP SSE 协议支持**：与 Claude Desktop / Cursor / Trae 无缝集成
- 📊 **元数据管理**：表结构查看、索引查询、表搜索等功能
- 🔍 **支持多 Schema 自动降级**
- ⚡ **跨平台兼容**：使用 Java 子进程调用 JDBC，支持 Windows 和 Mac
- 🛡️ **完善的错误处理**：详细的错误信息和日志记录
- 📝 **Oracle 兼容**：高度兼容 Oracle SQL 语法

## 前置要求

- Python 3.10+
- Java 17+（JDK，需要 javac 和 java 命令）
- 崖山数据库或其他兼容数据库
- 崖山 JDBC 驱动（`yashandb-jdbc-1.9.3.jar`）

## 支持的数据库

- 崖山数据库（YashanDB）
- Oracle 兼容的数据库

## 安装

```bash
pip install -r requirements.txt
```

## 配置

### 使用 .env 文件（推荐）

1. 复制配置模板：
```bash
cp .env.example .env
```

2. 编辑 `.env` 文件，填入你的数据库信息：
```bash
DB_HOST=your_database_host
DB_PORT=1688
DB_NAME=yashandb
DB_USER=your_username
DB_PASSWORD=your_password
```

### 使用环境变量

```bash
export DB_HOST=your_database_host
export DB_PORT=1688
export DB_NAME=yashandb
export DB_USER=your_username
export DB_PASSWORD=your_password
python server.py --host 0.0.0.0 --port 20302
```

### 使用完整的 JDBC URL

如果你的数据库有特殊的连接参数，可以直接设置完整的 JDBC URL：

```bash
export DB_JDBC_URL="jdbc:yasdb://host:port/dbname?param=value"
```

## 运行

```bash
python server.py --host 0.0.0.0 --port 20302
```

### 端点

- **MCP 端点**: `http://localhost:20302/mcp` (推荐)
- **SSE 端点**: `http://localhost:20302/sse` (兼容)
- **健康检查**: `http://localhost:20302/healthz`
- **日志目录**: `log/yashan_mcp_YYYY-MM-DD.log`（按天追加）

### Windows 开机自动启动

详见 [docs/WINDOWS_AUTOSTART.md](./docs/WINDOWS_AUTOSTART.md)

## MCP 工具能力

| 工具名 | 描述 | 参数 |
|--------|------|------|
| `test_connection` | 测试数据库连接 | - |
| `run_sql` | 执行 SQL 查询 | `sql_query`: SQL语句<br>`max_rows`: 最大返回行数 |
| `list_schemas` | 列出所有 Schema（用户） | - |
| `list_tables` | 列出表 | `schema`: 可选，指定 Schema 名 |
| `describe_table` | 查看表结构 | `table_name`: 表名<br>`schema`: 可选，指定 Schema |
| `search_tables` | 搜索表 | `pattern`: 表名关键字<br>`schema`: 可选，限定 Schema |
| `get_table_indexes` | 查看表索引 | `table_name`: 表名<br>`schema`: 可选，指定 Schema |
| `get_table_count` | 快速获取表行数 | `table_name`: 表名<br>`schema`: 可选，指定 Schema |
| `get_database_info` | 获取数据库信息 | - |
| `explain_sql` | 获取 SQL 执行计划 | `sql_query`: SQL语句 |

## 与 Claude Desktop 集成

在 `claude_desktop_config.json` 中添加：

```json
{
  "mcpServers": {
    "yashan": {
      "command": "python",
      "args": ["/path/to/server.py", "--host", "0.0.0.0", "--port", "20302"]
    }
  }
}
```

## 许可证

MIT License
