# 故障排查指南

本文档提供常见问题的诊断和解决方法。

---

## 📋 目录

- [快速诊断工具](#快速诊断工具)
- [常见问题速查表](#常见问题速查表)
- [详细故障排查](#详细故障排查)
- [日志分析](#日志分析)
- [获取帮助](#获取帮助)

---

## 快速诊断工具

### 一键健康检查

```bash
python3 scripts/health_check.py
```

自动检查：
- ✅ Python 和 Java 环境
- ✅ 依赖包完整性
- ✅ JDBC 驱动文件
- ✅ 数据库配置
- ✅ 数据库连接状态

### 配置向导

```bash
mcp-yashan --configure
```

重新配置数据库连接，并自动测试。

### 查看日志

```bash
# 实时查看日志
tail -f logs/yashan_mcp_stdio.log

# 查看最近 50 行
tail -50 logs/yashan_mcp_stdio.log

# 搜索错误
grep ERROR logs/yashan_mcp_stdio.log

# 搜索警告
grep WARNING logs/yashan_mcp_stdio.log
```

---

## 常见问题速查表

| 问题症状 | 可能原因 | 快速解决 |
|---------|---------|---------|
| "未找到 Java" | Java 未安装 | `brew install openjdk@17` (macOS) |
| "连接失败" | 数据库配置错误 | `mcp-yashan --configure` |
| "连接超时" | 网络不通或数据库未启动 | `telnet <host> <port>` 测试 |
| "认证失败" | 用户名或密码错误 | 检查 .env 文件 |
| "表不存在" | 表名错误或权限不足 | 使用 `list_tables` 查看 |
| "SQL 语法错误" | SQL 语法不兼容 | 参考 [SQL 指南](./YASHAN_SQL_GUIDE.md) |
| "查询超时" | 查询太复杂或数据量大 | 添加 WHERE 条件、减少返回行数 |
| "找不到模块" | 依赖未安装或路径错误 | `pip install -r requirements.txt` |
| "JDBC 驱动不存在" | 文件丢失 | 重新下载或检查路径 |

---

## 详细故障排查

### 1. 环境问题

#### 问题：Java 未找到

**症状**：
```
❌ 未找到可用的 Java 运行时
```

**原因**：
- Java 未安装
- Java 路径未配置

**解决**：

1. 检查 Java 是否安装：
   ```bash
   java -version
   ```

2. 如果未安装，根据系统安装：
   ```bash
   # macOS
   brew install openjdk@17
   
   # Ubuntu/Debian
   sudo apt install openjdk-17-jre
   
   # CentOS/RHEL
   sudo yum install java-17-openjdk
   ```

3. 如果已安装但找不到，设置 JAVA_HOME：
   ```bash
   export JAVA_HOME=/path/to/jdk
   export PATH=$JAVA_HOME/bin:$PATH
   ```

4. 或在 .env 中设置：
   ```env
   YASHAN_JAVA_HOME=/path/to/jdk
   ```

#### 问题：Python 版本过低

**症状**：
```
❌ Python 版本过低 (3.9，需要 3.10+)
```

**解决**：

```bash
# macOS
brew install python@3.11

# Ubuntu/Debian
sudo apt install python3.11

# 使用 pyenv
pyenv install 3.11.0
pyenv local 3.11.0
```

#### 问题：缺少 Python 依赖

**症状**：
```
ModuleNotFoundError: No module named 'xxx'
```

**解决**：

```bash
# 安装所有依赖
pip install -r requirements.txt

# 或单独安装缺失的包
pip install <package-name>

# 如果使用虚拟环境
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# 或 venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

---

### 2. 配置问题

#### 问题：找不到配置文件

**症状**：
```
⚠️ 未找到 .env 配置文件
```

**解决**：

1. 从模板创建配置：
   ```bash
   cp config/.env.example .env
   ```

2. 或使用配置向导：
   ```bash
   mcp-yashan --configure
   ```

3. 配置文件搜索路径（按顺序）：
   - 项目根目录 `.env`
   - 当前目录 `.env`
   - 用户主目录 `~/.mcp_yashan/.env`

#### 问题：配置不完整

**症状**：
```
❌ 缺少配置: DB_HOST, DB_USER, DB_PASSWORD
```

**解决**：

编辑 `.env` 文件，确保包含：

```env
DB_HOST=localhost
DB_PORT=1688
DB_NAME=yashandb
DB_USER=your_username
DB_PASSWORD=your_password
```

或通过配置向导重新配置：
```bash
mcp-yashan --configure
```

---

### 3. 连接问题

#### 问题：连接超时

**症状**：
```
❌ 连接失败: Connection timed out
```

**原因**：
- 数据库服务未启动
- 网络不通
- 防火墙阻止
- 主机地址或端口错误

**排查步骤**：

1. 测试网络连接：
   ```bash
   telnet <DB_HOST> <DB_PORT>
   # 或
   nc -zv <DB_HOST> <DB_PORT>
   ```

2. 检查数据库服务：
   ```bash
   # 如果是本地数据库
   systemctl status yashandb  # Linux
   # 或查看进程
   ps aux | grep yashan
   ```

3. 检查防火墙：
   ```bash
   # Linux (iptables)
   sudo iptables -L -n | grep <DB_PORT>
   
   # macOS
   # 系统偏好设置 -> 安全性与隐私 -> 防火墙
   ```

4. 确认配置正确：
   ```bash
   cat .env | grep DB_
   ```

#### 问题：认证失败

**症状**：
```
❌ 连接失败: ORA-01017: invalid username/password
```

**解决**：

1. 确认用户名和密码：
   ```bash
   # 在数据库客户端测试
   yasql <username>/<password>@<host>:<port>/<database>
   ```

2. 重新配置：
   ```bash
   mcp-yashan --configure
   ```

3. 检查用户权限：
   ```sql
   -- 以管理员身份连接
   SELECT * FROM DBA_USERS WHERE USERNAME = 'YOUR_USER';
   ```

#### 问题：连接被拒绝

**症状**：
```
❌ 连接失败: Connection refused
```

**原因**：
- 数据库未启动
- 端口错误
- 数据库不接受远程连接

**解决**：

1. 检查数据库是否启动
2. 确认端口配置正确（默认 1688）
3. 检查数据库监听配置：
   ```bash
   # 查看监听状态
   lsnrctl status
   ```

---

### 4. SQL 执行问题

#### 问题：表不存在

**症状**：
```
❌ SQL 执行失败: ORA-00942: table or view does not exist
```

**解决**：

1. 列出所有可用的表：
   ```
   AI 提示：列出所有数据库表
   ```

2. 检查表名大小写（崖山数据库默认大写）：
   ```sql
   -- 错误
   SELECT * FROM employees;
   
   -- 正确
   SELECT * FROM EMPLOYEES;
   ```

3. 使用完整的 Schema.Table 名称：
   ```sql
   SELECT * FROM MYSCHEMA.EMPLOYEES;
   ```

4. 检查权限：
   ```sql
   SELECT * FROM USER_TABLES;  -- 当前用户的表
   SELECT * FROM ALL_TABLES;   -- 有权限访问的所有表
   ```

#### 问题：列不存在

**症状**：
```
❌ SQL 执行失败: ORA-00904: invalid identifier
```

**解决**：

1. 查看表结构：
   ```
   AI 提示：查看 EMPLOYEES 表的结构
   ```

2. 检查列名拼写和大小写

3. 确认列确实存在：
   ```sql
   SELECT COLUMN_NAME FROM USER_TAB_COLUMNS 
   WHERE TABLE_NAME = 'EMPLOYEES';
   ```

#### 问题：SQL 语法错误

**症状**：
```
❌ SQL 执行失败: ORA-00933: SQL command not properly ended
```

**解决**：

1. 检查 SQL 语法是否完整
2. 参考 [崖山 SQL 指南](./YASHAN_SQL_GUIDE.md)
3. 在数据库客户端测试 SQL
4. 注意崖山和其他数据库的语法差异

#### 问题：查询超时

**症状**：
```
❌ SQL 执行失败: SQL 执行超时（60 秒）
```

**解决**：

1. 添加 WHERE 条件缩小范围：
   ```sql
   -- 不好
   SELECT * FROM LARGE_TABLE;
   
   -- 改进
   SELECT * FROM LARGE_TABLE WHERE DATE > '2024-01-01';
   ```

2. 减少返回行数：
   ```sql
   SELECT * FROM LARGE_TABLE WHERE ROWNUM <= 100;
   ```

3. 增加超时时间（.env）：
   ```env
   SQL_TIMEOUT=120  # 增加到 120 秒
   ```

4. 使用 EXPLAIN 分析性能：
   ```
   AI 提示：分析这个 SQL 的执行计划
   ```

---

### 5. 文件和路径问题

#### 问题：JDBC 驱动不存在

**症状**：
```
❌ JDBC 驱动不存在: yashandb-jdbc-1.9.3.jar
```

**解决**：

1. 检查文件是否存在：
   ```bash
   ls mcp_yashan/runtime/yashandb-jdbc-1.9.3.jar
   ```

2. 如果缺失，从项目仓库获取

3. 或设置自定义路径（.env）：
   ```env
   YASHAN_JDBC_JAR=/path/to/yashandb-jdbc.jar
   ```

#### 问题：找不到模块

**症状**：
```
ModuleNotFoundError: No module named 'mcp_yashan'
```

**解决**：

1. 确保在项目根目录：
   ```bash
   cd /path/to/mcp-yashan
   pwd  # 确认当前目录
   ```

2. 使用模块方式运行：
   ```bash
   python3 -m mcp_yashan.mcp_server
   ```

3. 或安装为包（开发模式）：
   ```bash
   pip install -e .
   ```

---

## 日志分析

### 日志位置

```
logs/yashan_mcp_stdio.log  # STDIO 模式
logs/yashan_mcp_http.log   # HTTP 模式（如果使用）
```

### 常用日志命令

```bash
# 实时查看
tail -f logs/yashan_mcp_stdio.log

# 查看最近 100 行
tail -100 logs/yashan_mcp_stdio.log

# 搜索错误
grep ERROR logs/yashan_mcp_stdio.log

# 搜索特定时间段
grep "2024-06-14" logs/yashan_mcp_stdio.log

# 统计错误类型
grep ERROR logs/yashan_mcp_stdio.log | cut -d'-' -f4 | sort | uniq -c
```

### 日志级别

在 .env 中设置：

```env
# 可选值：DEBUG, INFO, WARNING, ERROR
LOG_LEVEL=DEBUG  # 开发调试
LOG_LEVEL=WARNING  # 生产环境（默认）
```

---

## 获取帮助

### 自助诊断

1. 运行健康检查：
   ```bash
   python3 scripts/health_check.py
   ```

2. 查看日志：
   ```bash
   tail -50 logs/yashan_mcp_stdio.log
   ```

3. 尝试配置向导：
   ```bash
   mcp-yashan --configure
   ```

### 提交问题

如果以上方法无法解决，请提供以下信息：

1. **环境信息**：
   ```bash
   python3 --version
   java -version
   uname -a  # 或 systeminfo (Windows)
   ```

2. **健康检查结果**：
   ```bash
   python3 scripts/health_check.py > health_check.txt
   ```

3. **配置信息**（脱敏后）：
   ```bash
   cat .env | grep -v PASSWORD
   ```

4. **错误日志**（最近 50 行）：
   ```bash
   tail -50 logs/yashan_mcp_stdio.log
   ```

5. **重现步骤**：
   - 你做了什么
   - 预期结果
   - 实际结果

**提交到**：
- GitHub Issues: https://github.com/willorn/mcp-yashan/issues
- 公司内部工单系统

---

## 相关文档

- [快速开始](./QUICK_START.md)
- [使用示例](./EXAMPLES.md)
- [STDIO 模式](./STDIO_MODE.md)
- [SQL 指南](./YASHAN_SQL_GUIDE.md)
