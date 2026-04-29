# 崖山数据库 MCP Server

一个用于连接崖山数据库（YashanDB）的 MCP（Model Context Protocol）Server，让 AI 助手能够自然语言查询崖山数据库。

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

## 使用模式

本项目支持两种使用模式：

### 🌟 STDIO 模式（推荐）

**按需启动，用完即退，资源占用低**

适合：本地开发、AI 工具集成（Kiro、Claude Desktop 等）

```bash
python3 mcp_server.py
```

详见 [STDIO 模式文档](./docs/STDIO_MODE.md)

### 🌐 HTTP 模式

**常驻服务，支持远程访问**

适合：远程访问、多用户共享、高频查询

```bash
python3 server.py --host 0.0.0.0 --port 20302
```

详见 [HTTP 模式文档](./docs/HTTP_MODE.md)

---

## 快速入口

- **STDIO 模式**（推荐）：[docs/STDIO_MODE.md](./docs/STDIO_MODE.md)
- **HTTP 模式**：[docs/HTTP_MODE.md](./docs/HTTP_MODE.md)
- 快速上手：[docs/QUICK_START.md](./docs/QUICK_START.md)
- SQL 参考：[docs/YASHAN_SQL_GUIDE.md](./docs/YASHAN_SQL_GUIDE.md)
- Windows 开机启动：[docs/WINDOWS_AUTOSTART.md](./docs/WINDOWS_AUTOSTART.md)

## 特性

- 完整的数据库操作：支持查询、插入、更新、删除等 SQL 操作
- MCP SSE / Streamable HTTP 协议支持
- 元数据管理：表结构、索引、表搜索、行数统计
- 支持多 Schema 场景
- 详细的错误处理和日志记录
- Oracle 兼容语法支持
- 仓库内置 Java Runtime，普通使用场景下不依赖用户系统 Java

## 前置要求

- Python 3.10+
- 崖山数据库或其他兼容数据库
- JDBC 驱动：`yashandb-jdbc-1.9.3.jar`
- 内置 Java Runtime：`runtime/jre/`

## 安装

```bash
python3 -m pip install -r requirements.txt
```

## 配置

推荐使用 `.env`：

```bash
cp .env.example .env
```

然后填写：

```env
DB_HOST=your_database_host
DB_PORT=1688
DB_NAME=yashandb
DB_USER=your_username
DB_PASSWORD=your_password

# 可选：SQL 执行超时时间（秒），默认 60
# SQL_TIMEOUT=60
```

如果你的数据库连接参数较复杂，也可以直接配置完整 JDBC URL：

```env
DB_JDBC_URL=jdbc:yasdb://host:port/dbname?param=value
```

## 运行

### STDIO 模式（推荐）

```bash
python3 mcp_server.py
```

### HTTP 模式

```bash
./start.sh
# 或
python3 server.py --host 0.0.0.0 --port 20302
```

## 集成到 AI 工具

### STDIO 模式（推荐）

在 Kiro 或 Claude Desktop 的 MCP 配置中添加：

```json
{
  "mcpServers": {
    "yashan": {
      "command": "python3",
      "args": ["/path/to/mcp-yashan/mcp_server.py"]
    }
  }
}
```

### HTTP 模式

如果客户端支持 `streamable-http`：

```json
{
  "mcpServers": {
    "yashan": {
      "type": "streamable-http",
      "url": "http://你的服务IP:20302/mcp"
    }
  }
}
```

详见对应模式的文档。

## MCP 工具能力

| 工具名 | 描述 |
|--------|------|
| `test_connection` | 测试数据库连接 |
| `run_sql` | 执行 SQL 查询 |
| `list_schemas` | 列出所有 Schema |
| `list_tables` | 列出表 |
| `describe_table` | 查看表结构 |
| `search_tables` | 搜索表 |
| `get_table_indexes` | 查看表索引 |
| `get_table_count` | 获取表行数 |
| `get_database_info` | 获取数据库信息 |
| `explain_sql` | 获取 SQL 执行计划 |

## 发布

可使用：

```bash
./scripts/package_release.sh
```

打包后会在 `release/` 目录下生成可分发压缩包。

## 目录说明

- `server.py`：服务入口
- `core/`：SQL 执行和元数据逻辑
- `runtime/jre/`：随包分发的 Java Runtime
- `runtime/java/yashan-mcp-helper.jar`：预编译 Java helper
- `logs/`：按天滚动日志
- `docs/`：补充文档

## 许可证

MIT License
