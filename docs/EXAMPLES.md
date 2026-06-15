# 使用示例和最佳实践

本文档提供了 mcp-yashan 在公司内部的实际使用场景和最佳实践。

---

## 📋 目录

- [常见查询示例](#常见查询示例)
- [AI 提示词模板](#ai-提示词模板)
- [最佳实践](#最佳实践)
- [性能优化建议](#性能优化建议)
- [故障排查技巧](#故障排查技巧)

---

## 常见查询示例

### 1. 数据探索

#### 查看所有表
```
AI 提示：列出所有数据库表

预期工具：list_tables
```

#### 查看表结构
```
AI 提示：查看 EMPLOYEES 表的结构

预期工具：describe_table
参数：table_name="EMPLOYEES"
```

#### 搜索包含特定关键词的表
```
AI 提示：查找所有包含 "customer" 的表

预期工具：search_tables
参数：keyword="customer"
```

### 2. 数据查询

#### 简单查询
```sql
-- AI 提示：查询前 10 条员工记录
SELECT * FROM EMPLOYEES WHERE ROWNUM <= 10;

-- AI 提示：统计每个部门的员工数量
SELECT DEPARTMENT_ID, COUNT(*) as EMPLOYEE_COUNT
FROM EMPLOYEES
GROUP BY DEPARTMENT_ID;
```

#### 复杂查询
```sql
-- AI 提示：查询 2024 年销售额超过 100 万的客户
SELECT 
    c.CUSTOMER_NAME,
    SUM(o.ORDER_AMOUNT) as TOTAL_SALES
FROM CUSTOMERS c
JOIN ORDERS o ON c.CUSTOMER_ID = o.CUSTOMER_ID
WHERE o.ORDER_DATE >= TO_DATE('2024-01-01', 'YYYY-MM-DD')
GROUP BY c.CUSTOMER_NAME
HAVING SUM(o.ORDER_AMOUNT) > 1000000
ORDER BY TOTAL_SALES DESC;
```

### 3. 数据分析

#### 时间序列分析
```
AI 提示：分析过去 12 个月的月度销售趋势

期望生成：
- 按月分组的销售数据
- 环比增长率
- 简单的趋势分析
```

#### 数据对比
```
AI 提示：对比今年和去年同期的销售数据

期望：
- 使用 UNION 或 JOIN 对比数据
- 计算同比增长率
```

---

## AI 提示词模板

以下是针对不同场景的 AI 提示词模板，可以直接复制使用。

### 模板 1：探索性分析

```
请帮我分析崖山数据库中的 {表名} 表：
1. 查看表结构和字段说明
2. 统计总行数
3. 查看前 20 条样例数据
4. 分析数据分布特征（如果有数值字段）
5. 检查是否有空值或异常数据
```

**使用场景**：初次接触某个表，需要全面了解数据结构和内容

### 模板 2：业务指标查询

```
请从崖山数据库查询以下业务指标：
- 指标名称：{指标名}
- 时间范围：{开始日期} 到 {结束日期}
- 分组维度：{维度，如部门/地区/产品}
- 特殊要求：{如排除某些数据、只看 TOP N}

请提供 SQL 语句和执行结果。
```

**使用场景**：定期业务报表、KPI 监控

### 模板 3：数据质量检查

```
请帮我检查 {表名} 表的数据质量：
1. 统计每个字段的空值率
2. 检查主键是否有重复
3. 检查日期字段是否有未来日期或过于久远的日期
4. 检查数值字段是否有异常值（负数、超大值）
5. 给出数据质量评分和改进建议
```

**使用场景**：数据清洗前的质量评估

### 模板 4：性能优化分析

```
我需要优化这个 SQL 查询的性能：
```sql
{粘贴你的 SQL}
```

请：
1. 使用 EXPLAIN 分析执行计划
2. 指出潜在的性能瓶颈
3. 建议添加索引或重写 SQL
4. 如果可能，提供优化后的 SQL
```

**使用场景**：慢查询优化

### 模板 5：数据导出

```
请从崖山数据库导出以下数据：
- 表名：{表名}
- 筛选条件：{条件}
- 需要的字段：{字段列表}
- 排序方式：{排序字段}
- 最大行数：{行数}

请返回结果的前 50 行预览。
```

**使用场景**：数据导出、报表生成

---

## 最佳实践

### 1. 查询优化

#### ✅ 推荐做法

- **限制返回行数**：使用 `ROWNUM` 或 `FETCH FIRST N ROWS ONLY`
  ```sql
  SELECT * FROM LARGE_TABLE WHERE ROWNUM <= 100;
  ```

- **使用索引字段作为过滤条件**：
  ```sql
  SELECT * FROM ORDERS WHERE ORDER_ID = 12345; -- ORDER_ID 是索引
  ```

- **避免 SELECT \***：明确指定需要的字段
  ```sql
  SELECT ORDER_ID, ORDER_DATE, AMOUNT FROM ORDERS;
  ```

#### ❌ 避免的做法

- **不限制行数的全表扫描**：
  ```sql
  SELECT * FROM VERY_LARGE_TABLE; -- 可能返回百万行
  ```

- **复杂的嵌套子查询**：可能导致超时

- **不带 WHERE 的 UPDATE/DELETE**：危险操作

### 2. 与 AI 协作技巧

#### 清晰描述需求

**差的提示**：
```
查一下销售数据
```

**好的提示**：
```
查询 2024 年 1-3 月各产品线的销售额，按销售额降序排列，只要前 10 名
```

#### 分步骤执行复杂任务

对于复杂分析，将任务拆分成多步：

```
第一步：先查看 SALES 表的结构和字段
第二步：统计每月的总销售额
第三步：计算环比增长率
第四步：生成趋势图（如果支持）
```

#### 提供上下文信息

```
我们公司的财年是从 4 月 1 日开始的，请查询本财年（2024 财年）的销售数据
```

### 3. 安全实践

#### 只读操作优先

- 尽量使用 SELECT 查询
- 避免 UPDATE、DELETE、DROP 等修改操作
- 如需修改数据，先在测试环境验证

#### 敏感数据处理

- 不要在 AI 对话中暴露完整的密码、身份证号等敏感信息
- 查询结果如包含敏感信息，注意脱敏处理

#### 权限控制

- 使用只读账号进行日常查询
- 管理员账号仅用于必要的维护操作

---

## 性能优化建议

### 查询性能

1. **使用 EXPLAIN 分析执行计划**
   ```
   AI 提示：使用 EXPLAIN 分析这个 SQL 的执行计划
   ```

2. **合理使用索引**
   - 在常用的 WHERE 条件字段上建索引
   - 避免在索引字段上使用函数

3. **控制返回数据量**
   - 使用分页：`OFFSET ... FETCH NEXT ... ROWS ONLY`
   - 设置合理的 max_rows 参数（默认 1000）

### 系统性能

1. **避免高频查询**
   - STDIO 模式：每次查询有 100-300ms 启动开销
   - 如需高频查询，考虑使用 HTTP 模式

2. **合理设置超时时间**
   - 默认 60 秒超时
   - 可通过 `SQL_TIMEOUT` 环境变量调整

3. **监控日志**
   - 定期查看 `logs/yashan_mcp_stdio.log`
   - 关注慢查询和错误信息

---

## 故障排查技巧

### 常见问题速查

| 问题症状 | 可能原因 | 解决方法 |
|---------|---------|---------|
| 连接超时 | 数据库不可达 | 检查网络、防火墙、数据库状态 |
| 认证失败 | 用户名或密码错误 | 重新运行 `mcp-yashan --configure` |
| Java 未找到 | Java 未安装或路径不对 | 安装 Java 或设置 `JAVA_HOME` |
| SQL 语法错误 | SQL 不兼容崖山语法 | 参考 [SQL 指南](./YASHAN_SQL_GUIDE.md) |
| 查询超时 | 查询太复杂或数据量大 | 简化查询、添加 WHERE 条件 |

### 诊断工具

#### 1. 健康检查脚本

```bash
python3 scripts/health_check.py
```

一键检查：
- Python 和 Java 环境
- 依赖包完整性
- 配置文件正确性
- 数据库连接状态

#### 2. 配置向导

```bash
mcp-yashan --configure
```

交互式配置数据库连接，自动测试连接。

#### 3. 日志分析

```bash
# 实时查看日志
tail -f logs/yashan_mcp_stdio.log

# 搜索错误
grep ERROR logs/yashan_mcp_stdio.log

# 查看最近的警告
grep WARNING logs/yashan_mcp_stdio.log | tail -20
```

### 逐步排查流程

遇到问题时，按以下顺序排查：

1. **运行健康检查**
   ```bash
   python3 scripts/health_check.py
   ```

2. **检查日志**
   ```bash
   tail -50 logs/yashan_mcp_stdio.log
   ```

3. **测试数据库连接**
   ```bash
   mcp-yashan --configure
   # 选择测试连接
   ```

4. **验证 SQL 语法**
   - 在数据库客户端直接执行 SQL
   - 对比崖山和 Oracle 语法差异

5. **简化问题**
   - 从简单查询开始：`SELECT 1 FROM DUAL`
   - 逐步增加复杂度

---

## 公司内部使用指南

### 推荐的集成方式

**开发环境**：
```json
{
  "mcpServers": {
    "yashan-dev": {
      "command": "python3",
      "args": ["-m", "mcp_yashan.mcp_server"],
      "env": {
        "DB_HOST": "dev-db.company.internal",
        "DB_PORT": "1688",
        "DB_NAME": "dev_db"
      }
    }
  }
}
```

**生产环境（只读）**：
```json
{
  "mcpServers": {
    "yashan-prod-readonly": {
      "command": "python3",
      "args": ["-m", "mcp_yashan.mcp_server"],
      "env": {
        "DB_HOST": "prod-db.company.internal",
        "DB_PORT": "1688",
        "DB_NAME": "prod_db",
        "DB_USER": "readonly_user"
      }
    }
  }
}
```

### 团队协作建议

1. **统一配置管理**
   - 使用统一的 .env 模板
   - 敏感信息通过密钥管理系统分发

2. **SQL 规范**
   - 建立内部 SQL 编码规范
   - 常用查询保存为模板

3. **知识沉淀**
   - 记录常用的 AI 提示词
   - 分享优化案例和最佳实践

---

## 进阶技巧

### 批量查询

```
AI 提示：请依次查询以下表的行数：
CUSTOMERS, ORDERS, PRODUCTS, EMPLOYEES

每个表单独一条 SQL。
```

### 数据对比

```
AI 提示：对比 TEST 和 PROD 环境中 USERS 表的数据一致性：
1. 分别统计两个环境的总行数
2. 对比字段结构是否一致
3. 抽样对比前 100 条数据的差异
```

### 自动化报表

```
AI 提示：生成周报数据：
- 本周新增用户数
- 本周订单总额
- 本周 TOP 10 热销产品
- 与上周对比的增长率

格式化为 Markdown 表格。
```

---

## 反馈与改进

如果你在使用过程中：
- 发现更好的使用技巧
- 遇到文档未覆盖的问题
- 有功能改进建议

欢迎通过以下方式反馈：
- 提交 Issue: https://github.com/willorn/mcp-yashan/issues
- 内部工单系统
- 联系数据库团队

---

## 相关文档

- [快速开始](./QUICK_START.md)
- [STDIO 模式](./STDIO_MODE.md)
- [崖山 SQL 指南](./YASHAN_SQL_GUIDE.md)
