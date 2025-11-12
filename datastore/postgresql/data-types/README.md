# PostgreSQL 数据类型

PostgreSQL 提供了丰富的数据类型，包括标准 SQL 数据类型和许多特有的高级数据类型。这些数据类型使 PostgreSQL 能够处理各种复杂的数据存储需求。

## 标准数据类型

### 数值类型

#### 整数类型
```sql
-- 小整数：2字节，-32768 到 32767
CREATE TABLE products (
    id SMALLINT PRIMARY KEY,
    quantity SMALLINT
);

-- 整数：4字节，-2147483648 到 2147483647
CREATE TABLE orders (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL
);

-- 大整数：8字节，-9223372036854775808 到 9223372036854775807
CREATE TABLE big_data (
    id BIGINT PRIMARY KEY,
    count BIGINT
);
```

#### 自增整数类型
```sql
-- SERIAL 等价于创建序列
CREATE TABLE users (
    id SERIAL PRIMARY KEY,  -- 等价于 INTEGER NOT NULL DEFAULT nextval('users_id_seq'::regclass)
    name TEXT
);

-- BIGSERIAL 自增大整数
CREATE TABLE logs (
    id BIGSERIAL PRIMARY KEY,
    message TEXT
);
```

#### 精确数值类型
```sql
-- NUMERIC(精度, 小数位数)
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    price NUMERIC(10, 2)  -- 总共10位数字，其中2位小数
);

-- DECIMAL 是 NUMERIC 的别名
CREATE TABLE accounts (
    id SERIAL PRIMARY KEY,
    balance DECIMAL(15, 2)
);
```

#### 浮点类型
```sql
-- REAL: 4字节浮点数
CREATE TABLE measurements (
    id SERIAL PRIMARY KEY,
    temperature REAL
);

-- DOUBLE PRECISION: 8字节浮点数
CREATE TABLE scientific_data (
    id SERIAL PRIMARY KEY,
    value DOUBLE PRECISION
);
```

#### 货币类型
```sql
-- MONEY 类型，存储货币金额
CREATE TABLE transactions (
    id SERIAL PRIMARY KEY,
    amount MONEY,
    currency VARCHAR(3) DEFAULT 'USD'
);

-- 插入数据
INSERT INTO transactions (amount) VALUES ('$19.99');
```

### 字符类型

#### CHAR 和 VARCHAR
```sql
CREATE TABLE customers (
    id SERIAL PRIMARY KEY,
    -- CHAR: 定长字符串，不足长度用空格填充
    country_code CHAR(2),

    -- VARCHAR: 变长字符串，最多255字符
    name VARCHAR(100),

    -- TEXT: 变长文本，无长度限制
    description TEXT
);
```

### 日期时间类型

```sql
CREATE TABLE events (
    id SERIAL PRIMARY KEY,
    -- DATE: 日期（年月日）
    event_date DATE,

    -- TIME: 时间（时分秒）
    event_time TIME,

    -- TIMESTAMP: 日期和时间
    event_timestamp TIMESTAMP,

    -- TIMESTAMPTZ: 带时区的日期时间
    event_timestamp_tz TIMESTAMPTZ,

    -- INTERVAL: 时间间隔
    duration INTERVAL
);

-- 插入数据示例
INSERT INTO events VALUES (
    1,
    '2023-12-25',
    '14:30:00',
    '2023-12-25 14:30:00',
    '2023-12-25 14:30:00+08',
    '2 hours 30 minutes'
);
```

## PostgreSQL 特有数据类型

### ARRAY 数组类型

PostgreSQL 支持将任何数据类型定义为数组。

#### 一维数组
```sql
-- 创建包含数组的表
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    tags TEXT[],              -- 文本数组
    prices NUMERIC(10,2)[],   -- 价格数组
    available_days INTEGER[]  -- 可用日期数组
);

-- 插入数组数据
INSERT INTO products (name, tags, prices, available_days) VALUES
('Smartphone', ARRAY['electronics', 'mobile', 'tech'],
 ARRAY[299.99, 279.99, 259.99],
 ARRAY[1, 2, 3, 4, 5]);

-- 或者使用花括号语法
INSERT INTO products (name, tags, prices) VALUES
('Laptop', '{"computer", "work", "portable"}',
 '{999.99, 949.99, 899.99}');
```

#### 数组操作
```sql
-- 查询包含特定标签的产品
SELECT name, tags FROM products WHERE 'electronics' = ANY(tags);

-- 查询数组长度
SELECT name, array_length(tags, 1) AS tag_count FROM products;

-- 添加元素到数组
UPDATE products
SET tags = array_append(tags, 'new_tag')
WHERE id = 1;

-- 删除数组中的元素
UPDATE products
SET tags = array_remove(tags, 'old_tag')
WHERE id = 1;

-- 数组展开为多行
SELECT name, unnest(tags) as tag FROM products;

-- 数组连接
SELECT array_cat(ARRAY[1, 2, 3], ARRAY[4, 5, 6]);
-- 结果: {1,2,3,4,5,6}

-- 数组包含检查
SELECT 1 WHERE ARRAY[1, 2, 3] @> ARRAY[2, 3];  -- true
SELECT 1 WHERE ARRAY[1, 2, 3] && ARRAY[3, 4, 5]; -- true (有重叠)
```

### JSON 和 JSONB 类型

PostgreSQL 提供了两种 JSON 数据类型：
- `JSON`: 存储文本格式的 JSON，保留空格和顺序
- `JSONB`: 存储二进制格式的 JSON，支持索引，查询更快

#### JSON/JSONB 基础
```sql
CREATE TABLE documents (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255),
    metadata JSON,   -- 文本格式 JSON
    config JSONB     -- 二进制格式 JSON
);

-- 插入 JSON 数据
INSERT INTO documents (title, metadata, config) VALUES
('User Guide',
 '{"version": "1.0", "author": "John Doe", "tags": ["guide", "user"]}',
 '{"theme": "dark", "notifications": true, "settings": {"auto_save": true}}');
```

#### JSONB 查询操作
```sql
-- 获取 JSON 字段的值
SELECT title, config->>'theme' AS theme FROM documents;

-- 使用 -> 获取 JSON 对象（返回 JSONB）
SELECT title, config->'settings' AS settings FROM documents;

-- 使用 ->> 获取 JSON 对象的文本值
SELECT title, config->'settings'->>'auto_save' AS auto_save FROM documents;

-- 查询 JSON 数组
SELECT title, metadata->'tags' as tags FROM documents;

-- 检查 JSON 字段是否存在
SELECT title FROM documents WHERE config ? 'theme';

-- 检查 JSON 字段是否包含所有指定键
SELECT title FROM documents WHERE config ?& array['theme', 'notifications'];

-- 检查 JSON 字段是否包含任一指定键
SELECT title FROM documents WHERE config ?| array['theme', 'invalid_key'];
```

#### JSONB 修改操作
```sql
-- 更新 JSON 字段
UPDATE documents
SET config = jsonb_set(config, '{theme}', '"light"')
WHERE id = 1;

-- 添加新的 JSON 字段
UPDATE documents
SET config = config || '{"language": "en"}'
WHERE id = 1;

-- 删除 JSON 字段
UPDATE documents
SET config = config - 'notifications'
WHERE id = 1;

-- 增加 JSON 数组元素
UPDATE documents
SET metadata = jsonb_set(metadata, '{tags}',
    (metadata->'tags') || '["advanced"]')
WHERE id = 1;
```

#### JSONB 索引
```sql
-- 为 JSONB 字段创建 GIN 索引
CREATE INDEX idx_documents_config_gin ON documents USING GIN (config);

-- 创建表达式索引
CREATE INDEX idx_documents_config_theme ON documents USING BTREE ((config->>'theme'));

-- 使用 JSONB 操作符查询
SELECT * FROM documents WHERE config @> '{"theme": "dark"}';
```

### 范围类型 (RANGE)

范围类型用于存储连续范围的值，如时间范围、数字范围等。

#### 内置范围类型
```sql
-- int4range: 整数范围
-- int8range: 大整数范围
-- numrange: 数值范围
-- tsrange: 无时区时间戳范围
-- tstzrange: 带时区时间戳范围
-- daterange: 日期范围

CREATE TABLE schedules (
    id SERIAL PRIMARY KEY,
    event_name VARCHAR(100),
    time_range TSRANGE,           -- 时间戳范围
    date_range DATERANGE,         -- 日期范围
    price_range NUMRANGE          -- 数值范围
);

-- 插入范围数据
INSERT INTO schedules VALUES
(1, 'Conference',
 '[2023-12-01 09:00:00, 2023-12-01 18:00:00]',  -- 包含两端
 '[2023-12-01, 2023-12-03]',                     -- 包含两端
 '[100.00, 500.00]');

-- 使用不同的范围符号
INSERT INTO schedules VALUES
(2, 'Meeting',
 '(2023-12-02 14:00:00, 2023-12-02 16:00:00)',  -- 不包含两端
 '[2023-12-05, 2023-12-07)',                     -- 包含开始，不包含结束
 '(0.00, 1000.00]');                             -- 不包含开始，包含结束
```

#### 范围操作
```sql
-- 查询包含特定时间的事件
SELECT * FROM schedules WHERE time_range @> '2023-12-01 10:00:00'::TIMESTAMP;

-- 查询范围重叠的事件
SELECT * FROM schedules
WHERE time_range && '[2023-12-01 12:00:00, 2023-12-01 15:00:00]'::TSRANGE;

-- 查询完全包含在指定范围内的事件
SELECT * FROM schedules
WHERE time_range <@ '[2023-12-01 00:00:00, 2023-12-02 00:00:00]'::TSRANGE;

-- 范围的起始和结束值
SELECT
    event_name,
    lower(time_range) AS start_time,
    upper(time_range) AS end_time
FROM schedules;

-- 检查范围是否为空
SELECT event_name, isempty(time_range) FROM schedules;
```

#### 自定义范围类型
```sql
-- 创建自定义范围类型
CREATE TYPE floatrange AS RANGE (
    subtype = float8,
    subtype_diff = float8mi
);

CREATE TABLE temperature_readings (
    id SERIAL PRIMARY KEY,
    location VARCHAR(100),
    temp_range FLOATRANGE
);
```

### 网络地址类型

```sql
CREATE TABLE network_devices (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    -- INET: IPv4 和 IPv6 地址
    ip_address INET,
    -- CIDR: 网络地址
    network CIDR,
    -- MACADDR: MAC 地址
    mac_address MACADDR
);

-- 插入数据
INSERT INTO network_devices VALUES
(1, 'Server1', '192.168.1.10', '192.168.1.0/24', '08:00:2b:01:02:03'),
(2, 'Server2', '10.0.0.5', '10.0.0.0/8', '08:00:2b:01:02:04');

-- 网络地址操作
SELECT * FROM network_devices WHERE ip_address <<= '192.168.1.0/24';
-- 查询 IP 地址在指定网络内的设备

-- 检查网络包含关系
SELECT network, '192.168.1.50'::INET << network AS contains_ip
FROM (SELECT '192.168.1.0/24'::CIDR AS network) t;
```

### 几何类型

```sql
CREATE TABLE geographic_data (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    -- POINT: 点
    location POINT,
    -- LINE: 线
    path LINE,
    -- BOX: 矩形
    bounds BOX,
    -- CIRCLE: 圆
    area CIRCLE,
    -- POLYGON: 多边形
    shape POLYGON
);

-- 插入几何数据
INSERT INTO geographic_data VALUES
(1, 'City Center', '(10.5, 20.3)', NULL, NULL, NULL, NULL),
(2, 'Park', '(15.0, 25.0)', NULL, '((5,5), (25,5), (25,25), (5,25))',
 '<(15, 15), 10>', '((10,10), (20,10), (20,20), (10,20))');

-- 几何操作
SELECT name, location FROM geographic_data
WHERE box(location, location) && '((0,0), (30,30))'::BOX;

-- 计算两点距离
SELECT p1.name, p2.name, p1.location <-> p2.location AS distance
FROM geographic_data p1, geographic_data p2
WHERE p1.id = 1 AND p2.id = 2;
```

### 枚举类型 (ENUM)

```sql
-- 创建枚举类型
CREATE TYPE order_status AS ENUM ('pending', 'processing', 'shipped', 'delivered', 'cancelled');
CREATE TYPE user_role AS ENUM ('admin', 'editor', 'viewer');

CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    user_id INTEGER,
    status order_status DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    role user_role DEFAULT 'viewer'
);

-- 使用枚举类型
INSERT INTO orders (user_id, status) VALUES (1, 'processing');
INSERT INTO users (name, role) VALUES ('John Doe', 'admin');

-- 枚举类型操作
SELECT * FROM orders WHERE status = 'shipped';
UPDATE orders SET status = 'delivered' WHERE id = 1;

-- 查看枚举类型的所有值
SELECT unnest(enum_range(NULL::order_status));
```

### 全文搜索类型

```sql
CREATE TABLE articles (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255),
    content TEXT,
    -- TSVECTOR: 用于全文搜索的文档
    search_vector TSVECTOR
);

-- 创建搜索向量
UPDATE articles
SET search_vector = to_tsvector('english', title || ' ' || content);

-- 创建全文搜索索引
CREATE INDEX idx_articles_search ON articles USING GIN (search_vector);

-- 全文搜索
SELECT title, content FROM articles
WHERE search_vector @@ to_tsquery('english', 'database & performance');

-- 创建触发器自动更新搜索向量
CREATE OR REPLACE FUNCTION articles_search_vector_update() RETURNS TRIGGER AS $$
BEGIN
    NEW.search_vector := to_tsvector('english', NEW.title || ' ' || NEW.content);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER articles_search_vector_update
    BEFORE INSERT OR UPDATE ON articles
    FOR EACH ROW EXECUTE FUNCTION articles_search_vector_update();
```

### UUID 类型

```sql
-- 启用 UUID 扩展
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE unique_records (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 插入数据（UUID 自动生成）
INSERT INTO unique_records (name) VALUES ('Record 1');

-- 手动生成 UUID
INSERT INTO unique_records (id, name)
VALUES (uuid_generate_v1(), 'Record 2');
```

### 复合类型 (Composite Types)

```sql
-- 创建复合类型
CREATE TYPE address AS (
    street VARCHAR(100),
    city VARCHAR(50),
    state VARCHAR(50),
    zip_code VARCHAR(10)
);

CREATE TYPE contact_info AS (
    email VARCHAR(255),
    phone VARCHAR(20),
    address address
);

CREATE TABLE employees (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    contact contact_info
);

-- 插入复合类型数据
INSERT INTO employees (name, contact) VALUES
('John Doe', ROW('john@example.com', '555-1234',
                ROW('123 Main St', 'Anytown', 'CA', '12345')));

-- 查询复合类型字段
SELECT name, contact.email FROM employees;

-- 查询嵌套复合类型
SELECT name, contact.address.city FROM employees;

-- 更新复合类型字段
UPDATE employees
SET contact.address.city = 'New City'
WHERE id = 1;
```

## 数据类型转换

```sql
-- 显式类型转换
SELECT '123'::INTEGER;
SELECT 123.45::NUMERIC(10, 2);
SELECT CURRENT_TIMESTAMP::DATE;

-- CAST 函数
SELECT CAST('2023-12-25' AS DATE);
SELECT CAST(123.45 AS VARCHAR(10));

-- 自动类型转换
SELECT 1 + '2';  -- 自动将字符串转换为整数
```

这些丰富的数据类型使 PostgreSQL 能够处理各种复杂的数据存储需求，从简单的数值到复杂的地理空间数据，从基本的关系数据到灵活的文档数据。