# ClickHouse 性能调优实战

ClickHouse 性能调优是一个系统工程，涉及查询优化、配置调整、架构设计等多个方面。本章节介绍实用的性能调优技巧和最佳实践。

## 查询性能优化

### 1. 查询执行计划分析

```sql
-- 使用 EXPLAIN 分析查询执行计划
EXPLAIN PIPELINE
SELECT
    toDate(event_time) as date,
    event_type,
    count() as total_events,
    uniqExact(user_id) as unique_users
FROM events
WHERE event_time >= '2023-12-01'
  AND event_time < '2023-12-02'
GROUP BY date, event_type;

-- 查看查询优化建议
EXPLAIN SYNTAX
SELECT *
FROM events
WHERE event_date BETWEEN '2023-12-01' AND '2023-12-31'
  AND user_id IN (1001, 1002, 1003)
ORDER BY event_time;
```

### 2. 索引和分区利用优化

```sql
-- 确保查询利用分区裁剪
-- ✅ 好的查询 - 能利用分区
SELECT count() FROM events
WHERE event_date >= '2023-12-01' AND event_date < '2024-01-01';

-- ❌ 不好的查询 - 无法利用分区
SELECT count() FROM events
WHERE toDate(event_time) >= '2023-12-01' AND toDate(event_time) < '2024-01-01';

-- 优化查询利用主键索引
-- ✅ 好的查询 - 利用排序键
SELECT * FROM events
WHERE event_time >= '2023-12-01'
  AND user_id = 12345
  AND event_type = 'click'
ORDER BY event_time;

-- 使用 PREWHERE 子句优化过滤
SELECT user_id, page_url
FROM events
PREWHERE event_type = 'click'  -- 先过滤，再读取其他列
WHERE user_id IN (SELECT user_id FROM active_users);
```

### 3. 聚合函数优化

```sql
-- 选择合适的聚合函数
-- 最快: count() - 基于表统计
SELECT count() FROM events;

-- 较快: uniqApprox() - 近似去重，误差1-5%
SELECT uniqApprox(user_id) FROM events;

-- 精确但较慢: uniqExact() - 精确去重
SELECT uniqExact(user_id) FROM events;

-- 分位数优化
SELECT
    quantileExact(0.95)(response_time) as p95_exact,    -- 精确，内存消耗大
    quantile(0.95)(response_time) as p95_approx,       -- 近似，性能好
    medianExact(response_time) as median_exact
FROM metrics;

-- 条件聚合优化
SELECT
    countIf(event_type = 'click') as clicks,
    sumIf(revenue, event_type = 'purchase') as revenue,
    avgIf(response_time, event_type = 'click') as avg_response_time
FROM events;
```

### 4. JOIN 优化

```sql
-- 使用合适的 JOIN 策略
CREATE TABLE users (
    user_id UInt64,
    user_name String,
    registration_date Date
) ENGINE = MergeTree()
ORDER BY user_id;

CREATE TABLE events (
    event_time DateTime,
    user_id UInt64,
    event_type String
) ENGINE = MergeTree()
PARTITION BY toYYYYMM(event_time)
ORDER BY (event_time, user_id);

-- ✅ 推荐的 JOIN 方式
SELECT
    e.event_time,
    u.user_name,
    e.event_type
FROM events e
LEFT JOIN users u ON e.user_id = u.user_id
WHERE e.event_time >= '2023-12-01'
  AND e.event_time < '2023-12-02';

-- 使用字典表优化维度 JOIN
CREATE DICTIONARY user_dict (
    user_id UInt64,
    user_name String,
    user_type String
) PRIMARY KEY user_id
LAYOUT(HASHED())
SOURCE(CLICKHOUSE(
    QUERY 'SELECT user_id, user_name, user_type FROM users'
));

SELECT
    dictGet('user_dict', 'user_name', user_id),
    event_type,
    count() as events
FROM events
WHERE event_time >= today() - INTERVAL 1 DAY
GROUP BY dictGet('user_dict', 'user_name', user_id), event_type;
```

## 写入性能优化

### 1. 批量插入优化

```sql
-- 使用批量插入而非单条插入
-- ❌ 不推荐：单条插入
INSERT INTO events VALUES (now(), 1, 'click'), (now(), 2, 'view');

-- ✅ 推荐：批量插入
INSERT INTO events FORMAT CSV
2023-12-25 10:00:00,1001,click
2023-12-25 10:00:01,1002,view
2023-12-25 10:00:02,1003,click

-- 使用异步插入
SET async_insert = 1;
SET async_insert_threads = 4;
SET async_insert_max_data_size = 1000000;

INSERT INTO events VALUES (now(), 1, 'click');  -- 异步插入
```

### 2. 数据格式优化

```sql
-- 使用高效的导入格式
-- Native 格式（最快）
INSERT INTO events FORMAT Native
...

-- TSV 格式（较快）
INSERT INTO events FORMAT TSV
...

-- CSV 格式（较慢但通用）
INSERT INTO events FORMAT CSV
...

-- 从文件导入
INSERT INTO events FROM INFILE '/path/to/events.csv' FORMAT CSV;
```

### 3. 表结构优化

```sql
-- 优化表结构提升写入性能
CREATE TABLE optimized_events (
    event_time DateTime CODEC(DoubleDelta, LZ4),
    user_id UInt64 CODEC(Gorilla),
    event_type LowCardinality(String),
    page_url String CODEC(ZSTD),
    ip_address IPv4 CODEC(ZSTD),
    revenue Decimal(10,2) CODEC(Gorilla),
    properties Array(String) CODEC(ZSTD)
) ENGINE = MergeTree()
PARTITION BY toYYYYMM(event_time)
ORDER BY (event_time, user_id)
SETTINGS index_granularity = 8192;

-- 写入后立即合并（减少碎片）
OPTIMIZE TABLE events PARTITION '202312' FINAL;
```

## 配置参数调优

### 1. 内存配置

```sql
-- 查看当前内存配置
SELECT name, value, changed, description
FROM system.settings
WHERE name LIKE '%memory%';

-- 关键内存参数调优
SET max_memory_usage = 10000000000;           -- 10GB
SET max_bytes_before_external_group_by = 5000000000;  -- 5GB
SET max_bytes_before_external_sort = 5000000000;       -- 5GB
SET aggregation_memory_efficient = 1;       -- 优化聚合内存使用
```

### 2. 并发和线程配置

```sql
-- 线程配置调优
SET max_threads = 8;                        -- CPU核心数
SET max_insert_threads = 4;                 -- 插入线程数
SET max_concurrent_queries = 100;           -- 最大并发查询
SET background_pool_size = 8;               -- 后台任务池大小
```

### 3. MergeTree 引擎优化

```sql
-- 表级别优化设置
CREATE TABLE events_optimized (
    event_time DateTime,
    user_id UInt64,
    event_type String
) ENGINE = MergeTree()
PARTITION BY toYYYYMM(event_time)
ORDER BY (event_time, user_id)
SETTINGS
    index_granularity = 8192,              -- 索引粒度
    min_rows_for_wide_part = 1000000,       -- 小分片阈值
    merge_with_ttl_timeout = 60,            -- TTL合并超时
    parts_to_delay_insert = 150,            -- 延迟插入的分区数
    parts_to_throw_insert = 300;            -- 阻塞插入的分区数
```

### 4. 服务器配置文件优化

```xml
<!-- /etc/clickhouse-server/config.xml -->
<clickhouse>
    <!-- 内存配置 -->
    <max_memory_usage>10000000000</max_memory_usage>

    <!-- 并发配置 -->
    <max_threads>8</max_threads>
    <max_concurrent_queries>100</max_concurrent_queries>

    <!-- MergeTree 配置 -->
    <merge_tree>
        <min_bytes_for_wide_part>5368709120</min_bytes_for_wide_part>
        <min_rows_for_wide_part>1000000</min_rows_for_wide_part>
        <max_parts_in_total>1000</max_parts_in_total>
        <old_parts_lifetime>86400</old_parts_lifetime>
    </merge_tree>

    <!-- 压缩配置 -->
    <compression>
        <case>
            <min_part_size>1048576</min_part_size>
            <method>zstd</method>
        </case>
        <case>
            <min_part_size>10485760</min_part_size>
            <method>lz4</method>
        </case>
    </compression>
</clickhouse>
```

## 监控和诊断

### 1. 性能监控查询

```sql
-- 查看慢查询
SELECT
    query,
    duration_seconds,
    memory_usage,
    read_rows,
    read_bytes,
    result_rows,
    result_bytes
FROM system.query_log
WHERE type = 'QueryFinish'
  AND duration_seconds > 1
  AND event_date = today()
ORDER BY duration_seconds DESC
LIMIT 10;

-- 监控表状态
SELECT
    table,
    sum(rows) as total_rows,
    sum(bytes) as total_bytes,
    sum(data_uncompressed_bytes) as uncompressed_bytes,
    sum(compression_ratio) / count() as avg_compression
FROM system.parts
WHERE active = 1
  AND database = 'default'
GROUP BY table
ORDER BY total_bytes DESC;

-- 监控系统指标
SELECT
    metric,
    value,
    description
FROM system.metrics
WHERE metric LIKE 'Memory%'
   OR metric LIKE 'CPU%'
ORDER BY metric;
```

### 2. 实时性能监控

```sql
-- 当前运行的查询
SELECT
    query_id,
    user,
    address,
    query,
    elapsed_seconds,
    read_rows,
    memory_usage,
    thread_ids
FROM system.processes
ORDER BY elapsed_seconds DESC;

-- 系统负载
SELECT
    toInt64(extract(second from now())) as second,
    count() as active_queries,
    sum(memory_usage) as total_memory,
    avg(elapsed_seconds) as avg_duration
FROM system.processes
GROUP BY second
ORDER BY second DESC
LIMIT 10;
```

### 3. 存储性能分析

```sql
-- 分析数据压缩效果
SELECT
    table,
    sum(data_compressed_bytes) / sum(data_uncompressed_bytes) * 100 as compression_ratio,
    sum(data_uncompressed_bytes) / sum(rows) as avg_row_size,
    sum(rows) as total_rows
FROM system.parts
WHERE active = 1
GROUP BY table
ORDER BY compression_ratio;

-- 检查分区健康状态
SELECT
    partition,
    count() as part_count,
    sum(rows) as total_rows,
    sum(data_compressed_bytes) / 1024 / 1024 / 1024 as size_gb
FROM system.parts
WHERE table = 'events'
  AND active = 1
GROUP BY partition
ORDER BY partition DESC;
```

## 实际优化案例

### 案例 1: 实时用户行为分析优化

```sql
-- 优化前：全表扫描
SELECT
    user_id,
    count() as event_count,
    uniqExact(page_url) as unique_pages
FROM events
WHERE event_time >= now() - INTERVAL 1 HOUR
GROUP BY user_id;

-- 优化后：使用物化视图
CREATE MATERIALIZED VIEW mv_user_hourly_stats
ENGINE = AggregatingMergeTree()
PARTITION BY toYYYYMMDD(toStartOfHour(event_time))
ORDER BY (toStartOfHour(event_time), user_id)
AS SELECT
    toStartOfHour(event_time) as hour,
    user_id,
    uniqState(page_url) as unique_pages,
    sumState(1) as event_count
FROM events
GROUP BY hour, user_id;

-- 查询优化后的数据
SELECT
    user_id,
    sumMerge(event_count) as event_count,
    uniqMerge(unique_pages) as unique_pages
FROM mv_user_hourly_stats
WHERE hour >= toStartOfHour(now() - INTERVAL 1 HOUR)
GROUP BY user_id;
```

### 案例 2: 大规模指标计算优化

```sql
-- 优化前：复杂的窗口函数
SELECT
    minute,
    running_total,
    running_total / lag(running_total) OVER (ORDER BY minute) as growth_rate
FROM (
    SELECT
        toStartOfMinute(event_time) as minute,
        sum(revenue) as running_total
    FROM revenue_events
    WHERE event_time >= now() - INTERVAL 1 DAY
    GROUP BY minute
);

-- 优化后：预计算增量
CREATE TABLE revenue_metrics (
    minute DateTime,
    revenue Decimal(10,2),
    cumulative_revenue Decimal(10,2)
) ENGINE = SummingMergeTree()
ORDER BY minute;

CREATE MATERIALIZED VIEW mv_revenue_metrics
TO revenue_metrics
AS SELECT
    toStartOfMinute(event_time) as minute,
    sum(revenue) as revenue,
    sum(revenue) as cumulative_revenue
FROM revenue_events
GROUP BY minute;

-- 简化的查询
SELECT
    minute,
    cumulative_revenue,
    (cumulative_revenue - lag(cumulative_revenue) OVER (ORDER BY minute)) /
    lag(cumulative_revenue) OVER (ORDER BY minute) as growth_rate
FROM revenue_metrics
ORDER BY minute DESC;
```

## 性能基准测试

```sql
-- 基准测试脚本
CREATE TABLE benchmark_events (
    event_time DateTime,
    user_id UInt64,
    event_type String,
    value Float64
) ENGINE = MergeTree()
ORDER BY (event_time, user_id);

-- 插入性能测试
INSERT INTO benchmark_events
SELECT
    now() - INTERVAL rand() % 30 DAY,
    rand() % 1000000,
    ['click', 'view', 'purchase'][rand() % 3 + 1],
    rand() / 1000000
FROM numbers(1000000);

-- 查询性能测试
SELECT
    event_type,
    count() as events,
    uniqExact(user_id) as users,
    avg(value) as avg_value
FROM benchmark_events
WHERE event_time >= now() - INTERVAL 7 DAY
GROUP BY event_type;
```

通过这些性能调优技巧，ClickHouse 的查询和分析性能可以得到显著提升，充分发挥其在大数据处理方面的优势。