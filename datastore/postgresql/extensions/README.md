# PostgreSQL 扩展机制

PostgreSQL 的扩展机制是其最强大的特性之一，允许开发者添加新的功能、数据类型、函数和操作符。本章节介绍 PostgreSQL 的扩展系统以及常用的扩展。

## 扩展系统概述

### 什么是扩展

扩展是打包好的 SQL 对象集合，可以一次性安装到数据库中。扩展可以包含：
- 数据类型
- 函数
- 操作符
- 索引类型
- 聚合函数
- 转换

### 扩展的优势

1. **模块化**：将相关功能组合在一起
2. **可移植性**：易于在不同数据库间安装和卸载
3. **版本控制**：支持扩展的版本管理
4. **依赖管理**：自动处理扩展间的依赖关系

## 扩展管理命令

### 查看可用扩展
```sql
-- 查看所有可用的扩展
SELECT * FROM pg_available_extensions;

-- 查看已安装的扩展
SELECT * FROM pg_extension;

-- 查看特定扩展的详细信息
\dx plpgsql
\dx postgis
```

### 安装和卸载扩展
```sql
-- 安装扩展
CREATE EXTENSION extension_name;

-- 安装特定版本的扩展
CREATE EXTENSION extension_name VERSION '2.0';

-- 安装扩展到指定模式
CREATE EXTENSION extension_name SCHEMA schema_name;

-- 卸载扩展
DROP EXTENSION extension_name;

-- 卸载扩展并删除其数据
DROP EXTENSION extension_name CASCADE;
```

### 扩展更新
```sql
-- 更新扩展到最新版本
ALTER EXTENSION extension_name UPDATE;

-- 更新到指定版本
ALTER EXTENSION extension_name UPDATE TO '2.1';
```

## 核心扩展

### uuid-ossp

UUID 生成扩展，提供多种 UUID 生成算法。

```sql
-- 安装扩展
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 生成 UUID
SELECT uuid_generate_v1();    -- 基于MAC地址和时间
SELECT uuid_generate_v4();    -- 随机UUID
SELECT uuid_generate_v3(uuid_ns_dns(), 'example.com');  -- MD5 hash
SELECT uuid_generate_v5(uuid_ns_dns(), 'example.com');  -- SHA-1 hash

-- 在表中使用
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100),
    email VARCHAR(255)
);

-- 插入数据
INSERT INTO users (name, email) VALUES ('John Doe', 'john@example.com');
```

### pg_trgm

三元组扩展，提供模糊字符串匹配功能。

```sql
-- 安装扩展
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- 三元组相似度
SELECT similarity('hello', 'hallo');  -- 返回 0-1 之间的相似度

-- 模糊匹配
SELECT word FROM words WHERE word % 'hello';  -- 相似度 > 0.3

-- 自定义相似度阈值
SET pg_trgm.similarity_threshold = 0.5;
SELECT word FROM words WHERE word % 'hello';

-- 创建 GIN 索引支持模糊搜索
CREATE INDEX idx_words_word_gin ON words USING GIN (word gin_trgm_ops);

-- 使用 GIN 索引的模糊搜索
SELECT word FROM words WHERE word LIKE '%hello%';
```

### pgcrypto

加密扩展，提供各种加密函数。

```sql
-- 安装扩展
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- 密码哈希
SELECT crypt('password', gen_salt('bf', 12));

-- 验证密码
SELECT crypt('password', stored_hash) = stored_hash;

-- 数据加密
SELECT encrypt('secret data', 'encryption_key', 'aes');
SELECT decrypt(encrypted_data, 'encryption_key', 'aes');

-- 哈希函数
SELECT md5('data');
SELECT sha256('data');

-- 生成随机数据
SELECT gen_random_bytes(16);
```

### tablefunc

表格函数扩展，提供交叉表和类别数据转换功能。

```sql
-- 安装扩展
CREATE EXTENSION IF NOT EXISTS tablefunc;

-- 交叉表示例
CREATE TABLE sales (
    year INTEGER,
    quarter VARCHAR(10),
    amount NUMERIC
);

INSERT INTO sales VALUES
(2023, 'Q1', 100000),
(2023, 'Q2', 120000),
(2023, 'Q3', 110000),
(2023, 'Q4', 130000);

-- 创建交叉表
SELECT * FROM crosstab(
    'SELECT year, quarter, amount FROM sales ORDER BY 1,2',
    'SELECT DISTINCT quarter FROM sales ORDER BY 1'
) AS ct(year INTEGER, q1 NUMERIC, q2 NUMERIC, q3 NUMERIC, q4 NUMERIC);

-- 结果：
-- year |    q1    |    q2    |    q3    |    q4
-- -----+----------+----------+----------+----------
-- 2023 | 100000   | 120000   | 110000   | 130000
```

### adminpack

数据库管理扩展，提供服务器端管理功能。

```sql
-- 安装扩展（需要超级用户权限）
CREATE EXTENSION IF NOT EXISTS adminpack;

-- 重命名文件
SELECT pg_file_rename('old_file.txt', 'new_file.txt');

-- 复制文件
SELECT pg_file_copy('source.txt', 'destination.txt');

-- 创建目录
SELECT pg_file_mkdir('new_directory');

-- 获取文件信息
SELECT * FROM pg_file_stat('important_file.txt');
```

## 常用第三方扩展

### PostGIS

地理空间数据库扩展，是 PostgreSQL 最著名的扩展。

```sql
-- 安装 PostGIS
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS postgis_topology;

-- 创建地理空间表
CREATE TABLE locations (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    geom GEOMETRY(POINT, 4326)
);

-- 插入地理数据
INSERT INTO locations (name, geom) VALUES
('New York', ST_GeomFromText('POINT(-74.0060 40.7128)', 4326)),
('London', ST_GeomFromText('POINT(-0.1278 51.5074)', 4326));

-- 空间查询
-- 计算两点间距离
SELECT
    l1.name,
    l2.name,
    ST_Distance(l1.geom, l2.geom) as distance_meters
FROM locations l1, locations l2
WHERE l1.name = 'New York' AND l2.name = 'London';

-- 查找指定范围内的点
SELECT name FROM locations
WHERE ST_DWithin(
    geom,
    ST_GeomFromText('POINT(-74.0060 40.7128)', 4326),
    100000  -- 100km
);

-- 空间索引
CREATE INDEX idx_locations_geom ON locations USING GIST (geom);
```

### pg_stat_statements

查询统计扩展，用于监控和分析 SQL 查询性能。

```sql
-- 安装扩展
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;

-- 配置 postgresql.conf
# shared_preload_libraries = 'pg_stat_statements'
# pg_stat_statements.track = all
# pg_stat_statements.max = 10000

-- 重启数据库后查看查询统计
SELECT
    query,
    calls,
    total_time,
    mean_time,
    rows
FROM pg_stat_statements
ORDER BY total_time DESC
LIMIT 10;

-- 重置统计信息
SELECT pg_stat_statements_reset();

-- 查看最频繁的查询
SELECT query, calls FROM pg_stat_statements ORDER BY calls DESC LIMIT 10;
```

### hstore

键值对数据类型扩展。

```sql
-- 安装扩展
CREATE EXTENSION IF NOT EXISTS hstore;

-- 创建包含 hstore 的表
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    attributes hstore
);

-- 插入数据
INSERT INTO products (name, attributes) VALUES
('Laptop', '"color"=>"black", "weight"=>"1.5kg", "brand"=>"Dell"'),
('Phone', '"color"=>"white", "weight"=>"200g", "brand"=>"Apple"');

-- 查询 hstore 数据
SELECT name, attributes FROM products WHERE attributes->'brand' = 'Apple';

-- 获取所有键
SELECT akeys(attributes) FROM products WHERE id = 1;

-- 获取所有值
SELECT avals(attributes) FROM products WHERE id = 1;

-- 更新 hstore 数据
UPDATE products
SET attributes = attributes || hstore('price', '999')
WHERE id = 1;

-- 删除键值对
UPDATE products
SET attributes = delete(attributes, 'weight')
WHERE id = 1;

-- 检查键是否存在
SELECT name FROM products WHERE attributes ? 'color';

-- GIN 索引
CREATE INDEX idx_products_attributes_gin ON products USING GIN (attributes);
```

### citext

不区分大小写的文本数据类型。

```sql
-- 安装扩展
CREATE EXTENSION IF NOT EXISTS citext;

-- 创建使用 citext 的表
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username CITEXT UNIQUE,
    email CITEXT UNIQUE
);

-- 插入数据
INSERT INTO users (username, email) VALUES
('JohnDoe', 'john@example.com'),
('jane_smith', 'JANE@EXAMPLE.COM');

-- 不区分大小写的查询
SELECT * FROM users WHERE username = 'johndoe';
SELECT * FROM users WHERE email = 'JOHN@EXAMPLE.COM';

-- 创建索引
CREATE INDEX idx_users_username ON users (username);
CREATE INDEX idx_users_email ON users (email);
```

### btree_gin

为 B-Tree 索引支持的数据类型提供 GIN 索引。

```sql
-- 安装扩展
CREATE EXTENSION IF NOT EXISTS btree_gin;

-- 创建表
CREATE TABLE events (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    event_date DATE,
    status VARCHAR(20)
);

-- 使用 btree_gin 创建 GIN 索引
CREATE INDEX idx_events_gin ON events USING GIN (name, event_date, status);

-- 支持 AND 查询
SELECT * FROM events
WHERE name = 'Conference'
  AND event_date BETWEEN '2023-12-01' AND '2023-12-31'
  AND status = 'active';
```

### pg_hint_plan

查询计划提示扩展，允许优化器选择特定的查询计划。

```sql
-- 安装扩展（需要编译安装）
CREATE EXTENSION IF NOT EXISTS pg_hint_plan;

-- 使用提示
/*+ HashJoin(users orders) */
SELECT * FROM users JOIN orders ON users.id = orders.user_id;

/*+ IndexScan(products idx_products_category) */
SELECT * FROM products WHERE category = 'Electronics';

/*+ SeqScan(users) */
SELECT * FROM users WHERE active = true;
```

## 创建自定义扩展

### 扩展目录结构

```
my_extension/
├── my_extension.control    # 扩展控制文件
├── my_extension--1.0.sql   # 安装脚本
├── my_extension--1.0--1.1.sql  # 升级脚本
├── Makefile              # 构建文件
└── src/
    └── my_extension.c    # C 源码（如需要）
```

### 扩展控制文件

```sql
-- my_extension.control
comment = 'My Custom Extension'
default_version = '1.0'
module_pathname = '$libdir/my_extension'
relocatable = true
requires = 'uuid-ossp,pgcrypto'
```

### 安装脚本

```sql
-- my_extension--1.0.sql
-- 创建自定义函数
CREATE OR REPLACE FUNCTION calculate_vat(price NUMERIC, vat_rate NUMERIC)
RETURNS NUMERIC AS $$
BEGIN
    RETURN price * (vat_rate / 100);
END;
$$ LANGUAGE plpgsql;

-- 创建自定义数据类型
CREATE TYPE mood AS ENUM ('sad', 'happy', 'neutral');

-- 创建自定义操作符
CREATE OPERATOR === (
    LEFTARG = text,
    RIGHTARG = text,
    PROCEDURE = texteq,
    COMMUTATOR = ===
);

-- 创建自定义聚合函数
CREATE AGGREGATE weighted_average(NUMERIC, NUMERIC) (
    SFUNC = weighted_average_trans,
    STYPE = NUMERIC,
    FINALFUNC = weighted_average_final
);

-- 创建示例表
CREATE TABLE sample_data (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    name TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 编译和安装扩展

```bash
# 安装 PostgreSQL 开发包
sudo apt-get install postgresql-server-dev-all

# 编译扩展
make

# 安装扩展
sudo make install

# 在数据库中创建扩展
psql -d mydb -c "CREATE EXTENSION my_extension;"
```

### SQL 函数扩展示例

```sql
-- 创建复杂的字符串处理函数
CREATE OR REPLACE FUNCTION camel_case(input_text TEXT)
RETURNS TEXT AS $$
DECLARE
    words TEXT[];
    result TEXT := '';
BEGIN
    words := regexp_split_to_array(lower(input_text), '[^a-zA-Z]');

    FOREACH word IN ARRAY words LOOP
        IF word != '' THEN
            result := result || upper(substr(word, 1, 1)) || substr(word, 2);
        END IF;
    END LOOP;

    RETURN result;
END;
$$ LANGUAGE plpgsql;

-- 使用函数
SELECT camel_case('hello world example');  -- HelloWorldExample
```

## 扩展管理最佳实践

### 扩展安装规划

```sql
-- 1. 在安装前检查扩展依赖
SELECT * FROM pg_available_dependencies
WHERE refobjid = (SELECT oid FROM pg_extension WHERE extname = 'target_extension');

-- 2. 安装扩展前进行测试
BEGIN;
CREATE EXTENSION test_extension;
-- 测试功能
ROLLBACK;

-- 3. 记录扩展版本
SELECT extname, extversion FROM pg_extension;
```

### 扩展升级策略

```sql
-- 1. 备份数据库
pg_dump mydb > backup_before_extension_upgrade.sql

-- 2. 检查扩展升级路径
ALTER EXTENSION my_extension UPDATE TO '2.0';

-- 3. 验证升级结果
SELECT * FROM pg_extension WHERE extname = 'my_extension';
```

### 性能监控

```sql
-- 监控扩展使用的查询
SELECT query, calls, total_time
FROM pg_stat_statements
WHERE query LIKE '%extension_function%';

-- 检查扩展创建的对象
SELECT
    n.nspname as schema_name,
    c.relname as object_name,
    c.relkind as object_type
FROM pg_class c
JOIN pg_namespace n ON n.oid = c.relnamespace
WHERE n.nspname IN (
    SELECT extnamespace::regnamespace::text
    FROM pg_extension
    WHERE extname = 'extension_name'
);
```

PostgreSQL 的扩展机制为数据库提供了强大的可扩展性，允许开发者根据特定需求定制数据库功能。通过合理使用现有扩展和开发自定义扩展，可以显著增强 PostgreSQL 的功能性和适用性。