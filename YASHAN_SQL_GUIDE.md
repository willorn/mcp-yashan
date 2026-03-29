# 崖山数据库 (YashanDB) SQL 语法指南

> 版本: 1.0  
> 适用版本: YashanDB 23.x

---

## 目录

1. [简介](#简介)
2. [数据类型](#数据类型)
3. [DDL (数据定义语言)](#ddl-数据定义语言)
4. [DML (数据操作语言)](#dml-数据操作语言)
5. [DQL (数据查询语言)](#dql-数据查询语言)
6. [DCL (数据控制语言)](#dcl-数据控制语言)
7. [TCL (事务控制语言)](#tcl-事务控制语言)
8. [函数](#函数)
9. [高级特性](#高级特性)
10. [与 Oracle 的兼容性](#与-oracle-的兼容性)

---

## 简介

崖山数据库 (YashanDB) 是一款国产自主可控的关系型数据库，高度兼容 Oracle 语法，同时支持 MySQL 模式。

### 主要特点

- **Oracle 兼容**: 支持 PL/SQL、Oracle 数据类型、函数等
- **MySQL 兼容**: 支持 MySQL 协议和语法
- **高性能**: 自研存储引擎，优化器支持复杂查询
- **高可用**: 支持主备复制、自动故障切换

---

## 数据类型

### 数值类型

| 类型 | 描述 | 范围/精度 |
|------|------|----------|
| `NUMBER(p,s)` | 精确数值 | p: 1-38, s: -84 to 127 |
| `INTEGER` | 整数 | -2^31 到 2^31-1 |
| `BIGINT` | 大整数 | -2^63 到 2^63-1 |
| `SMALLINT` | 小整数 | -2^15 到 2^15-1 |
| `FLOAT` | 浮点数 | 二进制精度 1-126 |
| `BINARY_FLOAT` | 单精度浮点 | 32位 IEEE 754 |
| `BINARY_DOUBLE` | 双精度浮点 | 64位 IEEE 754 |
| `DECIMAL(p,s)` | 精确小数 | 同 NUMBER |

### 字符类型

| 类型 | 描述 | 最大长度 |
|------|------|----------|
| `CHAR(n)` | 定长字符串 | 2000 字节 |
| `VARCHAR(n)` | 变长字符串 | 4000 字节 |
| `VARCHAR2(n)` | Oracle 兼容变长字符串 | 4000 字节 |
| `NCHAR(n)` | 定长国家字符集字符串 | 2000 字符 |
| `NVARCHAR2(n)` | 变长国家字符集字符串 | 4000 字符 |
| `CLOB` | 大文本 | (4GB - 1) * DB_BLOCK_SIZE |
| `NCLOB` | 国家字符集大文本 | 同 CLOB |
| `LONG` | 长文本 (已废弃) | 2GB |

### 日期时间类型

| 类型 | 描述 | 精度 |
|------|------|------|
| `DATE` | 日期时间 | 秒级 |
| `TIMESTAMP` | 时间戳 | 秒级 |
| `TIMESTAMP(p)` | 带精度时间戳 | p: 0-9 (小数秒) |
| `TIMESTAMP WITH TIME ZONE` | 带时区时间戳 | - |
| `TIMESTAMP WITH LOCAL TIME ZONE` | 本地时区时间戳 | - |
| `INTERVAL YEAR TO MONTH` | 年月间隔 | - |
| `INTERVAL DAY TO SECOND` | 日时间隔 | - |

### 二进制类型

| 类型 | 描述 | 最大长度 |
|------|------|----------|
| `RAW(n)` | 定长二进制 | 2000 字节 |
| `VARBINARY(n)` | 变长二进制 | 4000 字节 |
| `BLOB` | 大二进制 | (4GB - 1) * DB_BLOCK_SIZE |
| `LONG RAW` | 长二进制 (已废弃) | 2GB |
| `BFILE` | 外部文件指针 | 文件系统限制 |

### 其他类型

| 类型 | 描述 |
|------|------|
| `ROWID` | 行唯一标识符 |
| `UROWID` | 通用行标识符 |
| `BOOLEAN` | 布尔值 (TRUE/FALSE/NULL) |
| `JSON` | JSON 数据 (23c+) |
| `XMLTYPE` | XML 数据 |
| `SPATIAL` | 空间数据 |

---

## DDL (数据定义语言)

### 创建表

```sql
-- 基本建表
CREATE TABLE employees (
    employee_id     NUMBER(6) PRIMARY KEY,
    first_name      VARCHAR2(20),
    last_name       VARCHAR2(25) NOT NULL,
    email           VARCHAR2(25) UNIQUE NOT NULL,
    phone_number    VARCHAR2(20),
    hire_date       DATE DEFAULT SYSDATE,
    job_id          VARCHAR2(10),
    salary          NUMBER(8,2) CHECK (salary > 0),
    commission_pct  NUMBER(2,2),
    manager_id      NUMBER(6),
    department_id   NUMBER(4),
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active       BOOLEAN DEFAULT TRUE
);

-- 带表注释和列注释
CREATE TABLE products (
    product_id      NUMBER(10) GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    product_name    VARCHAR2(100) NOT NULL,
    description     CLOB,
    price           NUMBER(10,2),
    category_id     NUMBER(5)
);

COMMENT ON TABLE products IS '产品信息表';
COMMENT ON COLUMN products.product_id IS '产品ID，自增主键';
COMMENT ON COLUMN products.product_name IS '产品名称';

-- 创建分区表
CREATE TABLE sales (
    sale_id         NUMBER,
    sale_date       DATE,
    amount          NUMBER(10,2),
    region          VARCHAR2(20)
) PARTITION BY RANGE (sale_date) (
    PARTITION p2024_q1 VALUES LESS THAN (TO_DATE('2024-04-01', 'YYYY-MM-DD')),
    PARTITION p2024_q2 VALUES LESS THAN (TO_DATE('2024-07-01', 'YYYY-MM-DD')),
    PARTITION p2024_q3 VALUES LESS THAN (TO_DATE('2024-10-01', 'YYYY-MM-DD')),
    PARTITION p2024_q4 VALUES LESS THAN (TO_DATE('2025-01-01', 'YYYY-MM-DD')),
    PARTITION p_max VALUES LESS THAN (MAXVALUE)
);

-- 创建外部表
CREATE TABLE external_employees (
    employee_id NUMBER,
    name        VARCHAR2(100),
    department  VARCHAR2(50)
)
ORGANIZATION EXTERNAL (
    TYPE ORACLE_LOADER
    DEFAULT DIRECTORY data_dir
    ACCESS PARAMETERS (
        RECORDS DELIMITED BY NEWLINE
        FIELDS TERMINATED BY ','
        MISSING FIELD VALUES ARE NULL
    )
    LOCATION ('employees.csv')
);
```

### 修改表

```sql
-- 添加列
ALTER TABLE employees ADD (
    address VARCHAR2(200),
    city    VARCHAR2(50)
);

-- 修改列
ALTER TABLE employees MODIFY (
    salary NUMBER(10,2),
    email  VARCHAR2(50)
);

-- 删除列
ALTER TABLE employees DROP COLUMN address;

-- 重命名列
ALTER TABLE employees RENAME COLUMN city TO location;

-- 重命名表
ALTER TABLE employees RENAME TO staff;

-- 添加约束
ALTER TABLE employees ADD CONSTRAINT pk_emp PRIMARY KEY (employee_id);
ALTER TABLE employees ADD CONSTRAINT fk_dept FOREIGN KEY (department_id) 
    REFERENCES departments(department_id);
ALTER TABLE employees ADD CONSTRAINT chk_salary CHECK (salary > 0);

-- 删除约束
ALTER TABLE employees DROP CONSTRAINT chk_salary;
ALTER TABLE employees DROP CONSTRAINT fk_dept CASCADE;

-- 启用/禁用约束
ALTER TABLE employees DISABLE CONSTRAINT pk_emp;
ALTER TABLE employees ENABLE CONSTRAINT pk_emp;
```

### 删除表

```sql
-- 删除表
DROP TABLE employees;

-- 级联删除（删除外键引用）
DROP TABLE employees CASCADE CONSTRAINTS;

-- 删除并清空回收站
DROP TABLE employees PURGE;

-- 清空表数据（保留结构）
TRUNCATE TABLE employees;

-- 清空表并重置高水位线
TRUNCATE TABLE employees REUSE STORAGE;
```

### 索引操作

```sql
-- 创建索引
CREATE INDEX idx_emp_name ON employees(last_name);

-- 创建复合索引
CREATE INDEX idx_emp_dept_job ON employees(department_id, job_id);

-- 创建唯一索引
CREATE UNIQUE INDEX idx_emp_email ON employees(email);

-- 创建函数索引
CREATE INDEX idx_emp_upper_name ON employees(UPPER(last_name));

-- 创建位图索引（适合低基数列）
CREATE BITMAP INDEX idx_emp_gender ON employees(gender);

-- 删除索引
DROP INDEX idx_emp_name;

-- 重建索引
ALTER INDEX idx_emp_name REBUILD;

-- 分析索引
ANALYZE INDEX idx_emp_name COMPUTE STATISTICS;
```

### 视图

```sql
-- 创建视图
CREATE VIEW emp_dept_view AS
SELECT e.employee_id, e.first_name, e.last_name, d.department_name
FROM employees e
JOIN departments d ON e.department_id = d.department_id;

-- 创建带检查选项的视图
CREATE VIEW high_salary_emp AS
SELECT * FROM employees WHERE salary > 10000
WITH CHECK OPTION;

-- 创建物化视图
CREATE MATERIALIZED VIEW mv_sales_summary
REFRESH COMPLETE ON DEMAND
AS
SELECT region, SUM(amount) as total_sales
FROM sales
GROUP BY region;

-- 刷新物化视图
REFRESH MATERIALIZED VIEW mv_sales_summary;

-- 删除视图
DROP VIEW emp_dept_view;
```

### 序列

```sql
-- 创建序列
CREATE SEQUENCE seq_employee_id
    START WITH 1
    INCREMENT BY 1
    NOMINVALUE
    NOMAXVALUE
    NOCYCLE
    CACHE 20;

-- 使用序列
INSERT INTO employees (employee_id, name) VALUES (seq_employee_id.NEXTVAL, '张三');
SELECT seq_employee_id.CURRVAL FROM DUAL;

-- 修改序列
ALTER SEQUENCE seq_employee_id INCREMENT BY 10;

-- 删除序列
DROP SEQUENCE seq_employee_id;
```

### 同义词

```sql
-- 创建同义词
CREATE SYNONYM emp FOR employees;
CREATE PUBLIC SYNONYM pub_emp FOR hr.employees;

-- 删除同义词
DROP SYNONYM emp;
DROP PUBLIC SYNONYM pub_emp;
```

---

## DML (数据操作语言)

### INSERT

```sql
-- 基本插入
INSERT INTO employees (employee_id, first_name, last_name, email)
VALUES (1, '张', '三', 'zhangsan@example.com');

-- 插入多行
INSERT ALL
    INTO employees (employee_id, first_name) VALUES (2, '李')
    INTO employees (employee_id, first_name) VALUES (3, '王')
    INTO employees (employee_id, first_name) VALUES (4, '赵')
SELECT 1 FROM DUAL;

-- 插入日期
INSERT INTO employees (employee_id, hire_date)
VALUES (5, TO_DATE('2024-01-15', 'YYYY-MM-DD'));

-- 插入时间戳
INSERT INTO employees (employee_id, created_at)
VALUES (6, TIMESTAMP '2024-01-15 10:30:00.000');

-- 使用序列插入
INSERT INTO employees (employee_id, name)
VALUES (seq_employee_id.NEXTVAL, '钱七');

-- 从其他表插入
INSERT INTO employees_backup
SELECT * FROM employees WHERE hire_date < DATE '2024-01-01';

-- 条件插入
INSERT FIRST
    WHEN salary > 20000 THEN INTO high_salary_emp
    WHEN salary > 10000 THEN INTO mid_salary_emp
    ELSE INTO low_salary_emp
SELECT * FROM employees;
```

### UPDATE

```sql
-- 基本更新
UPDATE employees
SET salary = salary * 1.1
WHERE department_id = 10;

-- 更新多列
UPDATE employees
SET salary = 15000,
    commission_pct = 0.15,
    updated_at = SYSDATE
WHERE employee_id = 101;

-- 使用子查询更新
UPDATE employees
SET (salary, commission_pct) = (
    SELECT AVG(salary), AVG(commission_pct)
    FROM employees
    WHERE department_id = 10
)
WHERE department_id = 20;

-- 关联更新
UPDATE employees e
SET e.salary = e.salary * 1.1
WHERE EXISTS (
    SELECT 1 FROM departments d
    WHERE d.department_id = e.department_id
    AND d.location_id = 1700
);

-- 使用 MERGE 更新
MERGE INTO employees e
USING (SELECT employee_id, new_salary FROM salary_updates) s
ON (e.employee_id = s.employee_id)
WHEN MATCHED THEN
    UPDATE SET e.salary = s.new_salary;
```

### DELETE

```sql
-- 基本删除
DELETE FROM employees WHERE employee_id = 101;

-- 删除所有数据
DELETE FROM employees;

-- 使用子查询删除
DELETE FROM employees
WHERE department_id IN (
    SELECT department_id FROM departments WHERE location_id = 1700
);

-- 关联删除
DELETE FROM employees e
WHERE EXISTS (
    SELECT 1 FROM terminated_employees t
    WHERE t.employee_id = e.employee_id
);

-- 使用 TRUNCATE 快速清空（不可回滚）
TRUNCATE TABLE temp_data;
```

### MERGE (UPSERT)

```sql
-- 基本 MERGE
MERGE INTO employees e
USING new_employees n
ON (e.employee_id = n.employee_id)
WHEN MATCHED THEN
    UPDATE SET
        e.first_name = n.first_name,
        e.last_name = n.last_name,
        e.salary = n.salary
WHEN NOT MATCHED THEN
    INSERT (employee_id, first_name, last_name, salary)
    VALUES (n.employee_id, n.first_name, n.last_name, n.salary);

-- 带条件的 MERGE
MERGE INTO employees e
USING new_employees n
ON (e.employee_id = n.employee_id)
WHEN MATCHED THEN
    UPDATE SET e.salary = n.salary
    WHERE e.salary <> n.salary
    DELETE WHERE n.status = 'TERMINATED'
WHEN NOT MATCHED THEN
    INSERT VALUES (n.employee_id, n.first_name, n.last_name, n.salary)
    WHERE n.status = 'ACTIVE';
```

---

## DQL (数据查询语言)

### 基本查询

```sql
-- 查询所有列
SELECT * FROM employees;

-- 查询指定列
SELECT employee_id, first_name, last_name, salary FROM employees;

-- 去重查询
SELECT DISTINCT department_id FROM employees;

-- 别名
SELECT e.employee_id AS "员工ID",
       e.first_name || ' ' || e.last_name AS "姓名",
       e.salary * 12 AS "年薪"
FROM employees e;

-- 限制行数
SELECT * FROM employees FETCH FIRST 10 ROWS ONLY;
SELECT * FROM employees WHERE ROWNUM <= 10;

-- 分页查询
SELECT * FROM employees
ORDER BY employee_id
OFFSET 20 ROWS FETCH NEXT 10 ROWS ONLY;
```

### 条件查询

```sql
-- 比较运算符
SELECT * FROM employees WHERE salary > 10000;
SELECT * FROM employees WHERE department_id <> 10;

-- 范围查询
SELECT * FROM employees WHERE salary BETWEEN 5000 AND 10000;
SELECT * FROM employees WHERE hire_date BETWEEN DATE '2024-01-01' AND DATE '2024-12-31';

-- IN 查询
SELECT * FROM employees WHERE department_id IN (10, 20, 30);
SELECT * FROM employees WHERE last_name IN ('Smith', 'Jones', 'Williams');

-- LIKE 模糊查询
SELECT * FROM employees WHERE first_name LIKE 'J%';      -- 以 J 开头
SELECT * FROM employees WHERE last_name LIKE '%son';     -- 以 son 结尾
SELECT * FROM employees WHERE email LIKE '%@%.com';      -- 包含 @ 和 .com
SELECT * FROM employees WHERE name LIKE 'J_n';           -- J + 任意字符 + n
SELECT * FROM employees WHERE name LIKE 'J\_%' ESCAPE '\'; -- 包含下划线

-- IS NULL
SELECT * FROM employees WHERE commission_pct IS NULL;
SELECT * FROM employees WHERE commission_pct IS NOT NULL;

-- 逻辑运算符
SELECT * FROM employees 
WHERE (salary > 10000 OR department_id = 10) 
  AND hire_date > DATE '2024-01-01';

-- EXISTS
SELECT * FROM departments d
WHERE EXISTS (SELECT 1 FROM employees e WHERE e.department_id = d.department_id);
```

### 排序

```sql
-- 基本排序
SELECT * FROM employees ORDER BY salary;
SELECT * FROM employees ORDER BY salary DESC;

-- 多列排序
SELECT * FROM employees 
ORDER BY department_id ASC, salary DESC;

-- 按位置排序
SELECT first_name, last_name, salary FROM employees ORDER BY 3 DESC;

-- NULL 排序
SELECT * FROM employees ORDER BY commission_pct NULLS FIRST;
SELECT * FROM employees ORDER BY commission_pct NULLS LAST;
```

### 聚合函数

```sql
-- 基本聚合
SELECT COUNT(*) FROM employees;
SELECT COUNT(commission_pct) FROM employees;  -- 非 NULL 计数
SELECT COUNT(DISTINCT department_id) FROM employees;

SELECT SUM(salary) FROM employees;
SELECT AVG(salary) FROM employees;
SELECT MAX(salary) FROM employees;
SELECT MIN(hire_date) FROM employees;

-- 分组聚合
SELECT department_id, 
       COUNT(*) AS emp_count,
       AVG(salary) AS avg_salary,
       MAX(salary) AS max_salary,
       MIN(salary) AS min_salary,
       SUM(salary) AS total_salary
FROM employees
GROUP BY department_id;

-- 多列分组
SELECT department_id, job_id, COUNT(*), AVG(salary)
FROM employees
GROUP BY department_id, job_id;

-- HAVING 过滤
SELECT department_id, AVG(salary)
FROM employees
GROUP BY department_id
HAVING AVG(salary) > 10000;

-- 复杂聚合
SELECT 
    department_id,
    COUNT(*) AS total_emp,
    COUNT(CASE WHEN salary > 10000 THEN 1 END) AS high_salary_emp,
    ROUND(AVG(salary), 2) AS avg_salary,
    LISTAGG(last_name, ', ') WITHIN GROUP (ORDER BY last_name) AS employees
FROM employees
GROUP BY department_id
HAVING COUNT(*) > 5
ORDER BY total_emp DESC;
```

### 连接查询

```sql
-- 内连接
SELECT e.*, d.department_name
FROM employees e
INNER JOIN departments d ON e.department_id = d.department_id;

-- 左连接
SELECT e.*, d.department_name
FROM employees e
LEFT JOIN departments d ON e.department_id = d.department_id;

-- 右连接
SELECT e.*, d.department_name
FROM employees e
RIGHT JOIN departments d ON e.department_id = d.department_id;

-- 全外连接
SELECT e.*, d.department_name
FROM employees e
FULL OUTER JOIN departments d ON e.department_id = d.department_id;

-- 交叉连接
SELECT * FROM employees CROSS JOIN departments;

-- 自然连接
SELECT * FROM employees NATURAL JOIN departments;

-- 使用 USING
SELECT * FROM employees 
JOIN departments USING (department_id);

-- 多表连接
SELECT e.first_name, d.department_name, l.city
FROM employees e
JOIN departments d ON e.department_id = d.department_id
JOIN locations l ON d.location_id = l.location_id;

-- 自连接
SELECT e.first_name || ' works for ' || m.first_name
FROM employees e
JOIN employees m ON e.manager_id = m.employee_id;
```

### 子查询

```sql
-- 单行子查询
SELECT * FROM employees 
WHERE salary > (SELECT AVG(salary) FROM employees);

-- 多行子查询
SELECT * FROM employees 
WHERE department_id IN (SELECT department_id FROM departments WHERE location_id = 1700);

-- 相关子查询
SELECT * FROM employees e
WHERE salary > (SELECT AVG(salary) FROM employees WHERE department_id = e.department_id);

-- EXISTS 子查询
SELECT * FROM departments d
WHERE EXISTS (SELECT 1 FROM employees e WHERE e.department_id = d.department_id);

-- FROM 子查询
SELECT * FROM (
    SELECT department_id, AVG(salary) AS avg_sal
    FROM employees
    GROUP BY department_id
) WHERE avg_sal > 10000;

-- WITH 子句 (CTE)
WITH dept_avg AS (
    SELECT department_id, AVG(salary) AS avg_sal
    FROM employees
    GROUP BY department_id
)
SELECT e.*, d.avg_sal
FROM employees e
JOIN dept_avg d ON e.department_id = d.department_id
WHERE e.salary > d.avg_sal;

-- 递归 CTE
WITH RECURSIVE employee_hierarchy AS (
    -- 锚点成员
    SELECT employee_id, first_name, manager_id, 0 AS level
    FROM employees
    WHERE manager_id IS NULL
    
    UNION ALL
    
    -- 递归成员
    SELECT e.employee_id, e.first_name, e.manager_id, eh.level + 1
    FROM employees e
    JOIN employee_hierarchy eh ON e.manager_id = eh.employee_id
)
SELECT * FROM employee_hierarchy;
```

### 集合操作

```sql
-- UNION (去重)
SELECT employee_id, job_id FROM employees_2023
UNION
SELECT employee_id, job_id FROM employees_2024;

-- UNION ALL (不去重)
SELECT employee_id FROM employees
UNION ALL
SELECT manager_id FROM employees;

-- INTERSECT
SELECT employee_id FROM employees_2023
INTERSECT
SELECT employee_id FROM employees_2024;

-- MINUS (EXCEPT)
SELECT employee_id FROM employees_2023
MINUS
SELECT employee_id FROM employees_2024;
```

### 窗口函数

```sql
-- ROW_NUMBER
SELECT employee_id, salary,
       ROW_NUMBER() OVER (ORDER BY salary DESC) AS rank
FROM employees;

-- RANK 和 DENSE_RANK
SELECT employee_id, salary,
       RANK() OVER (ORDER BY salary DESC) AS rank,
       DENSE_RANK() OVER (ORDER BY salary DESC) AS dense_rank
FROM employees;

-- 分组排名
SELECT department_id, employee_id, salary,
       ROW_NUMBER() OVER (PARTITION BY department_id ORDER BY salary DESC) AS dept_rank
FROM employees;

-- LAG 和 LEAD
SELECT employee_id, hire_date, salary,
       LAG(salary, 1) OVER (ORDER BY hire_date) AS prev_salary,
       LEAD(salary, 1) OVER (ORDER BY hire_date) AS next_salary
FROM employees;

-- FIRST_VALUE 和 LAST_VALUE
SELECT department_id, employee_id, salary,
       FIRST_VALUE(salary) OVER (PARTITION BY department_id ORDER BY salary DESC) AS highest_sal,
       LAST_VALUE(salary) OVER (PARTITION BY department_id ORDER BY salary DESC 
                                ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS lowest_sal
FROM employees;

-- 聚合窗口函数
SELECT employee_id, salary,
       AVG(salary) OVER () AS overall_avg,
       AVG(salary) OVER (PARTITION BY department_id) AS dept_avg,
       SUM(salary) OVER (ORDER BY hire_date ROWS UNBOUNDED PRECEDING) AS running_total
FROM employees;

-- NTILE
SELECT employee_id, salary,
       NTILE(4) OVER (ORDER BY salary) AS quartile
FROM employees;

-- 窗口框架
SELECT employee_id, hire_date, salary,
       AVG(salary) OVER (
           ORDER BY hire_date 
           ROWS BETWEEN 2 PRECEDING AND 2 FOLLOWING
       ) AS moving_avg
FROM employees;
```

---

## DCL (数据控制语言)

### 用户管理

```sql
-- 创建用户
CREATE USER app_user IDENTIFIED BY password123;
CREATE USER admin IDENTIFIED BY admin_password
    DEFAULT TABLESPACE users
    TEMPORARY TABLESPACE temp
    QUOTA 100M ON users
    ACCOUNT UNLOCK;

-- 修改用户
ALTER USER app_user IDENTIFIED BY new_password;
ALTER USER app_user ACCOUNT LOCK;
ALTER USER app_user ACCOUNT UNLOCK;
ALTER USER app_user DEFAULT TABLESPACE data_ts;

-- 删除用户
DROP USER app_user;
DROP USER app_user CASCADE;  -- 级联删除对象
```

### 权限管理

```sql
-- 系统权限
GRANT CREATE SESSION TO app_user;
GRANT CREATE TABLE TO app_user;
GRANT CREATE VIEW TO app_user;
GRANT CREATE SEQUENCE TO app_user;
GRANT CREATE TRIGGER TO app_user;
GRANT CREATE PROCEDURE TO app_user;

-- 对象权限
GRANT SELECT ON employees TO app_user;
GRANT INSERT, UPDATE ON employees TO app_user;
GRANT ALL ON employees TO app_user;

-- 带授权选项
GRANT SELECT ON employees TO app_user WITH GRANT OPTION;

-- 撤销权限
REVOKE CREATE TABLE FROM app_user;
REVOKE SELECT ON employees FROM app_user;

-- 查看权限
-- 用户系统权限
SELECT * FROM USER_SYS_PRIVS;
-- 用户对象权限
SELECT * FROM USER_TAB_PRIVS;
-- 角色权限
SELECT * FROM ROLE_SYS_PRIVS;
```

### 角色管理

```sql
-- 创建角色
CREATE ROLE app_read;
CREATE ROLE app_write;
CREATE ROLE app_admin IDENTIFIED BY role_password;

-- 给角色授权
GRANT SELECT ON employees TO app_read;
GRANT SELECT, INSERT, UPDATE ON employees TO app_write;
GRANT ALL PRIVILEGES TO app_admin;

-- 授予角色给用户
GRANT app_read TO app_user;
GRANT app_write TO developer;
GRANT app_admin TO admin_user WITH ADMIN OPTION;

-- 设置默认角色
ALTER USER app_user DEFAULT ROLE app_read;

-- 启用/禁用角色
SET ROLE app_write;
SET ROLE ALL;
SET ROLE NONE;
SET ROLE app_admin IDENTIFIED BY role_password;

-- 删除角色
DROP ROLE app_read;
```

---

## TCL (事务控制语言)

### 事务控制

```sql
-- 提交事务
COMMIT;
COMMIT WORK;

-- 回滚事务
ROLLBACK;
ROLLBACK WORK;

-- 回滚到保存点
ROLLBACK TO SAVEPOINT sp1;

-- 创建保存点
SAVEPOINT sp1;
SAVEPOINT before_update;

-- 设置事务属性
SET TRANSACTION READ ONLY;
SET TRANSACTION READ WRITE;
SET TRANSACTION ISOLATION LEVEL READ COMMITTED;
SET TRANSACTION ISOLATION LEVEL SERIALIZABLE;
SET TRANSACTION NAME 'update_salary';

-- 锁定表
LOCK TABLE employees IN EXCLUSIVE MODE;
LOCK TABLE employees IN SHARE MODE NOWAIT;

-- 自治事务 (在 PL/SQL 中)
PRAGMA AUTONOMOUS_TRANSACTION;
```

---

## 函数

### 字符串函数

```sql
-- 连接
SELECT CONCAT('Hello', ' ', 'World') FROM DUAL;
SELECT 'Hello' || ' ' || 'World' FROM DUAL;

-- 大小写转换
SELECT UPPER('hello'), LOWER('WORLD'), INITCAP('hello world') FROM DUAL;

-- 截取
SELECT SUBSTR('Hello World', 1, 5) FROM DUAL;     -- Hello
SELECT SUBSTR('Hello World', 7) FROM DUAL;        -- World
SELECT SUBSTR('Hello World', -5) FROM DUAL;       -- World

-- 长度
SELECT LENGTH('Hello') FROM DUAL;
SELECT LENGTHB('Hello') FROM DUAL;  -- 字节长度

-- 查找
SELECT INSTR('Hello World', 'o') FROM DUAL;       -- 5
SELECT INSTR('Hello World', 'o', 1, 2) FROM DUAL; -- 8

-- 替换
SELECT REPLACE('Hello World', 'World', 'Yashan') FROM DUAL;
SELECT TRANSLATE('1-2-3', '-', '/') FROM DUAL;

-- 填充
SELECT LPAD('42', 5, '0') FROM DUAL;  -- 00042
SELECT RPAD('42', 5, '*') FROM DUAL;  -- 42***

-- 修剪
SELECT TRIM('  hello  ') FROM DUAL;
SELECT LTRIM('  hello') FROM DUAL;
SELECT RTRIM('hello  ') FROM DUAL;
SELECT TRIM('x' FROM 'xxxhelloxxx') FROM DUAL;

-- 其他
SELECT CHR(65) FROM DUAL;                    -- A
SELECT ASCII('A') FROM DUAL;                 -- 65
SELECT REVERSE('hello') FROM DUAL;           -- olleh
SELECT REPEAT('ab', 3) FROM DUAL;            -- ababab
SELECT SPACE(5) FROM DUAL;                   -- '     '
```

### 数值函数

```sql
-- 绝对值和符号
SELECT ABS(-10), SIGN(-10), SIGN(10), SIGN(0) FROM DUAL;

-- 取整
SELECT ROUND(123.456, 2) FROM DUAL;    -- 123.46
SELECT ROUND(123.456, 0) FROM DUAL;    -- 123
SELECT ROUND(123.456, -1) FROM DUAL;   -- 120
SELECT TRUNC(123.456, 2) FROM DUAL;    -- 123.45
SELECT CEIL(123.1) FROM DUAL;          -- 124
SELECT FLOOR(123.9) FROM DUAL;         -- 123

-- 幂和对数
SELECT POWER(2, 10) FROM DUAL;         -- 1024
SELECT SQRT(16) FROM DUAL;             -- 4
SELECT EXP(1) FROM DUAL;               -- 2.718...
SELECT LN(2.718) FROM DUAL;            -- 自然对数
SELECT LOG(10, 100) FROM DUAL;         -- 2

-- 三角函数
SELECT SIN(3.14159/2), COS(0), TAN(3.14159/4) FROM DUAL;
SELECT ASIN(1), ACOS(1), ATAN(1) FROM DUAL;

-- 其他
SELECT MOD(17, 5) FROM DUAL;           -- 2
SELECT REMAINDER(17, 5) FROM DUAL;     -- 2
SELECT GREATEST(1, 5, 3, 9, 2) FROM DUAL;
SELECT LEAST(1, 5, 3, 9, 2) FROM DUAL;
SELECT NVL(NULL, 0) FROM DUAL;
SELECT NVL2(NULL, '有值', '无值') FROM DUAL;
SELECT COALESCE(NULL, NULL, 'a', 'b') FROM DUAL;
SELECT DECODE(grade, 'A', 90, 'B', 80, 'C', 70, 0) FROM students;
SELECT CASE WHEN salary > 10000 THEN 'High' WHEN salary > 5000 THEN 'Medium' ELSE 'Low' END FROM employees;
```

### 日期时间函数

```sql
-- 当前日期时间
SELECT SYSDATE FROM DUAL;
SELECT SYSTIMESTAMP FROM DUAL;
SELECT CURRENT_DATE FROM DUAL;
SELECT CURRENT_TIMESTAMP FROM DUAL;
SELECT LOCALTIMESTAMP FROM DUAL;
SELECT DBTIMEZONE FROM DUAL;
SELECT SESSIONTIMEZONE FROM DUAL;

-- 日期计算
SELECT SYSDATE + 1 FROM DUAL;                    -- 加1天
SELECT SYSDATE + INTERVAL '1' DAY FROM DUAL;
SELECT SYSDATE + INTERVAL '2' HOUR FROM DUAL;
SELECT SYSDATE + INTERVAL '30' MINUTE FROM DUAL;
SELECT SYSDATE - hire_date FROM employees;       -- 天数差
SELECT MONTHS_BETWEEN(SYSDATE, hire_date) FROM employees;
SELECT ADD_MONTHS(SYSDATE, 3) FROM DUAL;
SELECT LAST_DAY(SYSDATE) FROM DUAL;
SELECT NEXT_DAY(SYSDATE, 'FRIDAY') FROM DUAL;

-- 日期提取
SELECT EXTRACT(YEAR FROM SYSDATE) FROM DUAL;
SELECT EXTRACT(MONTH FROM SYSDATE) FROM DUAL;
SELECT EXTRACT(DAY FROM SYSDATE) FROM DUAL;
SELECT EXTRACT(HOUR FROM SYSTIMESTAMP) FROM DUAL;

SELECT TO_CHAR(SYSDATE, 'YYYY') FROM DUAL;
SELECT TO_CHAR(SYSDATE, 'MM') FROM DUAL;
SELECT TO_CHAR(SYSDATE, 'DD') FROM DUAL;
SELECT TO_CHAR(SYSDATE, 'HH24') FROM DUAL;
SELECT TO_CHAR(SYSDATE, 'MI') FROM DUAL;
SELECT TO_CHAR(SYSDATE, 'SS') FROM DUAL;

-- 日期截断和舍入
SELECT TRUNC(SYSDATE) FROM DUAL;                 -- 截断到日
SELECT TRUNC(SYSDATE, 'MM') FROM DUAL;           -- 截断到月
SELECT TRUNC(SYSDATE, 'YYYY') FROM DUAL;         -- 截断到年
SELECT ROUND(SYSDATE, 'MM') FROM DUAL;

-- 日期转换
SELECT TO_DATE('2024-01-15', 'YYYY-MM-DD') FROM DUAL;
SELECT TO_TIMESTAMP('2024-01-15 10:30:00', 'YYYY-MM-DD HH24:MI:SS') FROM DUAL;
SELECT TO_CHAR(SYSDATE, 'YYYY-MM-DD HH24:MI:SS') FROM DUAL;
SELECT TO_CHAR(SYSDATE, 'YYYY"年"MM"月"DD"日"') FROM DUAL;

-- 间隔类型
SELECT SYSDATE + INTERVAL '1-2' YEAR TO MONTH FROM DUAL;
SELECT SYSDATE + INTERVAL '10 05:30:00' DAY TO SECOND FROM DUAL;
```

### 转换函数

```sql
-- 显式转换
SELECT TO_CHAR(12345, '99,999') FROM DUAL;
SELECT TO_CHAR(12345.67, '99,999.99') FROM DUAL;
SELECT TO_CHAR(SYSDATE, 'YYYY-MM-DD') FROM DUAL;

SELECT TO_NUMBER('12345') FROM DUAL;
SELECT TO_NUMBER('$12,345.67', '$99,999.99') FROM DUAL;

SELECT TO_DATE('2024-01-15', 'YYYY-MM-DD') FROM DUAL;

-- 隐式转换和 CAST
SELECT CAST('123' AS NUMBER) FROM DUAL;
SELECT CAST(123 AS VARCHAR2(10)) FROM DUAL;
SELECT CAST(SYSDATE AS TIMESTAMP) FROM DUAL;
SELECT CAST(123.45 AS INTEGER) FROM DUAL;

-- BINARY 转换
SELECT BIN_TO_NUM(1,0,1,0) FROM DUAL;  -- 10
SELECT NUMTODSINTERVAL(100, 'DAY') FROM DUAL;
SELECT NUMTOYMINTERVAL(2, 'YEAR') FROM DUAL;
```

### 聚合函数

```sql
-- 基本聚合
SELECT COUNT(*), COUNT(DISTINCT deptno) FROM emp;
SELECT SUM(sal), AVG(sal), MAX(sal), MIN(sal) FROM emp;

-- 统计函数
SELECT STDDEV(sal) FROM emp;
SELECT VARIANCE(sal) FROM emp;
SELECT MEDIAN(sal) FROM emp;
SELECT STATS_MODE(sal) FROM emp;  -- 众数

-- 分析函数
SELECT CORR(sal, comm) FROM emp;  -- 相关系数
SELECT COVAR_POP(sal, comm) FROM emp;  -- 总体协方差
SELECT COVAR_SAMP(sal, comm) FROM emp;  -- 样本协方差
SELECT REGR_SLOPE(sal, comm) FROM emp;  -- 回归斜率
SELECT REGR_INTERCEPT(sal, comm) FROM emp;  -- 回归截距

-- LISTAGG (字符串聚合)
SELECT deptno,
       LISTAGG(ename, ', ') WITHIN GROUP (ORDER BY ename) AS employees
FROM emp
GROUP BY deptno;

-- XMLAGG
SELECT XMLAGG(XMLELEMENT("emp", ename) ORDER BY ename) FROM emp;
```

### NULL 处理函数

```sql
-- NVL
SELECT NVL(comm, 0) FROM emp;

-- NVL2
SELECT NVL2(comm, '有奖金', '无奖金') FROM emp;

-- COALESCE
SELECT COALESCE(comm, 0) FROM emp;
SELECT COALESCE(phone, mobile, email, '无联系方式') FROM contacts;

-- NULLIF
SELECT NULLIF(salary, 0) FROM employees;  -- salary 为 0 时返回 NULL

-- DECODE
SELECT DECODE(deptno, 10, 'ACCOUNTING', 20, 'RESEARCH', 30, 'SALES', 'OTHER') FROM emp;

-- CASE
SELECT 
    CASE 
        WHEN sal > 3000 THEN 'HIGH'
        WHEN sal > 1500 THEN 'MEDIUM'
        ELSE 'LOW'
    END AS salary_level
FROM emp;

-- LNNVL (逻辑非空值)
SELECT * FROM emp WHERE LNNVL(sal > 1000);  -- sal <= 1000 或 sal IS NULL
```

### 其他函数

```sql
-- 环境信息
SELECT USER FROM DUAL;
SELECT UID FROM DUAL;
SELECT USERENV('SESSIONID') FROM DUAL;
SELECT USERENV('TERMINAL') FROM DUAL;
SELECT SYS_CONTEXT('USERENV', 'CURRENT_SCHEMA') FROM DUAL;

-- 对象信息
SELECT DUMP('ABC') FROM DUAL;
SELECT VSIZE('ABC') FROM DUAL;

-- 比较函数
SELECT GREATEST(1, 5, 3) FROM DUAL;
SELECT LEAST(1, 5, 3) FROM DUAL;
SELECT WIDTH_BUCKET(sal, 0, 10000, 5) FROM emp;  -- 直方图分桶

-- 编码函数
SELECT RAWTOHEX('ABC') FROM DUAL;
SELECT HEXTORAW('414243') FROM DUAL;
SELECT UTL_RAW.CAST_TO_VARCHAR2(UTL_RAW.CAST_TO_RAW('ABC')) FROM DUAL;

-- 随机数
SELECT DBMS_RANDOM.VALUE FROM DUAL;
SELECT DBMS_RANDOM.VALUE(1, 100) FROM DUAL;
SELECT DBMS_RANDOM.STRING('A', 10) FROM DUAL;  -- 随机字母
```

---

## 高级特性

### 分区表

```sql
-- 范围分区
CREATE TABLE sales (
    sale_id NUMBER,
    sale_date DATE,
    amount NUMBER
) PARTITION BY RANGE (sale_date) (
    PARTITION p2023 VALUES LESS THAN (TO_DATE('2024-01-01', 'YYYY-MM-DD')),
    PARTITION p2024 VALUES LESS THAN (TO_DATE('2025-01-01', 'YYYY-MM-DD')),
    PARTITION p_max VALUES LESS THAN (MAXVALUE)
);

-- 列表分区
CREATE TABLE customers (
    customer_id NUMBER,
    region VARCHAR2(20),
    name VARCHAR2(100)
) PARTITION BY LIST (region) (
    PARTITION p_east VALUES ('NY', 'NJ', 'CT'),
    PARTITION p_west VALUES ('CA', 'OR', 'WA'),
    PARTITION p_other VALUES (DEFAULT)
);

-- 哈希分区
CREATE TABLE orders (
    order_id NUMBER,
    customer_id NUMBER,
    order_date DATE
) PARTITION BY HASH (customer_id)
PARTITIONS 4;

-- 复合分区
CREATE TABLE sales_composite (
    sale_id NUMBER,
    sale_date DATE,
    region VARCHAR2(20),
    amount NUMBER
) PARTITION BY RANGE (sale_date)
SUBPARTITION BY LIST (region) (
    PARTITION p2024_q1 VALUES LESS THAN (TO_DATE('2024-04-01', 'YYYY-MM-DD')) (
        SUBPARTITION p2024_q1_east VALUES ('NY', 'NJ'),
        SUBPARTITION p2024_q1_west VALUES ('CA', 'OR')
    ),
    PARTITION p2024_q2 VALUES LESS THAN (TO_DATE('2024-07-01', 'YYYY-MM-DD'))
);

-- 分区维护
ALTER TABLE sales ADD PARTITION p2025 VALUES LESS THAN (TO_DATE('2026-01-01', 'YYYY-MM-DD'));
ALTER TABLE sales DROP PARTITION p2023;
ALTER TABLE sales TRUNCATE PARTITION p2024;
ALTER TABLE sales SPLIT PARTITION p_max AT (TO_DATE('2026-01-01', 'YYYY-MM-DD')) INTO (
    PARTITION p2025,
    PARTITION p_max
);
ALTER TABLE sales MERGE PARTITIONS p2023, p2024 INTO PARTITION p_2023_2024;
```

### 索引高级特性

```sql
-- 复合索引
CREATE INDEX idx_emp_dept_job ON employees(department_id, job_id);

-- 函数索引
CREATE INDEX idx_emp_upper_name ON employees(UPPER(last_name));

-- 位图索引
CREATE BITMAP INDEX idx_emp_gender ON employees(gender);

-- 反向键索引
CREATE INDEX idx_emp_id_reverse ON employees(employee_id) REVERSE;

-- 压缩索引
CREATE INDEX idx_emp_name ON employees(last_name) COMPRESS;

-- 分区索引
CREATE INDEX idx_sales_date ON sales(sale_date) LOCAL;
CREATE INDEX idx_sales_global ON sales(sale_id) GLOBAL;

-- 不可见索引
CREATE INDEX idx_test ON employees(email) INVISIBLE;

-- 虚拟列索引
ALTER TABLE employees ADD (full_name AS (first_name || ' ' || last_name));
CREATE INDEX idx_emp_full_name ON employees(full_name);
```

### 约束

```sql
-- 主键约束
CREATE TABLE departments (
    dept_id NUMBER PRIMARY KEY,
    dept_name VARCHAR2(50) NOT NULL
);

-- 外键约束
CREATE TABLE employees (
    emp_id NUMBER PRIMARY KEY,
    dept_id NUMBER CONSTRAINT fk_emp_dept REFERENCES departments(dept_id)
);

-- 级联操作
CREATE TABLE employees (
    emp_id NUMBER PRIMARY KEY,
    dept_id NUMBER REFERENCES departments(dept_id) ON DELETE CASCADE
);

-- 检查约束
CREATE TABLE products (
    product_id NUMBER PRIMARY KEY,
    price NUMBER CHECK (price > 0),
    status VARCHAR2(20) CHECK (status IN ('ACTIVE', 'INACTIVE'))
);

-- 唯一约束
CREATE TABLE users (
    user_id NUMBER PRIMARY KEY,
    email VARCHAR2(100) UNIQUE,
    username VARCHAR2(50) CONSTRAINT uk_username UNIQUE
);

-- 延迟约束
CREATE TABLE orders (
    order_id NUMBER PRIMARY KEY,
    customer_id NUMBER,
    CONSTRAINT fk_order_customer FOREIGN KEY (customer_id) 
        REFERENCES customers(customer_id) DEFERRABLE INITIALLY DEFERRED
);

-- 启用/禁用约束
ALTER TABLE employees DISABLE CONSTRAINT fk_emp_dept;
ALTER TABLE employees ENABLE CONSTRAINT fk_emp_dept;
ALTER TABLE employees DROP CONSTRAINT fk_emp_dept;
```

### 触发器

```sql
-- 行级触发器
CREATE OR REPLACE TRIGGER trg_emp_salary_check
BEFORE INSERT OR UPDATE ON employees
FOR EACH ROW
BEGIN
    IF :NEW.salary < 0 THEN
        RAISE_APPLICATION_ERROR(-20001, '工资不能为负数');
    END IF;
END;
/

-- 语句级触发器
CREATE OR REPLACE TRIGGER trg_audit_emp
AFTER INSERT OR UPDATE OR DELETE ON employees
BEGIN
    INSERT INTO audit_log (table_name, action, action_time)
    VALUES ('EMPLOYEES', 'DML', SYSDATE);
END;
/

--  instead of 触发器 (用于视图)
CREATE OR REPLACE TRIGGER trg_emp_view_io
INSTEAD OF INSERT ON emp_dept_view
FOR EACH ROW
BEGIN
    INSERT INTO employees (employee_id, first_name, department_id)
    VALUES (:NEW.employee_id, :NEW.first_name, 
            (SELECT department_id FROM departments WHERE department_name = :NEW.department_name));
END;
/

-- 系统触发器
CREATE OR REPLACE TRIGGER trg_logon
AFTER LOGON ON DATABASE
BEGIN
    INSERT INTO logon_log (username, logon_time)
    VALUES (USER, SYSDATE);
END;
/

-- 启用/禁用触发器
ALTER TRIGGER trg_emp_salary_check DISABLE;
ALTER TRIGGER trg_emp_salary_check ENABLE;
```

### 序列高级用法

```sql
-- 创建序列
CREATE SEQUENCE seq_order_id
    START WITH 1000
    INCREMENT BY 1
    MINVALUE 1000
    MAXVALUE 999999999
    NOCYCLE
    CACHE 50
    ORDER;

-- 使用序列
INSERT INTO orders (order_id, order_date)
VALUES (seq_order_id.NEXTVAL, SYSDATE);

-- 获取当前值
SELECT seq_order_id.CURRVAL FROM DUAL;

-- 修改序列
ALTER SEQUENCE seq_order_id INCREMENT BY 10;
ALTER SEQUENCE seq_order_id MAXVALUE 999999999999;

-- 重置序列（删除重建）
DROP SEQUENCE seq_order_id;
CREATE SEQUENCE seq_order_id START WITH 1;
```

---

## 与 Oracle 的兼容性

### 高度兼容的特性

| 特性 | 兼容度 | 说明 |
|------|--------|------|
| SQL 语法 | 95%+ | 支持绝大多数 Oracle SQL |
| PL/SQL | 90%+ | 支持存储过程、函数、包 |
| 数据类型 | 95%+ | 完整支持 Oracle 类型 |
| 内置函数 | 90%+ | 常用函数完全兼容 |
| 系统视图 | 85%+ | ALL_*, USER_*, DBA_* 视图 |
| 分区表 | 90%+ | 支持各种分区类型 |
| 索引 | 95%+ | B-tree、Bitmap、函数索引等 |
| 约束 | 100% | 主键、外键、检查、唯一 |
| 触发器 | 90%+ | 行级、语句级、Instead Of |
| 序列 | 100% | 完整兼容 |
| 同义词 | 100% | 公有、私有同义词 |

### 差异点

```sql
-- 1. 部分系统包可能有差异
-- Oracle
DBMS_OUTPUT.PUT_LINE('Hello');
DBMS_RANDOM.VALUE;

-- YashanDB 可能使用不同的包名或需要额外安装

-- 2. 部分高级特性
-- Oracle 的某些高级分析函数可能需要验证

-- 3. 性能优化器提示
-- Oracle 提示
SELECT /*+ INDEX(emp idx_emp_name) */ * FROM employees emp;

-- YashanDB 可能支持不同的提示语法

-- 4. 数据字典视图
-- 大部分兼容，但部分列可能有差异
SELECT * FROM ALL_TABLES;  -- 基本兼容
SELECT * FROM ALL_TAB_COLUMNS;  -- 基本兼容
```

### 迁移建议

1. **SQL 迁移**：大部分 SQL 无需修改即可运行
2. **PL/SQL 迁移**：存储过程、函数基本兼容，需要测试验证
3. **数据类型**：完全兼容，无需转换
4. **函数**：常用函数完全兼容
5. **系统视图**：查询可能需要调整部分列名

---

## 最佳实践

### 1. SQL 编写规范

```sql
-- 使用表别名
SELECT e.employee_id, d.department_name
FROM employees e
JOIN departments d ON e.department_id = d.department_id;

-- 避免 SELECT *
SELECT employee_id, first_name, last_name FROM employees;

-- 使用绑定变量
SELECT * FROM employees WHERE employee_id = :emp_id;

-- 批量操作
INSERT ALL
    INTO employees VALUES (...)
    INTO employees VALUES (...)
SELECT 1 FROM DUAL;
```

### 2. 索引优化

```sql
-- 选择性高的列建索引
CREATE INDEX idx_emp_email ON employees(email);

-- 复合索引列顺序
CREATE INDEX idx_emp_dept_job ON employees(department_id, job_id);

-- 定期分析表
ANALYZE TABLE employees COMPUTE STATISTICS;
```

### 3. 分区策略

```sql
-- 大表按时间分区
CREATE TABLE logs (
    log_id NUMBER,
    log_time TIMESTAMP,
    message VARCHAR2(4000)
) PARTITION BY RANGE (log_time) INTERVAL (NUMTODSINTERVAL(1, 'DAY')) (
    PARTITION p_init VALUES LESS THAN (TO_DATE('2024-01-01', 'YYYY-MM-DD'))
);
```

---

## 参考资料

- [崖山数据库官方文档](https://doc.yashandb.com/)
- Oracle SQL 参考手册
- SQL 标准 (ANSI/ISO SQL)

---

*本文档最后更新: 2024年*
