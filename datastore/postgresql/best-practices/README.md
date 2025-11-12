# PostgreSQL 最佳实践

本章节涵盖了使用 PostgreSQL 的最佳实践，包括数据库设计、性能优化、安全配置和维护策略。

## 数据库设计最佳实践

### 1. 命名规范

```sql
-- 表命名：使用小写字母和下划线
CREATE TABLE user_profiles (
    -- 列命名：使用小写字母和下划线
    user_id SERIAL PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email_address VARCHAR(255) UNIQUE NOT NULL,
    -- 时间戳字段统一命名格式
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 索引命名：表名_列名_类型
CREATE INDEX idx_user_profiles_email ON user_profiles (email_address);
CREATE UNIQUE INDEX idx_user_profiles_user_id ON user_profiles (user_id);

-- 外键约束命名：fk_表名_列名
ALTER TABLE orders
ADD CONSTRAINT fk_orders_user_id
FOREIGN KEY (user_id) REFERENCES user_profiles (user_id);
```

### 2. 数据类型选择

```sql
-- 选择合适的数据类型
CREATE TABLE products (
    -- 使用 SERIAL 而不是 INTEGER，自动管理序列
    id SERIAL PRIMARY KEY,

    -- 使用精确的数值类型存储货币
    price NUMERIC(10,2) NOT NULL,
    discount_rate NUMERIC(5,4),

    -- 使用合适长度的 VARCHAR
    product_code VARCHAR(20) NOT NULL,
    description TEXT,  -- 长文本使用 TEXT

    -- 使用正确的布尔类型
    is_active BOOLEAN DEFAULT true,

    -- 使用数组类型存储相关数据
    tags TEXT[],
    specifications JSONB,

    -- 使用时间戳类型
    launch_date DATE,
    last_modified TIMESTAMPTZ
);

-- 使用枚举类型替代字符串常量
CREATE TYPE order_status AS ENUM ('pending', 'processing', 'shipped', 'delivered', 'cancelled');

CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    status order_status DEFAULT 'pending',
    -- 其他字段
);
```

### 3. 表结构设计

```sql
-- 规范化设计
CREATE TABLE customers (
    id SERIAL PRIMARY KEY,
    customer_type VARCHAR(20) CHECK (customer_type IN ('individual', 'business')),
    -- 客户基本信息
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    company_name VARCHAR(100),
    -- 联系信息（单独表，遵循第三范式）
);

CREATE TABLE customer_contacts (
    id SERIAL PRIMARY KEY,
    customer_id INTEGER NOT NULL REFERENCES customers(id),
    contact_type VARCHAR(20) NOT NULL CHECK (contact_type IN ('email', 'phone', 'address')),
    contact_value VARCHAR(255) NOT NULL,
    is_primary BOOLEAN DEFAULT false
);

-- 使用检查约束确保数据完整性
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    price NUMERIC(10,2) NOT NULL CHECK (price >= 0),
    stock_quantity INTEGER NOT NULL DEFAULT 0 CHECK (stock_quantity >= 0),
    weight NUMERIC(8,3) CHECK (weight > 0),

    -- 使用 CHECK 约束确保逻辑一致性
    CONSTRAINT check_price_stock CHECK (
        (stock_quantity > 0) OR (price = 0)  -- 无库存时可以为零价格
    )
);
```

## 索引策略最佳实践

### 1. 基本索引规则

```sql
-- 为 WHERE 子句中的列创建索引
CREATE INDEX idx_orders_customer_id ON orders (customer_id);
CREATE INDEX idx_orders_status ON orders (status);

-- 为 JOIN 条件创建索引
CREATE INDEX idx_order_items_order_id ON order_items (order_id);
CREATE INDEX idx_order_items_product_id ON order_items (product_id);

-- 为 ORDER BY 创建复合索引
CREATE INDEX idx_orders_created_desc ON orders (created_at DESC);

-- 复合索引顺序很重要
-- 经常查询特定客户的订单状态
CREATE INDEX idx_orders_customer_status ON orders (customer_id, status);

-- 为经常一起查询的列创建复合索引
CREATE INDEX idx_orders_customer_date ON orders (customer_id, created_at DESC);
```

### 2. 部分索引

```sql
-- 只为活跃用户创建索引
CREATE INDEX idx_active_users_email ON users (email) WHERE active = true;

-- 只为未完成的订单创建索引
CREATE INDEX idx_pending_orders ON orders (created_at)
WHERE status IN ('pending', 'processing');

-- 只为大额交易创建索引
CREATE INDEX idx_large_transactions ON transactions (amount, created_at)
WHERE amount > 10000;
```

### 3. 表达式索引

```sql
-- 为不区分大小写的搜索创建索引
CREATE INDEX idx_users_email_lower ON users (LOWER(email));

-- 为计算字段创建索引
CREATE INDEX idx_products_discounted_price ON products ((price * (1 - discount)));

-- 为日期部分创建索引
CREATE INDEX idx_orders_created_month ON orders (EXTRACT(MONTH FROM created_at));

-- 为条件创建索引
CREATE INDEX idx_products_available ON products ((stock_quantity > 0));
```

## 查询优化最佳实践

### 1. 查询编写技巧

```sql
-- 使用参数化查询
EXPLAIN ANALYZE
SELECT * FROM orders
WHERE customer_id = $1 AND status = $2;

-- 避免 SELECT *
SELECT id, customer_id, total_amount, created_at
FROM orders
WHERE customer_id = 123;

-- 使用 EXISTS 代替 IN 进行子查询
SELECT c.id, c.name
FROM customers c
WHERE EXISTS (
    SELECT 1 FROM orders o
    WHERE o.customer_id = c.id
    AND o.status = 'pending'
);

-- 使用适当的连接类型
SELECT c.name, COUNT(o.id) as order_count
FROM customers c
LEFT JOIN orders o ON c.id = o.customer_id
GROUP BY c.id, c.name;

-- 使用 CTE 提高可读性
WITH customer_orders AS (
    SELECT
        customer_id,
        COUNT(*) as total_orders,
        SUM(total_amount) as total_spent
    FROM orders
    WHERE created_at >= CURRENT_DATE - INTERVAL '1 year'
    GROUP BY customer_id
)
SELECT c.name, co.total_orders, co.total_spent
FROM customers c
JOIN customer_orders co ON c.id = co.customer_id
WHERE co.total_spent > 1000;
```

### 2. 使用窗口函数优化查询

```sql
-- 使用窗口函数避免自连接
SELECT
    id,
    customer_id,
    total_amount,
    ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY total_amount DESC) as rank_in_customer,
    LAG(total_amount) OVER (PARTITION BY customer_id ORDER BY created_at) as prev_order_amount
FROM orders;

-- 计算移动平均值
SELECT
    date_trunc('day', created_at) as order_date,
    SUM(total_amount) as daily_total,
    AVG(SUM(total_amount)) OVER (
        ORDER BY date_trunc('day', created_at)
        ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
    ) as weekly_avg
FROM orders
GROUP BY date_trunc('day', created_at)
ORDER BY order_date;
```

### 3. 批量操作优化

```sql
-- 批量插入使用 COPY
COPY large_table (column1, column2, column3)
FROM '/path/to/data.csv'
WITH (FORMAT csv, HEADER);

-- 批量更新使用 CTE
WITH updates AS (
    SELECT unnest(ARRAY[1, 2, 3]) as id,
           unnest(ARRAY['value1', 'value2', 'value3']) as value
)
UPDATE target_table t
SET value = u.value
FROM updates u
WHERE t.id = u.id;

-- 批量删除使用分区表
DELETE FROM orders_partitioned
WHERE created_at < '2022-01-01';
```

## 事务管理最佳实践

### 1. 事务设计原则

```sql
-- 保持事务简短
BEGIN;
UPDATE accounts SET balance = balance - 100 WHERE id = 1;
UPDATE accounts SET balance = balance + 100 WHERE id = 2;
COMMIT;

-- 使用保存点进行复杂事务
BEGIN;
INSERT INTO orders (customer_id, total_amount) VALUES (1, 100.00);
SAVEPOINT order_inserted;

UPDATE inventory SET quantity = quantity - 1 WHERE product_id = 1;
-- 如果更新失败，可以回滚到保存点
ROLLBACK TO SAVEPOINT order_inserted;

-- 尝试其他操作
INSERT INTO backorders (product_id, quantity) VALUES (1, 1);
COMMIT;

-- 设置适当的事务隔离级别
BEGIN TRANSACTION ISOLATION LEVEL READ COMMITTED;
SELECT balance FROM accounts WHERE id = 1;
COMMIT;
```

### 2. 并发控制

```sql
-- 使用 SELECT FOR UPDATE 避免竞态条件
BEGIN;
SELECT * FROM products WHERE id = 1 FOR UPDATE;
-- 检查库存并更新
UPDATE products SET stock_quantity = stock_quantity - 1 WHERE id = 1;
COMMIT;

-- 使用 advisory locks
SELECT pg_advisory_xact_lock(12345);
-- 执行需要锁定的操作
SELECT pg_advisory_xact_unlock(12345);

-- 使用乐观并发控制
UPDATE products
SET stock_quantity = stock_quantity - 1,
    version = version + 1
WHERE id = 1 AND version = current_version;
```

## 安全最佳实践

### 1. 用户权限管理

```sql
-- 创建应用专用用户
CREATE USER app_user WITH PASSWORD 'secure_password';

-- 最小权限原则
GRANT CONNECT ON DATABASE myapp TO app_user;
GRANT USAGE ON SCHEMA public TO app_user;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO app_user;
GRANT USAGE ON ALL SEQUENCES IN SCHEMA public TO app_user;

-- 创建只读用户
CREATE USER readonly_user WITH PASSWORD 'readonly_password';
GRANT CONNECT ON DATABASE myapp TO readonly_user;
GRANT USAGE ON SCHEMA public TO readonly_user;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO readonly_user;

-- 设置默认权限
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO app_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT USAGE ON SEQUENCES TO app_user;
```

### 2. 行级安全策略

```sql
-- 启用行级安全
ALTER TABLE orders ENABLE ROW LEVEL SECURITY;

-- 创建安全策略
CREATE POLICY orders_customer_policy ON orders
FOR ALL
USING (customer_id = current_setting('app.current_customer_id')::INTEGER);

-- 为管理员创建策略
CREATE POLICY orders_admin_policy ON orders
FOR ALL
USING (pg_has_role(current_user, 'admin', 'MEMBER'));

-- 在应用中设置上下文
SET app.current_customer_id = '123';
```

### 3. 数据加密

```sql
-- 安装 pgcrypto 扩展
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- 密码哈希存储
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    salt VARCHAR(64) NOT NULL
);

-- 插入用户时使用加密
INSERT INTO users (username, password_hash, salt)
VALUES ('user1', crypt('password123', gen_salt('bf', 12)), 'generated_salt');

-- 验证密码
SELECT * FROM users
WHERE username = 'user1'
AND password_hash = crypt('entered_password', password_hash);

-- 加密敏感数据
CREATE TABLE sensitive_data (
    id SERIAL PRIMARY KEY,
    data_content BYTEA,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 使用对称加密
INSERT INTO sensitive_data (data_content)
SELECT pgp_sym_encrypt('sensitive information', 'encryption_key');
```

## 性能调优最佳实践

### 1. 服务器配置

```sql
-- 内存配置（postgresql.conf）
shared_buffers = 256MB                    -- 系统内存的 25%
effective_cache_size = 1GB               -- 系统内存的 75%
work_mem = 4MB                           -- 每个查询操作的内存
maintenance_work_mem = 64MB              -- 维护操作内存

-- 连接配置
max_connections = 100                    -- 最大连接数
shared_preload_libraries = 'pg_stat_statements'  -- 预加载库

-- WAL 配置
wal_level = replica                     -- 支持复制
archive_mode = on                       -- 启用归档
archive_command = 'cp %p /backup/wal/%f'
checkpoint_completion_target = 0.9       -- 检查点完成目标

-- 查询规划器配置
random_page_cost = 1.1                  -- SSD 优化
effective_io_concurrency = 200          -- SSD 并发
```

### 2. 定期维护

```sql
-- 自动清理配置
ALTER SYSTEM SET autovacuum = on;
ALTER SYSTEM SET autovacuum_analyze_scale_factor = 0.1;
ALTER SYSTEM SET autovacuum_vacuum_scale_factor = 0.2;

-- 表级别的自动清理配置
ALTER TABLE large_table SET (
    autovacuum_vacuum_scale_factor = 0.05,
    autovacuum_analyze_scale_factor = 0.02
);

-- 手动清理和优化
VACUUM ANALYZE large_table;
REINDEX TABLE large_table;

-- 检查数据库状态
SELECT
    schemaname,
    tablename,
    n_tup_ins as inserts,
    n_tup_upd as updates,
    n_tup_del as deletes,
    n_live_tup as live_tuples,
    n_dead_tup as dead_tuples,
    last_vacuum,
    last_autovacuum,
    last_analyze,
    last_autoanalyze
FROM pg_stat_user_tables;
```

### 3. 监控和分析

```sql
-- 启用查询统计
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;

-- 查找慢查询
SELECT
    query,
    calls,
    total_exec_time,
    mean_exec_time,
    rows,
    100.0 * shared_blks_hit /
        nullif(shared_blks_hit + shared_blks_read, 0) AS hit_percent
FROM pg_stat_statements
ORDER BY total_exec_time DESC
LIMIT 10;

-- 监控锁等待
SELECT
    pid,
    state,
    query,
    wait_event_type,
    wait_event
FROM pg_stat_activity
WHERE state = 'active'
AND wait_event IS NOT NULL;

-- 查看锁信息
SELECT
    locktype,
    database,
    relation,
    page,
    tuple,
    virtualxid,
    transactionid,
    classid,
    objid,
    objsubid,
    virtualtransaction,
    pid,
    mode,
    granted,
    fastpath
FROM pg_locks;
```

## 备份和恢复最佳实践

### 1. 备份策略

```bash
#!/bin/bash
# 完整备份脚本
BACKUP_DIR="/backup"
DATE=$(date +%Y%m%d_%H%M%S)
DB_NAME="myapp"

# 创建逻辑备份
pg_dump -Fc -f $BACKUP_DIR/${DB_NAME}_${DATE}.dump $DB_NAME

# 创建物理备份
pg_basebackup -D $BACKUP_DIR/base_${DATE} -U postgres -v -P

# 备份 WAL 归档
tar -czf $BACKUP_DIR/wal_${DATE}.tar.gz /backup/wal_archive/

# 清理旧备份（保留 7 天）
find $BACKUP_DIR -name "*.dump" -mtime +7 -delete
find $BACKUP_DIR -name "base_*" -mtime +7 -exec rm -rf {} \;
```

### 2. 恢复测试

```bash
#!/bin/bash
# 恢复测试脚本
BACKUP_FILE=$1
TEST_DB="test_restore_$(date +%s)"

# 创建测试数据库
createdb $TEST_DB

# 尝试恢复
if pg_restore -d $TEST_DB $BACKUP_FILE; then
    echo "备份恢复测试成功"

    # 验证数据完整性
    psql -d $TEST_DB -c "SELECT count(*) FROM users;"

    # 清理测试数据库
    dropdb $TEST_DB
else
    echo "备份恢复测试失败"
    dropdb $TEST_DB
    exit 1
fi
```

## 高可用性配置

### 1. 流复制设置

```sql
-- 主库配置
-- postgresql.conf
wal_level = replica
max_wal_senders = 3
wal_keep_segments = 64
archive_mode = on
archive_command = 'cp %p /backup/wal_archive/%f'

-- pg_hba.conf
host replication replicator 192.168.1.100/32 md5

-- 创建复制用户
CREATE USER replicator WITH REPLICATION ENCRYPTED PASSWORD 'repl_password';
```

### 2. 故障转移

```bash
#!/bin/bash
# 故障转移脚本
MASTER_IP="192.168.1.10"
STANDBY_IP="192.168.1.11"

# 检查主库状态
if ! pg_isready -h $MASTER_IP -p 5432; then
    echo "主库不可用，执行故障转移"

    # 提升备库
    pg_ctl promote -D /var/lib/postgresql/16/main

    # 更新应用配置指向新主库
    # ...

    echo "故障转移完成"
fi
```

## 应用集成最佳实践

### 1. 连接池配置

```ini
# PgBouncer 配置
[databases]
myapp = host=localhost port=5432 dbname=myapp

[pgbouncer]
listen_port = 6432
listen_addr = 127.0.0.1
auth_type = md5
auth_file = /etc/pgbouncer/userlist.txt
logfile = /var/log/pgbouncer/pgbouncer.log
admin_users = postgres
stats_users = stats, postgres

# 连接池设置
pool_mode = transaction
max_client_conn = 200
default_pool_size = 25
min_pool_size = 5
reserve_pool_size = 5
reserve_pool_timeout = 5
max_db_connections = 100
max_user_connections = 100

# 超时设置
server_reset_query = DISCARD ALL
server_check_delay = 30
server_check_query = select 1
server_lifetime = 3600
server_idle_timeout = 600
```

### 2. 应用配置

```python
# Python 应用连接配置示例
import psycopg2
from psycopg2 import pool

# 连接池配置
connection_pool = psycopg2.pool.SimpleConnectionPool(
    minconn=1,
    maxconn=20,
    user="app_user",
    password="secure_password",
    host="localhost",
    port="6432",  # PgBouncer 端口
    database="myapp"
)

# 使用连接池
def get_connection():
    return connection_pool.getconn()

def release_connection(conn):
    connection_pool.putconn(conn)

# 执行查询的函数
def execute_query(query, params=None):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(query, params)
            if query.strip().upper().startswith('SELECT'):
                return cur.fetchall()
            else:
                conn.commit()
                return cur.rowcount
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        release_connection(conn)
```

这些最佳实践涵盖了 PostgreSQL 数据库管理的各个方面，通过遵循这些指导原则，可以确保数据库系统的高性能、高可用性和安全性。