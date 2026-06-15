# mcp-yashan 安装和配置指南

## 📦 安装

### 方式 1: 使用 uvx（推荐）

```bash
uvx mcp-yashan
```

### 方式 2: 使用 pip

```bash
pip install mcp-yashan
```

## ⚙️ 配置

### 前置要求

1. **Java 环境**（必需）
   - Java 8 或更高版本（JRE 或 JDK）
   - 安装方法：
     - macOS: `brew install openjdk@17`
     - Ubuntu: `sudo apt install openjdk-17-jre`
     - CentOS: `sudo yum install java-17-openjdk`
     - Windows: 从 [Oracle](https://www.oracle.com/java/technologies/downloads/) 或 [OpenJDK](https://adoptium.net/) 下载安装

2. **崖山数据库**
   - 需要有可访问的崖山数据库实例
   - 需要数据库连接信息（主机、端口、用户名、密码）

### 配置方式

mcp-yashan 支持三种配置方式（按优先级）：

#### 方式 1: 环境变量（推荐用于 MCP 集成）

直接在 MCP 配置文件中设置环境变量：

**Kiro / Claude Desktop / Cline 配置示例：**

```json
{
  "mcpServers": {
    "yashan": {
      "command": "uvx",
      "args": ["mcp-yashan"],
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

**可用的环境变量：**

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `DB_HOST` | 数据库主机 | `localhost` |
| `DB_PORT` | 数据库端口 | `1688` |
| `DB_NAME` | 数据库名称 | `yashandb` |
| `DB_USER` | 数据库用户名 | （必需） |
| `DB_PASSWORD` | 数据库密码 | （必需） |
| `DB_JDBC_URL` | 完整 JDBC URL（可选，会覆盖上面的配置） | - |
| `SQL_TIMEOUT` | SQL 执行超时（秒） | `60` |
| `JAVA_HOME` | Java 安装路径（可选） | - |

#### 方式 2: .env 文件（推荐用于开发）

在以下任一位置创建 `.env` 文件：

1. **当前工作目录**（优先级最高）
   ```bash
   # 在你运行命令的目录
   touch .env
   ```

2. **用户主目录**（全局配置）
   ```bash
   # 创建配置目录
   mkdir -p ~/.mcp_yashan
   
   # 创建配置文件
   cat > ~/.mcp_yashan/.env << 'EOF'
   DB_HOST=localhost
   DB_PORT=1688
   DB_NAME=yashandb
   DB_USER=your_username
   DB_PASSWORD=your_password
   EOF
   ```

**.env 文件示例：**

```bash
# 数据库连接配置
DB_HOST=localhost
DB_PORT=1688
DB_NAME=yashandb
DB_USER=your_username
DB_PASSWORD=your_password

# 可选配置
SQL_TIMEOUT=60
# JAVA_HOME=/path/to/java
```

#### 方式 3: 系统环境变量

```bash
# Linux / macOS
export DB_HOST=localhost
export DB_PORT=1688
export DB_NAME=yashandb
export DB_USER=your_username
export DB_PASSWORD=your_password

# Windows (PowerShell)
$env:DB_HOST="localhost"
$env:DB_PORT="1688"
$env:DB_NAME="yashandb"
$env:DB_USER="your_username"
$env:DB_PASSWORD="your_password"

# Windows (CMD)
set DB_HOST=localhost
set DB_PORT=1688
set DB_NAME=yashandb
set DB_USER=your_username
set DB_PASSWORD=your_password
```

## 🚀 使用

### STDIO 模式（用于 AI 工具集成）

```bash
# 直接运行（需要先配置环境变量或 .env）
mcp-yashan

# 或使用 uvx
uvx mcp-yashan
```

### HTTP 模式（用于远程访问）

```bash
# 启动 HTTP 服务器
mcp-yashan-http

# 默认监听 http://localhost:3000
```

## 🧪 测试连接

安装后，可以通过以下方式测试连接：

```python
from mcp_yashan.core import get_executor

executor = get_executor()
result = executor.test_connection()
print(result)
```

或者在 AI 工具中使用 `test_connection` 工具。

## 📝 配置文件位置优先级

1. **当前目录** `.env`（最高优先级）
2. **用户主目录** `~/.mcp_yashan/.env`
3. **环境变量**（最低优先级，但 MCP 配置中的 env 会覆盖）

## ⚠️ 安全建议

1. **不要提交 .env 文件到 Git**
   - 已在 `.gitignore` 中排除
   - 包含敏感信息（密码）

2. **使用只读账号**
   - 建议为 AI 工具创建只读数据库账号
   - 限制访问权限

3. **网络安全**
   - HTTP 模式仅用于开发/内网
   - 生产环境建议使用 STDIO 模式

## 🔧 故障排查

### 问题 1: 找不到 Java

**错误信息：**
```
❌ 未找到 Java 运行时环境
```

**解决方法：**
1. 安装 Java（见上文"前置要求"）
2. 设置 `JAVA_HOME` 环境变量
3. 或在 MCP 配置中指定：
   ```json
   "env": {
     "JAVA_HOME": "/path/to/java"
   }
   ```

### 问题 2: 数据库连接失败

**错误信息：**
```
❌ 数据库连接失败
```

**检查清单：**
1. 数据库是否运行？
2. 主机和端口是否正确？
3. 用户名和密码是否正确？
4. 网络是否可达？
5. 防火墙是否开放端口？

### 问题 3: 导入错误

**错误信息：**
```
ImportError: cannot import name 'get_metadata_manager'
```

**解决方法：**
- 这是 v2.1.0 的 bug，请升级到 v2.1.1：
  ```bash
  pip install --upgrade mcp-yashan
  ```

## 📚 更多文档

- [5 分钟快速上手](./docs/QUICK_START.md)
- [STDIO 模式详解](./docs/STDIO_MODE.md)
- [HTTP 模式详解](./docs/HTTP_MODE.md)
- [崖山 SQL 语法指南](./docs/YASHAN_SQL_GUIDE.md)

## 🆘 获取帮助

- GitHub Issues: https://github.com/willorn/mcp-yashan/issues
- 文档: https://github.com/willorn/mcp-yashan
