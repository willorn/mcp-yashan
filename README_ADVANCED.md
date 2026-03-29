# 崖山数据库 MCP Server Pro

> 专业的崖山数据库 MCP 服务器，提供完整的数据库操作能力

![Version](https://img.shields.io/badge/version-2.0.0-blue)
![Python](https://img.shields.io/badge/python-3.10+-green)
![License](https://img.shields.io/badge/license-MIT-yellow)

---

## 特性

- ✅ **完整的数据库操作**：支持查询、插入、更新、删除等所有 SQL 操作
- ✅ **元数据管理**：表结构查看、索引查询、表搜索等功能
- ✅ **性能监控**：内置性能监控和日志记录
- ✅ **连接池管理**：高效的数据库连接管理
- ✅ **多种运行模式**：支持 stdio、sse、http 三种模式
- ✅ **完善的错误处理**：详细的错误信息和日志记录
- ✅ **Oracle 兼容**：高度兼容 Oracle SQL 语法

---

## 快速开始

### 1. 环境要求

- Python 3.10+
- JDK 17+ (用于 JDBC 连接)
- 崖山数据库 JDBC 驱动

### 2. 安装依赖

```bash
# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows

# 安装依赖
pip install fastmcp jpype1 jaydebeapi
```

### 3. 配置数据库连接

复制 `.env.example` 为 `.env` 并修改配置：

```bash
cp .env.example .env
```

编辑 `.env` 文件：

```env
# 数据库地址
DB_HOST=10.9.18.73

# 数据库端口
DB_PORT=1688

# 数据库名称
DB_NAME=yashandb

# 数据库用户名
DB_USER=SZ_NCIS_SYSTEM

# 数据库密码
DB_PASSWORD=your_password

# 日志级别 (DEBUG, INFO, WARNING, ERROR)
LOG_LEVEL=INFO
```

### 4. 启动服务器

#### 模式一：stdio 模式（默认）

```bash
python yashan_mcp_server_pro.py
```

#### 模式二：SSE 模式（推荐用于 IDE 集成）

```bash
python yashan_mcp_server_pro.py --mode sse --port 8080
```

#### 模式三：HTTP 模式

```bash
python yashan_mcp_server_pro.py --mode http --port 8080
```

---

## 可用工具

### 基础工具

| 工具名 | 描述 | 参数 |
|--------|------|------|
| `test_connection` | 测试数据库连接 | 无 |
| `get_database_info` | 获取数据库信息 | 无 |
| `run_sql` | 执行 SQL 语句 | `sql_query`: SQL 语句<br>`max_rows`: 最大返回行数 |

### 元数据工具

| 工具名 | 描述 | 参数 |
|--------|------|------|
| `list_schemas` | 列出所有 Schema | 无 |
| `list_tables` | 列出表 | `schema`: Schema 名（可选） |
| `describe_table` | 查看表结构 | `table_name`: 表名<br>`schema`: Schema 名（可选） |
| `search_tables` | 搜索表 | `pattern`: 关键字<br>`schema`: Schema 名（可选） |
| `get_table_indexes` | 查看表索引 | `table_name`: 表名<br>`schema`: Schema 名（可选） |
| `get_table_count` | 获取表行数 | `table_name`: 表名<br>`schema`: Schema 名（可选） |
| `explain_sql` | 获取 SQL 执行计划 | `sql_query`: SQL 语句 |

---

## 使用示例

### 测试连接

```python
# 使用 MCP 工具
test_connection()
```

输出：
```
✅ 崖山数据库连接正常！
主机：10.9.18.73:1688
用户：SZ_NCIS_SYSTEM
当前会话用户：SZ_NCIS_SYSTEM
数据库：yashandb
驱动：JayDeBeApi + YashanDB JDBC
```

### 查询数据

```python
# 使用 MCP 工具
run_sql(
    sql_query="SELECT * FROM SZ_NCIS_SYSTEM.XJR_MESSAGE_TEMPLATE WHERE ROWNUM <= 5",
    max_rows=10
)
```

### 查看表结构

```python
# 使用 MCP 工具
describe_table(
    table_name="XJR_MESSAGE_TEMPLATE",
    schema="SZ_NCIS_SYSTEM"
)
```

### 搜索表

```python
# 使用 MCP 工具
search_tables(
    pattern="MESSAGE",
    schema="SZ_NCIS_SYSTEM"
)
```

---

## 配置文件

### 环境变量 (.env)

```env
# 数据库连接配置
DB_HOST=localhost
DB_PORT=1688
DB_NAME=yashandb
DB_USER=your_username
DB_PASSWORD=your_password

# JDBC 配置（可选）
DB_DRIVER_CLASS=com.yashandb.jdbc.Driver
DB_JDBC_URL=jdbc:yasdb://localhost:1688/yashandb

# JVM 路径（可选，自动检测）
JVM_LIB=/path/to/libjvm.dylib

# 日志配置
LOG_LEVEL=INFO
```

### MCP 配置（Trae IDE）

在 Trae IDE 中配置 MCP 服务器：

```json
{
  "mcpServers": {
    "yashan-db": {
      "command": "python",
      "args": ["/path/to/yashan_mcp_server_pro.py"],
      "env": {
        "DB_HOST": "10.9.18.73",
        "DB_PORT": "1688",
        "DB_NAME": "yashandb",
        "DB_USER": "SZ_NCIS_SYSTEM",
        "DB_PASSWORD": "your_password"
      }
    }
  }
}
```

---

## 项目结构

```
mcp-yashan/
├── yashan_mcp_server_pro.py    # MCP 服务器主程序（Pro 版）
├── yashan_mcp_server.py        # MCP 服务器（基础版）
├── yashandb-jdbc-1.7.19-21.jar # JDBC 驱动
├── .env                        # 环境变量配置
├── .env.example                # 环境变量模板
├── YASHAN_SQL_GUIDE.md         # SQL 语法指南
├── README_PRO.md               # 本文档
├── requirements.txt            # Python 依赖
└── venv/                       # 虚拟环境
```

---

## 崖山数据库 SQL 语法

崖山数据库高度兼容 Oracle SQL 语法。详细语法请参考：

📖 [YASHAN_SQL_GUIDE.md](./YASHAN_SQL_GUIDE.md)

### 快速参考

```sql
-- 基本查询
SELECT * FROM employees WHERE department_id = 10;

-- 连接查询
SELECT e.*, d.department_name
FROM employees e
JOIN departments d ON e.department_id = d.department_id;

-- 聚合查询
SELECT department_id, AVG(salary), COUNT(*)
FROM employees
GROUP BY department_id
HAVING AVG(salary) > 5000;

-- 窗口函数
SELECT employee_id, salary,
       ROW_NUMBER() OVER (PARTITION BY department_id ORDER BY salary DESC) as rank
FROM employees;

-- 递归 CTE
WITH RECURSIVE hierarchy AS (
    SELECT employee_id, manager_id, 0 as level
    FROM employees WHERE manager_id IS NULL
    UNION ALL
    SELECT e.employee_id, e.manager_id, h.level + 1
    FROM employees e
    JOIN hierarchy h ON e.manager_id = h.employee_id
)
SELECT * FROM hierarchy;
```

---

## 日志

日志文件位于：`yashan_mcp.log`

日志级别可通过环境变量 `LOG_LEVEL` 设置：
- `DEBUG` - 调试信息
- `INFO` - 一般信息（默认）
- `WARNING` - 警告信息
- `ERROR` - 错误信息

---

## 故障排除

### 1. JVM 找不到

**错误**：`找不到 JVM！请安装 JDK 17+ 或设置 JVM_LIB 环境变量`

**解决**：
```bash
# 设置 JVM 路径
export JVM_LIB=/path/to/libjvm.dylib

# 或在 .env 文件中设置
JVM_LIB=/Library/Java/JavaVirtualMachines/jdk-17.jdk/Contents/Home/lib/server/libjvm.dylib
```

### 2. JDBC 驱动找不到

**错误**：`JDBC 驱动找不到`

**解决**：
确保 `yashandb-jdbc-1.7.19-21.jar` 文件位于项目根目录。

### 3. 数据库连接失败

**错误**：`无法连接到崖山数据库`

**解决**：
1. 检查数据库地址、端口、用户名、密码
2. 确认数据库服务已启动
3. 检查网络连接
4. 查看日志文件获取详细错误信息

---

## 开发计划

- [ ] 支持更多数据库类型（MySQL、PostgreSQL 等）
- [ ] 添加 SQL 智能提示功能
- [ ] 支持数据库图形化展示
- [ ] 添加数据导入导出功能
- [ ] 支持数据库备份恢复

---

## 贡献

欢迎提交 Issue 和 Pull Request！

---

## 许可证

MIT License

---

## 联系方式

如有问题或建议，请提交 Issue。

---

**Happy Coding with YashanDB! 🚀**
