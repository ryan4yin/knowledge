# ClickHouse 快速入门

本章节帮助你在 5 分钟内快速上手 ClickHouse，体验其强大的分析查询能力。

## 安装部署

### 方式 1: Docker（推荐）
```bash
# 启动 ClickHouse 服务
docker run -d --name clickhouse-server \
  -p 8123:8123 -p 9000:9000 \
  -e CLICKHOUSE_DB=analytics \
  -e CLICKHOUSE_USER=analyst \
  -e CLICKHOUSE_PASSWORD=secure123 \
  clickhouse/clickhouse-server:latest

# 等待服务启动（约10秒）
sleep 10

# 连接客户端
docker exec -it clickhouse-server clickhouse-client
```

### 方式 2: 系统包安装

#### Ubuntu/Debian
```bash
# 添加仓库
curl https://repo.clickhouse.com/CLICKHOUSE-KEY.GPG | sudo apt-key add -
echo "deb https://repo.clickhouse.com/deb/stable/ main/" | sudo tee /etc/apt/sources.list.d/clickhouse.list

# 安装
sudo apt-get update
sudo apt-get install -y clickhouse-server clickhouse-client

# 启动服务
sudo systemctl start clickhouse-server
sudo systemctl enable clickhouse-server

# 连接
clickhouse-client
```

### 方式 3: 在线体验
直接访问 [ClickHouse Play](https://play.clickhouse.com/) 即可体验，无需安装。

## 第一个查询

连接到 ClickHouse 后，执行以下查询：

```sql
-- 查看版本信息
SELECT version();

-- 查看当前数据库
SHOW DATABASES;

-- 创建测试数据库
CREATE DATABASE IF NOT EXISTS test;

-- 使用数据库
USE test;

-- 创建第一个表
CREATE TABLE events (
    event_id UInt64,
    user_id UInt32,
    event_type String,
    event_time DateTime,
    page_url String,
    ip_address String,
    browser String
) ENGINE = MergeTree()
PARTITION BY toYYYYMM(event_time)
ORDER BY (event_time, user_id, event_type);

-- 插入测试数据
INSERT INTO events VALUES
(1, 1001, 'page_view', '2023-12-25 10:00:00', '/home', '192.168.1.100', 'Chrome'),
(2, 1001, 'click', '2023-12-25 10:01:00', '/home', '192.168.1.100', 'Chrome'),
(3, 1002, 'page_view', '2023-12-25 10:02:00', '/products', '192.168.1.101', 'Firefox'),
(4, 1002, 'add_to_cart', '2023-12-25 10:03:00', '/products', '192.168.1.101', 'Firefox'),
(5, 1003, 'page_view', '2023-12-25 10:04:00', '/home', '192.168.1.102', 'Safari');

-- 查询数据
SELECT * FROM events ORDER BY event_time;

-- 统计事件类型
SELECT
    event_type,
    count() as event_count,
    countDistinct(user_id) as unique_users
FROM events
GROUP BY event_type
ORDER BY event_count DESC;
```

## 理解核心概念

### 1. 列式存储
```sql
-- 创建大型测试表
CREATE TABLE large_events (
    event_time DateTime,
    user_id UInt64,
    event_type Enum('page_view' = 1, 'click' = 2, 'add_to_cart' = 3, 'purchase' = 4),
    page_url String,
    ip_address IPv4,
    revenue Decimal(10,2)
) ENGINE = MergeTree()
PARTITION BY toYYYYMMDD(event_time)
ORDER BY (event_time, user_id);

-- 生成100万条测试数据
INSERT INTO large_events
SELECT
    now() - INTERVAL rand() % 30 DAY,
    rand() % 10000,
    ['page_view', 'click', 'add_to_cart', 'purchase'][rand() % 4 + 1],
    concat('https://example.com/page', toString(rand() % 1000)),
    IPv4StringToNum(concat('192.168.', toString(rand() % 255), '.', toString(rand() % 255))),
    round(rand() % 10000 / 100, 2)
FROM numbers(1000000);

-- 测试查询性能
SELECT
    toStartOfHour(event_time) as hour,
    count() as events,
    sumIf(revenue, event_type = 'purchase') as total_revenue
FROM large_events
WHERE event_time >= now() - INTERVAL 1 DAY
GROUP BY hour
ORDER BY hour DESC
LIMIT 10;
```

### 2. 物化视图 - 实时聚合
```sql
-- 创建物化视图实时统计
CREATE MATERIALIZED VIEW mv_hourly_stats
ENGINE = AggregatingMergeTree()
PARTITION BY toYYYYMMDD(hour)
ORDER BY hour
AS SELECT
    toStartOfHour(event_time) as hour,
    event_type,
    uniqState(user_id) as unique_users,
    sumState(1) as event_count,
    sumState(revenue) as total_revenue
FROM large_events
GROUP BY hour, event_type;

-- 查询实时统计
SELECT
    hour,
    event_type,
    uniqMerge(unique_users) as unique_users,
    sumMerge(event_count) as events,
    sumMerge(total_revenue) as revenue
FROM mv_hourly_stats
WHERE hour >= now() - INTERVAL 1 DAY
GROUP BY hour, event_type
ORDER BY hour DESC, events DESC
LIMIT 10;
```

### 3. 实时插入性能测试
```sql
-- 批量插入测试
INSERT INTO large_events
SELECT
    now() as event_time,
    number as user_id,
    'page_view' as event_type,
    '/test-page' as page_url,
    IPv4StringToNum('127.0.0.1') as ip_address,
    0 as revenue
FROM numbers(100000);

-- 检查插入结果
SELECT count() FROM large_events;
```

## 实用查询示例

### 1. 时间序列分析
```sql
-- 每小时活跃用户数
SELECT
    toStartOfHour(event_time) as hour,
    uniqExact(user_id) as active_users
FROM large_events
WHERE event_time >= now() - INTERVAL 7 DAY
GROUP BY hour
ORDER BY hour DESC
LIMIT 24;
```

### 2. 漏斗分析
```sql
-- 用户行为漏斗
SELECT
    event_type,
    uniqExact(user_id) as users,
    arrayJoin(groupArray(user_id)) as user_list
FROM (
    SELECT
        event_type,
        user_id,
        row_number() OVER (PARTITION BY user_id ORDER BY event_time) as rn
    FROM large_events
    WHERE event_type IN ('page_view', 'add_to_cart', 'purchase')
)
GROUP BY event_type
ORDER BY
    CASE event_type
        WHEN 'page_view' THEN 1
        WHEN 'add_to_cart' THEN 2
        WHEN 'purchase' THEN 3
    END;
```

### 3. 同期对比分析
```sql
-- 本月 vs 上月对比
WITH
current_month AS (
    SELECT
        countDistinct(user_id) as users,
        count() as events
    FROM large_events
    WHERE event_time >= now() - INTERVAL 1 MONTH
),
last_month AS (
    SELECT
        countDistinct(user_id) as users,
        count() as events
    FROM large_events
    WHERE event_time >= now() - INTERVAL 2 MONTH
        AND event_time < now() - INTERVAL 1 MONTH
)
SELECT
    current_month.users as current_users,
    last_month.users as last_users,
    round((current_month.users - last_month.users) / last_month.users * 100, 2) as growth_rate
FROM current_month, last_month;
```

## 性能测试

```sql
-- 测试复杂查询性能
EXPLAIN PIPELINE
SELECT
    toYYYYMM(event_time) as month,
    event_type,
    quantile(0.50)(user_id) as p50_user,
    quantile(0.95)(user_id) as p95_user,
    sum(revenue) as total_revenue
FROM large_events
WHERE event_time >= now() - INTERVAL 1 YEAR
GROUP BY month, event_type
ORDER BY month DESC, total_revenue DESC;

-- 查看执行计划
EXPLAIN SYNTAX
SELECT
    event_type,
    sumIf(revenue, event_type = 'purchase') as purchase_revenue,
    uniqIf(user_id, event_type = 'purchase') as unique_customers
FROM large_events
GROUP BY event_type;
```

## 系统监控查询

```sql
-- 查看系统表
SHOW TABLES FROM system;

-- 监控查询性能
SELECT
    query,
    read_rows,
    read_bytes,
    result_rows,
    result_bytes,
    memory_usage,
    elapsed_seconds
FROM system.query_log
WHERE event_date = today()
  AND type = 'QueryFinish'
ORDER BY elapsed_seconds DESC
LIMIT 10;

-- 查看表大小和分区信息
SELECT
    database,
    table,
    formatReadableSize(sum(data_compressed_bytes) AS compressed) as compressed_size,
    formatReadableSize(sum(data_uncompressed_bytes) AS uncompressed) as uncompressed_size,
    round(sum(data_uncompressed_bytes) / sum(data_compressed_bytes), 2) as ratio,
    count() as parts_count
FROM system.parts
WHERE active = 1
GROUP BY database, table
ORDER BY sum(data_uncompressed_bytes) DESC;
```

## 下一步

恭喜！你已经完成了 ClickHouse 快速入门。接下来可以：

1. **深入学习架构设计**: 了解 [架构与模式设计](../schema-design/README.md)
2. **掌握 MergeTree**: 深入学习 [MergeTree 深度解析](../merge-tree-engine/README.md)
3. **优化性能**: 学习 [性能调优实战](../performance-tuning/README.md)
4. **实战案例**: 查看 [实时分析案例](../realtime-analytics/README.md)

## 常见问题

### Q: ClickHouse 和 PostgreSQL 有什么区别？
A: ClickHouse 是 OLAP 数据库，适合分析查询；PostgreSQL 是 OLTP 数据库，适合事务处理。

### Q: 什么时候应该使用 ClickHouse？
A: 当你有大量数据需要实时分析、报表生成、数据聚合时，ClickHouse 是理想选择。

### Q: 如何选择分区键？
A: 通常使用时间字段作为分区键，按天、周或月分区，便于数据管理和查询优化。

### Q: ClickHouse 支持事务吗？
A: ClickHouse 不支持传统事务，专注于高吞吐的写入和快速分析查询。