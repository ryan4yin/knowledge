# PostgreSQL 备份与恢复

PostgreSQL 提供了强大的备份和恢复机制，主要基于 WAL (Write-Ahead Logging) 预写日志系统。本章节介绍 PostgreSQL 的 WAL 机制、备份策略和恢复方法。

## WAL (Write-Ahead Logging) 机制

### WAL 工作原理

WAL 是 PostgreSQL 的核心事务日志机制，确保数据的持久性和一致性：

1. **数据修改流程**：
   - 数据修改首先写入 WAL 缓冲区
   - WAL 记录写入磁盘
   - 然后修改实际的数据页面
   - 定期检查点将脏页写入磁盘

2. **WAL 的作用**：
   - 确保事务的原子性和持久性
   - 支持时间点恢复 (PITR)
   - 实现流复制
   - 支持数据库恢复

### WAL 配置参数

```sql
-- 查看当前 WAL 配置
SELECT name, setting, unit, short_desc
FROM pg_settings
WHERE name LIKE '%wal%';

-- 重要 WAL 配置参数
-- wal_level: minimal, replica, 或 logical
-- fsync: on 或 off（强烈建议设为 on）
-- synchronous_commit: on, remote_write, local, 或 off
-- wal_sync_method: 数据同步方法
-- wal_buffers: WAL 缓冲区大小
-- wal_writer_delay: WAL 写入进程延迟
-- checkpoint_timeout: 检查点超时时间
-- checkpoint_completion_target: 检查点完成目标
```

### WAL 文件管理

```sql
-- 查看 WAL 文件信息
SELECT pg_walfile_name(pg_current_wal_lsn());  -- 当前 WAL 文件名
SELECT pg_current_wal_lsn();                   -- 当前 WAL 位置
SELECT pg_last_wal_replay_lsn();               -- 最后重放的 WAL 位置（备库）

-- 查看 WAL 文件大小和数量
SHOW wal_segment_size;    -- WAL 段大小（通常 16MB）
SHOW wal_keep_segments;   -- 保留的 WAL 段数量

-- 手动切换 WAL 文件
SELECT pg_switch_wal();

-- 手动创建检查点
CHECKPOINT;
```

## 备份类型

### 1. 逻辑备份 (Logical Backup)

使用 `pg_dump` 和 `pg_dumpall` 工具创建 SQL 格式的备份。

#### pg_dump - 单个数据库备份
```bash
# 基本备份
pg_dump -h localhost -U postgres -d mydb > mydb_backup.sql

# 压缩备份
pg_dump -h localhost -U postgres -d mydb | gzip > mydb_backup.sql.gz

# 自定义格式备份（推荐）
pg_dump -h localhost -U postgres -d mydb -Fc -f mydb_backup.dump

# 目录格式备份（支持并行）
pg_dump -h localhost -U postgres -d mydb -Fd -j 4 -f mydb_backup_dir/

# 只导出特定表
pg_dump -h localhost -U postgres -d mydb -t users -t orders > tables_backup.sql

# 只导出数据
pg_dump -h localhost -U postgres -d mydb -a > data_only.sql

# 只导出模式
pg_dump -h localhost -U postgres -d mydb -s > schema_only.sql

# 条件导出
pg_dump -h localhost -U postgres -d mydb \
  --where="created_at > '2023-01-01'" -t orders > recent_orders.sql
```

#### pg_dumpall - 所有数据库备份
```bash
# 备份所有数据库和全局对象
pg_dumpall -h localhost -U postgres > all_databases_backup.sql

# 只备份全局对象（角色、表空间）
pg_dumpall -h localhost -U postgres -g > globals_backup.sql

# 只备份数据库定义
pg_dumpall -h localhost -U postgres -s > schemas_backup.sql
```

#### 逻辑备份恢复
```bash
# 从 SQL 文件恢复
psql -h localhost -U postgres -d mydb < mydb_backup.sql

# 从自定义格式恢复
pg_restore -h localhost -U postgres -d mydb mydb_backup.dump

# 只恢复特定表
pg_restore -h localhost -U postgres -d mydb -t users mydb_backup.dump

-- 恢复数据前清理数据库
pg_restore -h localhost -U postgres -d mydb --clean --if-exists mydb_backup.dump

-- 并行恢复
pg_restore -h localhost -U postgres -d mydb -j 4 mydb_backup.dump
```

### 2. 物理备份 (Physical Backup)

物理备份是数据库文件系统的直接副本，包括基础备份和 WAL 归档。

#### 基础备份创建
```bash
# 方法 1: 使用 pg_basebackup（推荐）
pg_basebackup -h localhost -D /backup/base_$(date +%Y%m%d) -U postgres -v -P -W

# 使用压缩
pg_basebackup -h localhost -D /backup/base_$(date +%Y%m%d) -U postgres -v -P -W -z -Z 9

# 创建表空间映射
pg_basebackup -h localhost -D /backup/base_$(date +%Y%m%d) -U postgres -T /opt/pgdata/ts1=/backup/ts1

# 方法 2: 文件系统级别备份（需要停机或冷备份）
-- 1. 停止 PostgreSQL 服务
sudo systemctl stop postgresql

-- 2. 复制数据目录
sudo cp -r /var/lib/postgresql/16/main /backup/base_backup_$(date +%Y%m%d)

-- 3. 重启服务
sudo systemctl start postgresql
```

#### WAL 归档配置
```sql
-- postgresql.conf 配置
-- 启用 WAL 归档
wal_level = replica
archive_mode = on
archive_command = 'cp %p /backup/wal_archive/%f'
-- 或使用 rsync
-- archive_command = 'rsync -a %p /backup/wal_archive/%f'

-- 自动清理归档
archive_cleanup_command = 'pg_archivecleanup /backup/wal_archive %r'
```

#### 定期 WAL 归档脚本
```bash
#!/bin/bash
# wal_archive.sh - WAL 归档脚本

ARCHIVE_DIR="/backup/wal_archive"
RETENTION_DAYS=30

# 创建归档目录
mkdir -p $ARCHIVE_DIR

# 归档当前 WAL 文件
pg_receivewal -h localhost -D $ARCHIVE_DIR -U postgres -v -Z 9

# 清理旧的 WAL 文件
find $ARCHIVE_DIR -name "*.gz" -mtime +$RETENTION_DAYS -delete

# 记录归档信息
echo "$(date): WAL archive completed" >> /var/log/postgresql/wal_archive.log
```

## 备份策略

### 1. 完整备份策略

```bash
#!/bin/bash
# full_backup.sh - 完整备份脚本

BACKUP_DIR="/backup"
DATE=$(date +%Y%m%d_%H%M%S)
DB_NAME="mydb"

# 创建备份目录
mkdir -p $BACKUP_DIR/$DATE

# 创建逻辑备份
echo "Creating logical backup..."
pg_dump -h localhost -U postgres -d $DB_NAME -Fc -f $BACKUP_DIR/$DATE/${DB_NAME}_${DATE}.dump

# 创建物理备份
echo "Creating physical backup..."
pg_basebackup -h localhost -D $BACKUP_DIR/$DATE/base_backup -U postgres -v -P -W

# 备份 WAL 归档
echo "Backing up WAL archives..."
tar -czf $BACKUP_DIR/$DATE/wal_archive_${DATE}.tar.gz /backup/wal_archive/

# 备份配置文件
echo "Backing up configuration files..."
cp /etc/postgresql/16/main/postgresql.conf $BACKUP_DIR/$DATE/
cp /etc/postgresql/16/main/pg_hba.conf $BACKUP_DIR/$DATE/

# 清理旧备份（保留 7 天）
find $BACKUP_DIR -type d -mtime +7 -exec rm -rf {} +

echo "Backup completed: $BACKUP_DIR/$DATE"
```

### 2. 增量备份策略

PostgreSQL 的增量备份主要通过 WAL 归档实现：

```sql
-- 查看当前 WAL 位置
SELECT pg_current_wal_lsn();

-- 备份从某个 LSN 开始的 WAL 记录
pg_receivewal -h localhost -D /backup/incremental --startpos LSN_VALUE
```

### 3. 连续归档备份设置

```sql
-- postgresql.conf 完整配置
-- WAL 配置
wal_level = replica
archive_mode = on
archive_command = '/usr/local/bin/archive_wal.sh %p %f'
archive_timeout = 300  -- 5分钟强制归档

-- 检查点配置
checkpoint_timeout = 15min
checkpoint_completion_target = 0.9
wal_buffers = 16MB

-- 日志配置
log_destination = 'stderr'
logging_collector = on
log_directory = 'pg_log'
log_filename = 'postgresql-%Y-%m-%d_%H%M%S.log'
log_min_duration_statement = 1000  -- 记录慢查询
```

## 恢复方法

### 1. 时间点恢复 (PITR)

#### 配置恢复
```bash
# 1. 停止 PostgreSQL 服务
sudo systemctl stop postgresql

# 2. 恢复基础备份
rm -rf /var/lib/postgresql/16/main/*
cp -r /backup/base_20231201/main/* /var/lib/postgresql/16/main/

# 3. 配置恢复参数
# postgresql.auto.conf 或 recovery.conf
echo "restore_command = 'cp /backup/wal_archive/%f %p'" >> /var/lib/postgresql/16/main/recovery.conf
echo "recovery_target_time = '2023-12-01 10:30:00'" >> /var/lib/postgresql/16/main/recovery.conf
# 或者恢复到特定事务 ID
# echo "recovery_target_xid = '12345'" >> /var/lib/postgresql/16/main/recovery.conf

# 4. 设置权限
sudo chown -R postgres:postgres /var/lib/postgresql/16/main

# 5. 启动 PostgreSQL 服务
sudo systemctl start postgresql
```

#### 使用 pgBackRest (高级备份工具)
```bash
# 安装 pgBackRest
sudo apt-get install pgbackrest

# 配置 pgBackRest
# /etc/pgbackrest/pgbackrest.conf
[global]
repo1-path=/backup/pgbackrest
repo1-retention-full=30
repo1-retention-diff=14

[main]
db1-path=/var/lib/postgresql/16/main

# 创建备份
pgbackrest --stanza=main backup

# 时间点恢复
pgbackrest --stanza=main --delta --type=time "--target=2023-12-01 10:30:00" restore
```

### 2. 表级别恢复

从逻辑备份中恢复特定表：
```bash
# 查看备份内容
pg_restore --list mydb_backup.dump > backup_contents.txt

# 选择恢复特定表
pg_restore -h localhost -U postgres -d mydb -t users -t orders mydb_backup.dump

# 从 SQL 文件恢复特定表
sed -n '/COPY public.users/,/\./p' mydb_backup.sql > users_data.sql
psql -h localhost -U postgres -d mydb < users_data.sql
```

### 3. 从 WAL 记录恢复数据

```sql
-- 使用 wal2json 扩展查看 WAL 记录
CREATE EXTENSION wal2json;

-- 查看特定表的变更
SELECT * FROM pg_logical_slot_get_changes('slot_name', NULL, NULL, 'format-version', '1');
```

## 备份验证

### 备份完整性检查
```bash
#!/bin/bash
# backup_verification.sh - 备份验证脚本

BACKUP_FILE=$1
TEST_DB="test_restore_$(date +%s)"

echo "Verifying backup: $BACKUP_FILE"

# 创建测试数据库
createdb $TEST_DB

# 尝试恢复备份
if pg_restore -d $TEST_DB $BACKUP_FILE > /dev/null 2>&1; then
    echo "✓ Backup verification successful"

    # 检查表数量
    TABLE_COUNT=$(psql -d $TEST_DB -t -c "SELECT count(*) FROM information_schema.tables WHERE table_schema = 'public'")
    echo "✓ Database contains $TABLE_COUNT tables"

    # 删除测试数据库
    dropdb $TEST_DB

    exit 0
else
    echo "✗ Backup verification failed"
    dropdb $TEST_DB
    exit 1
fi
```

### 自动化备份和验证
```bash
#!/bin/bash
# automated_backup.sh - 自动化备份和验证

BACKUP_DIR="/backup"
DB_NAME="mydb"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/${DB_NAME}_${DATE}.dump"

# 创建备份
echo "Creating backup..."
pg_dump -Fc -f $BACKUP_FILE $DB_NAME

# 验证备份
echo "Verifying backup..."
./backup_verification.sh $BACKUP_FILE

if [ $? -eq 0 ]; then
    echo "Backup successful and verified"

    # 上传到云存储（可选）
    # aws s3 cp $BACKUP_FILE s3://my-backups/postgresql/

    # 发送通知（可选）
    # echo "Database backup completed successfully" | mail -s "Backup Success" admin@example.com
else
    echo "Backup verification failed"
    # 发送告警
    # echo "Database backup failed" | mail -s "Backup Failure" admin@example.com
fi
```

## 高级备份配置

### Barman (专业备份管理工具)
```bash
# 安装 Barman
sudo apt-get install barman

# 配置 Barman
# /etc/barman/barman.conf
[barman]
barman_home = /var/lib/barman
barman_user = barman
log_file = /var/log/barman/barman.log

[main_server]
description = "Main PostgreSQL Server"
conninfo = host=localhost user=postgres dbname=postgres
backup_method = postgres
streaming_archiver = on
backup_directory = /backup/barman/main
retention_policy = RECOVERY WINDOW OF 30 DAYS

# 创建备份
barman backup main_server

# 列出备份
barman list-backups main_server

# 恢复数据库
barman recover main_server latest /var/lib/postgresql/16/main
```

### 备份到云存储
```bash
#!/bin/bash
# cloud_backup.sh - 云备份脚本

BACKUP_DIR="/backup"
BUCKET_NAME="my-db-backups"
DATE=$(date +%Y%m%d_%H%M%S)

# Google Cloud Storage
upload_to_gcs() {
    local file=$1
    gsutil cp $file gs://$BUCKET_NAME/postgresql/
}

# AWS S3
upload_to_s3() {
    local file=$1
    aws s3 cp $file s3://$BUCKET_NAME/postgresql/
}

# Azure Blob Storage
upload_to_azure() {
    local file=$1
    az storage blob upload --file $file --container-name postgres-backups --name $(basename $file)
}

# 创建并上传备份
pg_dump -Fc -f $BACKUP_DIR/db_backup_$DATE.dump mydb
upload_to_s3 $BACKUP_DIR/db_backup_$DATE.dump

echo "Backup uploaded to cloud storage"
```

## 备份最佳实践

### 1. 备份策略建议
```sql
-- 每日完整备份 + 连续 WAL 归档
-- 完整备份保留 30 天
-- WAL 归档保留 60 天
-- 异地备份（至少一个异地副本）
-- 定期恢复测试（每月一次）
```

### 2. 监控备份状态
```sql
-- 查看最近的备份信息
SELECT
    database_name,
    backup_start_time,
    backup_end_time,
    backup_size
FROM pg_stat_backup
WHERE backup_end_time > NOW() - INTERVAL '7 days';

-- 监控 WAL 生成速率
SELECT
    pg_current_wal_lsn() as current_lsn,
    pg_wal_lsn_diff(pg_current_wal_lsn(), '0/0') as total_bytes;
```

### 3. 恢复时间目标 (RTO) 和恢复点目标 (RPO)
```sql
-- 根据业务需求设置：
-- RTO: 恢复时间目标（如 1 小时）
-- RPO: 恢复点目标（如 15 分钟）

-- 配置相应的备份频率和保留策略
```

PostgreSQL 的备份和恢复系统非常强大和灵活，能够满足各种规模和可用性要求。正确配置备份策略和定期测试恢复流程是确保数据安全的关键。