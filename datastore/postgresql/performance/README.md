# PostgreSQL 性能优化

本章节涵盖 PostgreSQL 的性能优化技术，包括慢查询分析、查询计划分析和系统调优。

## 慢查询分析

### 1. 启用查询日志

```sql
-- postgresql.conf 配置
-- 记录慢查询（毫秒）
log_min_duration_statement = 1000  -- 记录超过1秒的查询
log_statement = 'all'              -- 记录所有语句
log_duration = on                  -- 记录执行时间

-- 详细的日志配置
log_checkpoints = on
log_connections = on
log_disconnections = on
log_lock_waits = on
log_temp_files = 0                 -- 记录临时文件
log_autovacuum_min_duration = 0    -- 记录自动清理

-- 慢查询日志示例
-- LOG:  duration: 1234.567 ms  statement: SELECT * FROM large_table WHERE complex_condition = 'value'
```

### 2. 使用 pg_stat_statements

```sql
-- 安装扩展
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;

-- 配置参数（postgresql.conf）
shared_preload_libraries = 'pg_stat_statements'
pg_stat_statements.max = 10000
pg_stat_statements.track = all
pg_stat_statements.track_utility = off
pg_stat_statements.save = on

-- 查找最耗时的查询
SELECT
    query,
    calls,
    total_exec_time,
    mean_exec_time,
    stddev_exec_time,
    rows,
    100.0 * shared_blks_hit /
        nullif(shared_blks_hit + shared_blks_read, 0) AS hit_percent
FROM pg_stat_statements
ORDER BY total_exec_time DESC
LIMIT 10;

-- 查找执行次数最多的查询
SELECT
    query,
    calls,
    total_exec_time,
    mean_exec_time
FROM pg_stat_statements
ORDER BY calls DESC
LIMIT 10;

-- 查找 I/O 密集型查询
SELECT
    query,
    calls,
    shared_blks_read,
    shared_blks_hit,
    local_blks_read,
    local_blks_hit,
    temp_blks_read,
    temp_blks_written
FROM pg_stat_statements
WHERE shared_blks_read > 0 OR temp_blks_read > 0
ORDER BY (shared_blks_read + temp_blks_read) DESC
LIMIT 10;

-- 按用户查看查询统计
SELECT
    r.rolname,
    s.query,
    s.calls,
    s.total_exec_time
FROM pg_stat_statements s
JOIN pg_roles r ON s.userid = r.oid
ORDER BY s.total_exec_time DESC;
```

### 3. auto_explain 插件

```sql
-- 安装和配置
CREATE EXTENSION IF NOT EXISTS auto_explain;

-- postgresql.conf 配置
shared_preload_libraries = 'auto_explain'
auto_explain.log_min_duration = 1000        -- 记录慢查询的执行计划
auto_explain.log_analyze = on              -- 包含实际执行统计
auto_explain.log_verbose = on              -- 详细输出
auto_explain.log_format = json             -- JSON 格式
auto_explain.log_timing = on               -- 包含时间信息
auto_explain.log_triggers = on             -- 包含触发器信息
auto_explain.log_buffers = on              -- 包含缓冲区信息

-- 在会话中临时启用
LOAD 'auto_explain';
SET auto_explain.log_min_duration = 500;
SET auto_explain.log_analyze = on;

-- 示例日志输出
-- LOG:  duration: 234.567 ms  plan:
-- {
--   "Plan": {
--     "Node Type": "Hash Join",
--     "Join Type": "Inner",
--     "Startup Cost": 1.12,
--     "Total Cost": 45.89,
--     "Plan Rows": 1000,
--     "Plan Width": 20,
--     "Actual Startup Time": 0.045,
--     "Actual Total Time": 234.567,
--     "Actual Rows": 1000,
--     "Actual Loops": 1
--   }
-- }
```

## 查询计划分析

### 1. EXPLAIN 基础

```sql
-- 基本执行计划
EXPLAIN SELECT * FROM orders WHERE customer_id = 123;

-- 执行并分析
EXPLAIN ANALYZE SELECT * FROM orders WHERE customer_id = 123;

-- 包含缓冲区使用情况
EXPLAIN (ANALYZE, BUFFERS) SELECT * FROM orders WHERE customer_id = 123;

-- 包含 WAL 信息
EXPLAIN (ANALYZE, BUFFERS, WAL) UPDATE orders SET status = 'shipped' WHERE id = 1;

-- 格式化输出
EXPLAIN (ANALYZE, FORMAT JSON) SELECT * FROM orders WHERE customer_id = 123;
EXPLAIN (ANALYZE, FORMAT XML) SELECT * FROM orders WHERE customer_id = 123;
```

### 2. 读取执行计划

```sql
-- 示例执行计划解释
EXPLAIN ANALYZE
SELECT o.id, c.name, o.total_amount
FROM orders o
JOIN customers c ON o.customer_id = c.id
WHERE o.created_at >= CURRENT_DATE - INTERVAL '30 days';

-- 输出解释：
-- Hash Join  (cost=445.00..1256.50 rows=10000 width=32) (actual time=15.234..89.456 rows=10000 loops=1)
--   Hash Cond: (o.customer_id = c.id)
--   ->  Seq Scan on orders o  (cost=0.00..800.00 rows=10000 width=16) (actual time=0.123..45.678 rows=10000 loops=1)
--         Filter: (created_at >= ('2023-11-25'::date - '30 days'::interval))
--   ->  Hash  (cost=25.00..25.00 rows=1000 width=16) (actual time=0.456..0.456 rows=1000 loops=1)
--         Buckets: 1024  Batches: 1  Memory Usage: 64kB
--         ->  Seq Scan on customers c  (cost=0.00..25.00 rows=1000 width=16) (actual time=0.012..0.234 rows=1000 loops=1)
-- Planning Time: 0.567 ms
-- Execution Time: 90.123 ms
```

### 3. 常见执行计划节点

```sql
-- 顺序扫描
EXPLAIN ANALYZE SELECT * FROM large_table WHERE condition = 'value';

-- 索引扫描
EXPLAIN ANALYZE SELECT * FROM indexed_table WHERE indexed_column = 'value';

-- 位图索引扫描
EXPLAIN ANALYZE SELECT * FROM table WHERE col1 = 'a' AND col2 = 'b';

-- 位图堆扫描
EXPLAIN ANALYZE SELECT * FROM table WHERE non_indexed_col = 'value';

-- 嵌套循环连接
EXPLAIN ANALYZE SELECT * FROM table1 JOIN table2 ON table1.id = table2.t1_id;

-- 哈希连接
EXPLAIN ANALYZE SELECT * FROM large_table1 JOIN large_table2 ON table1.key = table2.key;

-- 合并连接
EXPLAIN ANALYZE SELECT * FROM sorted_table1 JOIN sorted_table2 ON table1.key = table2.key;

-- 聚合
EXPLAIN ANALYZE SELECT category, COUNT(*) FROM products GROUP BY category;

-- 排序
EXPLAIN ANALYZE SELECT * FROM table ORDER BY column;
```

## 性能调优工具

### 1. pgbench - 基准测试

```bash
# 初始化测试数据库
pgbench -i -s 50 mydb  # 创建50倍标准大小的测试数据

# 运行基准测试
pgbench -c 10 -j 2 -t 1000 mydb  # 10个客户端，2个线程，每个客户端1000个事务

# 运行指定时间的测试
pgbench -c 5 -j 2 -T 300 mydb     # 5个客户端，运行300秒

# 自定义脚本测试
pgbench -c 5 -j 2 -T 300 -f my_script.sql mydb

# 输出结果示例
-- transaction type: TPC-B (sort of)
-- scaling factor: 50
-- query mode: simple
-- number of clients: 10
-- number of threads: 2
-- duration: 300 s
-- number of transactions actually processed: 150000
-- latency average = 20.000 ms
-- tps = 500.000000 (including connections establishing)
-- tps = 501.000000 (excluding connections establishing)
```

### 2. 系统监控查询

```sql
-- 监控活跃连接
SELECT
    pid,
    datname,
    usename,
    application_name,
    state,
    waiting,
    query_start,
    state_change,
    query
FROM pg_stat_activity
WHERE state = 'active'
ORDER BY query_start;

-- 监控锁等待
SELECT
    blocked_locks.pid AS blocked_pid,
    blocked_activity.usename AS blocked_user,
    blocking_locks.pid AS blocking_pid,
    blocking_activity.usename AS blocking_user,
    blocked_activity.query AS blocked_statement,
    blocking_activity.query AS current_statement_in_blocking_process
FROM pg_catalog.pg_locks blocked_locks
JOIN pg_catalog.pg_stat_activity blocked_activity ON blocked_activity.pid = blocked_locks.pid
JOIN pg_catalog.pg_locks blocking_locks ON blocking_locks.locktype = blocked_locks.locktype
JOIN pg_catalog.pg_stat_activity blocking_activity ON blocking_activity.pid = blocking_locks.pid
WHERE NOT blocked_locks.granted;

-- 监控表膨胀
SELECT
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size,
    pg_size_pretty(pg_relation_size(schemaname||'.'||tablename)) AS table_size,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename) - pg_relation_size(schemaname||'.'||tablename)) AS index_size,
    (SELECT count(*) FROM pg_stats WHERE schemaname = s.schemaname AND tablename = s.tablename) AS column_count
FROM pg_tables s
WHERE schemaname NOT IN ('information_schema', 'pg_catalog')
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

### 3. 索引使用情况分析

```sql
-- 查看索引使用统计
SELECT
    schemaname,
    tablename,
    indexname,
    idx_scan,
    idx_tup_read,
    idx_tup_fetch,
    pg_size_pretty(pg_relation_size(indexrelid::regclass)) AS index_size
FROM pg_stat_user_indexes
ORDER BY idx_scan DESC;

-- 查找未使用的索引
SELECT
    schemaname,
    tablename,
    indexname,
    pg_size_pretty(pg_relation_size(indexrelid::regclass)) AS index_size
FROM pg_stat_user_indexes
WHERE idx_scan = 0
ORDER BY pg_relation_size(indexrelid::regclass) DESC;

-- 查看表的统计信息
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

## 查询优化技巧

### 1. 索引优化

```sql
-- 检查缺失的索引
SELECT
    schemaname,
    tablename,
    attname,
    n_distinct,
    correlation
FROM pg_stats
WHERE schemaname NOT IN ('information_schema', 'pg_catalog')
ORDER BY n_distinct DESC;

-- 创建复合索引优化查询
CREATE INDEX idx_orders_customer_date ON orders (customer_id, created_at DESC);

-- 使用部分索引减少索引大小
CREATE INDEX idx_active_users ON users (email) WHERE active = true;

-- 创建表达式索引支持函数查询
CREATE INDEX idx_users_email_lower ON users (LOWER(email));
```

### 2. 查询重写

```sql
-- 使用 EXISTS 代替 IN
-- 不推荐
SELECT * FROM customers c
WHERE c.id IN (SELECT customer_id FROM orders WHERE total > 1000);

-- 推荐
SELECT * FROM customers c
WHERE EXISTS (SELECT 1 FROM orders o WHERE o.customer_id = c.id AND o.total > 1000);

-- 使用 UNION ALL 代替 UNION（如果不需要去重）
-- 不推荐
SELECT name FROM employees WHERE department = 'IT'
UNION
SELECT name FROM contractors WHERE department = 'IT';

-- 推荐
SELECT name FROM employees WHERE department = 'IT'
UNION ALL
SELECT name FROM contractors WHERE department = 'IT';

-- 使用 LIMIT 减少处理的数据量
EXPLAIN ANALYZE SELECT * FROM large_table ORDER BY created_at DESC LIMIT 100;
```

### 3. 分区表优化

```sql
-- 创建分区表
CREATE TABLE orders_partitioned (
    id BIGINT,
    customer_id INTEGER,
    total_amount NUMERIC(10,2),
    created_at TIMESTAMP
) PARTITION BY RANGE (created_at);

-- 创建分区
CREATE TABLE orders_2023_q1 PARTITION OF orders_partitioned
FOR VALUES FROM ('2023-01-01') TO ('2023-04-01');

CREATE TABLE orders_2023_q2 PARTITION OF orders_partitioned
FOR VALUES FROM ('2023-04-01') TO ('2023-07-01');

-- 分区裁剪查询
EXPLAIN ANALYZE SELECT * FROM orders_partitioned
WHERE created_at BETWEEN '2023-01-15' AND '2023-01-31';
```

## 系统配置优化

### 1. 内存配置

```sql
-- 查看当前内存配置
SELECT name, setting, unit, short_desc
FROM pg_settings
WHERE name IN (
    'shared_buffers',
    'effective_cache_size',
    'work_mem',
    'maintenance_work_mem'
);

-- 内存配置建议（基于系统内存 16GB）
-- shared_buffers = 4GB        -- 系统内存的 25%
-- effective_cache_size = 12GB -- 系统内存的 75%
-- work_mem = 64MB            -- 根据并发连接数调整
-- maintenance_work_mem = 1GB -- 维护操作内存
```

### 2. 连接配置

```sql
-- 连接配置
-- max_connections = 200       -- 最大连接数
-- superuser_reserved_connections = 3
-- shared_preload_libraries = 'pg_stat_statements,auto_explain'

-- 使用连接池减少连接数
-- PgBouncer 或 Pgpool-II 配置
```

### 3. WAL 配置

```sql
-- WAL 优化配置
-- wal_level = replica                    -- 支持复制和备份
-- wal_buffers = 16MB                     -- WAL 缓冲区
-- checkpoint_completion_target = 0.9     -- 检查点完成目标
-- wal_compression = on                   -- WAL 压缩
-- wal_writer_delay = 200ms               -- WAL 写入延迟
```

通过系统性的性能分析和优化，可以显著提升 PostgreSQL 数据库的查询性能和整体运行效率。