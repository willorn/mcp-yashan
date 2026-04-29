# STDIO 模式使用指南

## 概述

STDIO 模式是**推荐的默认使用方式**，适合本地开发和 AI 工具集成（如 Kiro、Claude Desktop 等）。

### 优势

- ✅ **按需启动**：每次调用时启动，用完即退出
- ✅ **资源节省**：不占用常驻端口和内存
- ✅ **配置简单**：无需管理服务进程
- ✅ **安全性高**：仅本地访问，无网络暴露

### 对比 HTTP 模式

| 特性 | STDIO 模式 | HTTP 模式 |
|------|-----------|----------|
| 启动方式 | 按需启动 | 常驻服务 |
| 资源占用 | 低（用完即退） | 中（持续运行） |
| 适用场景 | 本地 AI 工具 | 远程访问、多用户 |
| 配置复杂度 | 简单 | 中等 |
| 网络暴露 | 无 | 有（需配置防火墙） |

---

## 快速开始

### 1. 配置数据库连接

```bash
cp .env.example .env
```

编辑 `.env`：

```env
DB_HOST=localhost
DB_PORT=1688
DB_NAME=yashandb
DB_USER=your_username
DB_PASSWORD=your_password
```

### 2. 测试运行

```bash
python3 mcp_server.py
```

然后输入测试请求（JSON 格式）：

```json
{"jsonrpc":"2.0","id":1,"method":"initialize","params":{}}
```

按 `Ctrl+D` 结束输入，应该看到返回：

```json
{"jsonrpc":"2.0","id":1,"result":{"protocolVersion":"2024-11-05",...}}
```

---

## 集成到 AI 工具

### Kiro 配置

在 Kiro 的 MCP 配置文件中添加：

```json
{
  "mcpServers": {
    "yashan": {
      "command": "python3",
      "args": ["/path/to/mcp-yashan/mcp_server.py"],
      "autoApprove": [
        "test_connection",
        "run_sql",
        "list_schemas",
        "list_tables",
        "describe_table",
        "search_tables",
        "get_table_indexes",
        "get_table_count",
        "get_database_info",
        "explain_sql"
      ]
    }
  }
}
```

**获取路径**：
```bash
# 在项目目录下执行
pwd
# 输出示例：/Users/username/mcp-yashan
```

将输出的路径替换到配置中的 `/path/to/mcp-yashan`。

### Claude Desktop 配置

编辑 `~/Library/Application Support/Claude/claude_desktop_config.json`（macOS）：

```json
{
  "mcpServers": {
    "yashan": {
      "command": "python3",
      "args": ["/Users/your-username/mcp-yashan/mcp_server.py"]
    }
  }
}
```

### 通用配置模板

```json
{
  "mcpServers": {
    "yashan": {
      "command": "python3",
      "args": ["<项目绝对路径>/mcp_server.py"]
    }
  }
}
```

---

## 可用工具

STDIO 模式支持所有 MCP 工具：

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

---

## 环境变量配置

### 数据库连接

```bash
# 基础配置
DB_HOST=localhost
DB_PORT=1688
DB_NAME=yashandb
DB_USER=your_username
DB_PASSWORD=your_password

# 或使用完整 JDBC URL
DB_JDBC_URL=jdbc:yasdb://host:port/dbname?param=value
```

### 高级配置（可选）

```bash
# SQL 执行超时（秒），默认 60
# SQL_TIMEOUT=120

# 日志级别：DEBUG, INFO, WARNING, ERROR
# LOG_LEVEL=WARNING

# 自定义 Java 路径（可选）
# YASHAN_JAVA_HOME=/path/to/jre

# 自定义 JDBC 驱动路径（可选）
# YASHAN_JDBC_JAR=/path/to/yashandb-jdbc.jar
```

---

## 日志

日志文件位置：`logs/yashan_mcp_stdio.log`

查看日志：

```bash
tail -f logs/yashan_mcp_stdio.log
```

默认日志级别为 `WARNING`，只记录警告和错误。如需调试，设置：

```bash
export LOG_LEVEL=DEBUG
python3 mcp_server.py
```

---

## 故障排查

### 问题 1：找不到 Python 模块

**错误**：`ModuleNotFoundError: No module named 'core'`

**解决**：
```bash
# 确保在项目根目录运行
cd /path/to/mcp-yashan
python3 mcp_server.py
```

### 问题 2：数据库连接失败

**错误**：`连接失败: Connection refused`

**检查**：
1. 数据库是否启动
2. `.env` 配置是否正确
3. 网络是否可达

```bash
# 测试数据库连接
telnet localhost 1688
```

### 问题 3：JDBC 驱动不存在

**错误**：`JDBC 驱动不存在: yashandb-jdbc-1.9.3.jar`

**解决**：
```bash
# 确保 JDBC 驱动在项目根目录
ls yashandb-jdbc-1.9.3.jar

# 或指定路径
export YASHAN_JDBC_JAR=/path/to/yashandb-jdbc-1.9.3.jar
```

### 问题 4：Java 运行时未找到

**错误**：`未找到可用的 Java 运行时`

**解决**：
```bash
# 使用内置 JRE（推荐）
ls runtime/jre/bin/java

# 或设置 JAVA_HOME
export JAVA_HOME=/path/to/jdk
```

---

## 性能特征

### 启动开销

- **首次启动**：~200-500ms（加载 Python + 初始化）
- **后续调用**：~100-300ms（Java 进程启动）
- **查询执行**：实际 SQL 执行时间 + 50-100ms

### 适用场景

✅ **适合**：
- 本地 AI 助手（Kiro、Claude Desktop）
- 低频查询（< 10 次/分钟）
- 单用户使用
- 开发和调试

❌ **不适合**：
- 高频查询（> 100 次/分钟）
- 多用户并发
- 需要持久连接的场景
- 远程访问

**如需高频或远程访问，请使用 [HTTP 模式](./HTTP_MODE.md)**

---

## 安全建议

### 1. 保护 .env 文件

```bash
# 确保 .env 不被提交
echo ".env" >> .gitignore

# 设置文件权限（仅所有者可读）
chmod 600 .env
```

### 2. 使用只读数据库用户

```sql
-- 创建只读用户
CREATE USER readonly_user IDENTIFIED BY password;
GRANT CONNECT TO readonly_user;
GRANT SELECT ON schema.* TO readonly_user;
```

### 3. 限制查询结果

在 `.env` 中设置：

```bash
# 限制单次查询最大行数（已内置，1-10000）
# 如需更严格限制，可修改 core/executor.py
```

---

## 与 HTTP 模式对比

### 何时使用 STDIO 模式

- ✅ 本地开发和使用
- ✅ 集成到 AI 工具
- ✅ 不需要远程访问
- ✅ 希望节省资源

### 何时使用 HTTP 模式

- ✅ 需要远程访问
- ✅ 多用户共享
- ✅ 需要 Web UI
- ✅ 高频查询场景

详见 [HTTP 模式文档](./HTTP_MODE.md)

---

## 常见问题

### Q: STDIO 模式是否支持所有功能？

A: 是的，STDIO 模式和 HTTP 模式功能完全一致，只是通信方式不同。

### Q: 可以同时使用两种模式吗？

A: 可以。两种模式互不干扰，可以根据场景选择。

### Q: STDIO 模式是否更安全？

A: 是的。STDIO 模式仅本地访问，无网络暴露，更安全。

### Q: 性能差异大吗？

A: STDIO 模式每次启动有 ~100-300ms 开销，但用完即退出，不占用资源。HTTP 模式常驻，无启动开销，但持续占用资源。

### Q: 如何调试 STDIO 模式？

A: 设置 `LOG_LEVEL=DEBUG`，查看 `logs/yashan_mcp_stdio.log`。

---

## 进阶配置

### 多数据库配置

为不同数据库创建不同的项目目录：

```bash
# 生产环境
mcp-yashan-prod/
  .env  # 生产数据库配置
  mcp_server.py

# 开发环境
mcp-yashan-dev/
  .env  # 开发数据库配置
  mcp_server.py
```

在 MCP 配置中分别配置：

```json
{
  "mcpServers": {
    "yashan-prod": {
      "command": "python3",
      "args": ["/path/to/mcp-yashan-prod/mcp_server.py"]
    },
    "yashan-dev": {
      "command": "python3",
      "args": ["/path/to/mcp-yashan-dev/mcp_server.py"]
    }
  }
}
```

---

## 总结

STDIO 模式是**推荐的默认方式**，适合大多数本地使用场景。它简单、安全、资源占用低。

如需远程访问或高频查询，请参考 [HTTP 模式文档](./HTTP_MODE.md)。
