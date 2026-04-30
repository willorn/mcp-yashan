# 5 分钟快速上手

本文档帮助你在 5 分钟内完成本地 STDIO 模式的配置和测试。

> 💡 **推荐场景**：本地开发、集成到 Kiro/Claude Desktop 等 AI 工具

---

## 前置检查

```bash
# 1. 检查 Python 版本（需要 3.10+）
python3 --version

# 2. 检查 Java 版本（需要 1.8+）
java -version
```

**如果 Java 未安装**：
- macOS: `brew install openjdk@17`
- Ubuntu: `sudo apt install openjdk-17-jre`
- CentOS: `sudo yum install java-17-openjdk`

---

## 三步启动

### 1️⃣ 安装依赖

```bash
pip install -r requirements.txt
```

### 2️⃣ 配置数据库

```bash
cp config/.env.example .env
```

编辑 `.env`，填写数据库连接信息：

```env
DB_HOST=localhost
DB_PORT=1688
DB_NAME=yashandb
DB_USER=your_username
DB_PASSWORD=your_password
```

### 3️⃣ 测试连接

```bash
python3 -m mcp_yashan.mcp_server
```

输入测试请求（复制粘贴后按 `Ctrl+D`）：

```json
{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}
```

看到返回 10 个工具列表即成功 ✅

---

## 集成到 AI 工具

### Kiro 配置

编辑 `.kiro/settings/mcp.json`：

```json
{
  "mcpServers": {
    "yashan": {
      "command": "python3",
      "args": ["-m", "mcp_yashan.mcp_server"],
      "autoApprove": ["test_connection", "run_sql", "list_schemas", "list_tables"]
    }
  }
}
```

**获取绝对路径**：在项目目录执行 `pwd`

或使用开发环境路径：

```json
{
  "mcpServers": {
    "yashan": {
      "command": "python3",
      "args": ["/绝对路径/mcp-yashan/mcp_yashan/mcp_server.py"],
      "autoApprove": ["test_connection", "run_sql", "list_schemas", "list_tables"]
    }
  }
}
```

### Claude Desktop 配置

编辑 `~/Library/Application Support/Claude/claude_desktop_config.json`：

```json
{
  "mcpServers": {
    "yashan": {
      "command": "python3",
      "args": ["/绝对路径/mcp-yashan/src/mcp_server.py"]
    }
  }
}
```

---

## 快速测试

配置完成后，在 AI 工具中尝试：

```
测试崖山数据库连接
```

或

```
列出所有数据库表
```

---

## 下一步

- 📖 详细配置：[STDIO 模式文档](./STDIO_MODE.md)
- 🌐 远程访问：[HTTP 模式文档](./HTTP_MODE.md)
- 📚 SQL 语法：[崖山 SQL 指南](./YASHAN_SQL_GUIDE.md)

---

## 常见问题

**Q: 找不到 Java？**  
A: 确保 `java -version` 能正常输出，或设置 `JAVA_HOME` 环境变量

**Q: 数据库连接失败？**  
A: 检查 `.env` 配置是否正确，数据库是否启动

**Q: 找不到模块？**  
A: 确保在项目根目录运行，且已执行 `pip install -r requirements.txt`
