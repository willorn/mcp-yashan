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

## 项目结构

```
mcp-yashan/
├── src/                        # 源代码
│   ├── mcp_server.py          # STDIO 模式入口
│   ├── http_server.py         # HTTP 模式入口
│   └── core/                  # 核心逻辑
│       ├── executor.py        # SQL 执行器
│       ├── metadata.py        # 元数据管理
│       └── tools.py           # MCP 工具定义
├── config/                     # 配置文件
│   └── .env.example           # 配置模板
├── scripts/                    # 脚本工具
│   ├── start.sh               # HTTP 模式启动脚本
│   ├── package_release.sh     # 打包脚本
│   └── create_autostart_task.ps1
├── tests/                      # 测试
│   ├── test_stability.py      # 稳定性测试
│   └── test_jdbc.py           # JDBC 连接测试
├── runtime/                    # 运行时依赖
│   ├── jre/                   # Java 运行时
│   ├── java/                  # Java helper
│   └── yashandb-jdbc-1.9.3.jar
├── docs/                       # 文档
│   ├── STDIO_MODE.md          # STDIO 模式文档
│   ├── HTTP_MODE.md           # HTTP 模式文档
│   ├── QUICK_START.md         # 快速开始
│   └── YASHAN_SQL_GUIDE.md    # SQL 语法指南
├── README.md                   # 项目说明
├── requirements.txt            # Python 依赖
└── LICENSE                     # MIT 许可证
```

---

- 完整的数据库操作：支持查询、插入、更新、删除等 SQL 操作
- MCP SSE / Streamable HTTP 协议支持
- 元数据管理：表结构、索引、表搜索、行数统计
- 支持多 Schema 场景
- 详细的错误处理和日志记录
- Oracle 兼容语法支持
- 仓库内置 Java Runtime，普通使用场景下不依赖用户系统 Java

## 前置要求

- Python 3.10+
- **Java 8+ (JDK 或 JRE)**
- 崖山数据库或其他兼容数据库
- JDBC 驱动：`yashandb-jdbc-1.9.3.jar`（已包含在 `runtime/` 目录）

### Java 安装

项目需要 Java 运行时环境（JRE 8+）来执行 SQL 查询。

**检查 Java 版本**：
```bash
java -version
# 需要显示 1.8 或更高版本
```

**如果未安装 Java**：

- **macOS**: `brew install openjdk@17`
- **Ubuntu/Debian**: `sudo apt install openjdk-17-jre`
- **CentOS/RHEL**: `sudo yum install java-17-openjdk`
- **Windows**: 从 [Oracle](https://www.oracle.com/java/technologies/downloads/) 或 [OpenJDK](https://adoptium.net/) 下载安装

**注意**：项目会自动查找系统 Java，无需额外配置。

## 安装

```bash
python3 -m pip install -r requirements.txt
```

**注意**：确保已安装 Java 8+ (JRE 或 JDK)。检查：`java -version`

## 配置

推荐使用 `.env`：

```bash
cp config/.env.example .env
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
python3 src/mcp_server.py
```

### HTTP 模式

```bash
./scripts/start.sh
# 或
python3 src/http_server.py --host 0.0.0.0 --port 20302
```

**注意**：首次运行前请确保已安装 Java 并配置 `.env` 文件。

## 集成到 AI 工具

### STDIO 模式（推荐）

在 Kiro 或 Claude Desktop 的 MCP 配置中添加：

```json
{
  "mcpServers": {
    "yashan": {
      "command": "python3",
      "args": ["<项目绝对路径>/src/mcp_server.py"]
    }
  }
}
```

获取项目绝对路径：在项目目录下执行 `pwd`

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
