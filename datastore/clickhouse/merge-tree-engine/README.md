# MergeTree 引擎深度解析

MergeTree 是 ClickHouse 最核心的表引擎系列，专为 OLAP 查询优化而设计。本章节深入解析 MergeTree 引擎的原理、特性和最佳实践。

## MergeTree 引擎家族

### 引擎类型概览

```sql
-- MergeTree 基础引擎族
-- 1. MergeTree - 基础引擎
-- 2. ReplacingMergeTree - 去重引擎
-- 3. SummingMergeTree - 数值聚合引擎
-- 4. AggregatingMergeTree - 复杂聚合引擎
-- 5. VersionedCollapsingMergeTree - 版本化折叠引擎
-- 6. GraphiteMergeTree - Graphite 数据引擎
-- 7. CollapsingMergeTree - 折叠引擎
-- 8. ReplicatedMergeTree - 副本引擎
-- 9. Distributed - 分布式引擎
```

## MergeTree 基础引擎

### 核心概念

```sql
-- 基础 MergeTree 表结构
CREATE TABLE events (
    event_time DateTime,
    event_date Date MATERIALIZED toDate(event_time),
    user_id UInt64,
    event_type String,
    page_url String,
    revenue Decimal(10,2)
) ENGINE = MergeTree()
PARTITION BY toYYYYMM(event_date)        -- 分区键
ORDER BY (event_time, user_id, event_type) -- 排序键
SETTINGS index_granularity = 8192;         -- 索引粒度
```

### 数据存储结构

```
MergeTree 数据文件结构
├── partition_1_100_1/
│   ├── event_time.bin          # 时间列数据
│   ├── user_id.bin             # 用户ID列数据
│   ├── event_type.bin          # 事件类型列数据
│   ├── revenue.bin             # 收入列数据
│   ├── primary.idx             # 主键索引
│   ├── minmax_event_time.idx   # 分区最小最大值索引
│   └── marks                   # 数据标记（每8192行一个）
├── partition_101_200_1/
│   └── ...
└── count.txt                  # 总行数
```

### 索引原理

```sql
-- 主键索引工作原理
-- 排序键决定了数据的物理存储顺序
ORDER BY (event_time, user_id, event_type)

-- 数据按排序键排序，形成有序数据块
event_time ↑, user_id ↑, event_type ↑

-- 索引标记结构
mark_0: rows 0-8191     -> [min_time_0, max_time_0, min_user_0, max_user_0, ...]
mark_1: rows 8192-16383 -> [min_time_1, max_time_1, min_user_1, max_user_1, ...]
mark_2: rows 16384-24575 -> [min_time_2, max_time_2, min_user_2, max_user_2, ...]
```

### 分区机制

```sql
-- 分区策略示例
CREATE TABLE events_partitioned (
    event_time DateTime,
    user_id UInt64,
    event_type String,
    region String
) ENGINE = MergeTree()
PARTITION BY (toYYYYMM(event_time), region)  -- 复合分区
ORDER BY (event_time, user_id, event_type);

-- 查看分区信息
SELECT
    partition,
    count() as rows,
    sum(bytes) as size_bytes
FROM system.parts
WHERE table = 'events_partitioned'
  AND active = 1
GROUP BY partition
ORDER BY partition;

-- 分区操作
-- 删除分区（节省存储）
ALTER TABLE events_partitioned DROP PARTITION '202312';

-- 复制分区
ALTER TABLE events_partitioned REPLACE PARTITION '202312'
FROM events_backup;

-- 合并分区（优化查询）
ALTER TABLE events_partitioned MERGE PARTITION '202310', '202311';
```

## ReplacingMergeTree 去重引擎

### 基础用法

```sql
-- ReplacingMergeTree 用于数据去重
CREATE TABLE user_profiles (
    user_id UInt64,
    last_update DateTime,
    profile_data String,
    score Float64
) ENGINE = ReplacingMergeTree(last_update)  -- 根据 last_update 去重
PARTITION BY toYYYYMM(last_update)
ORDER BY user_id;

-- 插入数据（相同 user_id 保留最新记录）
INSERT INTO user_profiles VALUES
(1, '2023-12-25 10:00:00', '{"name": "Alice"}', 85.5),
(1, '2023-12-25 10:01:00', '{"name": "Alice"}', 90.0),  -- 会替换上一条
(2, '2023-12-25 10:00:00', '{"name": "Bob"}', 75.0);

-- 查询结果（最新的数据）
SELECT * FROM user_profiles;
```

### 版本控制

```sql
-- 多版本控制
CREATE TABLE user_status_history (
    user_id UInt64,
    update_time DateTime,
    status String,
    version UInt64
) ENGINE = ReplacingMergeTree(version)
PARTITION BY toYYYYMM(update_time)
ORDER BY (user_id, version);

-- 插入不同版本的数据
INSERT INTO user_status_history VALUES
(1, '2023-12-25 10:00:00', 'active', 1),
(1, '2023-12-25 10:01:00', 'inactive', 2),
(1, '2023-12-25 10:02:00', 'active', 3);

-- 最终查询结果（保留版本号最大的记录）
SELECT * FROM user_status_history;
```

## SummingMergeTree 聚合引擎

### 数值聚合

```sql
-- SummingMergeTree 自动聚合数值列
CREATE TABLE daily_revenue (
    date Date,
    product_id UInt64,
    category String,
    revenue Decimal(10,2),
    order_count UInt32
) ENGINE = SummingMergeTree()
PARTITION BY (category, toYYYYMM(date))
ORDER BY (date, product_id, category);

-- 插入多条记录，自动聚合
INSERT INTO daily_revenue VALUES
('2023-12-25', 1001, 'electronics', 100.50, 5),
('2023-12-25', 1001, 'electronics', 50.25, 2),  -- 会自动聚合成一条
('2023-12-25', 1002, 'clothing', 75.00, 3);

-- 查询聚合结果
SELECT * FROM daily_revenue;
-- 结果：('2023-12-25', 1001, 'electronics', 150.75, 7)
```

### 复杂聚合配置

```sql
-- 指定需要聚合的列
CREATE TABLE product_metrics (
    date Date,
    product_id UInt64,
    views UInt32,
    clicks UInt32,
    revenue Decimal(10,2),
    orders UInt32
) ENGINE = SummingMergeTree((views, clicks, revenue, orders))
PARTITION BY toYYYYMM(date)
ORDER BY (date, product_id);

-- 只有指定的列会被聚合
```

## AggregatingMergeTree 复杂聚合

### 聚合函数状态

```sql
-- 使用 AggregatingMergeTree 存储聚合状态
CREATE TABLE hourly_user_stats (
    hour DateTime,
    event_type String,
    user_id AggregateFunction(uniq, UInt64),
    session_time AggregateFunction(avg, UInt32),
    revenue AggregateFunction(sum, Decimal(10,2))
) ENGINE = AggregatingMergeTree()
PARTITION BY toYYYYMMDD(hour)
ORDER BY (hour, event_type);

-- 插入聚合状态数据
INSERT INTO hourly_user_stats
SELECT
    toStartOfHour(event_time) as hour,
    event_type,
    uniqState(user_id) as user_id_state,
    avgState(duration) as session_time_state,
    sumState(revenue) as revenue_state
FROM events
WHERE event_time >= now() - INTERVAL 1 HOUR
GROUP BY hour, event_type;

-- 查询聚合结果（需要使用对应的合并函数）
SELECT
    hour,
    event_type,
    uniqMerge(user_id) as unique_users,
    avgMerge(session_time) as avg_session_time,
    sumMerge(revenue) as total_revenue
FROM hourly_user_stats
GROUP BY hour, event_type;
```

### 实时聚合示例

```sql
-- 创建实时用户活跃度统计
CREATE MATERIALIZED VIEW mv_user_activity
TO user_activity_agg
AS SELECT
    toStartOfHour(event_time) as hour,
    event_type,
    uniqState(user_id) as active_users,
    sumState(1) as total_events
FROM events
GROUP BY hour, event_type;

-- 创建目标表
CREATE TABLE user_activity_agg (
    hour DateTime,
    event_type String,
    active_users AggregateFunction(uniq, UInt64),
    total_events AggregateFunction(sum, UInt64)
) ENGINE = AggregatingMergeTree()
PARTITION BY toYYYYMMDD(hour)
ORDER BY (hour, event_type);
```

## CollapsingMergeTree 折叠引擎

### 数据折叠原理

```sql
-- CollapsingMergeTree 通过 sign 字段实现数据折叠
CREATE TABLE inventory_changes (
    item_id UInt64,
    timestamp DateTime,
    quantity Int32,  -- 数量变化
    sign Int8       -- 标记字段：1=新增，-1=删除
) ENGINE = CollapsingMergeTree(sign)
PARTITION BY toYYYYMM(timestamp)
ORDER BY (item_id, timestamp);

-- 插入数据
INSERT INTO inventory_changes VALUES
(1001, '2023-12-25 10:00:00', 10, 1),   -- 新增10个商品
(1001, '2023-12-25 10:05:00', 3, 1),    -- 新增3个商品
(1001, '2023-12-25 10:10:00', 2, -1);  -- 删除2个商品

-- 查询结果（会自动折叠）
SELECT item_id, sum(quantity * sign) as current_quantity
FROM inventory_changes
GROUP BY item_id;
-- 结果：item_id=1001, current_quantity=11
```

### VersionedCollapsingMergeTree

```sql
-- 版本化的折叠引擎，避免数据竞争问题
CREATE TABLE inventory_changes_v2 (
    item_id UInt64,
    timestamp DateTime,
    quantity Int32,
    sign Int8,
    version UInt64
) ENGINE = VersionedCollapsingMergeTree(sign, version)
PARTITION BY toYYYYMM(timestamp)
ORDER BY (item_id, timestamp, version);

-- 插入版本化数据
INSERT INTO inventory_changes_v2 VALUES
(1001, '2023-12-25 10:00:00', 10, 1, 1),
(1001, '2023-12-25 10:05:00', 3, 1, 2),
(1001, '2023-12-25 10:10:00', 2, -1, 3);
```

## 副本引擎 ReplicatedMergeTree

### 副本配置

```sql
-- 创建复制表
CREATE TABLE replicated_events (
    event_time DateTime,
    user_id UInt64,
    event_type String
) ENGINE = ReplicatedMergeTree(
    '/clickhouse/tables/{shard}/replicated_events',  -- ZK路径
    '{replica}'                                       -- 副本标识
)
PARTITION BY toYYYYMM(event_time)
ORDER BY (event_time, user_id);

-- 副本相关系统表
SELECT * FROM system.replicas WHERE table = 'replicated_events';
SELECT * FROM system.replication_queue WHERE table = 'replicated_events';
```

### 副本操作

```sql
-- 同步副本数据
SYSTEM SYNC REPLICA replicated_events;

-- 检查副本状态
SELECT
    table,
    is_leader,
    absolute_delay,
    queue_size,
    log_pointer,
    total_replicas
FROM system.replicas
WHERE table = 'replicated_events';
```

## MergeTree 性能优化

### 索引粒度优化

```sql
-- 调整索引粒度
-- 小索引粒度：更适合高精度查询，但索引开销大
CREATE TABLE fine_index (
    event_time DateTime,
    user_id UInt64,
    value Float64
) ENGINE = MergeTree()
ORDER BY (event_time, user_id)
SETTINGS index_granularity = 1024;  -- 1K 行一个标记

-- 大索引粒度：更适合范围查询，索引开销小
CREATE TABLE coarse_index (
    event_time DateTime,
    user_id UInt64,
    value Float64
) ENGINE = MergeTree()
ORDER BY (event_time, user_id)
SETTINGS index_granularity = 16384;  -- 16K 行一个标记
```

### 宽分区配置

```sql
-- 优化宽分区设置
CREATE TABLE optimized_table (
    event_time DateTime,
    user_id UInt64,
    large_field String,
    metadata Tuple(String, String, Float64)
) ENGINE = MergeTree()
ORDER BY (event_time, user_id)
SETTINGS
    min_bytes_for_wide_part = 1073741824,  -- 1MB以上使用宽分区
    min_rows_for_wide_part = 1000000;       -- 100万行以上使用宽分区
```

### TTL 数据生命周期

```sql
-- TTL 配置示例
CREATE TABLE events_with_ttl (
    event_time DateTime,
    user_id UInt64,
    event_type String,
    data String
) ENGINE = MergeTree()
PARTITION BY toYYYYMM(event_time)
ORDER BY (event_time, user_id)
TTL
    event_time + INTERVAL 90 DAY DELETE,                -- 90天后删除
    event_time + INTERVAL 7 DAY TO DISK 'cold_storage',  -- 7天后移到冷存储
    event_time + INTERVAL 1 DAY TO VOLUME 'fast_storage';  -- 1天后移到快速存储
```

## 实际应用案例

### 用户行为分析表

```sql
-- 完整的用户行为分析表
CREATE TABLE user_events (
    event_time DateTime,
    event_date Date MATERIALIZED toDate(event_time),
    user_id UInt64,
    session_id String,
    event_type Enum8('view' = 1, 'click' = 2, 'purchase' = 3),
    page_url String,
    referrer String,
    user_agent String,
    ip_address IPv4,
    device_type LowCardinality(String),
    browser LowCardinality(String),
    os LowCardinality(String),
    country LowCardinality(String),
    city LowCardinality(String),
    revenue Decimal(10,2) DEFAULT 0,
    properties Array(String),
    metadata Tuple(String, String, Float64)
) ENGINE = ReplicatedMergeTree(
    '/clickhouse/tables/{shard}/user_events',
    '{replica}'
)
PARTITION BY (toYYYYMM(event_time), event_type)
ORDER BY (event_time, user_id, event_type)
TTL event_time + INTERVAL 2 YEAR DELETE
SETTINGS index_granularity = 8192;
```

### 实时统计聚合表

```sql
-- 实时统计表
CREATE TABLE real_time_stats (
    metric_time DateTime,
    metric_name String,
    metric_value Float64,
    tags Array(String)
) ENGINE = SummingMergeTree()
PARTITION BY (toYYYYMMDD(metric_time), metric_name)
ORDER BY (metric_time, metric_name, tags)
TTL metric_time + INTERVAL 1 YEAR DELETE;
```

通过合理使用 MergeTree 引擎系列，可以构建高性能的实时分析系统，充分发挥 ClickHouse 在大数据处理方面的优势。