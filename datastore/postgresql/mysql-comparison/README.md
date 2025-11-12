# PostgreSQL 与 MySQL 主要区别速查表

本章节提供了 PostgreSQL 与 MySQL 之间的主要区别对比，帮助开发者从 MySQL 迁移到 PostgreSQL 或在两个数据库之间做出选择。

## 核心架构区别

### ACID 合规性
| 特性 | PostgreSQL | MySQL (InnoDB) |
|------|------------|----------------|
| ACID 完全合规 | ✅ 完全合规 | ✅ 完全合规 |
| MVCC (多版本并发控制) | ✅ 原生支持 | ✅ InnoDB 支持 |
| 外键约束 | ✅ 完整支持 | ✅ InnoDB 支持 |
| 事务隔离级别 | ✅ 全部 4 个级别 | ✅ 全部 4 个级别 |

### 数据库架构
```sql
-- PostgreSQL
CREATE DATABASE myapp;
CREATE SCHEMA sales;
CREATE TABLE sales.orders (...);
-- 完整路径: myapp.sales.orders

-- MySQL
CREATE DATABASE myapp;
CREATE TABLE myapp.orders (...);
-- 完整路径: myapp.orders (MySQL 8.0+ 支持类似 schema 的概念)
```

## 数据类型对比

### 基本数据类型
| PostgreSQL | MySQL | 说明 |
|------------|-------|------|
| `INTEGER` | `INT` | 4字节整数 |
| `BIGINT` | `BIGINT` | 8字节整数 |
| `DECIMAL(p,s)` | `DECIMAL(p,s)` | 精确数值 |
| `NUMERIC(p,s)` | `DECIMAL(p,s)` | 精确数值别名 |
| `REAL` | `FLOAT` | 4字节浮点数 |
| `DOUBLE PRECISION` | `DOUBLE` | 8字节浮点数 |
| `VARCHAR(n)` | `VARCHAR(n)` | 变长字符串 |
| `TEXT` | `TEXT` | 长文本 |
| `TIMESTAMP` | `TIMESTAMP` | 时间戳 |
| `TIMESTAMPTZ` | `TIMESTAMP` | PostgreSQL 支持时区 |

### PostgreSQL 特有数据类型
```sql
-- PostgreSQL 独有数据类型
CREATE TABLE advanced_types (
    id SERIAL PRIMARY KEY,
    tags TEXT[],                    -- 数组类型
    config JSONB,                   -- JSON 二进制类型
    time_range TSRANGE,             -- 范围类型
    ip_address INET,                -- 网络地址类型
    point POINT,                    -- 几何点类型
    mood ENUM('sad', 'happy'),      -- 枚举类型
    uuid UUID DEFAULT uuid_generate_v4()  -- UUID 类型
);

-- MySQL 对应实现（需要使用 JSON 或文本）
CREATE TABLE mysql_equivalent (
    id INT AUTO_INCREMENT PRIMARY KEY,
    tags JSON,                      -- JSON 存储数组
    config JSON,                    -- JSON
    time_range_start TIMESTAMP,     -- 分别存储开始和结束
    time_range_end TIMESTAMP,
    ip_address VARCHAR(45),         -- 存储 IP 地址字符串
    point_lat DECIMAL(10,8),        -- 分别存储纬度和经度
    point_lng DECIMAL(11,8),
    mood ENUM('sad', 'happy'),      -- MySQL 支持枚举
    uuid CHAR(36)                   -- UUID 字符串
);
```

## 自增字段

### PostgreSQL
```sql
-- 使用 SERIAL (自动创建序列)
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100)
);

-- 或者显式使用序列
CREATE SEQUENCE users_id_seq;
CREATE TABLE users (
    id INTEGER PRIMARY KEY DEFAULT nextval('users_id_seq'),
    name VARCHAR(100)
);

-- 获取最后插入的 ID
INSERT INTO users (name) VALUES ('John');
SELECT currval('users_id_seq');  -- 获取当前序列值
-- 或使用 RETURNING 子句
INSERT INTO users (name) VALUES ('Jane') RETURNING id;
```

### MySQL
```sql
-- 使用 AUTO_INCREMENT
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100)
);

-- 获取最后插入的 ID
INSERT INTO users (name) VALUES ('John');
SELECT LAST_INSERT_ID();
```

## JSON 支持

### PostgreSQL JSONB
```sql
CREATE TABLE documents (
    id SERIAL PRIMARY KEY,
    metadata JSONB
);

-- 插入 JSON 数据
INSERT INTO documents (metadata) VALUES
('{"name": "John", "age": 30, "tags": ["developer", "admin"]}');

-- JSONB 查询操作
SELECT * FROM documents WHERE metadata->>'name' = 'John';
SELECT * FROM documents WHERE metadata @> '{"age": 30}';
SELECT * FROM documents WHERE metadata ? 'tags';

-- JSONB 修改操作
UPDATE documents
SET metadata = jsonb_set(metadata, '{age}', '31')
WHERE id = 1;

-- GIN 索引支持 JSON 查询
CREATE INDEX idx_documents_metadata_gin ON documents USING GIN (metadata);
```

### MySQL JSON
```sql
CREATE TABLE documents (
    id INT AUTO_INCREMENT PRIMARY KEY,
    metadata JSON
);

-- 插入 JSON 数据
INSERT INTO documents (metadata) VALUES
('{"name": "John", "age": 30, "tags": ["developer", "admin"]}');

-- JSON 查询操作
SELECT * FROM documents WHERE JSON_EXTRACT(metadata, '$.name') = 'John';
SELECT * FROM documents WHERE metadata->>'name' = 'John';
SELECT * FROM documents WHERE JSON_CONTAINS(metadata, '{"age": 30}');
SELECT * FROM documents WHERE JSON_CONTAINS_PATH(metadata, 'one', '$.tags');

-- JSON 修改操作
UPDATE documents
SET metadata = JSON_SET(metadata, '$.age', 31)
WHERE id = 1;

-- 创建 JSON 索引
CREATE INDEX idx_documents_name ON documents ((JSON_EXTRACT(metadata, '$.name')));
```

## 数组和集合

### PostgreSQL 数组
```sql
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    tags TEXT[]
);

-- 插入数组数据
INSERT INTO products (name, tags) VALUES
('Laptop', ARRAY['electronics', 'computer']),
('Phone', '{"mobile", "electronics"}');

-- 数组查询
SELECT * FROM products WHERE 'electronics' = ANY(tags);
SELECT * FROM products WHERE tags && ARRAY['electronics', 'mobile'];

-- 数组函数
SELECT array_length(tags, 1) FROM products WHERE id = 1;
SELECT array_append(tags, 'new_tag') FROM products WHERE id = 1;
```

### MySQL 集合
```sql
-- MySQL SET 类型（有限的预定义值）
CREATE TABLE products (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100),
    tags SET('electronics', 'computer', 'mobile', 'tablet')
);

-- 或者使用 JSON 数组
CREATE TABLE products_json (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100),
    tags JSON
);

-- 插入数据
INSERT INTO products (name, tags) VALUES
('Laptop', 'electronics,computer');

INSERT INTO products_json (name, tags) VALUES
('Laptop', JSON_ARRAY('electronics', 'computer'));

-- 查询
SELECT * FROM products WHERE FIND_IN_SET('electronics', tags) > 0;
SELECT * FROM products_json WHERE JSON_CONTAINS(tags, '"electronics"');
```

## 全文搜索

### PostgreSQL 全文搜索
```sql
CREATE TABLE articles (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255),
    content TEXT,
    search_vector TSVECTOR
);

-- 创建搜索向量
UPDATE articles
SET search_vector = to_tsvector('english', title || ' ' || content);

-- 全文搜索
SELECT title FROM articles
WHERE search_vector @@ to_tsquery('english', 'database & performance');

-- 创建索引
CREATE INDEX idx_articles_search ON articles USING GIN (search_vector);

-- 排名结果
SELECT title, ts_rank(search_vector, query) as rank
FROM articles, to_tsquery('english', 'database') query
WHERE search_vector @@ query
ORDER BY rank DESC;
```

### MySQL 全文搜索
```sql
CREATE TABLE articles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255),
    content TEXT,
    FULLTEXT(title, content)  -- 创建全文索引
) ENGINE=InnoDB;

-- 全文搜索
SELECT title FROM articles
WHERE MATCH(title, content) AGAINST('database performance' IN NATURAL LANGUAGE MODE);

-- 布尔模式
SELECT title FROM articles
WHERE MATCH(title, content) AGAINST('+database -performance' IN BOOLEAN MODE);

-- 查询扩展
SELECT title FROM articles
WHERE MATCH(title, content) AGAINST('database' WITH QUERY EXPANSION);
```

## 窗口函数

### PostgreSQL (完全支持)
```sql
SELECT
    name,
    salary,
    ROW_NUMBER() OVER (ORDER BY salary DESC) as rank,
    DENSE_RANK() OVER (ORDER BY salary DESC) as dense_rank,
    LAG(salary) OVER (ORDER BY salary) as prev_salary,
    AVG(salary) OVER (PARTITION BY department) as dept_avg
FROM employees;
```

### MySQL 8.0+ (支持)
```sql
-- MySQL 8.0+ 支持相同的窗口函数语法
SELECT
    name,
    salary,
    ROW_NUMBER() OVER (ORDER BY salary DESC) as rank,
    LAG(salary) OVER (ORDER BY salary) as prev_salary
FROM employees;
```

## 递归查询 (CTE)

### PostgreSQL 递归查询
```sql
-- 组织架构递归查询
WITH RECURSIVE employee_hierarchy AS (
    SELECT id, name, manager_id, 1 as level
    FROM employees
    WHERE manager_id IS NULL

    UNION ALL

    SELECT e.id, e.name, e.manager_id, eh.level + 1
    FROM employees e
    JOIN employee_hierarchy eh ON e.manager_id = eh.id
)
SELECT * FROM employee_hierarchy;
```

### MySQL 8.0+ 递归查询
```sql
-- MySQL 8.0+ 支持类似的递归 CTE 语法
WITH RECURSIVE employee_hierarchy AS (
    SELECT id, name, manager_id, 1 as level
    FROM employees
    WHERE manager_id IS NULL

    UNION ALL

    SELECT e.id, e.name, e.manager_id, eh.level + 1
    FROM employees e
    JOIN employee_hierarchy eh ON e.manager_id = eh.id
)
SELECT * FROM employee_hierarchy;
```

## 触发器和存储过程

### PostgreSQL 触发器
```sql
-- 创建触发器函数
CREATE OR REPLACE FUNCTION update_modified_time()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 创建触发器
CREATE TRIGGER trigger_update_modified_time
BEFORE UPDATE ON users
FOR EACH ROW EXECUTE FUNCTION update_modified_time();
```

### MySQL 触发器
```sql
-- 创建触发器
DELIMITER //
CREATE TRIGGER trigger_update_modified_time
BEFORE UPDATE ON users
FOR EACH ROW
BEGIN
    SET NEW.updated_at = CURRENT_TIMESTAMP;
END//
DELIMITER ;
```

## 索引类型

### PostgreSQL 索引
```sql
-- 多种索引类型
CREATE INDEX idx_name ON users (name);                    -- B-Tree
CREATE INDEX idx_email_hash ON users USING HASH (email);   -- Hash
CREATE INDEX idx_tags_gin ON products USING GIN (tags);   -- GIN (数组)
CREATE INDEX idx_geom_gist ON locations USING GIST (geom); -- GiST (几何)

-- 部分索引
CREATE INDEX idx_active_users ON users (id) WHERE active = true;

-- 表达式索引
CREATE INDEX idx_users_email_lower ON users (LOWER(email));
```

### MySQL 索引
```sql
-- 主要支持 B-Tree 和 Fulltext
CREATE INDEX idx_name ON users (name);          -- B-Tree
CREATE FULLTEXT INDEX idx_content ON articles(content);  -- Fulltext

-- 复合索引
CREATE INDEX idx_name_email ON users (name, email);

-- MySQL 8.0+ 支持函数索引
CREATE INDEX idx_users_email_lower ON users ((LOWER(email)));
```

## 字符串处理

### PostgreSQL 字符串函数
```sql
-- 字符串函数
SELECT SUBSTRING('hello' FROM 1 FOR 3);  -- 'hel'
SELECT POSITION('l' IN 'hello');        -- 3
SELECT TRIM(BOTH 'x' FROM 'xhellox');   -- 'hello'
SELECT REGEXP_REPLACE('hello world', 'world', 'PostgreSQL');  -- 'hello PostgreSQL'
SELECT SPLIT_PART('a,b,c', ',', 2);     -- 'b'
SELECT STRING_AGG(name, ',') FROM users;  -- 逗号分隔的字符串
```

### MySQL 字符串函数
```sql
-- 字符串函数
SELECT SUBSTRING('hello', 1, 3);        -- 'hel'
SELECT LOCATE('l', 'hello');            -- 3
SELECT TRIM('x' FROM 'xhellox');        -- 'hello'
SELECT REGEXP_REPLACE('hello world', 'world', 'MySQL');  -- 'hello MySQL'
SELECT SUBSTRING_INDEX('a,b,c', ',', 2); -- 'a,b'
SELECT GROUP_CONCAT(name SEPARATOR ',') FROM users;  -- 逗号分隔的字符串
```

## 日期时间处理

### PostgreSQL 日期时间
```sql
-- 日期时间操作
SELECT CURRENT_TIMESTAMP;               -- 当前时间戳（带时区）
SELECT NOW();                          -- 当前时间戳
SELECT CURRENT_DATE;                   -- 当前日期
SELECT CURRENT_TIME;                   -- 当前时间

-- 日期运算
SELECT CURRENT_DATE + INTERVAL '1 day';     -- 明天
SELECT CURRENT_DATE - INTERVAL '1 month';   -- 上个月
SELECT AGE(CURRENT_DATE, '2000-01-01');     -- 年龄间隔

-- 日期格式化
SELECT TO_CHAR(CURRENT_TIMESTAMP, 'YYYY-MM-DD HH24:MI:SS');

-- 日期提取
SELECT EXTRACT(YEAR FROM CURRENT_DATE);
SELECT DATE_PART('month', CURRENT_TIMESTAMP);
```

### MySQL 日期时间
```sql
-- 日期时间操作
SELECT NOW();                          -- 当前时间戳
SELECT CURRENT_TIMESTAMP;              -- 当前时间戳
SELECT CURDATE();                      -- 当前日期
SELECT CURTIME();                      -- 当前时间

-- 日期运算
SELECT DATE_ADD(CURDATE(), INTERVAL 1 DAY);     -- 明天
SELECT DATE_SUB(CURDATE(), INTERVAL 1 MONTH);   -- 上个月
SELECT DATEDIFF(CURDATE(), '2000-01-01');       -- 天数差

-- 日期格式化
SELECT DATE_FORMAT(NOW(), '%Y-%m-%d %H:%i:%s');

-- 日期提取
SELECT YEAR(NOW());
SELECT MONTH(NOW());
SELECT DAY(NOW());
```

## 数据库连接与客户端工具

### 连接命令
| 操作 | PostgreSQL | MySQL |
|------|------------|-------|
| 连接数据库 | `psql -h host -U user -d db` | `mysql -h host -u user -p db` |
| 列出数据库 | `\l` | `SHOW DATABASES;` |
| 切换数据库 | `\c dbname` | `USE dbname;` |
| 列出表 | `\dt` | `SHOW TABLES;` |
| 描述表结构 | `\d table` | `DESC table;` |
| 退出 | `\q` | `QUIT;` 或 `EXIT;` |

## 配置文件位置

### PostgreSQL
```
数据目录:
├── postgresql.conf    # 主配置文件
├── pg_hba.conf       # 访问控制
├── pg_ident.conf     # 用户映射
└── postgresql.auto.conf  # 自动生成的配置
```

### MySQL
```
配置目录:
├── my.cnf            # 主配置文件
├── my.ini            # Windows 配置文件
└── mysql.conf.d/     # 配置目录（Linux）
```

## 迁移注意事项

### 数据迁移工具
```bash
# 使用 pgloader 从 MySQL 迁移到 PostgreSQL
pgloader mysql://user:password@localhost/mydb postgresql://user:password@localhost/mydb

# 使用 mysqldump 导出数据
mysqldump -u user -p mydb > mysql_dump.sql

# 使用 psql 导入到 PostgreSQL
psql -d mydb -f mysql_dump.sql
```

### SQL 语法调整
```sql
-- MySQL 自动递增
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100)
);

-- PostgreSQL SERIAL
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100)
);

-- MySQL 反引号
SELECT `name`, `email` FROM `users`;

-- PostgreSQL 双引号或无引号
SELECT "name", "email" FROM "users";
-- 或
SELECT name, email FROM users;
```

## 性能特点对比

### 查询优化
- **PostgreSQL**: 更复杂的查询优化器，支持更多索引类型
- **MySQL**: 简单高效的查询优化器，适合简单查询

### 并发控制
- **PostgreSQL**: MVCC，读写不互相阻塞
- **MySQL**: MVCC (InnoDB)，但有一些限制

### 复制
- **PostgreSQL**: 流复制，逻辑复制
- **MySQL**: 二进制日志复制，半同步复制

## 选择建议

### 选择 PostgreSQL 的场景
- 需要复杂查询和数据分析
- 需要地理空间数据（PostGIS）
- 需要时间序列数据
- 需要严格的数据一致性
- 需要自定义扩展和数据类型

### 选择 MySQL 的场景
- 简单的 CRUD 操作
- 高并发读取
- 需要与现有 MySQL 生态系统集成
- 团队更熟悉 MySQL

## 常见迁移问题及解决方案

### 数据类型映射
```sql
-- MySQL ENUM -> PostgreSQL CHECK 或 ENUM
-- MySQL TINYINT(1) -> PostgreSQL BOOLEAN
-- MySQL DATETIME -> PostgreSQL TIMESTAMP
-- MySQL TEXT -> PostgreSQL TEXT
```

### 字符集问题
```sql
-- MySQL 默认字符集
SET NAMES 'utf8mb4';

-- PostgreSQL 字符集
CREATE DATABASE mydb WITH ENCODING 'UTF8';
```

### 自增字段处理
```sql
-- 迁移后重建序列
SELECT setval('users_id_seq', (SELECT max(id) FROM users));
```

PostgreSQL 和 MySQL 都是非常优秀的数据库系统，选择哪个主要取决于具体的应用场景、团队经验和性能需求。PostgreSQL 在功能丰富性和标准合规性方面更胜一筹，而 MySQL 在简单性和易用性方面有优势。