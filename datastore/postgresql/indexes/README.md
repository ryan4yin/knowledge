# PostgreSQL 索引类型

PostgreSQL 提供了多种索引类型，每种类型都针对特定的查询模式进行了优化。正确选择和使用索引类型可以显著提高查询性能。

## B-Tree 索引

B-Tree (平衡树) 是 PostgreSQL 中最常用的索引类型，也是默认的索引类型。它适合处理等值查询和范围查询。

### 基本用法
```sql
-- 创建示例表
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    category VARCHAR(50),
    price NUMERIC(10,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 创建 B-Tree 索引
CREATE INDEX idx_products_name ON products (name);
CREATE INDEX idx_products_price ON products (price);

-- 复合索引
CREATE INDEX idx_products_category_price ON products (category, price);

-- 唯一索引
CREATE UNIQUE INDEX idx_products_name_unique ON products (name);

-- 使用索引的查询
EXPLAIN SELECT * FROM products WHERE name = 'iPhone';
EXPLAIN SELECT * FROM products WHERE price BETWEEN 100 AND 500;
EXPLAIN SELECT * FROM products WHERE category = 'Electronics' AND price > 100;
```

### 索引排序选项
```sql
-- 升序索引（默认）
CREATE INDEX idx_products_price_asc ON products (price ASC);

-- 降序索引
CREATE INDEX idx_products_price_desc ON products (price DESC);

-- 复合排序索引
CREATE INDEX idx_products_category_price_asc_desc ON products (category ASC, price DESC);

-- NULLS FIRST/LAST
CREATE INDEX idx_products_price_nulls_first ON products (price NULLS FIRST);
```

## Hash 索引

Hash 索引只支持等值比较，不支持范围查询。在 PostgreSQL 10 之前，Hash 索引不被 WAL 记录，存在崩溃恢复问题。从 PostgreSQL 10 开始，这个问题已经解决。

### 基本用法
```sql
-- 创建 Hash 索引
CREATE INDEX idx_users_email_hash ON users USING HASH (email);

-- Hash 索引只支持等值查询
EXPLAIN SELECT * FROM users WHERE email = 'user@example.com';

-- 不支持范围查询
SELECT * FROM users WHERE email > 'a';  -- 不会使用 Hash 索引
```

### Hash 索引的适用场景
```sql
-- 适合 Hash 索引的场景
CREATE TABLE user_sessions (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(128) NOT NULL,
    user_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 为 session_id 创建 Hash 索引
CREATE INDEX idx_sessions_session_hash ON user_sessions USING HASH (session_id);

-- 查询会使用 Hash 索引
SELECT * FROM user_sessions WHERE session_id = 'abc123def456';
```

## GIN 索引

GIN (Generalized Inverted Index) 索引适用于复合数据类型，如数组、JSONB 和全文搜索。

### 数组索引
```sql
CREATE TABLE articles (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255),
    tags TEXT[],
    content TEXT
);

-- 为数组创建 GIN 索引
CREATE INDEX idx_articles_tags_gin ON articles USING GIN (tags);

-- 查询数组包含特定元素
EXPLAIN SELECT * FROM articles WHERE tags @> ARRAY['postgresql'];
EXPLAIN SELECT * FROM articles WHERE 'database' = ANY(tags);

-- 查询数组重叠
EXPLAIN SELECT * FROM articles WHERE tags && ARRAY['sql', 'nosql'];
```

### JSONB 索引
```sql
CREATE TABLE documents (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255),
    metadata JSONB
);

-- 为 JSONB 字段创建 GIN 索引
CREATE INDEX idx_documents_metadata_gin ON documents USING GIN (metadata);

-- JSONB 查询会使用 GIN 索引
EXPLAIN SELECT * FROM documents WHERE metadata @> '{"author": "John"}';
EXPLAIN SELECT * FROM documents WHERE metadata ? 'category';
EXPLAIN SELECT * FROM documents WHERE metadata ?| array['title', 'author'];
```

### 默认 GIN 索引选项
```sql
-- 使用 fastupdate 选项（默认）
CREATE INDEX idx_articles_tags_gin_fast ON articles USING GIN (tags) WITH (fastupdate = on);

-- 禁用 fastupdate（插入性能稍差，但查询更及时）
CREATE INDEX idx_articles_tags_gin_nofast ON articles USING GIN (tags) WITH (fastupdate = off);
```

## GiST 索引

GiST (Generalized Search Tree) 索引适用于索引复合数据类型和几何数据，支持多种查询操作符。

### 几何数据索引
```sql
CREATE TABLE locations (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    point POINT,
    polygon POLYGON
);

-- 为几何数据创建 GiST 索引
CREATE INDEX idx_locations_point_gist ON locations USING GIST (point);
CREATE INDEX idx_locations_polygon_gist ON locations USING GIST (polygon);

-- 几何查询会使用 GiST 索引
EXPLAIN SELECT * FROM locations WHERE point <@ '(0,0), (10,10)'::BOX;
EXPLAIN SELECT * FROM locations WHERE polygon && '((5,5), (15,15))::BOX;
```

### 全文搜索索引
```sql
-- 为全文搜索创建 GiST 索引
CREATE TABLE articles_fts (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255),
    content TEXT,
    search_vector TSVECTOR
);

-- 更新搜索向量
UPDATE articles_fts
SET search_vector = to_tsvector('english', title || ' ' || content);

-- 创建 GiST 索引（比 GIN 小但更新快）
CREATE INDEX idx_articles_fts_vector_gist ON articles_fts USING GIST (search_vector);

-- 全文搜索查询
EXPLAIN SELECT title FROM articles_fts
WHERE search_vector @@ to_tsquery('english', 'database & performance');
```

### 范围类型索引
```sql
CREATE TABLE schedules (
    id SERIAL PRIMARY KEY,
    event_name VARCHAR(100),
    time_range TSRANGE
);

-- 为范围类型创建 GiST 索引
CREATE INDEX idx_schedules_time_gist ON schedules USING GIST (time_range);

-- 范围查询会使用 GiST 索引
EXPLAIN SELECT * FROM schedules WHERE time_range && '[2023-12-01, 2023-12-31]'::TSRANGE;
EXPLAIN SELECT * FROM schedules WHERE time_range @> '2023-12-25 10:00:00'::TIMESTAMP;
```

## SP-GiST 索引

SP-GiST (Space-Partitioned Generalized Search Tree) 索引适用于非平衡数据结构，如前缀树、四叉树等。

### 文本前缀索引
```sql
CREATE TABLE words (
    id SERIAL PRIMARY KEY,
    word VARCHAR(100)
);

-- 为文本前缀搜索创建 SP-GiST 索引
CREATE INDEX idx_words_word_spgist ON words USING SPGIST (word);

-- 前缀查询会使用 SP-GiST 索引
EXPLAIN SELECT * FROM words WHERE word LIKE 'auto%';
EXPLAIN SELECT * FROM words WHERE word ~ '^auto';
```

### 网络地址索引
```sql
CREATE TABLE ip_addresses (
    id SERIAL PRIMARY KEY,
    ip INET,
    description VARCHAR(255)
);

-- 为网络地址创建 SP-GiST 索引
CREATE INDEX idx_ip_addresses_ip_spgist ON ip_addresses USING SPGIST (ip);

-- 网络查询会使用 SP-GiST 索引
EXPLAIN SELECT * FROM ip_addresses WHERE ip <<= '192.168.1.0/24';
```

## BRIN 索引

BRIN (Block Range Index) 索引适用于很大的表，其中数据按物理顺序有某种自然排序。

### 时间序列数据索引
```sql
CREATE TABLE sensor_readings (
    id BIGSERIAL PRIMARY KEY,
    sensor_id INTEGER,
    reading_time TIMESTAMP,
    value NUMERIC(10,4)
);

-- 为时间序列数据创建 BRIN 索引
CREATE INDEX idx_sensor_readings_time_brin ON sensor_readings USING BRIN (reading_time);

-- 为传感器 ID 创建 BRIN 索引
CREATE INDEX idx_sensor_readings_sensor_brin ON sensor_readings USING BRIN (sensor_id);

-- 时间范围查询会使用 BRIN 索引
EXPLAIN SELECT * FROM sensor_readings
WHERE reading_time BETWEEN '2023-12-01' AND '2023-12-31';

-- BRIN 索引参数
CREATE INDEX idx_sensor_readings_time_brin_custom ON sensor_readings
USING BRIN (reading_time) WITH (pages_per_range = 128);
```

### BRIN 索引的适用场景
```sql
-- 适合 BRIN 索引的表特征：
-- 1. 表非常大（数百万行以上）
-- 2. 数据按物理位置有自然排序
-- 3. 查询主要是范围查询

-- 不适合 BRIN 索引的场景：
-- 1. 小表
-- 2. 数据随机分布
-- 3. 需要精确匹配查询
```

## 部分索引 (Partial Index)

部分索引只对表中满足特定条件的行创建索引，可以减少索引大小并提高性能。

### 创建部分索引
```sql
CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    customer_id INTEGER,
    status VARCHAR(20) DEFAULT 'pending',
    total_amount NUMERIC(10,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 只为活跃订单创建索引
CREATE INDEX idx_orders_active_customer ON orders (customer_id)
WHERE status IN ('pending', 'processing');

-- 只为大额订单创建索引
CREATE INDEX idx_orders_large_amount ON orders (customer_id, created_at)
WHERE total_amount > 1000;

-- 使用部分索引的查询
EXPLAIN SELECT * FROM orders WHERE customer_id = 123 AND status = 'pending';
EXPLAIN SELECT * FROM orders WHERE customer_id = 456 AND total_amount > 1500;
```

### 部分索引的最佳实践
```sql
-- 1. 对布尔字段创建部分索引
CREATE INDEX idx_users_active ON users (id) WHERE active = true;

-- 2. 对软删除数据创建部分索引
CREATE INDEX idx_articles_not_deleted ON articles (created_at) WHERE deleted_at IS NULL;

-- 3. 对时间序列的最新数据创建部分索引
CREATE INDEX idx_logs_recent ON logs (created_at) WHERE created_time > CURRENT_DATE - INTERVAL '7 days';
```

## 表达式索引

表达式索引基于计算表达式而不是简单的列值创建索引。

### 基本表达式索引
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255),
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 为小写邮箱创建索引（支持不区分大小写搜索）
CREATE INDEX idx_users_email_lower ON users (LOWER(email));

-- 为全名创建索引
CREATE INDEX idx_users_full_name ON users ((first_name || ' ' || last_name));

-- 为日期部分创建索引
CREATE INDEX idx_users_created_year ON users (EXTRACT(YEAR FROM created_at));

-- 使用表达式索引的查询
EXPLAIN SELECT * FROM users WHERE LOWER(email) = 'USER@EXAMPLE.COM';
EXPLAIN SELECT * FROM users WHERE (first_name || ' ' || last_name) = 'John Doe';
EXPLAIN SELECT * FROM users WHERE EXTRACT(YEAR FROM created_at) = 2023;
```

### 复杂表达式索引
```sql
-- 为计算字段创建索引
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    price NUMERIC(10,2),
    cost NUMERIC(10,2),
    discount NUMERIC(5,2)
);

-- 为利润率创建索引
CREATE INDEX idx_products_profit_margin ON products ((price - cost) / price);

-- 为折扣后价格创建索引
CREATE INDEX idx_products_discounted_price ON products ((price * (1 - discount / 100)));

-- 使用复杂表达式索引
SELECT * FROM products WHERE (price - cost) / price > 0.3;
SELECT * FROM products WHERE price * (1 - discount / 100) < 100;
```

## 唯一索引和约束

### 唯一索引
```sql
-- 创建唯一索引
CREATE UNIQUE INDEX idx_users_email_unique ON users (email);

-- 复合唯一索引
CREATE UNIQUE INDEX idx_user_roles_unique ON user_roles (user_id, role_id);

-- 部分唯一索引
CREATE UNIQUE INDEX idx_users_active_email ON users (email) WHERE active = true;

-- 表达式唯一索引
CREATE UNIQUE INDEX idx_users_username_lower ON users (LOWER(username));
```

### 唯一约束 vs 唯一索引
```sql
-- 唯一约束（推荐方式）
ALTER TABLE users ADD CONSTRAINT users_email_unique UNIQUE (email);

-- 唯一索引（功能相同，但不能作为约束）
CREATE UNIQUE INDEX idx_users_email_unique ON users (email);
```

## 索引维护

### 查看索引信息
```sql
-- 查看表的所有索引
SELECT indexname, indexdef FROM pg_indexes WHERE tablename = 'products';

-- 查看索引大小
SELECT schemaname, tablename, indexname,
       pg_size_pretty(pg_relation_size(indexname::regclass)) AS size
FROM pg_indexes
JOIN pg_class ON pg_class.relname = indexname
JOIN pg_namespace ON pg_namespace.oid = pg_class.relnamespace
WHERE tablename = 'products';

-- 查看索引使用统计
SELECT schemaname, tablename, indexname, idx_scan, idx_tup_read, idx_tup_fetch
FROM pg_stat_user_indexes
WHERE tablename = 'products';
```

### 重建索引
```sql
-- 重建单个索引
REINDEX INDEX idx_products_name;

-- 重建表的所有索引
REINDEX TABLE products;

-- 重建数据库的所有索引（需要超级用户权限）
REINDEX DATABASE mydatabase;
```

### 并行创建索引
```sql
-- 使用并行创建索引（PostgreSQL 11+）
CREATE INDEX CONCURRENTLY idx_products_name_parallel ON products (name)
WITH (parallel_workers = 4);

-- 设置默认并行度
SET parallel_index_create_workers = 4;
CREATE INDEX idx_products_category ON products (category);
```

## 索引优化建议

### 选择合适的索引类型
```sql
-- 1. B-Tree: 默认选择，适用于等值和范围查询
-- 2. Hash: 只适用于等值查询，查询速度更快但功能有限
-- 3. GIN: 适用于数组、JSONB、全文搜索
-- 4. GiST: 适用于几何数据、范围数据、全文搜索
-- 5. SP-GiST: 适用于前缀搜索、网络地址搜索
-- 6. BRIN: 适用于大表的范围查询
```

### 索引设计原则
```sql
-- 1. 为经常出现在 WHERE 子句中的列创建索引
-- 2. 为经常用于 JOIN 的列创建索引
-- 3. 为 ORDER BY 和 GROUP BY 的列创建索引
-- 4. 避免过度索引，每个索引都会增加写操作的开销
-- 5. 使用部分索引减少索引大小
-- 6. 使用表达式索引支持特定查询模式
```

### 查询优化
```sql
-- 查看查询执行计划
EXPLAIN ANALYZE SELECT * FROM products WHERE category = 'Electronics';

-- 强制使用特定索引（通常不需要）
SET enable_seqscan = off;  -- 禁用全表扫描
SET enable_indexscan = on; -- 启用索引扫描
```

通过正确选择和配置索引类型，可以显著提高 PostgreSQL 数据库的查询性能。定期监控索引使用情况并进行必要的调整是数据库优化的关键环节。