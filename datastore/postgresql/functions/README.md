# PostgreSQL 常用函数

PostgreSQL 提供了丰富的内置函数，涵盖字符串处理、数值计算、日期时间操作、类型转换等多个方面。本章节介绍最常用的函数及其用法。

## 字符串函数

### 基本字符串操作

```sql
-- 字符串长度
SELECT LENGTH('hello world');           -- 11
SELECT CHAR_LENGTH('你好世界');          -- 4（Unicode 字符数）

-- 字符串连接
SELECT 'Hello' || ' ' || 'World';      -- Hello World
SELECT CONCAT('Hello', ' ', 'World');  -- Hello World

-- 大小写转换
SELECT UPPER('hello');                 -- HELLO
SELECT LOWER('WORLD');                 -- world
SELECT INITCAP('hello world');         -- Hello World

-- 字符串提取
SELECT SUBSTRING('hello world', 1, 5); -- hello
SELECT SUBSTRING('hello world' FROM 1 FOR 5); -- hello
SELECT LEFT('hello world', 5);         -- hello
SELECT RIGHT('hello world', 5);        -- world

-- 字符串去除空白
SELECT TRIM('  hello  ');              -- hello
SELECT LTRIM('  hello');               -- hello
SELECT RTRIM('hello  ');               -- hello
SELECT TRIM(BOTH 'x' FROM 'xxhelloxx'); -- hello
```

### 字符串搜索和替换

```sql
-- 字符串搜索
SELECT POSITION('world' IN 'hello world'); -- 7
SELECT STRPOS('hello world', 'world');     -- 7

-- 字符串替换
SELECT REPLACE('hello world', 'world', 'PostgreSQL'); -- hello PostgreSQL
SELECT REGEXP_REPLACE('abc123def', '[0-9]', '', 'g');   -- abcdef

-- 正则表达式匹配
SELECT 'hello' ~ '^h.*o$';     -- true
SELECT 'hello' ~* '^H.*O$';    -- true（不区分大小写）
SELECT '123' ~ '^[0-9]+$';     -- true

-- 字符串分割
SELECT SPLIT_PART('a,b,c,d', ',', 2);  -- b
SELECT STRING_TO_ARRAY('a,b,c', ',');  -- {a,b,c}
SELECT ARRAY_TO_STRING(ARRAY[1, 2, 3], ','); -- 1,2,3

-- 字符串重复
SELECT REPEAT('ha', 3);  -- hahaha

-- 字符串填充
SELECT LPAD('hello', 10, '*');  -- *****hello
SELECT RPAD('hello', 10, '*');  -- hello*****
```

### 字符串格式化

```sql
-- 字符串格式化
SELECT FORMAT('Hello %s, you have %d messages', 'John', 5);
-- Hello John, you have 5 messages

-- 字符串转义
SELECT QUOTE_LITERAL('O''Reilly');  -- 'O''Reilly'
SELECT QUOTE_IDENT('user name');    -- "user name"
```

## 数值函数

### 基本数学运算

```sql
-- 绝对值
SELECT ABS(-10);          -- 10

-- 四舍五入
SELECT ROUND(3.14159);    -- 3
SELECT ROUND(3.14159, 2); -- 3.14

-- 向上/向下取整
SELECT CEIL(3.2);         -- 4
SELECT FLOOR(3.8);        -- 3

-- 截断小数
SELECT TRUNC(3.14159);    -- 3
SELECT TRUNC(3.14159, 2); -- 3.14

-- 模运算
SELECT MOD(10, 3);        -- 1

-- 幂运算
SELECT POWER(2, 3);       -- 8
SELECT SQRT(16);          -- 4

-- 指数和对数
SELECT EXP(1);            -- e^1 ≈ 2.718
SELECT LN(2.718);         -- 1
SELECT LOG10(100);        -- 2
SELECT LOG2(8);           -- 3
```

### 三角函数

```sql
-- 三角函数（角度以弧度为单位）
SELECT SIN(PI()/2);       -- 1
SELECT COS(PI());         -- -1
SELECT TAN(PI()/4);       -- 1

-- 反三角函数
SELECT ASIN(1);           -- π/2
SELECT ACOS(0);           -- π/2
SELECT ATAN(1);           -- π/4

-- 角度转换
SELECT DEGREES(PI());     -- 180
SELECT RADIANS(180);      -- π
```

### 随机数函数

```sql
-- 随机数生成
SELECT RANDOM();          -- 0.0 到 1.0 之间的随机数
SELECT RANDOM() * 100;    -- 0.0 到 100.0 之间的随机数
SELECT FLOOR(RANDOM() * 100) + 1;  -- 1 到 100 之间的随机整数

-- 设置随机种子
SELECT SETSEED(0.5);
```

## 日期时间函数

### 获取当前时间

```sql
-- 当前日期时间
SELECT CURRENT_TIMESTAMP;          -- 带时区的时间戳
SELECT CURRENT_DATE;               -- 当前日期
SELECT CURRENT_TIME;               -- 当前时间
SELECT NOW();                      -- 当前时间戳（同 CURRENT_TIMESTAMP）
SELECT LOCALTIMESTAMP;             -- 不带时区的时间戳
SELECT statement_timestamp();      -- 语句开始时间
SELECT clock_timestamp();          -- 当前实际时间
```

### 日期时间运算

```sql
-- 日期时间加减
SELECT CURRENT_DATE + INTERVAL '1 day';           -- 明天
SELECT CURRENT_DATE - INTERVAL '1 month';          -- 上个月
SELECT CURRENT_TIMESTAMP + INTERVAL '2 hours 30 minutes';  -- 2小时30分钟后

-- 日期差值
SELECT AGE(CURRENT_DATE, '1990-01-01');           -- 33 years 11 months
SELECT EXTRACT(YEAR FROM AGE(CURRENT_DATE, '1990-01-01'));  -- 33

-- 日期部分提取
SELECT EXTRACT(YEAR FROM CURRENT_DATE);           -- 2023
SELECT EXTRACT(MONTH FROM CURRENT_DATE);          -- 12
SELECT EXTRACT(DAY FROM CURRENT_DATE);            -- 25
SELECT EXTRACT(HOUR FROM CURRENT_TIMESTAMP);      -- 14
SELECT EXTRACT(MINUTE FROM CURRENT_TIMESTAMP);    -- 30
SELECT EXTRACT(SECOND FROM CURRENT_TIMESTAMP);    -- 45

-- 日期部分函数
SELECT DATE_PART('year', CURRENT_DATE);           -- 同 EXTRACT(YEAR FROM ...)
SELECT DATE_TRUNC('day', CURRENT_TIMESTAMP);      -- 截断到天
SELECT DATE_TRUNC('hour', CURRENT_TIMESTAMP);     -- 截断到小时
```

### 日期时间格式化

```sql
-- TO_CHAR 日期格式化
SELECT TO_CHAR(CURRENT_TIMESTAMP, 'YYYY-MM-DD HH24:MI:SS'); -- 2023-12-25 14:30:45
SELECT TO_CHAR(CURRENT_DATE, 'Month DD, YYYY');            -- December 25, 2023
SELECT TO_CHAR(CURRENT_TIMESTAMP, 'Day');                  -- Monday

-- TO_DATE 字符串转日期
SELECT TO_DATE('2023-12-25', 'YYYY-MM-DD');               -- 2023-12-25

-- TO_TIMESTAMP 字符串转时间戳
SELECT TO_TIMESTAMP('2023-12-25 14:30:45', 'YYYY-MM-DD HH24:MI:SS');

-- 格式化选项
SELECT TO_CHAR(1234.56, '9999.99');      -- 1234.56
SELECT TO_CHAR(1234.56, '9,999.99');     -- 1,234.56
SELECT TO_CHAR(-123.45, '999.99MI');     -- 123.45-
```

### 时间间隔

```sql
-- 创建时间间隔
SELECT INTERVAL '1 day 2 hours 30 minutes';
SELECT INTERVAL '1-2' YEAR TO MONTH;     -- 1年2个月
SELECT INTERVAL '12:30:45' HOUR TO SECOND;

-- 时间间隔运算
SELECT INTERVAL '1 day' * 3;             -- 3 days
SELECT INTERVAL '1 hour' + INTERVAL '30 minutes';  -- 01:30:00

-- 时间间隔提取
SELECT EXTRACT(DAY FROM INTERVAL '3 days 2 hours'); -- 3
SELECT EXTRACT(HOUR FROM INTERVAL '3 days 2 hours'); -- 2
```

## 类型转换函数

```sql
-- 显式类型转换
SELECT CAST('123' AS INTEGER);           -- 123
SELECT CAST(123 AS VARCHAR);             -- '123'
SELECT CAST('2023-12-25' AS DATE);       -- 2023-12-25

-- 类型转换操作符
SELECT '123'::INTEGER;                   -- 123
SELECT 123::TEXT;                        -- '123'
SELECT CURRENT_DATE::TEXT;               -- '2023-12-25'

-- 类型检查
SELECT pg_typeof('hello');               -- text
SELECT pg_typeof(123);                   -- integer
SELECT pg_typeof(CURRENT_TIMESTAMP);     -- timestamp with time zone
```

## 条件函数

### CASE 表达式

```sql
-- 简单 CASE
SELECT
    name,
    CASE grade
        WHEN 'A' THEN '优秀'
        WHEN 'B' THEN '良好'
        WHEN 'C' THEN '及格'
        ELSE '不及格'
    END as grade_desc
FROM students;

-- 搜索 CASE
SELECT
    name,
    score,
    CASE
        WHEN score >= 90 THEN 'A'
        WHEN score >= 80 THEN 'B'
        WHEN score >= 70 THEN 'C'
        WHEN score >= 60 THEN 'D'
        ELSE 'F'
    END as letter_grade
FROM students;
```

### NULL 处理

```sql
-- COALESCE：返回第一个非 NULL 值
SELECT COALESCE(NULL, NULL, 'default', 'value');  -- default
SELECT COALESCE(name, 'Unknown') FROM users;      -- 如果 name 为 NULL 则显示 Unknown

-- NULLIF：如果两个参数相等则返回 NULL
SELECT NULLIF(1, 1);                -- NULL
SELECT NULLIF(1, 2);                -- 1

-- GREATEST/LEAST：最大值/最小值
SELECT GREATEST(10, 20, 5, 15);     -- 20
SELECT LEAST(10, 20, 5, 15);        -- 5
SELECT GREATEST(NULL, 10, NULL);    -- 10
```

## 聚合函数

### 基本聚合函数

```sql
-- COUNT：计数
SELECT COUNT(*) FROM orders;                    -- 总行数
SELECT COUNT(order_id) FROM orders;             -- 非空值的行数
SELECT COUNT(DISTINCT customer_id) FROM orders; -- 去重计数

-- SUM：求和
SELECT SUM(amount) FROM orders;
SELECT SUM(DISTINCT amount) FROM orders;

-- AVG：平均值
SELECT AVG(amount) FROM orders;
SELECT AVG(CASE WHEN amount > 0 THEN amount END) FROM orders;

-- MIN/MAX：最小值/最大值
SELECT MIN(amount), MAX(amount) FROM orders;
SELECT MIN(created_at), MAX(created_at) FROM orders;
```

### 高级聚合函数

```sql
-- 数组聚合
SELECT STRING_AGG(name, ', ') FROM users;       -- 逗号分隔的字符串
SELECT ARRAY_AGG(name) FROM users;              -- 名字数组
SELECT ARRAY_AGG(DISTINCT name) FROM users;     -- 去重后的名字数组

-- 统计聚合
SELECT STDDEV(amount) FROM orders;              -- 标准差
SELECT VARIANCE(amount) FROM orders;            -- 方差
SELECT CORRELATION(x, y) FROM data;             -- 相关系数

-- 有序集聚合
SELECT PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY amount) FROM orders; -- 中位数
SELECT PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY amount) FROM orders; -- 第25百分位数
SELECT RANK() WITHIN GROUP (ORDER BY amount DESC) FROM orders; -- 排名
```

## 窗口函数

### 基本窗口函数

```sql
-- 排名函数
SELECT
    name,
    salary,
    ROW_NUMBER() OVER (ORDER BY salary DESC) as row_num,
    RANK() OVER (ORDER BY salary DESC) as rank,
    DENSE_RANK() OVER (ORDER BY salary DESC) as dense_rank,
    NTILE(4) OVER (ORDER BY salary DESC) as quartile
FROM employees;

-- 偏移函数
SELECT
    order_date,
    amount,
    LAG(amount, 1, 0) OVER (ORDER BY order_date) as prev_amount,
    LEAD(amount, 1, 0) OVER (ORDER BY order_date) as next_amount,
    FIRST_VALUE(amount) OVER (ORDER BY order_date) as first_amount,
    LAST_VALUE(amount) OVER (ORDER BY order_date RANGE BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) as last_amount
FROM orders;
```

### 分析窗口函数

```sql
-- 累积函数
SELECT
    date,
    sales,
    SUM(sales) OVER (ORDER BY date ROWS UNBOUNDED PRECEDING) as cumulative_sales,
    AVG(sales) OVER (ORDER BY date ROWS 5 PRECEDING) as moving_avg_5days
FROM daily_sales;

-- 分区窗口函数
SELECT
    department,
    name,
    salary,
    AVG(salary) OVER (PARTITION BY department) as dept_avg,
    ROW_NUMBER() OVER (PARTITION BY department ORDER BY salary DESC) as dept_rank
FROM employees;
```

## JSON 函数

```sql
-- JSON 创建和转换
SELECT row_to_json(users) FROM users WHERE id = 1;
SELECT json_build_object('name', 'John', 'age', 30);
SELECT json_array('apple', 'banana', 'orange');

-- JSON 查询操作
SELECT json_data->>'name' as name FROM documents WHERE json_data ? 'name';
SELECT json_data->'address'->'city' as city FROM documents;

-- JSON 修改操作
SELECT jsonb_set('{"a": 1, "b": 2}'::jsonb, '{c}', '3');  -- 添加字段
SELECT '{"a": 1, "b": 2}'::jsonb || '{"c": 3}'::jsonb;    -- 合并对象
SELECT '["a", "b", "c"]'::jsonb || '["d"]'::jsonb;       -- 合并数组
```

## 数组函数

```sql
-- 数组创建和操作
SELECT ARRAY[1, 2, 3, 4, 5];               -- 创建数组
SELECT ARRAY(SELECT id FROM users LIMIT 5); -- 从查询创建数组

-- 数组信息
SELECT ARRAY_LENGTH(ARRAY[1, 2, 3], 1);     -- 数组长度
SELECT ARRAY_POSITION(ARRAY[1, 2, 3, 2], 2); -- 元素位置
SELECT CARDINALITY(ARRAY[1, 2, 3]);        -- 数组大小

-- 数组操作
SELECT ARRAY_APPEND(ARRAY[1, 2, 3], 4);     -- 添加元素
SELECT ARRAY_PREPEND(0, ARRAY[1, 2, 3]);    -- 前置元素
SELECT ARRAY_REMOVE(ARRAY[1, 2, 3, 2], 2);  -- 删除元素
SELECT ARRAY_REPLACE(ARRAY[1, 2, 3], 2, 20); -- 替换元素

-- 数组搜索
SELECT 2 = ANY(ARRAY[1, 2, 3]);           -- 包含检查
SELECT ARRAY[1, 2, 3] @> ARRAY[2, 3];     -- 包含检查
SELECT ARRAY[1, 2, 3] && ARRAY[3, 4, 5];  -- 重叠检查

-- 数组展开
SELECT unnest(ARRAY[1, 2, 3]);             -- 展开为多行
```

## 系统信息函数

```sql
-- 数据库信息
SELECT current_database();                 -- 当前数据库名
SELECT current_schema();                   -- 当前模式名
SELECT current_user;                       -- 当前用户名
SELECT session_user;                       -- 会话用户名

-- 版本信息
SELECT version();                          -- PostgreSQL 版本信息
SELECT pg_postmaster_start_time();         -- 服务器启动时间

-- 配置信息
SELECT current_setting('shared_buffers');  -- 获取配置参数
SELECT set_config('work_mem', '8MB', false); -- 设置配置参数
```

## 自定义函数

### SQL 函数

```sql
-- 创建简单 SQL 函数
CREATE OR REPLACE FUNCTION get_customer_name(customer_id INTEGER)
RETURNS TEXT AS $$
SELECT name FROM customers WHERE id = customer_id;
$$ LANGUAGE SQL SECURITY DEFINER;

-- 创建带参数的函数
CREATE OR REPLACE FUNCTION calculate_discount(price NUMERIC, discount_rate NUMERIC)
RETURNS NUMERIC AS $$
SELECT price * (1 - discount_rate / 100);
$$ LANGUAGE SQL;

-- 创建返回表格的函数
CREATE OR REPLACE FUNCTION get_customer_orders(customer_id INTEGER)
RETURNS TABLE(order_id INTEGER, order_date TIMESTAMP, total NUMERIC) AS $$
SELECT id, created_at, total_amount
FROM orders
WHERE customer_id = $1;
$$ LANGUAGE SQL;
```

### PL/pgSQL 函数

```sql
-- 创建 PL/pgSQL 函数
CREATE OR REPLACE FUNCTION update_customer_balance(
    customer_id INTEGER,
    amount NUMERIC
) RETURNS NUMERIC AS $$
DECLARE
    current_balance NUMERIC;
BEGIN
    -- 获取当前余额
    SELECT balance INTO current_balance
    FROM customers
    WHERE id = customer_id
    FOR UPDATE;

    -- 更新余额
    UPDATE customers
    SET balance = current_balance + amount
    WHERE id = customer_id;

    -- 返回新余额
    RETURN current_balance + amount;
END;
$$ LANGUAGE plpgsql;

-- 创建带异常处理的函数
CREATE OR REPLACE FUNCTION safe_divide(a NUMERIC, b NUMERIC)
RETURNS NUMERIC AS $$
BEGIN
    IF b = 0 THEN
        RETURN NULL;
    END IF;

    RETURN a / b;
EXCEPTION
    WHEN division_by_zero THEN
        RETURN NULL;
    WHEN numeric_value_out_of_range THEN
        RETURN NULL;
END;
$$ LANGUAGE plpgsql;
```

这些函数是 PostgreSQL 中最常用的内置函数，掌握它们可以大大提高 SQL 查询的效率和灵活性。在实际应用中，可以根据具体需求选择合适的函数组合使用。