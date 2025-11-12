# ClickHouse 架构与模式设计

理解 ClickHouse 的架构原理和正确的模式设计是充分发挥其性能的关键。本章节深入讲解 ClickHouse 的核心设计概念。

## ClickHouse 存储架构

### 列式存储原理

```
行式存储 vs 列式存储
┌─────────────────────┬─────────────────────┐
│     行式存储        │     列式存储        │
├─────────────────────┼─────────────────────┤
│ id,name,age,salary  │ id: 1,2,3,4,5      │
│ 1,Alice,25,5000     │ name: Alice,Bob,... │
│ 2,Bob,30,6000       │ age: 25,30,35,28,32 │
│ 3,Carol,35,7000     │ salary: 5000,...   │
│ 4,David,28,5500     │                    │
│ 5,Eve,32,6500       │                    │
└─────────────────────┴─────────────────────┘
```

**优势**:
- **压缩比高**: 同类型数据更容易压缩
- **查询快**: 只读取需要的列
- **缓存友好**: CPU 向量化处理

### 数据文件结构
```
Table Directory Structure
├── all_1_100_1/
│   ├── id.bin          # 列数据文件
│   ├── name.bin        # 字符串列数据
│   ├── age.bin         # 数值列数据
│   ├── primary.idx     # 主键索引
│   └── marks           # 数据标记
├── all_101_200_1/
│   └── ...
└── count.txt          # 总行数
```

## 表引擎选择指南

### MergeTree 系列引擎决策树

```sql
-- 基础决策流程
-- 1. 需要实时写入和查询？ → MergeTree 系列
-- 2. 需要去重？ → ReplacingMergeTree/SummingMergeTree
-- 3. 需要聚合？ → AggregatingMergeTree
-- 4. 需要副本？ → ReplicatedMergeTree
-- 5. 需要分布式？ → Distributed
```

### 引擎选择矩阵

| 场景 | 推荐引擎 | 示例 |
|------|----------|------|
| 基础分析 | MergeTree | 用户行为日志 |
| 实时去重 | ReplacingMergeTree | 设备状态更新 |
| 增量聚合 | SummingMergeTree | 实时统计 |
| 复杂聚合 | AggregatingMergeTree | 实时指标计算 |
| 高可用 | ReplicatedMergeTree | 生产环境 |
| 分布式 | Distributed + ReplicatedMergeTree | 大规模集群 |

### 详细引擎示例

```sql
-- 1. MergeTree - 基础引擎
CREATE TABLE events (
    event_time DateTime,
    user_id UInt64,
    event_type String,
    properties String
) ENGINE = MergeTree()
PARTITION BY toYYYYMM(event_time)
ORDER BY (event_time, user_id, event_type);

-- 2. ReplacingMergeTree - 去重
CREATE TABLE user_profiles (
    user_id UInt64,
    last_update DateTime,
    profile_data String
) ENGINE = ReplacingMergeTree(last_update)
PARTITION BY toYYYYMM(last_update)
ORDER BY user_id;

-- 3. SummingMergeTree - 数值聚合
CREATE TABLE daily_stats (
    date Date,
    user_id UInt64,
    page_views UInt64,
    revenue Decimal(10,2)
) ENGINE = SummingMergeTree()
PARTITION BY (date)
ORDER BY (date, user_id);

-- 4. AggregatingMergeTree - 复杂聚合
CREATE TABLE hourly_user_stats (
    hour DateTime,
    event_type String,
    user_id AggregateFunction(uniq, UInt64),
    revenue AggregateFunction(sum, Decimal(10,2))
) ENGINE = AggregatingMergeTree()
PARTITION BY toYYYYMMDD(hour)
ORDER BY (hour, event_type);

-- 5. ReplicatedMergeTree - 高可用
CREATE TABLE replica_events (
    event_time DateTime,
    user_id UInt64,
    event_type String
) ENGINE = ReplicatedMergeTree(
    '/clickhouse/tables/{shard}/events',
    '{replica}'
)
PARTITION BY toYYYYMM(event_time)
ORDER BY (event_time, user_id);
```

## 分区设计策略

### 分区键选择原则

```sql
-- 好的分区键示例

-- 1. 时间分区（最常用）
PARTITION BY toYYYYMM(event_time)           -- 按月分区
PARTITION BY toYYYYMMDD(event_time)         -- 按日分区
PARTITION BY toYYYYMM(event_time, event_type) -- 时间+事件类型

-- 2. 分类分区
PARTITION BY region                         -- 地区分区
PARTITION BY device_type                    -- 设备类型分区

-- 3. 复合分区
PARTITION BY (toYYYYMM(event_time), region) -- 时间+地区

-- 不推荐的分区键
PARTITION BY hash(user_id)                  -- 随机哈希导致分散查询
PARTITION BY event_type                     -- 基数太小
```

### 分区大小控制

```sql
-- 查看分区大小
SELECT
    partition,
    count() as rows,
    formatReadableSize(sum(bytes)) as size,
    formatReadableSize(sum(bytes) / count()) as avg_row_size
FROM system.parts
WHERE table = 'events' AND active = 1
GROUP BY partition
ORDER BY partition DESC;

-- 分区数据管理
-- 删除旧分区（节省存储）
ALTER TABLE events DROP PARTITION '202310';

-- 合并分区（优化查询）
ALTER TABLE events MERGE PARTITION '202310', '202311';

-- 复制分区
ALTER TABLE events REPLACE PARTITION '202312' FROM events_backup;
```

## 排序键（ORDER BY）设计

### 排序键设计原则

```sql
-- 排序键的黄金法则
-- 1. 查询过滤条件字段放在前面
-- 2. 高基数字段优先
-- 3. 按使用频率排序
-- 4. 避免过多字段（影响性能）

-- 好的排序键设计
CREATE TABLE user_events (
    event_time DateTime,
    user_id UInt64,
    event_type String,
    page_url String,
    session_id String,
    ip_address IPv4
) ENGINE = MergeTree()
PARTITION BY toYYYYMM(event_time)
ORDER BY (event_time, user_id, event_type); -- ✅ 优化时间范围+用户查询

-- 不同查询模式的排序键
-- 时间范围查询为主
ORDER BY (event_time, user_id, event_type)

-- 用户查询为主
ORDER BY (user_id, event_time, event_type)

-- 多维度查询
ORDER BY (event_time, user_id, event_type, page_url)
```

### 排序键对查询性能的影响

```sql
-- 测试不同排序键的性能差异

-- 方案 1: 按时间排序
CREATE TABLE events_by_time (
    event_time DateTime,
    user_id UInt64,
    event_type String
) ENGINE = MergeTree()
ORDER BY (event_time, user_id);

-- 方案 2: 按用户排序
CREATE TABLE events_by_user (
    event_time DateTime,
    user_id UInt64,
    event_type String
) ENGINE = MergeTree()
ORDER BY (user_id, event_time);

-- 性能测试查询
-- 查询 1: 时间范围过滤
SELECT count() FROM events_by_time WHERE event_time > '2023-12-01';
-- 结果: events_by_time 更快

-- 查询 2: 用户过滤
SELECT count() FROM events_by_user WHERE user_id = 12345;
-- 结果: events_by_user 更快
```

## 数据类型优化

### 数值类型选择

```sql
-- 数值类型选择指南
CREATE TABLE optimized_types (
    -- 根据实际范围选择合适的整数类型
    status UInt8,           -- 枚举值 0-255
    age UInt8,              -- 年龄 0-255
    user_id UInt64,         -- 用户ID，大数值
    click_count UInt32,     -- 点击计数

    -- 精度要求选择浮点类型
    price Decimal(10,2),    -- 价格，精确到分
    ratio Float32,          -- 比例，精度要求不高
    metric Float64          -- 指标，需要高精度

    -- 时间类型选择
    event_time DateTime,    -- 精确到秒
    timestamp_ms DateTime64(3) -- 精确到毫秒

    -- 字符串类型
    short_string FixedString(32),  -- 固定长度
    variable_string String,        -- 可变长度
    low_cardinality LowCardinality(String) -- 低基数枚举值
);
```

### 枚举类型优化

```sql
-- 使用 Enum 类型替代字符串
CREATE TABLE user_actions (
    user_id UInt64,
    action Enum8(
        'view' = 1,
        'click' = 2,
        'purchase' = 3,
        'refund' = 4
    ),
    timestamp DateTime
) ENGINE = MergeTree()
ORDER BY (timestamp, user_id);

-- 性能对比
-- 字符串: action = 'purchase'
-- Enum类型: action = 'purchase' (内部转换为 action = 3)
```

### Array 和 Tuple 使用

```sql
-- 数组类型优化设计
CREATE TABLE user_properties (
    user_id UInt64,
    tags Array(String),
    metrics Array(Float32),
    dimensions Tuple(String, String, Float64)
) ENGINE = MergeTree()
ORDER BY user_id;

-- 数组查询示例
SELECT
    user_id,
    arrayContains(tags, 'premium') as is_premium,
    arrayAvg(metrics) as avg_metric,
    dimensions.1 as dimension_1
FROM user_properties
WHERE arrayLength(tags) > 0;
```

## 物化视图设计

### 实时聚合视图

```sql
-- 实时用户活动统计
CREATE TABLE daily_user_stats (
    date Date,
    total_users UInt64,
    active_users UInt64,
    new_users UInt64,
    returning_users UInt64
) ENGINE = SummingMergeTree()
ORDER BY date;

-- 实时聚合物化视图
CREATE MATERIALIZED VIEW mv_daily_user_stats
TO daily_user_stats
AS SELECT
    toDate(event_time) as date,
    count() as total_users,
    uniqIf(user_id, event_type = 'active') as active_users,
    uniqIf(user_id, is_new_user) as new_users,
    uniqIf(user_id, NOT is_new_user) as returning_users
FROM (
    SELECT
        event_time,
        user_id,
        event_type,
        event_type = 'active' as is_active,
        event_type = 'signup' as is_new_user
    FROM user_events
)
GROUP BY date;
```

### 滚动窗口聚合

```sql
-- 7天滚动窗口活跃用户统计
CREATE TABLE rolling_active_users (
    date Date,
    active_users_7d UInt64,
    active_users_30d UInt64
) ENGINE = ReplacingMergeTree()
ORDER BY date;

CREATE MATERIALIZED VIEW mv_rolling_active_users
TO rolling_active_users
AS SELECT
    toDate(event_time) as date,
    uniqStateIf(user_id, event_time >= date - INTERVAL 7 DAY) as active_users_7d,
    uniqStateIf(user_id, event_time >= date - INTERVAL 30 DAY) as active_users_30d
FROM user_events
WHERE event_time >= today() - INTERVAL 30 DAY
GROUP BY date;
```

## TTL 和数据生命周期

### TTL 数据清理

```sql
-- 基于时间的 TTL
CREATE TABLE events_with_ttl (
    event_time DateTime,
    user_id UInt64,
    event_data String
) ENGINE = MergeTree()
PARTITION BY toYYYYMM(event_time)
ORDER BY (event_time, user_id)
TTL event_time + INTERVAL 90 DAY DELETE;  -- 90天后自动删除

-- 基于条件的 TTL
CREATE TABLE device_status (
    device_id String,
    last_seen DateTime,
    status String
) ENGINE = ReplacingMergeTree()
ORDER BY device_id
TTL last_seen + INTERVAL 30 DAY REPLACE PARTITION;  -- 30天后替换分区

-- 多级 TTL
CREATE TABLE user_behaviors (
    event_time DateTime,
    user_id UInt64,
    behavior_data String
) ENGINE = MergeTree()
PARTITION BY toYYYYMM(event_time)
ORDER BY (event_time, user_id)
TTL
    event_time + INTERVAL 1 MONTH DELETE,                -- 1个月后删除
    event_time + INTERVAL 7 DAY TO DISK 'cold_storage', -- 7天后移到冷存储
    event_time + INTERVAL 1 DAY TO VOLUME 'fast';       -- 1天后移到快速存储
```

## 实际应用案例

### 用户行为分析表设计

```sql
-- 完整的用户行为分析表
CREATE TABLE user_behaviors (
    event_time DateTime,
    event_date Date MATERIALIZED toDate(event_time),
    user_id UInt64,
    session_id String,
    event_type Enum8(
        'page_view' = 1,
        'click' = 2,
        'add_to_cart' = 3,
        'purchase' = 4,
        'search' = 5
    ),
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
    '/clickhouse/tables/{shard}/user_behaviors',
    '{replica}'
)
PARTITION BY (toYYYYMM(event_time), event_type)
ORDER BY (event_time, user_id, event_type)
TTL event_time + INTERVAL 2 YEAR DELETE
SETTINGS index_granularity = 8192;
```

### 实时指标计算表

```sql
-- 实时业务指标表
CREATE TABLE real_time_metrics (
    metric_time DateTime,
    metric_name String,
    metric_value Float64,
    tags Array(String)
) ENGINE = SummingMergeTree()
PARTITION BY toYYYYMMDD(metric_time)
ORDER BY (metric_time, metric_name, tags)
TTL metric_time + INTERVAL 1 YEAR DELETE;

-- 聚合物化视图
CREATE MATERIALIZED VIEW mv_real_time_metrics
TO real_time_metrics
AS SELECT
    now() as metric_time,
    name as metric_name,
    value as metric_value,
    [tag1, tag2, tag3] as tags
FROM kafka_metrics_stream;
```

通过合理的模式设计，ClickHouse 可以充分发挥其性能优势，为实时数据分析提供强大的支持。