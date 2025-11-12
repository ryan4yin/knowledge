# ClickHouse 监控与运维

ClickHouse 集群的稳定运行需要完善的监控体系和运维工具。本章节介绍 ClickHouse 的监控指标、运维工具和最佳实践。

## 核心监控指标

### 系统性能指标

```sql
-- 查看系统指标概览
SELECT
    name,
    value,
    formatReadableSize(value) as readable_value,
    description
FROM system.metrics
WHERE name IN (
    'Memory',
    'MemoryPeak',
    'MemoryTracking',
    'DiskSpace',
    'DiskSpaceReserved',
    'NetworkReceive',
    'NetworkSend'
);

-- 内存使用情况
SELECT
    formatReadableSize(value) as memory_usage,
    name
FROM system.metrics
WHERE name LIKE '%memory%' OR name LIKE '%Memory%'
ORDER BY value DESC;

-- 磁盘使用情况
SELECT
    formatReadableSize(value) as disk_usage,
    name
FROM system.metrics
WHERE name LIKE '%disk%' OR name LIKE '%Disk%'
ORDER BY value DESC;
```

### 查询性能指标

```sql
-- 慢查询监控
SELECT
    query,
    duration_seconds,
    memory_usage,
    read_rows,
    read_bytes,
    result_rows,
    result_bytes,
    thread_ids,
    user,
    address,
    formatReadableSize(memory_usage) as memory_readable,
    formatReadableSize(read_bytes) as read_readable,
    formatReadableSize(result_bytes) as result_readable
FROM system.query_log
WHERE type = 'QueryFinish'
  AND duration_seconds > 1
  AND event_date = today()
ORDER BY duration_seconds DESC
LIMIT 20;

-- 最消耗内存的查询
SELECT
    query,
    duration_seconds,
    formatReadableSize(memory_usage) as memory_usage,
    read_rows,
    result_rows,
    user
FROM system.query_log
WHERE type = 'QueryFinish'
  AND memory_usage > 100000000  -- 100MB
  AND event_date = today()
ORDER BY memory_usage DESC
LIMIT 10;

-- 查询吞吐量统计
SELECT
    toStartOfMinute(event_time) as minute,
    count() as query_count,
    avg(duration_seconds) as avg_duration,
    max(duration_seconds) as max_duration,
    sum(read_bytes) as total_read,
    sum(result_bytes) as total_result
FROM system.query_log
WHERE type = 'QueryFinish'
  AND event_date = today()
GROUP BY minute
ORDER BY minute DESC
LIMIT 24;
```

### 表状态监控

```sql
-- 表大小和分区状态
SELECT
    database,
    table,
    formatReadableSize(sum(bytes)) as total_size,
    formatReadableSize(sum(data_uncompressed_bytes)) as uncompressed_size,
    sum(data_compressed_bytes) / sum(data_uncompressed_bytes) * 100 as compression_ratio,
    sum(rows) as total_rows,
    count() as part_count,
    countIf(active = 1) as active_parts,
    countIf(active = 0) as inactive_parts
FROM system.parts
GROUP BY database, table
ORDER BY total_size DESC;

-- 分区健康状态
SELECT
    database,
    table,
    partition,
    sum(rows) as rows,
    formatReadableSize(sum(bytes)) as size,
    count() as parts_count,
    max(modification_time) as last_modified
FROM system.parts
WHERE active = 1
GROUP BY database, table, partition
ORDER BY partition DESC, database, table;

-- 复制状态监控
SELECT
    database,
    table,
    is_leader,
    absolute_delay,
    queue_size,
    log_pointer,
    total_replicas,
    active_replicas,
    is_readonly,
    is_session_expired
FROM system.replicas
WHERE absolute_delay > 0
ORDER BY absolute_delay DESC;
```

## 集群监控

### 集群状态监控

```sql
-- 集群节点状态
SELECT
    cluster,
    shard_num,
    replica_num,
    host_name,
    port,
    uptime,
    errors_count,
    last_error,
    last_error_time
FROM system.clusters
WHERE cluster = 'production_cluster'
ORDER BY shard_num, replica_num;

-- 各节点负载情况
SELECT
    shard_num,
    replica_num,
    host_name,
    port,
    avg(duration_seconds) as avg_query_time,
    count() as query_count,
    sum(read_rows) as total_reads,
    sum(result_rows) as total_results
FROM cluster('production_cluster', system.processes)
GROUP BY shard_num, replica_num, host_name, port
ORDER BY query_count DESC;

-- 数据分布情况
SELECT
    shard_num,
    host_name,
    formatReadableSize(sum(bytes)) as total_size,
    sum(rows) as total_rows,
    count() as table_count
FROM cluster('production_cluster', system.parts)
WHERE active = 1
GROUP BY shard_num, host_name
ORDER BY shard_num, host_name;
```

### 分布式查询监控

```sql
-- 分布式查询执行统计
SELECT
    cluster,
    query,
    min(duration_seconds) as min_duration,
    max(duration_seconds) as max_duration,
    avg(duration_seconds) as avg_duration,
    sum(read_rows) as total_reads,
    sum(result_rows) as total_results
FROM system.query_log
WHERE cluster IS NOT NULL
  AND event_date = today()
GROUP BY cluster, query
ORDER BY avg_duration DESC;

-- 分片查询延迟
SELECT
    shard_num,
    avg(duration_seconds) as avg_duration,
    count() as query_count
FROM cluster('production_cluster', system.query_log)
WHERE type = 'QueryFinish'
  AND event_date = today()
GROUP BY shard_num
ORDER BY avg_duration DESC;
```

## 实时监控仪表板

### 关键指标仪表板

```sql
-- 实时仪表板查询
WITH
-- 当前活跃查询数
active_queries AS (
    SELECT count() as count
    FROM system.processes
),

-- 最近1小时查询统计
hour_stats AS (
    SELECT
        count() as total_queries,
        avg(duration_seconds) as avg_duration,
        sum(read_bytes) as total_read,
        sum(result_bytes) as total_result
    FROM system.query_log
    WHERE type = 'QueryFinish'
      AND event_time >= now() - INTERVAL 1 HOUR
),

-- 内存使用情况
memory_stats AS (
    SELECT
        value as memory_used,
        description
    FROM system.metrics
    WHERE name = 'Memory'
),

-- 磁盘使用情况
disk_stats AS (
    SELECT
        value as disk_used,
        description
    FROM system.metrics
    WHERE name = 'DiskSpace'
)
SELECT
    active_queries.count as active_queries,
    hour_stats.total_queries as hourly_queries,
    round(hour_stats.avg_duration, 2) as avg_query_duration,
    formatReadableSize(memory_stats.memory_used) as memory_used,
    formatReadableSize(disk_stats.disk_used) as disk_used,
    formatReadableSize(hour_stats.total_read) as hourly_read,
    formatReadableSize(hour_stats.total_result) as hourly_result
FROM active_queries, hour_stats, memory_stats, disk_stats;
```

### 查询性能监控

```sql
-- 查询性能热力图
SELECT
    hour_of_day,
    user,
    count() as query_count,
    avg(duration_seconds) as avg_duration,
    max(duration_seconds) as max_duration,
    sum(read_bytes) as total_read
FROM (
    SELECT
        toHour(event_time) as hour_of_day,
        user,
        duration_seconds,
        read_bytes
    FROM system.query_log
    WHERE type = 'QueryFinish'
      AND event_date = today()
) t
GROUP BY hour_of_day, user
ORDER BY hour_of_day, user;

-- 错误查询监控
SELECT
    error_time,
    query,
    exception,
    user,
    stack_trace
FROM system.text_log
WHERE level = 'Error'
  AND event_date = today()
ORDER BY error_time DESC
LIMIT 10;
```

## 监控告警

### 告警规则配置

```sql
-- 创建告警规则表
CREATE TABLE alert_rules (
    rule_name String,
    metric_name String,
    condition String,
    threshold_value Float64,
    severity Enum8('info' = 1, 'warning' = 2, 'critical' = 3),
    enabled UInt8 DEFAULT 1,
    description String
) ENGINE = ReplacingMergeTree()
ORDER BY rule_name;

-- 插入告警规则
INSERT INTO alert_rules VALUES
('high_query_duration', 'query_duration', 'gt', 5.0, 'warning', 1, '查询执行时间超过5秒'),
('high_memory_usage', 'memory_usage', 'gt', 0.8, 'critical', 1, '内存使用率超过80%'),
('slow_replication', 'replication_delay', 'gt', 300, 'critical', 1, '复制延迟超过5分钟'),
('disk_usage_high', 'disk_usage', 'gt', 0.9, 'critical', 1, '磁盘使用率超过90%');

-- 告警检查查询
CREATE MATERIALIZED VIEW mv_alert_monitoring
TO alert_events
AS SELECT
    now() as alert_time,
    ar.rule_name,
    ar.metric_name,
    ar.severity,
    concat(
        'Alert: ', ar.rule_name,
        ' - ', ar.description,
        ', Current value: ', toString(current_value),
        ', Threshold: ', toString(ar.threshold_value)
    ) as message
FROM (
    -- 查询持续时间告警
    SELECT
        'query_duration' as metric_name,
        max(duration_seconds) as current_value,
        max(user) as context
    FROM system.processes
    WHERE elapsed_seconds > 5

    UNION ALL

    -- 内存使用率告警
    SELECT
        'memory_usage' as metric_name,
        value / (SELECT value FROM system.metrics WHERE name = 'Memory') as current_value,
        'system' as context
    FROM system.metrics
    WHERE name = 'MemoryUsage'

    UNION ALL

    -- 复制延迟告警
    SELECT
        'replication_delay' as metric_name,
        max(absolute_delay) as current_value,
        table_name as context
    FROM system.replicas
    WHERE absolute_delay > 0
) current_metrics
JOIN alert_rules ar ON current_metrics.metric_name = ar.metric_name
WHERE ar.enabled = 1
  AND (
      (ar.condition = 'gt' AND current_metrics.current_value > ar.threshold_value) OR
      (ar.condition = 'lt' AND current_metrics.current_value < ar.threshold_value) OR
      (ar.condition = 'eq' AND current_metrics.current_value = ar.threshold_value)
  );
```

### 自动化监控脚本

```bash
#!/bin/bash
# clickhouse_monitor.sh - 自动化监控脚本

CLICKHOUSE_HOST="localhost"
ALERT_EMAIL="admin@example.com"
LOG_FILE="/var/log/clickhouse_monitor.log"

# 检查 ClickHouse 服务状态
check_service_status() {
    echo "$(date): Checking ClickHouse service status..." >> $LOG_FILE

    if ! pgrep -f clickhouse-server > /dev/null; then
        echo "ALERT: ClickHouse service is not running!" >> $LOG_FILE
        send_alert "ClickHouse Service Down" "ClickHouse service is not running on $CLICKHOUSE_HOST"
        return 1
    fi

    echo "Service status: OK" >> $LOG_FILE
    return 0
}

# 检查集群状态
check_cluster_status() {
    echo "$(date): Checking cluster status..." >> $LOG_FILE

    result=$(clickhouse-client --host $CLICKHOUSE_HOST --query "
        SELECT COUNT(*)
        FROM system.clusters
        WHERE errors_count > 0
    ")

    if [ "$result" -gt 0 ]; then
        echo "ALERT: Cluster has errors" >> $LOG_FILE
        send_alert "Cluster Error" "ClickHouse cluster has $result errors"
    fi
}

# 检查查询性能
check_query_performance() {
    echo "$(date): Checking query performance..." >> $LOG_FILE

    slow_queries=$(clickhouse-client --host $CLICKHOUSE_HOST --query "
        SELECT COUNT(*)
        FROM system.query_log
        WHERE type = 'QueryFinish'
          AND duration_seconds > 10
          AND event_time >= now() - INTERVAL 1 HOUR
    ")

    if [ "$slow_queries" -gt 10 ]; then
        echo "ALERT: $slow_queries slow queries in last hour" >> $LOG_FILE
        send_alert "Query Performance Issue" "Found $slow_queries queries taking more than 10 seconds"
    fi
}

# 检查磁盘空间
check_disk_space() {
    echo "$(date): Checking disk space..." >> $LOG_FILE

    disk_usage=$(clickhouse-client --host $CLICKHOUSE_HOST --query "
        SELECT round(value / (SELECT value FROM system.metrics WHERE name = 'DiskSpace') * 100, 2)
        FROM system.metrics
        WHERE name = 'DiskSpaceUsage'
    ")

    if (( $(echo "$disk_usage > 90" | bc -l) )); then
        echo "ALERT: Disk usage is ${disk_usage}%" >> $LOG_FILE
        send_alert "Disk Space Critical" "Disk usage is ${disk_usage}%, above 90% threshold"
    fi
}

# 发送告警
send_alert() {
    local subject=$1
    local message=$2
    echo "$message" | mail -s "$subject" $ALERT_EMAIL
}

# 主监控循环
main() {
    echo "Starting ClickHouse monitoring..." >> $LOG_FILE

    check_service_status
    check_cluster_status
    check_query_performance
    check_disk_space

    echo "Monitoring completed at $(date)" >> $LOG_FILE
}

main
```

## Grafana 仪表板

### 系统性能仪表板配置

```json
{
  "dashboard": {
    "title": "ClickHouse Cluster Monitoring",
    "panels": [
      {
        "title": "Active Queries",
        "type": "stat",
        "targets": [
          {
            "expr": "SELECT count() FROM system.processes",
            "refId": "A"
          }
        ]
      },
      {
        "title": "Query Duration",
        "type": "graph",
        "targets": [
          {
            "expr": "SELECT avg(duration_seconds) FROM system.query_log WHERE type = 'QueryFinish' AND event_time >= now() - INTERVAL 1 HOUR GROUP BY minute(event_time)",
            "refId": "B"
          }
        ]
      },
      {
        "title": "Memory Usage",
        "type": "gauge",
        "targets": [
          {
            "expr": "SELECT value / (SELECT value FROM system.metrics WHERE name = 'Memory') * 100 FROM system.metrics WHERE name = 'MemoryUsage'",
            "refId": "C"
          }
        ]
      },
      {
        "title": "Replication Delay",
        "type": "table",
        "targets": [
          {
            "expr": "SELECT table, absolute_delay FROM system.replicas WHERE absolute_delay > 0 ORDER BY absolute_delay DESC",
            "refId": "D"
          }
        ]
      }
    ]
  }
}
```

### 自定义监控指标

```sql
-- 创建自定义监控指标表
CREATE TABLE monitoring_metrics (
    timestamp DateTime,
    metric_name String,
    metric_value Float64,
    tags Array(String)
) ENGINE = SummingMergeTree()
PARTITION BY toYYYYMMDD(timestamp)
ORDER BY (timestamp, metric_name, tags);

-- 创建监控指标的物化视图
CREATE MATERIALIZED VIEW mv_system_metrics
TO monitoring_metrics
AS SELECT
    now() as timestamp,
    name as metric_name,
    value as metric_value,
    arrayExtract(groupArray(splitByChar(' ', description)), 1) as tags
FROM system.metrics
WHERE value > 0
GROUP BY name, value;

-- 业务指标监控
CREATE MATERIALIZED VIEW mv_business_metrics
TO monitoring_metrics
AS SELECT
    now() as timestamp,
    concat('active_users_', toStartOfHour(event_time)) as metric_name,
    uniqExact(user_id) as metric_value,
    ['realtime', 'hourly'] as tags
FROM events
WHERE event_time >= now() - INTERVAL 1 HOUR
GROUP BY toStartOfHour(event_time);
```

## 日志分析

### 查询日志分析

```sql
-- 查询模式分析
SELECT
    extract(pattern FROM query, '(SELECT|INSERT|CREATE|ALTER|DROP)') as query_type,
    count() as query_count,
    avg(duration_seconds) as avg_duration,
    max(duration_seconds) as max_duration,
    sum(read_bytes) as total_read
FROM system.query_log
WHERE type = 'QueryFinish'
  AND event_date = today()
GROUP BY query_type
ORDER BY query_count DESC;

-- 用户查询分析
SELECT
    user,
    count() as query_count,
    avg(duration_seconds) as avg_duration,
    sum(read_bytes) as total_read,
    arrayDistinct(extract(pattern FROM query, 'FROM (\w+)')) as tables_accessed
FROM system.query_log
WHERE type = 'QueryFinish'
  AND event_date = today()
GROUP BY user
ORDER BY query_count DESC;

-- 错误日志分析
SELECT
    toStartOfMinute(event_time) as minute,
    level,
    count() as error_count
FROM system.text_log
WHERE level IN ('Error', 'Fatal')
  AND event_date = today()
GROUP BY minute, level
ORDER BY minute DESC;
```

通过完善的监控体系，可以及时发现和解决 ClickHouse 集群的问题，确保系统的稳定运行和高效服务。