# PostgreSQL 常见故障排查

本章节介绍 PostgreSQL 的常见问题和故障排查方法，包括连接问题、性能问题、复制问题和数据恢复等。

## 连接问题排查

### 1. 连接被拒绝

```bash
# 检查 PostgreSQL 服务状态
sudo systemctl status postgresql
sudo systemctl status postgresql@16-main

# 检查端口是否监听
sudo netstat -tlnp | grep 5432
# 或使用 ss
sudo ss -tlnp | grep 5432

# 检查防火墙设置
sudo ufw status
sudo iptables -L -n | grep 5432

# 检查 PostgreSQL 配置
# postgresql.conf
listen_addresses = '*'  # 确保监听正确的地址
port = 5432             # 确保端口正确

# pg_hba.conf 检查访问控制
sudo -u postgres psql -c "SHOW hba_file;"
cat /etc/postgresql/16/main/pg_hba.conf
```

### 2. 认证失败

```sql
-- 检查用户是否存在
SELECT rolname, rolcanlogin FROM pg_roles WHERE rolname = 'your_user';

-- 检查用户密码
-- 如果忘记了密码，可以重置
ALTER USER your_user WITH PASSWORD 'new_password';

-- 检查密码加密方式
SHOW password_encryption;

-- 检查 pg_hba.conf 认证方法
-- 确保认证方法与用户密码格式匹配
-- 例如：scram-sha-256 密码需要使用 scram-sha-256 认证方法
```

### 3. 连接数超限

```sql
-- 检查当前连接数
SELECT count(*) FROM pg_stat_activity;

-- 检查最大连接数
SHOW max_connections;

-- 查看当前连接详情
SELECT
    pid,
    usename,
    application_name,
    client_addr,
    state,
    backend_start,
    query_start,
    state_change
FROM pg_stat_activity
ORDER BY backend_start;

-- 终止空闲连接
SELECT pg_terminate_backend(pid) FROM pg_stat_activity
WHERE state = 'idle' AND backend_start < NOW() - INTERVAL '1 hour';

-- 调整连接数限制（需要重启）
-- postgresql.conf
max_connections = 300
```

## 性能问题排查

### 1. 查询缓慢

```sql
-- 查找长时间运行的查询
SELECT
    pid,
    now() - query_start AS duration,
    query,
    state
FROM pg_stat_activity
WHERE now() - query_start > INTERVAL '1 minute'
AND state = 'active'
ORDER BY duration DESC;

-- 查找慢查询（使用 pg_stat_statements）
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;

SELECT
    query,
    calls,
    total_exec_time,
    mean_exec_time,
    rows
FROM pg_stat_statements
ORDER BY mean_exec_time DESC
LIMIT 10;

-- 分析查询执行计划
EXPLAIN (ANALYZE, BUFFERS) SELECT * FROM large_table WHERE condition = 'value';

-- 检查索引使用情况
SELECT
    schemaname,
    tablename,
    indexname,
    idx_scan,
    idx_tup_read,
    idx_tup_fetch
FROM pg_stat_user_indexes
WHERE idx_scan = 0
ORDER BY tablename;
```

### 2. 锁等待问题

```sql
-- 查看锁等待情况
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

-- 查看详细的锁信息
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
FROM pg_locks
WHERE NOT granted;

-- 终止阻塞进程
SELECT pg_terminate_backend(blocking_pid);
```

### 3. CPU 和内存使用过高

```sql
-- 查看资源使用情况
SELECT
    pid,
    usename,
    application_name,
    client_addr,
    backend_start,
    state_change,
    state,
    query
FROM pg_stat_activity
WHERE state = 'active'
ORDER BY backend_start;

-- 检查内存使用
SELECT
    datname,
    numbackends,
    xact_commit,
    xact_rollback,
    blks_read,
    blks_hit,
    tup_returned,
    tup_fetched,
    tup_inserted,
    tup_updated,
    tup_deleted
FROM pg_stat_database;

-- 检查临时文件使用
SELECT
    datname,
    temp_files,
    temp_bytes
FROM pg_stat_database
WHERE temp_files > 0;
```

## 复制问题排查

### 1. 流复制延迟

```sql
-- 在主库上检查复制状态
SELECT
    pid,
    usesysid,
    usename,
    application_name,
    client_addr,
    state,
    sync_state,
    reply_lsn,
    write_lsn,
    flush_lsn,
    replay_lsn,
    write_lag,
    flush_lag,
    replay_lag
FROM pg_stat_replication;

-- 检查 WAL 发送状态
SELECT * FROM pg_stat_wal;

-- 在备库上检查接收状态
SELECT
    pid,
    usesysid,
    usename,
    application_name,
    state,
    flushed_lsn,
    received_lsn,
    replayed_lsn,
    write_lag,
    flush_lag,
    replay_lag
FROM pg_stat_wal_receiver;
```

### 2. 复制中断恢复

```bash
# 检查复制状态
sudo -u postgres psql -x -c "SELECT * FROM pg_stat_replication;"

# 重建备库
# 1. 停止备库
sudo systemctl stop postgresql

# 2. 删除旧数据
sudo rm -rf /var/lib/postgresql/16/main/*

# 3. 使用 pg_basebackup 重建
sudo -u postgres pg_basebackup -h master_ip -D /var/lib/postgresql/16/main -U replicator -v -P -W

# 4. 配置 recovery.conf 或 standby.signal
sudo -u postgres touch /var/lib/postgresql/16/main/standby.signal

# 5. 创建 recovery.conf（PostgreSQL 12 以下）
echo "standby_mode = 'on'" >> /var/lib/postgresql/16/main/recovery.conf
echo "primary_conninfo = 'host=master_ip port=5432 user=replicator'" >> /var/lib/postgresql/16/main/recovery.conf

# 6. 设置权限
sudo chown -R postgres:postgres /var/lib/postgresql/16/main

# 7. 启动备库
sudo systemctl start postgresql
```

### 3. 时间点恢复

```sql
-- 1. 停止 PostgreSQL
sudo systemctl stop postgresql

-- 2. 恢复基础备份
rm -rf /var/lib/postgresql/16/main/*
cp -r /backup/base_20231201/main/* /var/lib/postgresql/16/main/

-- 3. 创建恢复配置
# PostgreSQL 12+ 使用 standby.signal 和 recovery.conf
sudo -u postgres touch /var/lib/postgresql/16/main/recovery.signal

# recovery.conf
cat > /var/lib/postgresql/16/main/postgresql.auto.conf << EOF
restore_command = 'cp /backup/wal_archive/%f %p'
recovery_target_time = '2023-12-25 10:30:00'
EOF

-- 4. 设置权限
sudo chown -R postgres:postgres /var/lib/postgresql/16/main

-- 5. 启动 PostgreSQL
sudo systemctl start postgresql
```

## 数据损坏问题

### 1. 数据库损坏检测

```sql
-- 检查数据库一致性
-- 需要单用户模式运行
sudo -u postgres pg_resetwal /var/lib/postgresql/16/main/
sudo -u postgres psql -d postgres -c "SELECT pg_database_size('mydb');"

-- 检查表级别损坏
SELECT relname, relfilenode FROM pg_class WHERE relname = 'problematic_table';

-- 使用 pg_filedump 检查文件
pg_filedump /var/lib/postgresql/16/main/base/16384/16385
```

### 2. 修复损坏的数据

```bash
# 使用 pg_resetwal 重置 WAL（危险操作，仅当数据库无法启动时）
sudo -u postgres pg_resetwal /var/lib/postgresql/16/main/

# 从备份恢复数据
pg_restore -d mydb /backup/mydb_backup.dump

# 表级别的数据恢复
-- 创建新表
CREATE TABLE table_name_backup AS SELECT * FROM table_name WHERE false;

-- 从备份恢复数据
pg_restore -d mydb -t table_name --data-only /backup/mydb_backup.dump
```

## 磁盘空间问题

### 1. 检查磁盘使用情况

```sql
-- 查看数据库大小
SELECT
    datname,
    pg_size_pretty(pg_database_size(datname)) as size
FROM pg_database
ORDER BY pg_database_size(datname) DESC;

-- 查看表大小
SELECT
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as total_size,
    pg_size_pretty(pg_relation_size(schemaname||'.'||tablename)) as table_size,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename) - pg_relation_size(schemaname||'.'||tablename)) as index_size
FROM pg_tables
WHERE schemaname NOT IN ('information_schema', 'pg_catalog')
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- 查看膨胀情况
SELECT
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as total_size,
    pg_size_pretty((pg_total_relation_size(schemaname||'.'||tablename) / (SELECT COUNT(*) FROM schemaname||'.'||tablename))) as avg_row_size
FROM pg_tables
WHERE schemaname NOT IN ('information_schema', 'pg_catalog');
```

### 2. 清理磁盘空间

```sql
-- 清理 WAL 文件
SELECT pg_switch_wal();  -- 切换 WAL 文件

-- 删除旧 WAL 文件（需要先配置 archive_command）
-- 或手动删除
sudo rm /var/lib/postgresql/16/main/pg_wal/00000001000000000000000*

-- 清理临时文件
SELECT pg_size_pretty(pg_database_size('postgres'));
VACUUM FULL;

-- 清理大表
VACUUM FULL large_table;

-- 删除不需要的数据
DELETE FROM logs WHERE created_at < CURRENT_DATE - INTERVAL '90 days';
VACUUM logs;
```

## 日志分析

### 1. 错误日志分析

```bash
# 查看最近的错误
tail -f /var/log/postgresql/postgresql-16-main.log | grep -i error

# 查看特定时间段的错误
sudo journalctl -u postgresql@16-main --since "2023-12-25" | grep -i error

# 分析日志模式
grep -E "(FATAL|ERROR|PANIC)" /var/log/postgresql/postgresql-16-main.log | tail -50

# 查看连接失败
grep -i "connection" /var/log/postgresql/postgresql-16-main.log | tail -20
```

### 2. 性能日志分析

```bash
# 查找慢查询
grep "duration:" /var/log/postgresql/postgresql-16-main.log | awk '$3 > 1000' | tail -10

# 分析检查点日志
grep "checkpoint" /var/log/postgresql/postgresql-16-main.log | tail -10

# 查看自动清理日志
grep "automatic vacuum" /var/log/postgresql/postgresql-16-main.log | tail -10

# 查看锁等待日志
grep -i "lock" /var/log/postgresql/postgresql-16-main.log | tail -10
```

## 系统级问题排查

### 1. 内存不足

```bash
# 检查内存使用
free -h
cat /proc/meminfo | grep Mem

# 检查 PostgreSQL 内存使用
ps aux | grep postgres | grep -v grep

# 调整 PostgreSQL 内存配置
# postgresql.conf
shared_buffers = 256MB    # 减少共享缓冲区
work_mem = 1MB           # 减少工作内存
maintenance_work_mem = 16MB  # 减少维护内存
```

### 2. I/O 问题

```bash
# 检查磁盘 I/O
iostat -x 1
iotop

# 检查磁盘空间
df -h
du -sh /var/lib/postgresql/16/main/*

# 检查磁盘错误
dmesg | grep -i error
smartctl -a /dev/sda
```

## 监控和告警

### 1. 创建监控脚本

```bash
#!/bin/bash
# pg_monitor.sh - PostgreSQL 监控脚本

LOG_FILE="/var/log/postgresql/pg_monitor.log"
DATE=$(date '+%Y-%m-%d %H:%M:%S')

# 检查连接数
CONNECTIONS=$(psql -U postgres -t -c "SELECT count(*) FROM pg_stat_activity;")
MAX_CONN=$(psql -U postgres -t -c "SHOW max_connections;")

if [ "$CONNECTIONS" -gt $(($MAX_CONN * 80 / 100)) ]; then
    echo "$DATE WARNING: High connection count: $CONNECTIONS/$MAX_CONN" >> $LOG_FILE
fi

# 检查复制延迟
REPLICATION_LAG=$(psql -U postgres -t -c "
SELECT COALESCE(
    EXTRACT(EPOCH FROM (now() - replay_lag)), 0
)::integer FROM pg_stat_replication LIMIT 1;")

if [ "$REPLICATION_LAG" -gt 300 ]; then
    echo "$DATE WARNING: High replication lag: ${REPLICATION_LAG}s" >> $LOG_FILE
fi

# 检查数据库大小
DB_SIZE=$(psql -U postgres -t -c "SELECT pg_size_pretty(pg_database_size('mydb'));")
echo "$DATE INFO: Database size: $DB_SIZE" >> $LOG_FILE
```

### 2. 健康检查查询

```sql
-- 数据库健康检查
CREATE OR REPLACE FUNCTION health_check()
RETURNS TABLE(
    metric TEXT,
    value TEXT,
    status TEXT
) AS $$
BEGIN
    -- 连接数检查
    RETURN QUERY
    SELECT
        'connection_count',
        count(*)::TEXT,
        CASE
            WHEN count(*) < (SELECT setting::integer FROM pg_settings WHERE name = 'max_connections') * 0.8 THEN 'OK'
            ELSE 'WARNING'
        END
    FROM pg_stat_activity;

    -- 复制状态检查
    RETURN QUERY
    SELECT
        'replication_status',
        count(*)::TEXT,
        CASE
            WHEN count(*) > 0 THEN 'OK'
            ELSE 'ERROR'
        END
    FROM pg_stat_replication;

    -- 数据库大小检查
    RETURN QUERY
    SELECT
        'database_size',
        pg_size_pretty(pg_database_size(current_database())),
        'OK';
END;
$$ LANGUAGE plpgsql;

-- 运行健康检查
SELECT * FROM health_check();
```

通过系统性的故障排查方法，可以快速定位和解决 PostgreSQL 的各种问题，确保数据库系统的稳定运行。