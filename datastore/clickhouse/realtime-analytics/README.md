# ClickHouse 实时分析案例

ClickHouse 在实时数据分析方面表现出色，本章节通过实际案例展示如何使用 ClickHouse 构建高效的实时分析系统。

## 案例 1: 用户行为实时分析

### 数据模型设计

```sql
-- 用户事件表
CREATE TABLE user_events (
    event_time DateTime,
    event_date Date MATERIALIZED toDate(event_time),
    user_id UInt64,
    session_id String,
    event_type Enum8(
        'page_view' = 1,
        'click' = 2,
        'add_to_cart' = 3,
        'purchase' = 4,
        'search' = 5,
        'logout' = 6
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
    duration UInt32,  -- 页面停留时间（秒）
    is_new_user UInt8 DEFAULT 0
) ENGINE = ReplicatedMergeTree(
    '/clickhouse/tables/{shard}/user_events',
    '{replica}'
)
PARTITION BY (toYYYYMM(event_time), event_type)
ORDER BY (event_time, user_id, event_type)
TTL event_time + INTERVAL 1 YEAR DELETE
SETTINGS index_granularity = 8192;
```

### 实时统计指标

```sql
-- 实时用户活跃度统计
CREATE MATERIALIZED VIEW mv_user_activity
TO user_activity_stats
AS SELECT
    toStartOfMinute(event_time) as minute,
    toStartOfHour(event_time) as hour,
    event_type,
    uniqState(user_id) as unique_users,
    sumState(1) as total_events,
    uniqStateIf(user_id, is_new_user = 1) as new_users,
    sumState(duration) as total_duration,
    avgState(duration) as avg_duration
FROM user_events
GROUP BY minute, hour, event_type;

-- 查询实时活跃用户
SELECT
    hour,
    event_type,
    uniqMerge(unique_users) as active_users,
    uniqMerge(new_users) as new_users,
    sumMerge(total_events) as total_events,
    avgMerge(avg_duration) as avg_duration
FROM user_activity_stats
WHERE hour >= toStartOfHour(now() - INTERVAL 24 HOUR)
GROUP BY hour, event_type
ORDER BY hour DESC, active_users DESC;
```

### 用户漏斗分析

```sql
-- 用户行为漏斗统计
CREATE MATERIALIZED VIEW mv_conversion_funnel
TO conversion_funnel_stats
AS SELECT
    toDate(event_time) as date,
    event_type,
    uniqState(user_id) as unique_users,
    arrayFilter(x -> x != 0, groupArray(CASE WHEN event_type = 'page_view' THEN 1
                                            WHEN event_type = 'click' THEN 2
                                            WHEN event_type = 'add_to_cart' THEN 3
                                            WHEN event_type = 'purchase' THEN 4 ELSE 0 END)) as funnel_steps
FROM user_events
WHERE event_type IN ('page_view', 'click', 'add_to_cart', 'purchase')
GROUP BY date, event_type;

-- 计算转化率
WITH funnel_data AS (
    SELECT date, event_type, uniqMerge(unique_users) as users
    FROM conversion_funnel_stats
    WHERE date >= today() - INTERVAL 7 DAY
    GROUP BY date, event_type
),
funnel_sequence AS (
    SELECT
        date,
        anyIf(users, event_type = 'page_view') as page_views,
        anyIf(users, event_type = 'click') as clicks,
        anyIf(users, event_type = 'add_to_cart') as carts,
        anyIf(users, event_type = 'purchase') as purchases
    FROM funnel_data
    GROUP BY date
)
SELECT
    date,
    page_views,
    clicks,
    carts,
    purchases,
    round(clicks / page_views * 100, 2) as click_rate,
    round(carts / clicks * 100, 2) as cart_rate,
    round(purchases / carts * 100, 2) as purchase_rate,
    round(purchases / page_views * 100, 2) as overall_conversion
FROM funnel_sequence
ORDER BY date DESC;
```

### 用户留存分析

```sql
-- 用户留存统计
CREATE TABLE user_retention (
    cohort_date Date,
    return_date Date,
    days_offset UInt8,
    user_count AggregateFunction(uniq, UInt64)
) ENGINE = AggregatingMergeTree()
PARTITION BY cohort_date
ORDER BY (cohort_date, return_date);

-- 计算留存数据
INSERT INTO user_retention
WITH user_first_day AS (
    SELECT
        min(toDate(event_time)) as cohort_date,
        user_id
    FROM user_events
    WHERE event_type = 'page_view'
      AND is_new_user = 1
    GROUP BY user_id
),
daily_active_users AS (
    SELECT
        toDate(event_time) as activity_date,
        user_id
    FROM user_events
    WHERE event_type = 'page_view'
    GROUP BY activity_date, user_id
)
SELECT
    fd.cohort_date,
    dau.activity_date as return_date,
    datediff(dau.activity_date, fd.cohort_date) as days_offset,
    uniqState(fd.user_id) as user_count
FROM user_first_day fd
JOIN daily_active_users dau ON fd.user_id = dau.user_id
WHERE dau.activity_date >= fd.cohort_date
  AND dau.activity_date < fd.cohort_date + INTERVAL 30 DAY;

-- 查询留存率矩阵
SELECT
    cohort_date,
    sumMerge(user_count) as cohort_size,
    arrayJoin(arrayMap(
        x -> round(x / cohort_size * 100, 1),
        arrayAggregate(
            x -> sumMerge(user_count),
            groupArray(days_offset)
        )
    )) as retention_rates
FROM user_retention
GROUP BY cohort_date
ORDER BY cohort_date DESC;
```

## 案例 2: 业务指标实时监控

### 业务指标表设计

```sql
-- 业务指标表
CREATE TABLE business_metrics (
    metric_time DateTime,
    metric_name String,
    metric_value Float64,
    metric_unit String,
    tags Array(String),
    metadata Tuple(String, String, Float64)
) ENGINE = SummingMergeTree()
PARTITION BY (toYYYYMM(metric_time), metric_name)
ORDER BY (metric_time, metric_name, tags)
TTL metric_time + INTERVAL 2 YEAR DELETE;

-- 指标别名表（用于名称映射）
CREATE TABLE metric_aliases (
    metric_name String,
    display_name String,
    description String,
    unit String
) ENGINE = ReplacingMergeTree()
ORDER BY metric_name;
```

### 实时指标计算

```sql
-- 实时收入统计
CREATE MATERIALIZED VIEW mv_revenue_metrics
TO business_metrics
AS SELECT
    now() as metric_time,
    'total_revenue' as metric_name,
    sum(revenue) as metric_value,
    'USD' as metric_unit,
    [] as tags,
    tuple('source', 'events', 0) as metadata
FROM user_events
WHERE event_type = 'purchase' AND revenue > 0;

-- 实时订单统计
CREATE MATERIALIZED VIEW mv_order_metrics
TO business_metrics
AS SELECT
    now() as metric_time,
    'total_orders' as metric_name,
    count() as metric_value,
    'count' as metric_unit,
    [] as tags,
    tuple('source', 'events', 0) as metadata
FROM user_events
WHERE event_type = 'purchase';

-- 按地区分组的指标
CREATE MATERIALIZED VIEW mv_regional_metrics
TO business_metrics
AS SELECT
    now() as metric_time,
    concat('regional_revenue_', country) as metric_name,
    sum(revenue) as metric_value,
    'USD' as metric_unit,
    [country] as tags,
    tuple('country', country, 0) as metadata
FROM user_events
WHERE event_type = 'purchase' AND revenue > 0
GROUP BY country;
```

### 指标查询分析

```sql
-- 多维度指标对比
SELECT
    metric_name,
    sum(metric_value) as total_value,
    arrayJoin(tags) as dimension,
    count() as data_points
FROM business_metrics
WHERE metric_time >= now() - INTERVAL 1 HOUR
  AND metric_name IN ('total_revenue', 'total_orders')
GROUP BY metric_name, dimension
ORDER BY total_value DESC;

-- 同比分析
WITH
current_metrics AS (
    SELECT
        metric_name,
        sum(metric_value) as current_value
    FROM business_metrics
    WHERE metric_time >= now() - INTERVAL 1 DAY
      AND metric_name = 'total_revenue'
    GROUP BY metric_name
),
previous_metrics AS (
    SELECT
        metric_name,
        sum(metric_value) as previous_value
    FROM business_metrics
    WHERE metric_time >= now() - INTERVAL 2 DAY
      AND metric_time < now() - INTERVAL 1 DAY
      AND metric_name = 'total_revenue'
    GROUP BY metric_name
)
SELECT
    current_metrics.current_value,
    previous_metrics.previous_value,
    round((current_metrics.current_value - previous_metrics.previous_value) /
          previous_metrics.previous_value * 100, 2) as growth_rate
FROM current_metrics, previous_metrics;
```

## 案例 3: 实时监控告警

### 监控指标表

```sql
-- 系统监控指标
CREATE TABLE system_metrics (
    timestamp DateTime,
    host String,
    metric_name String,
    metric_value Float64,
    tags Array(String)
) ENGINE = MergeTree()
PARTITION BY toYYYYMMDD(timestamp)
ORDER BY (timestamp, host, metric_name)
TTL timestamp + INTERVAL 30 DAY DELETE;

-- 告警规则表
CREATE TABLE alert_rules (
    rule_name String,
    metric_name String,
    condition String,
    threshold_value Float64,
    severity Enum8('info' = 1, 'warning' = 2, 'critical' = 3),
    enabled UInt8 DEFAULT 1
) ENGINE = ReplacingMergeTree()
ORDER BY rule_name;

-- 告警事件表
CREATE TABLE alert_events (
    alert_time DateTime,
    rule_name String,
    host String,
    metric_value Float64,
    threshold_value Float64,
    severity Enum8('info' = 1, 'warning' = 2, 'critical' = 3),
    message String,
    resolved_time DateTime DEFAULT toDateTime(0)
) ENGINE = MergeTree()
PARTITION BY toYYYYMM(alert_time)
ORDER BY (alert_time, rule_name, host)
TTL alert_time + INTERVAL 90 DAY DELETE;
```

### 实时告警检查

```sql
-- 检查告警条件
CREATE MATERIALIZED VIEW mv_alert_checks
TO alert_events
AS SELECT
    now() as alert_time,
    ar.rule_name,
    sm.host,
    sm.metric_value,
    ar.threshold_value,
    ar.severity,
    concat(
        'Alert: ', ar.rule_name,
        ' on ', sm.host,
        ' - ', sm.metric_name, ' = ', toString(sm.metric_value),
        ' (threshold: ', toString(ar.threshold_value), ')'
    ) as message
FROM system_metrics sm
JOIN alert_rules ar ON sm.metric_name = ar.metric_name
WHERE sm.timestamp >= now() - INTERVAL 5 MINUTE
  AND ar.enabled = 1
  AND (
      (ar.condition = 'gt' AND sm.metric_value > ar.threshold_value) OR
      (ar.condition = 'lt' AND sm.metric_value < ar.threshold_value) OR
      (ar.condition = 'eq' AND sm.metric_value = ar.threshold_value)
  )
  AND NOT EXISTS (
      SELECT 1 FROM alert_events ae
      WHERE ae.rule_name = ar.rule_name
        AND ae.host = sm.host
        AND ae.resolved_time = toDateTime(0)
  );

-- 查询活跃告警
SELECT
    alert_time,
    rule_name,
    host,
    metric_value,
    threshold_value,
    severity,
    message,
    dateDiff('second', alert_time, now()) as alert_duration_seconds
FROM alert_events
WHERE resolved_time = toDateTime(0)
ORDER BY alert_time DESC;
```

### 性能趋势分析

```sql
-- 系统性能趋势
SELECT
    host,
    toStartOfMinute(timestamp) as minute,
    avgIf(metric_value, metric_name = 'cpu_usage') as cpu_avg,
    maxIf(metric_value, metric_name = 'cpu_usage') as cpu_max,
    avgIf(metric_value, metric_name = 'memory_usage') as memory_avg,
    maxIf(metric_value, metric_name = 'memory_usage') as memory_max,
    avgIf(metric_value, metric_name = 'disk_usage') as disk_avg,
    sumIf(metric_value, metric_name = 'network_in') as network_in,
    sumIf(metric_value, metric_name = 'network_out') as network_out
FROM system_metrics
WHERE timestamp >= now() - INTERVAL 1 HOUR
  AND metric_name IN ('cpu_usage', 'memory_usage', 'disk_usage', 'network_in', 'network_out')
GROUP BY host, minute
ORDER BY minute DESC;
```

## 案例 4: 实时日志分析

### 日志表设计

```sql
-- 应用日志表
CREATE TABLE application_logs (
    timestamp DateTime,
    level Enum8('DEBUG' = 1, 'INFO' = 2, 'WARNING' = 3, 'ERROR' = 4, 'FATAL' = 5),
    service String,
    host String,
    message String,
    trace_id String,
    user_id Nullable(UInt64),
    request_id String,
    duration_ms UInt32,
    status_code UInt16,
    tags Array(String),
    raw_log String
) ENGINE = MergeTree()
PARTITION BY (toYYYYMM(timestamp), level)
ORDER BY (timestamp, service, level, trace_id)
TTL timestamp + INTERVAL 30 DAY DELETE
SETTINGS index_granularity = 8192;

-- 错误日志汇总
CREATE MATERIALIZED VIEW mv_error_summary
TO error_summary
AS SELECT
    toStartOfMinute(timestamp) as minute,
    service,
    host,
    level,
    count() as error_count,
    uniqState(trace_id) as unique_traces,
    sumState(duration_ms) as total_duration,
    avgState(duration_ms) as avg_duration,
    arrayFilter(x -> x != '', groupArray(message)) as sample_messages
FROM application_logs
WHERE level >= 3  -- WARNING, ERROR, FATAL
GROUP BY minute, service, host, level;
```

### 日志分析查询

```sql
-- 错误率趋势分析
SELECT
    minute,
    service,
    sumMerge(error_count) as total_errors,
    uniqMerge(unique_traces) as affected_traces,
    avgMerge(avg_duration) as avg_duration,
    arrayJoin(sample_messages) as sample_error
FROM error_summary
WHERE minute >= now() - INTERVAL 1 HOUR
GROUP BY minute, service
ORDER BY minute DESC, total_errors DESC;

-- 性能问题分析
SELECT
    service,
    host,
    round(avg(duration_ms), 2) as avg_duration,
    max(duration_ms) as max_duration,
    quantile(0.95)(duration_ms) as p95_duration,
    quantile(0.99)(duration_ms) as p99_duration,
    count() as request_count
FROM application_logs
WHERE timestamp >= now() - INTERVAL 1 HOUR
  AND level = 'INFO'
  AND duration_ms > 0
GROUP BY service, host
HAVING avg_duration > 1000  -- 平均响应时间超过1秒
ORDER BY avg_duration DESC;
```

## 案例 5: 实时仪表板查询

### 仪表板关键指标

```sql
-- 仪表板综合查询
WITH
-- 今日概览
today_stats AS (
    SELECT
        countDistinct(user_id) as today_users,
        count() as today_events,
        sumIf(revenue, event_type = 'purchase') as today_revenue,
        uniqIf(user_id, event_type = 'purchase') as today_customers
    FROM user_events
    WHERE event_date = today()
),
-- 同期对比
yesterday_stats AS (
    SELECT
        sumIf(revenue, event_type = 'purchase') as yesterday_revenue,
        uniqIf(user_id, event_type = 'purchase') as yesterday_customers
    FROM user_events
    WHERE event_date = today() - INTERVAL 1 DAY
),
-- 实时指标
realtime_stats AS (
    SELECT
        uniqMerge(unique_users) as active_users_now,
        sumMerge(total_events) as events_last_minute
    FROM user_activity_stats
    WHERE minute >= toStartOfMinute(now() - INTERVAL 1 MINUTE)
)
SELECT
    today_users,
    today_events,
    today_revenue,
    today_customers,
    round(today_revenue / yesterday_revenue * 100 - 100, 1) as revenue_growth_percent,
    active_users_now,
    events_last_minute
FROM today_stats, yesterday_stats, realtime_stats;

-- 热门页面分析
SELECT
    page_url,
    uniqExact(user_id) as unique_visitors,
    count() as page_views,
    avg(duration) as avg_duration_seconds
FROM user_events
WHERE event_type = 'page_view'
  AND event_time >= now() - INTERVAL 1 HOUR
GROUP BY page_url
ORDER BY unique_visitors DESC
LIMIT 10;

-- 地区分布分析
SELECT
    country,
    uniqExact(user_id) as unique_users,
    sumIf(revenue, event_type = 'purchase') as total_revenue,
    count() as total_events
FROM user_events
WHERE event_time >= now() - INTERVAL 24 HOUR
GROUP BY country
ORDER BY unique_users DESC;
```

通过这些实时分析案例，ClickHouse 可以很好地支持大规模数据的实时分析和监控需求，为业务决策提供及时的数据支撑。