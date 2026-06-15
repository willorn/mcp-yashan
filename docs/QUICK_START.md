# 5 分钟快速上手

本文档帮助你在 5 分钟内完成配置和测试。

> 💡 **推荐场景**：本地开发、集成到 Kiro/Claude Desktop 等 AI 工具

---

## ⚡ 最快路径

### 方式一：使用配置向导（推荐）

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 运行配置向导
mcp-yashan --configure
```

配置向导会：
- ✅ 检查 Java 环境
- ✅ 引导你输入数据库连接信息
- ✅ 自动测试连接
- ✅ 保存配置到安全位置

### 方式二：手动配置

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 复制配置模板
cp config/.env.example .env

# 3. 编辑 .env 文件
# 填写你的数据库信息

# 4. 测试连接
python3 -m mcp_yashan.mcp_server
# 输入: {"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}
# 按 Ctrl+D 发送
```

---

## 前置检查

运行健康检查脚本，一键检查所有环境：

```bash
python3 scripts/health_check.py
```

或者手动检查：

```bash
# 检查 Python 版本（需要 3.10+）
python3 --version

# 检查 Java 版本（需要 1.8+）
java -version
```

**如果 Java 未安装**：
- macOS: `brew install openjdk@17`
- Ubuntu: `sudo apt install openjdk-17-jre`
- CentOS: `sudo yum install java-17-openjdk`
- Windows: 从 [Adoptium](https://adoptium.net/) 下载安装

---

## 配置数据库连接

### 方式 1：配置向导（推荐）

```bash
mcp-yashan --configure
```

按照提示输入：
- 数据库主机（默认 localhost）
- 端口（默认 1688）
- 数据库名（默认 yashandb）
- 用户名
- 密码

### 方式 2：环境变量

编辑 `.env` 文件：

```env
DB_HOST=localhost
DB_PORT=1688
DB_NAME=yashandb
DB_USER=your_username
DB_PASSWORD=your_password
```

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
      "env": {
        "DB_HOST": "localhost",
        "DB_PORT": "1688",
        "DB_NAME": "yashandb",
        "DB_USER": "your_username",
        "DB_PASSWORD": "your_password"
      }
    }
  }
}
```

**提示**：可以直接在配置中设置环境变量，无需 .env 文件。

### Claude Desktop 配置

编辑 `~/Library/Application Support/Claude/claude_desktop_config.json`（macOS）：

```json
{
  "mcpServers": {
    "yashan": {
      "command": "python3",
      "args": ["-m", "mcp_yashan.mcp_server"]
    }
  }
}
```

**注意**：Claude Desktop 需要在用户主目录或项目根目录下有 `.env` 文件。

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

或

```
查询 EMPLOYEES 表的前 10 条记录
```

---

## 常用 AI 提示

复制以下提示词，快速开始使用：

### 探索数据
```
帮我了解一下崖山数据库有哪些表，并展示前 3 个表的结构
```

### 查询数据
```
查询 EMPLOYEES 表中工资最高的 5 名员工
```

### 数据分析
```
分析 ORDERS 表中每个月的订单数量趋势
```

更多示例请查看 [使用示例文档](./EXAMPLES.md)。

---

## 故障排查

### 问题：Java 未找到

```bash
# 检查 Java 是否安装
java -version

# 如未安装，根据系统安装
# macOS
brew install openjdk@17

# Ubuntu/Debian
sudo apt install openjdk-17-jre

# 或设置 JAVA_HOME
export JAVA_HOME=/path/to/jdk
```

### 问题：数据库连接失败

```bash
# 1. 运行健康检查
python3 scripts/health_check.py

# 2. 重新配置
mcp-yashan --configure

# 3. 检查数据库是否启动
telnet localhost 1688
```

### 问题：找不到模块

```bash
# 确保在项目根目录
cd /path/to/mcp-yashan

# 重新安装依赖
pip install -r requirements.txt

# 使用模块方式运行
python3 -m mcp_yashan.mcp_server
```

### 查看日志

```bash
# 实时查看日志
tail -f logs/yashan_mcp_stdio.log

# 查看最近的错误
grep ERROR logs/yashan_mcp_stdio.log | tail -20
```

---

## 下一步

- 📖 查看 [使用示例](./EXAMPLES.md) 学习常见查询和最佳实践
- 🔧 阅读 [STDIO 模式详细文档](./STDIO_MODE.md)
- 🌐 了解 [HTTP 模式](./HTTP_MODE.md)（远程访问、多用户）
- 📚 参考 [崖山 SQL 指南](./YASHAN_SQL_GUIDE.md)

---

## 获取帮助

- GitHub Issues: https://github.com/willorn/mcp-yashan/issues
- 文档首页: [README.md](../README.md)
- 健康检查: `python3 scripts/health_check.py`
- 配置向导: `mcp-yashan --configure`

