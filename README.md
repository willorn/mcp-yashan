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

### 1. 修改数据库配置

编辑 `config.py` 文件，修改数据库连接信息：

```python
DATABASE_CONFIG = {
    "driver_class": "com.yashandb.jdbc.Driver",
    "jdbc_url": "jdbc:yasdb://localhost:1688/yashandb",
    "username": "your_username",
    "password": "your_password",
    "jvm_lib": "/path/to/your/libjvm.so",
}
```

### 2. 指定 JVM 路径

根据你的系统，修改 `jvm_lib` 配置：

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
