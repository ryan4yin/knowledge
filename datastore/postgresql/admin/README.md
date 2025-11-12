# PostgreSQL 服务器配置管理

本章节详细介绍 PostgreSQL 服务器的配置管理，包括配置文件、参数调优和日常维护。

## 配置文件详解

### 1. postgresql.conf 主配置文件

```ini
# 连接和认证配置
listen_addresses = '*'                  # 监听地址，'*' 表示所有地址
port = 5432                            # 数据库端口
max_connections = 200                   # 最大连接数
superuser_reserved_connections = 3      # 为超级用户保留的连接数
unix_socket_directories = '/tmp'        # Unix socket 目录

# 内存配置
shared_buffers = 256MB                  # 共享缓冲区（系统内存的 25%）
temp_buffers = 8MB                      # 临时缓冲区
max_prepared_transactions = 0           # 最大预准备事务数
work_mem = 4MB                          # 工作内存
maintenance_work_mem = 64MB             # 维护操作内存
autovacuum_work_mem = -1                # 自动清理内存（-1 表示使用 maintenance_work_mem）
max_stack_depth = 2MB                   # 最大栈深度

# WAL (Write-Ahead Logging) 配置
wal_level = replica                     # WAL 级别：minimal, replica, logical
fsync = on                              # 强制同步到磁盘
synchronous_commit = on                 # 同步提交
wal_sync_method = fsync                 # WAL 同步方法
full_page_writes = on                   # 完整页写入
wal_compression = on                    # WAL 压缩
wal_log_hints = off                     # 记录提示信息
wal_buffers = 16MB                      # WAL 缓冲区
wal_writer_delay = 200ms                # WAL 写入延迟
commit_delay = 0                        # 提交延迟
commit_siblings = 5                     # 并发提交兄弟事务数

# 检查点配置
checkpoint_segments = 64                # 检查点段数（PostgreSQL 10 以下版本）
checkpoint_completion_target = 0.9      # 检查点完成目标
wal_writer_flush_after = 1MB            # WAL 写入刷新阈值
checkpoint_timeout = 15min              # 检查点超时时间

# 归档配置
archive_mode = on                       # 归档模式
archive_command = 'cp %p /backup/wal/%f' # 归档命令
archive_timeout = 300                   # 归档超时时间

# 复制配置
max_wal_senders = 3                     # 最大 WAL 发送进程数
wal_keep_segments = 64                  -- 保留的 WAL 段数
hot_standby = on                        # 热备库支持
max_standby_archive_delay = 30s         # 备库归档延迟
max_standby_streaming_delay = 30s       # 备库流复制延迟

# 查询规划器配置
enable_bitmapscan = on                  # 启用位图扫描
enable_hashagg = on                     # 启用哈希聚合
enable_hashjoin = on                    # 启用哈希连接
enable_indexscan = on                   # 启用索引扫描
enable_indexonlyscan = on               # 启用纯索引扫描
enable_material = on                    # 启用物化
enable_mergejoin = on                   # 启用合并连接
enable_nestloop = on                    # 启用嵌套循环连接
enable_seqscan = on                     # 启用顺序扫描
enable_sort = on                        # 启用排序
enable_tidscan = on                     # 启用 TID 扫描

# 规划器方法配置
seq_page_cost = 1.0                     # 顺序页成本
random_page_cost = 4.0                  # 随机页成本（SSD 可以设置为 1.1）
cpu_tuple_cost = 0.01                   # CPU 元组成本
cpu_index_tuple_cost = 0.005            # CPU 索引元组成本
cpu_operator_cost = 0.0025              # CPU 操作符成本
parallel_tuple_cost = 0.1               # 并行元组成本
parallel_setup_cost = 1000.0            # 并行设置成本
effective_cache_size = 4GB              # 有效缓存大小（系统内存的 75%）
jit = on                                # 即时编译（PostgreSQL 11+）

# 报告和日志配置
logging_collector = on                  # 日志收集器
log_destination = 'stderr'              # 日志目标
log_directory = 'pg_log'                # 日志目录
log_filename = 'postgresql-%Y-%m-%d_%H%M%S.log'  # 日志文件名
log_file_mode = 0600                    # 日志文件权限
log_truncate_on_rotation = off          # 日志轮转时截断
log_rotation_age = 1d                   # 日志轮转时间间隔
log_rotation_size = 10MB                # 日志轮转大小

# 运行时统计
track_activities = on                   # 跟踪活动
track_counts = on                       # 跟踪计数
track_io_timing = on                    # 跟踪 I/O 时间
track_functions = none                  # 跟踪函数调用
track_activity_query_size = 1024        # 活动查询大小
log_temp_files = 10MB                   # 记录临时文件
log_checkpoints = on                    # 记录检查点
log_connections = on                    # 记录连接
log_disconnections = on                 # 记录断开连接
log_duration = off                      # 记录语句持续时间
log_statement = 'none'                  # 记录语句类型
log_min_duration_statement = 1000       # 记录慢查询（毫秒）

# 自动清理配置
autovacuum = on                         # 自动清理
log_autovacuum_min_duration = 0         # 记录自动清理
autovacuum_max_workers = 3              # 最大自动清理工作进程
autovacuum_naptime = 1min               # 自动清理间隔
autovacuum_vacuum_threshold = 50         -- 触发清理的行数阈值
autovacuum_analyze_threshold = 50       -- 触发分析的行数阈值
autovacuum_vacuum_scale_factor = 0.2    -- 清理比例因子
autovacuum_analyze_scale_factor = 0.1   -- 分析比例因子
autovacuum_freeze_max_age = 200000000   -- 最大冻结年龄
autovacuum_multixact_freeze_max_age = 400000000  -- 多事务最大冻结年龄
```

### 2. pg_hba.conf 访问控制文件

```bash
# 格式：TYPE DATABASE USER ADDRESS METHOD

# 本地连接
local   all             postgres                                peer
local   all             all                                     md5

# IPv4 本地连接
host    all             all             127.0.0.1/32            md5

# IPv6 本地连接
host    all             all             ::1/128                 md5

# 内网连接
host    myapp           app_user        10.0.0.0/8              md5
host    analytics       analytics_user  192.168.1.0/24          md5
host    replication     replicator      192.168.1.100/32        md5

# SSL 连接
hostssl all             all             0.0.0.0/0               md5
hostssl all             all             ::/0                    md5

# 管理员连接
host    all             postgres        192.168.1.0/24          md5

# 特殊数据库
host    template0       all             127.0.0.1/32            md5
host    template1       all             127.0.0.1/32            md5
```

### 3. pg_ident.conf 用户映射文件

```bash
# 格式：MAPNAME SYSTEM-USERNAME PG-USERNAME

# 本地用户映射
localuser   john    john
localuser   jane    jane

# 系统用户映射
sysadmin    root    postgres
sysadmin    admin   postgres

# 应用用户映射
appuser     apache  app_user
appuser     nginx   app_user
```

## 配置参数管理

### 1. 查看配置参数

```sql
-- 查看所有配置参数
SHOW ALL;

-- 查看特定参数
SHOW shared_buffers;
SHOW max_connections;
SHOW work_mem;

-- 查看参数详细信息
SELECT
    name,
    setting,
    unit,
    category,
    short_desc,
    extra_desc,
    vartype,
    min_val,
    max_val,
    enumvals,
    boot_val,
    reset_val,
    sourcefile,
    sourceline
FROM pg_settings
WHERE name = 'work_mem';

-- 查看参数来源
SELECT name, setting, source, context
FROM pg_settings
WHERE source != 'default';

-- 查看需要重启的参数
SELECT name, setting, context
FROM pg_settings
WHERE context = 'postmaster';
```

### 2. 动态修改参数

```sql
-- 会话级别修改
SET work_mem = '8MB';
SET search_path = 'public, extensions';

-- 事务级别修改
BEGIN;
SET LOCAL work_mem = '16MB';
-- 执行复杂查询
COMMIT;

-- 用户级别修改
ALTER USER app_user SET work_mem = '4MB';
ALTER USER app_user SET search_path = 'app_schema, public';

-- 数据库级别修改
ALTER DATABASE myapp SET maintenance_work_mem = '128MB';
ALTER DATABASE myapp SET timezone = 'UTC';
```

### 3. 配置文件重载

```sql
-- 重新加载配置文件（不需要重启）
SELECT pg_reload_conf();

-- 检查是否需要重启
SELECT name, setting, unit, context
FROM pg_settings
WHERE context IN ('postmaster', 'sighup');

-- 查看配置加载状态
SELECT * FROM pg_file_settings;
```

## 性能调优配置

### 1. 内存优化配置

```sql
-- 内存配置建议（基于 16GB 系统）
-- shared_buffers = 4GB (系统内存的 25%)
-- effective_cache_size = 12GB (系统内存的 75%)
-- work_mem = 64MB (根据并发连接数调整)
-- maintenance_work_mem = 1GB (维护操作内存)
-- autovacuum_work_mem = -1 (使用 maintenance_work_mem)

-- 验证内存配置
SELECT name, setting, unit,
       setting::bigint * pg_size_bytes(unit) as size_bytes
FROM pg_settings
WHERE name IN (
    'shared_buffers',
    'effective_cache_size',
    'work_mem',
    'maintenance_work_mem'
);
```

### 2. I/O 优化配置

```ini
# SSD 优化
random_page_cost = 1.1                  # SSD 随机访问成本
effective_io_concurrency = 200          # SSD 并发 I/O
maintenance_io_concurrency = 10         # 维护操作并发 I/O

# HDD 优化
random_page_cost = 4.0                  # HDD 随机访问成本
effective_io_concurrency = 2            # HDD 并发 I/O

# 检查点优化
checkpoint_completion_target = 0.9      # 平滑检查点
max_wal_size = 1GB                      -- WAL 最大大小（PostgreSQL 11+）
min_wal_size = 80MB                     -- WAL 最小大小
```

### 3. 并行查询配置

```ini
# 并行查询参数（PostgreSQL 9.6+）
max_parallel_workers_per_gather = 2      # 每个节点的并行工作进程
max_parallel_workers = 8                # 系统总并行工作进程
parallel_tuple_cost = 0.1               # 并行元组成本
parallel_setup_cost = 1000.0            # 并行设置成本
```

## 连接池配置

### 1. PgBouncer 配置

```ini
# pgbouncer.ini 配置文件
[databases]
myapp = host=localhost port=5432 dbname=myapp
analytics = host=localhost port=5432 dbname=analytics
template1 = host=localhost port=5432 dbname=template1

[pgbouncer]
listen_port = 6432
listen_addr = 127.0.0.1
admin_users = postgres
stats_users = stats, postgres

# 认证
auth_type = md5
auth_file = /etc/pgbouncer/userlist.txt

# 连接池设置
pool_mode = transaction                  # 连接池模式：session, transaction, statement
max_client_conn = 200                   # 最大客户端连接数
default_pool_size = 25                  # 默认池大小
min_pool_size = 5                       # 最小池大小
reserve_pool_size = 5                   # 保留池大小
reserve_pool_timeout = 5                # 保留池超时
max_db_connections = 100                # 每个数据库最大连接数
max_user_connections = 100              # 每个用户最大连接数

# 超时设置
server_reset_query = DISCARD ALL        # 服务器重置查询
server_check_delay = 30                 # 服务器检查延迟
server_check_query = select 1           # 服务器检查查询
server_lifetime = 3600                  # 服务器连接生存时间
server_idle_timeout = 600               # 服务器空闲超时

# 日志
logfile = /var/log/pgbouncer/pgbouncer.log
log_disconnections = 1
log_pooler_errors = 1
stats_period = 60

# 管理界面
admin_port = 6433                       # 管理端口
admin_users = postgres, admin
```

### 2. Pgpool-II 配置

```ini
# pgpool.conf 配置文件
# 连接设置
listen_addresses = '*'
port = 9999
socket_dir = '/tmp'

# 后端节点设置
backend_hostname0 = 'localhost'
backend_port0 = 5432
backend_weight0 = 1
backend_data_directory0 = '/var/lib/postgresql/16/main'
backend_flag0 = 'ALLOW_TO_FAILOVER'

# 负载均衡
load_balance_mode = on
ignore_leading_white_space = on
white_function_list = ''
black_function_list = 'nextval,setval'

# 复制模式
master_slave_mode = on
master_slave_sub_mode = 'stream'
sr_check_user = 'nobody'
sr_check_password = ''
delay_threshold = 1000000

# 健康检查
health_check_period = 30
health_check_timeout = 20
health_check_user = 'nobody'
health_check_password = ''
health_check_max_retries = 3
health_check_retry_delay = 1
```

## 配置模板与示例

### 1. 开发环境配置

```ini
# postgresql.conf - 开发环境
memory_context_size = 1MB

# 较小的内存限制
shared_buffers = 128MB
effective_cache_size = 512MB
work_mem = 1MB
maintenance_work_mem = 16MB

# 较多的调试信息
log_statement = 'all'
log_min_duration_statement = 0
log_error_verbosity = verbose

# 自动清理更积极
autovacuum_naptime = 30s
autovacuum_vacuum_threshold = 20
autovacuum_analyze_threshold = 20
```

### 2. 生产环境配置

```ini
# postgresql.conf - 生产环境
# 较大的内存限制（基于 32GB 内存）
shared_buffers = 8GB
effective_cache_size = 24GB
work_mem = 256MB
maintenance_work_mem = 2GB

# 性能优化
random_page_cost = 1.1                  # SSD
effective_io_concurrency = 200
max_parallel_workers_per_gather = 4

# 日志配置
logging_collector = on
log_destination = 'csvlog'
log_filename = 'postgresql-%Y-%m-%d_%H%M%S.csv'
log_rotation_age = 1d
log_rotation_size = 100MB
log_min_duration_statement = 1000
log_checkpoints = on
log_connections = on
log_disconnections = on
log_lock_waits = on

# 安全配置
ssl = on
password_encryption = scram-sha-256
```

### 3. 数据仓库配置

```ini
# postgresql.conf - 数据仓库
# 大内存配置
shared_buffers = 16GB
effective_cache_size = 48GB
work_mem = 1GB
maintenance_work_mem = 4GB

# 大型查询优化
seq_page_cost = 1.0
random_page_cost = 1.1
cpu_tuple_cost = 0.001
effective_io_concurrency = 1000

# 并行查询
max_parallel_workers_per_gather = 8
max_parallel_workers = 32
parallel_setup_cost = 100
parallel_tuple_cost = 0.01

# 批量操作优化
wal_level = minimal
synchronous_commit = off
fsync = on                               # 数据安全仍需保证
```

## 配置管理最佳实践

### 1. 配置文件管理

```bash
# 配置文件版本控制
git init /etc/postgresql/16/main
cd /etc/postgresql/16/main
git add postgresql.conf pg_hba.conf pg_ident.conf
git commit -m "Initial PostgreSQL configuration"

# 配置文件备份
#!/bin/bash
# backup_config.sh
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backup/postgres_config"

mkdir -p $BACKUP_DIR
cp /etc/postgresql/16/main/*.conf $BACKUP_DIR/$DATE/
tar -czf $BACKUP_DIR/config_$DATE.tar.gz -C $BACKUP_DIR $DATE/
rm -rf $BACKUP_DIR/$DATE/
```

### 2. 配置监控

```sql
-- 监控配置变更
CREATE TABLE config_changes (
    id SERIAL PRIMARY KEY,
    config_name VARCHAR(255),
    old_value TEXT,
    new_value TEXT,
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    changed_by TEXT
);

-- 配置变更监控函数
CREATE OR REPLACE FUNCTION log_config_change()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO config_changes (config_name, old_value, new_value, changed_by)
    VALUES (TG_ARGV[0], OLD.setting, NEW.setting, current_user);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 配置变更告警
SELECT
    name,
    setting,
    reset_val,
    sourcefile,
    sourceline
FROM pg_settings
WHERE setting != reset_val;
```

### 3. 配置验证脚本

```bash
#!/bin/bash
# validate_config.sh
PG_DATA="/var/lib/postgresql/16/main"
LOG_FILE="/var/log/postgresql/postgresql-16-main.log"

# 检查配置文件语法
sudo -u postgres /usr/lib/postgresql/16/bin/postgres -t -c config_file=$PG_DATA/postgresql.conf

# 检查参数设置
sudo -u postgres psql -c "
SELECT name, setting, unit, context
FROM pg_settings
WHERE context = 'postmaster' AND setting != boot_val;
"

# 检查日志错误
grep -i error $LOG_FILE | tail -10
```

通过合理的配置管理，可以确保 PostgreSQL 服务器的高性能、高可用性和安全性。