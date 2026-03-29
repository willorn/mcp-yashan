# YashanDB MCP Server

一个用于连接崖山数据库（YashanDB）的 MCP（Model Context Protocol）服务器，让 AI 助手能够自然语言查询崖山数据库。

![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

## 特性

- 🔌 支持崖山数据库（Oracle 兼容语法）
- 🤖 MCP 协议支持，与 Claude Desktop / Cursor 无缝集成
- 📊 提供丰富的数据库工具：表结构查询、索引查看、数据搜索等
- 🔍 支持多 Schema 自动降级
- 🐳 Docker 支持，易于部署
- ⚡ 使用 JDBC 驱动，兼容性好

## 前置要求

- Python 3.12+
- Java 17+（用于运行 JDBC 驱动）
- 崖山数据库或其他兼容数据库
- 崖山 JDBC 驱动（[下载地址](https://www.yashandb.com/download)）

## 支持的数据库

- 崖山数据库（YashanDB）
- Oracle 兼容的数据库

## 安装

### 前置要求

- Python 3.12+
- Java 17+（用于运行 JDBC 驱动）
- 崖山数据库或其他兼容数据库

### 方式一：pip 安装

```bash
pip install -r requirements.txt
```

### 方式二：Docker 运行

```bash
# 构建镜像
docker build -t yashan-mcp .

# 运行容器
docker run -d -p 8080:8080 --name yashan-mcp yashan-mcp
```

## 配置

### 方式一：使用 .env 文件（推荐）

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

### 方式二：使用环境变量

```bash
export DB_HOST=your_database_host
export DB_PORT=1688
export DB_NAME=yashandb
export DB_USER=your_username
export DB_PASSWORD=your_password
python yashan_mcp_server.py
```

### 方式三：使用完整的 JDBC URL

如果你的数据库有特殊的连接参数，可以直接设置完整的 JDBC URL：

```bash
export DB_JDBC_URL="jdbc:yasdb://host:port/dbname?param=value"
```

### JVM 配置

JVM 路径会自动检测，也可以手动指定：

| 系统 | 示例路径 |
|------|---------|
| macOS | `/Library/Java/JavaVirtualMachines/jdk-17/Contents/Home/lib/server/libjvm.dylib` |
| Linux | `/usr/lib/jvm/java-17-openjdk/lib/server/libjvm.so` |
| Windows | `C:\Program Files\Java\jdk-17\bin\server\jvm.dll` |

```bash
export JVM_LIB=/path/to/libjvm.so
```

| 系统 | 示例路径 |
|------|---------|
| macOS | `/Library/Java/JavaVirtualMachines/jdk-17/Contents/Home/lib/server/libjvm.dylib` |
| Linux | `/usr/lib/jvm/java-17-openjdk/lib/server/libjvm.so` |
| Windows | `C:\Program Files\Java\jdk-17\bin\server\jvm.dll` |

## 使用

### 启动 MCP 服务

```bash
python yashan_mcp_server.py
```

### Claude Desktop 配置

编辑 `~/.claude.json`：

```json
{
  "mcpServers": {
    "yashan-db": {
      "command": "python3",
      "args": ["/path/to/yashan_mcp_server.py"]
    }
  }
}
```

### Cursor 配置

编辑 `~/.cursor/mcp.json`：

```json
{
  "mcpServers": {
    "yashan-db": {
      "command": "python3",
      "args": ["/path/to/yashan_mcp_server.py"]
    }
  }
}
```

## 可用工具

| 工具 | 说明 | 参数 |
|------|------|------|
| `test_connection` | 测试数据库连接 | - |
| `run_sql` | 执行 SQL 查询 | `sql_query`, `max_rows` |
| `list_schemas` | 列出所有 Schema | - |
| `list_tables` | 列出表 | `schema` (可选) |
| `search_tables` | 搜索表名 | `pattern`, `schema` (可选) |
| `describe_table` | 查看表结构 | `table_name`, `schema` (可选) |
| `get_table_indexes` | 查看表索引 | `table_name`, `schema` (可选) |
| `get_table_count` | 获取表行数 | `table_name`, `schema` (可选) |
| `get_database_info` | 获取数据库信息 | - |

## 使用示例

### 查看表结构

```
用户：查看 CUS_DEVICE 表的结构
AI：调用 describe_table("CUS_DEVICE")
```

### 搜索表

```
用户：搜索包含 ORDER 的表
AI：调用 search_tables("ORDER")
```

### 执行查询

```
用户：查询 CUS_DEVICE 表有多少条数据
AI：调用 get_table_count("CUS_DEVICE")
```

## 常见问题

### Q: 连接失败，提示 "JVM DLL not found"

确保正确配置了 `jvm_lib` 路径，指向 `libjvm.so`（Linux）或 `libjvm.dylib`（macOS）。

### Q: 表不在当前用户下

使用 `schema` 参数指定表所属的用户：
```python
describe_table("TABLE_NAME", "SCHEMA_NAME")
```

### Q: 如何查看所有可用的 Schema？

使用 `list_schemas()` 工具查看所有可用的 Schema。

## 开发

```bash
# 克隆仓库
git clone https://github.com/yourusername/yashandb-mcp.git
cd yashandb-mcp

# 安装依赖
pip install -r requirements.txt

# 运行测试
python test_jdbc.py
```

## 贡献

欢迎提交 Issue 和 Pull Request！

## 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件
