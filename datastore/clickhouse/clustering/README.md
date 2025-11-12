# ClickHouse 集群管理

ClickHouse 的分布式架构是其处理 PB 级数据的关键。本章节详细介绍 ClickHouse 集群的部署、管理、高可用和性能优化。

## 集群架构概览

### 分布式架构组件

```
ClickHouse 集群架构
┌─────────────────────────────────────────────────────────────┐
│                    Load Balancer                          │
│                   (nginx/haproxy)                           │
└─────────────────┬───────────────────────┬─────────────────┘
                  │                       │
        ┌─────────▼─────────┐     ┌─────────▼─────────┐
        │   Shard 1          │     │   Shard 2          │
        │  ┌─────────┐        │     │  ┌─────────┐        │
        │  │Replica 1│        │     │  │Replica 3│        │
        │  └─────────┘        │     │  └─────────┘        │
        │  ┌─────────┐        │     │  ┌─────────┐        │
        │  │Replica 2│        │     │  │Replica 4│        │
        │  └─────────┘        │     │  └─────────┘        │
        └─────────────────────┘     └─────────────────────┘
                  │                       │
        ┌─────────▼─────────┐     ┌─────────▼─────────┐
        │    ZooKeeper      │     │   ClickHouse      │
        │   (coordination)  │     │   Metastore        │
        └───────────────────┘     └───────────────────┘
```

### 核心概念

- **分片 (Sharding)**: 数据水平分布
- **副本 (Replication)**: 数据冗余备份
- **集群 (Cluster)**: 多个分片的集合
- **副本组 (Replica Group)**: 同一分区的多个副本

## ZooKeeper 配置

### 基础配置

```xml
<!-- /etc/clickhouse-server/config.xml -->
<zookeeper>
    <node>
        <host>zk1.example.com</host>
        <port>2181</port>
    </node>
    <node>
        <host>zk2.example.com</host>
        <port>2181</port>
    </node>
    <node>
        <host>zk3.example.com</host>
        <port>2181</port>
    </node>
</zookeeper>

<!-- 集群定义 -->
<remote_servers>
    <production_cluster>
        <shard>
            <replica>
                <host>ch-node-1.example.com</host>
                <port>9000</port>
                <user>default</user>
                <password></password>
            </replica>
            <replica>
                <host>ch-node-2.example.com</host>
                <port>9000</port>
                <user>default</user>
                <password></password>
            </replica>
        </shard>
        <shard>
            <replica>
                <host>ch-node-3.example.com</host>
                <port>9000</port>
                <user>default</user>
                <password></password>
            </replica>
            <replica>
                <host>ch-node-4.example.com</host>
                <port>9000</port>
                <user>default</user>
                <password></password>
            </replica>
        </shard>
    </production_cluster>
</remote_servers>
```

### 高可用 ZooKeeper

```xml
<!-- 高可用 ZooKeeper 配置 -->
<zookeeper>
    <node index="1">
        <host>zk1.example.com</host>
        <port>2181</port>
        <user>zookeeper</user>
        <password>zk_password</password>
    </node>
    <node index="2">
        <host>zk2.example.com</host>
        <port>2181</port>
        <user>zookeeper</user>
        <password>zk_password</password>
    </node>
    <node index="3">
        <host>zk3.example.com</host>
        <port>2181</port>
        <user>zookeeper</user>
        <password>zk_password</password>
    </node>
</zookeeper>
```

## 分片策略

### 哈希分片

```sql
-- 基于用户ID的哈希分片
CREATE TABLE distributed_events ON CLUSTER production_cluster
(
    event_time DateTime,
    user_id UInt64,
    event_type String
) ENGINE = Distributed(
    production_cluster,  -- 集群名称
    default,           -- 本地表的数据库
    events_local,       -- 本地表名
    cityHash64(user_id) -- 分片键：用户ID哈希
);

-- 查看分片分布
SELECT
    shard_num,
    shard_value,
    host,
    port
FROM cluster('production_cluster', system.parts)
WHERE table = 'distributed_events';
```

### 自定义分片

```sql
-- 基于时间的分片
CREATE TABLE time_sharded_logs ON CLUSTER production_cluster
(
    timestamp DateTime,
    log_level String,
    message String
) ENGINE = Distributed(
    production_cluster,
    default,
    logs_local,
    XXHash64(toString(toYYYYMM(timestamp)))  -- 按月份分片
);

-- 按地区分片
CREATE TABLE regional_events ON CLUSTER production_cluster
(
    event_time DateTime,
    user_id UInt64,
    region String,
    event_data String
) ENGINE = Distributed(
    production_cluster,
    default,
    regional_events_local,
    murmurHash3_32(region)  -- 按地区分片
);
```

## 副本配置

### ReplicatedMergeTree 副本

```sql
-- 创建副本表
CREATE TABLE events_local ON CLUSTER production_cluster
(
    event_time DateTime,
    user_id UInt64,
    event_type String
) ENGINE = ReplicatedMergeTree(
    '/clickhouse/tables/{shard}/events',  -- ZK路径模板
    '{replica}'                          -- 副本标识模板
)
PARTITION BY toYYYYMM(event_time)
ORDER BY (event_time, user_id);

-- 在不同节点上的表结构相同，但副本标识不同
-- node1: replica = 'replica1'
-- node2: replica = 'replica2'
```

### 多副本策略

```xml
<!-- 多副本集群配置 -->
<remote_servers>
    <production_cluster>
        <shard>
            <internal_replication>false</internal_replication>  -- 允许跨分片复制
            <replica>
                <host>ch-node-1.example.com</host>
                <port>9000</port>
                <weight>1</weight>  <!-- 权重 -->
                <default_database>default</default_database>
            </replica>
            <replica>
                <host>ch-node-2.example.com</host>
                <port>9000</port>
                <weight>1</weight>
            </replica>
        </shard>
        <shard>
            <replica>
                <host>ch-node-3.example.com</host>
                <port>9000</port>
                <weight>2</weight>  <!-- 权重更高 -->
            </replica>
            <replica>
                <host>ch-node-4.example.com</host>
                <port>9000</port>
                <weight>2</weight>
            </replica>
        </shard>
    </production_cluster>
</remote_servers>
```

## 分布式表引擎

### 基础 Distributed 表

```sql
-- 创建分布式表
CREATE TABLE distributed_table ON CLUSTER production_cluster
(
    id UInt64,
    timestamp DateTime,
    value Float64
) ENGINE = Distributed(
    production_cluster,  -- 集群名
    default,           -- 数据库
    local_table,       -- 本地表
    rand()             -- 分片键（随机）
);

-- 查询分布式表（会查询所有分片）
SELECT id, timestamp, value FROM distributed_table
WHERE timestamp >= now() - INTERVAL 1 DAY;

-- 查看查询执行计划
EXPLAIN PIPELINE
SELECT count() FROM distributed_table
WHERE timestamp >= now() - INTERVAL 1 DAY;
```

### 高级分布式配置

```sql
-- 带权重的分布式表
CREATE TABLE weighted_distributed ON CLUSTER production_cluster
(
    event_time DateTime,
    user_id UInt64,
    event_type String
) ENGINE = Distributed(
    production_cluster,
    default,
    events_local,
    cityHash64(user_id),
    sharding_key,         -- 分片键
    policy_name = 'round_robin',  -- 分布策略
    weight_expr = 'rand()'        -- 权重表达式
);

-- 分布策略配置
<distributed_ddl>
    <!-- 分布策略 -->
    <round_robin>
        <shards_weight>
            <weight_shard>0.5</weight_shard>
            <weight_replica>0.5</weight_replica>
        </shards_weight>
    </round_robin>
</distributed_ddl>
```

## 高可用和故障转移

### 主从切换

```sql
-- 检查副本状态
SELECT
    table,
    is_leader,
    absolute_delay,
    queue_size,
    log_pointer,
    total_replicas,
    active_replicas
FROM system.replicas
WHERE table = 'events_local';

-- 手动切换主节点
SYSTEM RESTART REPLICA events_local;

-- 检查副本延迟
SELECT
    host,
    port,
    absolute_delay,
    queue_size,
    is_leader
FROM system.replicas
WHERE table = 'events_local'
ORDER BY absolute_delay DESC;
```

### 自动故障转移

```xml
<!-- 故障转移配置 -->
<replicated_merge_tree>
    <!-- 副本同步配置 -->
    <replicated_fetches_part_count>4</replicated_fetches_part_count>
    <replicated_max_parallel_fetches>8</replicated_max_parallel_fetches>

    <!-- 任务队列配置 -->
    <replicated_deduplication_window>10000</replicated_deduplication_window>
    <replicated_max_block_size>1048576</replicated_max_block_size>

    <!-- 数据同步配置 -->
    <remote_fs_method>hdfs</remote_fs_method>
    <remote_fs_buffer_size>1048576</remote_fs_buffer_size>
</replicated_merge_tree>
```

## 集群监控

### 集群状态监控

```sql
-- 查看集群状态
SELECT
    cluster,
    shard_num,
    replica_num,
    host,
    port,
    user,
    errors_count,
    uptime
FROM system.clusters;

-- 查看分片状态
SELECT
    cluster,
    shard_num,
    replica_num,
    host_name,
    port,
    error_count,
    uptime
FROM system.clusters
WHERE cluster = 'production_cluster';

-- 查看表在各个节点的分布
SELECT
    cluster,
    shard_num,
    replica_num,
    database,
    table,
    bytes_on_disk,
    parts_count
FROM cluster('production_cluster', system.parts)
WHERE active = 1
ORDER BY cluster, shard_num, replica_num;
```

### 性能监控

```sql
-- 集群查询性能监控
SELECT
    cluster,
    query_type,
    avg(duration) as avg_duration,
    max(duration) as max_duration,
    count() as query_count,
    sum(read_rows) as total_rows
FROM cluster('production_cluster', system.query_log)
WHERE event_date = today()
GROUP BY cluster, query_type
ORDER BY avg_duration DESC;

-- 各分片的负载分布
SELECT
    shard_num,
    host,
    avg(elapsed_seconds) as avg_duration,
    count() as query_count,
    sum(memory_usage) as total_memory
FROM cluster('production_cluster', system.processes)
GROUP BY shard_num, host
ORDER BY query_count DESC;
```

## 数据分布和均衡

### 数据分布检查

```sql
-- 检查各分片的数据分布
SELECT
    shard_num,
    host,
    formatReadableSize(sum(bytes)) as size,
    sum(rows) as rows,
    count() as tables
FROM cluster('production_cluster', system.parts)
WHERE active = 1
GROUP BY shard_num, host
ORDER BY shard_num, host;

-- 检查分片键分布
SELECT
    shard_num,
    count() as record_count,
    min(user_id) as min_user_id,
    max(user_id) as max_user_id
FROM cluster('production_cluster', events)
GROUP BY shard_num
ORDER BY shard_num;
```

### 数据重分布

```sql
-- 重新平衡分片数据
ALTER TABLE distributed_events ON CLUSTER production_cluster
RESHARDING PARTITION '202312';

-- 手动移动分区到特定分片
ALTER TABLE distributed_events ON CLUSTER production_cluster
MOVE PARTITION '202312' TO SHARD 1;

-- 创建均衡的分布式表
CREATE TABLE balanced_events ON CLUSTER production_cluster
(
    event_time DateTime,
    user_id UInt64,
    event_type String
) ENGINE = Distributed(
    production_cluster,
    default,
    events_local,
    cityHash64(user_id),
    policy_name = 'balanced'  -- 使用平衡策略
);
```

## 集群维护

### 滚动升级

```bash
#!/bin/bash
# 滚动升级脚本
CLUSTER_NODES=("ch-node-1" "ch-node-2" "ch-node-3" "ch-node-4")

for node in "${CLUSTER_NODES[@]}"; do
    echo "Upgrading $node..."

    # 1. 从集群中移除节点
    ssh $node "systemctl stop clickhouse-server"

    # 2. 备份数据
    ssh $node "cp -r /var/lib/clickhouse /backup/$(date +%Y%m%d)"

    # 3. 升级软件
    ssh $node "yum update clickhouse-server -y"

    # 4. 启动服务
    ssh $node "systemctl start clickhouse-server"

    # 5. 检查节点状态
    ssh $node "clickhouse-client --query 'SELECT version()'"

    # 6. 重新加入集群（ZooKeeper 会自动同步）

    echo "Waiting for data sync..."
    sleep 60
done
```

### 数据同步检查

```sql
-- 检查副本同步状态
SELECT
    host,
    absolute_delay,
    queue_size,
    log_pointer,
    total_replicas,
    active_replicas,
    is_leader
FROM system.replicas
WHERE absolute_delay > 0
ORDER BY absolute_delay DESC;

-- 检查 ZooKeeper 集群状态
SELECT
    name,
    value
FROM system.zookeeper
WHERE path = '/';
```

## 安全配置

### 集群间认证

```xml
<!-- 集群间认证配置 -->
<remote_servers>
    <production_cluster>
        <secure_connection>yes</secure_connection>
        <require_ssl>yes</require_ssl>

        <shard>
            <replica>
                <host>ch-node-1.example.com</host>
                <port>9440</port>  <!-- SSL 端口 -->
                <secure>1</secure>
                <tcp_port_secure>9440</tcp_port_secure>
                <user>cluster_user</user>
                <password>cluster_password</password>
                <ca_cert>/etc/clickhouse-server/ca.crt</ca_cert>
                <cert_file>/etc/clickhouse-server/client.crt</cert_file>
                <key_file>/etc/clickhouse-server/client.key</key_file>
            </replica>
        </shard>
    </production_cluster>
</remote_servers>
```

### 网络安全

```xml
<!-- 网络安全配置 -->
<listen_host>::</listen_host>

<!-- 限制来源IP -->
<max_connections_per_user>100</max_connections_per_user>
<max_concurrent_queries_for_user>10</max_concurrent_queries_for_user>

<!-- 访问控制 -->
<access_control_path>/var/lib/clickhouse/access/</access_control_path>
```

通过合理的集群设计和配置，可以构建高可用、高性能的 ClickHouse 分布式系统，满足大规模数据处理的需求。