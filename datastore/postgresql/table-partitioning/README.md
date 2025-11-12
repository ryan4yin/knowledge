# PostgreSQL 表分区 (Table Partitioning)

表分区是将一个大表分割成多个较小、更易于管理的部分的技术。每个分区都是一个独立的表，但从逻辑上仍然被视为一个统一的表。

> 跟索引名称一样，分区名称也只是用于标识分区的一个 ID，在 CRUD 时不会被用到，PostgreSQL 底层会自动根据分区情况进行查询。

## 分区的优势

### 1. 性能提升
- **查询性能**：查询可以只扫描相关分区，而不是整个表
- **索引效率**：索引更小，查询更快
- **并行处理**：不同分区可以并行处理

### 2. 维护便利
- **批量操作**：可以快速删除或添加整个分区
- **备份策略**：可以对不同分区制定不同的备份策略
- **数据归档**：可以轻松将历史数据分区移至低成本存储

### 3. 存储优化
- **磁盘空间**：可以针对不同分区使用不同的存储策略
- **压缩设置**：可以为不同分区配置不同的压缩选项

## 分区类型

### 1. 范围分区 (RANGE)

按数值范围、日期范围等进行分区。

```sql
-- 创建主表
CREATE TABLE measurement (
    city_id         int not null,
    logdate         date not null,
    peaktemp        int,
    unitsales       int
) PARTITION BY RANGE (logdate);

-- 创建分区
CREATE TABLE measurement_2023_01 PARTITION OF measurement
    FOR VALUES FROM ('2023-01-01') TO ('2023-02-01');

CREATE TABLE measurement_2023_02 PARTITION OF measurement
    FOR VALUES FROM ('2023-02-01') TO ('2023-03-01');

CREATE TABLE measurement_2023_q1 PARTITION OF measurement
    FOR VALUES FROM ('2023-01-01') TO ('2023-04-01');
```

**适用场景**：
- 时间序列数据（按天、周、月、季度、年分区）
- 数值范围数据（如年龄、价格区间）
- ID 范围数据

### 2. 列表分区 (LIST)

按离散值列表进行分区。

```sql
-- 创建主表
CREATE TABLE orders (
    order_id    serial,
    customer_id int,
    order_date  date,
    region      text,
    amount      numeric
) PARTITION BY LIST (region);

-- 创建分区
CREATE TABLE orders_north_america PARTITION OF orders
    FOR VALUES IN ('USA', 'Canada', 'Mexico');

CREATE TABLE orders_europe PARTITION OF orders
    FOR VALUES IN ('UK', 'Germany', 'France', 'Italy', 'Spain');

CREATE TABLE orders_asia PARTITION OF orders
    FOR VALUES IN ('China', 'Japan', 'Korea', 'India');

-- 处理不匹配的值
CREATE TABLE orders_other PARTITION OF orders
    FOR VALUES IN ('Brazil', 'Argentina', 'Australia', 'DEFAULT');
```

**适用场景**：
- 地理区域数据
- 产品类别
- 用户类型
- 状态枚举值

### 3. 哈希分区 (HASH)

通过哈希函数将数据均匀分布到各个分区。

```sql
-- 创建主表
CREATE TABLE users (
    user_id     serial primary key,
    username    text,
    email       text,
    created_at  timestamp
) PARTITION BY HASH (user_id);

-- 创建4个分区
CREATE TABLE users_0 PARTITION OF users
    FOR VALUES WITH (MODULUS 4, REMAINDER 0);

CREATE TABLE users_1 PARTITION OF users
    FOR VALUES WITH (MODULUS 4, REMAINDER 1);

CREATE TABLE users_2 PARTITION OF users
    FOR VALUES WITH (MODULUS 4, REMAINDER 2);

CREATE TABLE users_3 PARTITION OF users
    FOR VALUES WITH (MODULUS 4, REMAINDER 3);
```

**适用场景**：
- 需要均匀分布数据
- 没有明显的分区键
- 避免热点数据问题

## 分区管理

### 1. 创建分区策略

#### 自动创建分区（PostgreSQL 10+）

```sql
-- 创建分区表函数
CREATE OR REPLACE FUNCTION create_monthly_partition(table_name text, start_date date)
RETURNS void AS $$
DECLARE
    partition_name text;
    end_date date;
BEGIN
    partition_name := table_name || '_' || to_char(start_date, 'YYYY_MM');
    end_date := start_date + interval '1 month';

    EXECUTE format('CREATE TABLE %I PARTITION OF %I
                    FOR VALUES FROM (%L) TO (%L)',
                   partition_name, table_name, start_date, end_date);

    EXECUTE format('CREATE INDEX ON %I (logdate)', partition_name);
END;
$$ LANGUAGE plpgsql;

-- 使用示例
SELECT create_monthly_partition('measurement', '2023-12-01');
```

### 2. 分区维护

#### 添加新分区

```sql
-- 手动添加分区
CREATE TABLE measurement_2023_12 PARTITION OF measurement
    FOR VALUES FROM ('2023-12-01') TO ('2024-01-01');

-- 分离分区（ATTACH/DETACH）
-- 创建新表
CREATE TABLE measurement_2024_temp (
    LIKE measurement INCLUDING ALL
);

-- 附加到分区表
ALTER TABLE measurement
    ATTACH PARTITION measurement_2024_temp
    FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');

-- 分离分区
ALTER TABLE measurement
    DETACH PARTITION measurement_2023_01;
```

#### 删除分区

```sql
-- 快速删除整个分区
DROP TABLE measurement_2023_01;

-- 先分离再删除（更安全）
ALTER TABLE measurement DETACH PARTITION measurement_2023_01;
DROP TABLE measurement_2023_01;
```

#### 分区数据迁移

```sql
-- 将分区移动到其他表空间
ALTER TABLE measurement_2023_01
    SET TABLESPACE fast_storage;

-- 重命名分区
ALTER TABLE measurement_2023_01
    RENAME TO measurement_jan_2023;
```

### 3. 分区约束和索引

#### 分区约束

```sql
-- 添加额外约束到分区
ALTER TABLE measurement_2023_01
    ADD CONSTRAINT check_peaktemp
    CHECK (peaktemp BETWEEN -50 AND 60);
```

#### 分区索引

```sql
-- 为每个分区创建索引
CREATE INDEX ON measurement_2023_01 (city_id);
CREATE INDEX ON measurement_2023_02 (city_id);

-- 或者在主表上创建索引（会自动应用到所有分区）
CREATE INDEX ON measurement (city_id, logdate);
```

## 查询优化

### 1. 分区裁剪（Partition Pruning）

PostgreSQL 会自动优化查询，只扫描相关分区：

```sql
-- 这个查询只会扫描 2023年1月的分区
EXPLAIN (COSTS OFF)
SELECT * FROM measurement
WHERE logdate >= '2023-01-15' AND logdate < '2023-01-20';

-- 查询分区裁剪情况
EXPLAIN (ANALYZE, BUFFERS)
SELECT * FROM measurement
WHERE logdate = '2023-01-15';
```

### 2. 分区连接优化

```sql
-- 分区间的连接优化
SELECT m.city_id, m.peaktemp, c.city_name
FROM measurement m
JOIN cities c ON m.city_id = c.city_id
WHERE m.logdate >= '2023-01-01' AND m.logdate < '2023-02-01';
```

## 最佳实践

### 1. 分区键选择

```sql
-- 好的分区键示例
CREATE TABLE event_logs (
    event_id    bigserial,
    event_type  text,
    created_at  timestamp,
    user_id     bigint
) PARTITION BY RANGE (created_at);  -- 时间序列数据

CREATE TABLE user_data (
    user_id     bigint,
    region      text,
    data        jsonb
) PARTITION BY LIST (region);       -- 地理分布

CREATE TABLE distributed_cache (
    key_hash    bigint,
    value       text
) PARTITION BY HASH (key_hash);     -- 均匀分布
```

**分区键选择原则**：
- 选择查询条件中常用的列
- 避免过于频繁更新的列
- 确保数据分布相对均匀
- 考虑业务查询模式

### 2. 分区数量控制

```sql
-- 建议的分区数量
-- 小型表（< 1GB）：不分区
-- 中型表（1-100GB）：10-50个分区
-- 大型表（> 100GB）：50-200个分区

-- 使用分区表视图来管理大量分区
CREATE VIEW recent_measurements AS
SELECT * FROM measurement
WHERE logdate >= CURRENT_DATE - INTERVAL '1 year';
```

### 3. 性能监控

```sql
-- 查看分区统计信息
SELECT
    schemaname,
    tablename,
    n_tup_ins,
    n_tup_upd,
    n_tup_del,
    n_live_tup,
    n_dead_tup
FROM pg_stat_user_tables
WHERE tablename LIKE 'measurement_%'
ORDER BY n_live_tup DESC;

-- 查看分区大小
SELECT
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
FROM pg_tables
WHERE tablename LIKE 'measurement_%'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

## 常见问题和解决方案

### 1. 分区裁剪不生效

```sql
-- 问题：查询没有触发分区裁剪
EXPLAIN SELECT * FROM measurement WHERE logdate = '2023-01-15';

-- 解决方案：确保分区键的条件是确定性的
-- 不要在分区键上使用函数
SELECT * FROM measurement
WHERE DATE_TRUNC('day', logdate) = '2023-01-15';  -- 不好

SELECT * FROM measurement
WHERE logdate >= '2023-01-15' AND logdate < '2023-01-16';  -- 好
```

### 2. 外键约束

```sql
-- 分区表的外键约束需要在每个分区上单独设置
CREATE TABLE orders (
    order_id    serial,
    customer_id int,
    ...
) PARTITION BY RANGE (order_date);

-- 创建分区
CREATE TABLE orders_2023_q1 PARTITION OF orders
    FOR VALUES FROM ('2023-01-01') TO ('2023-04-01');

-- 在分区上添加外键
ALTER TABLE orders_2023_q1
    ADD CONSTRAINT fk_customer
    FOREIGN KEY (customer_id) REFERENCES customers(id);
```

### 3. 唯一约束

```sql
-- 分区表的唯一约束必须包含分区键
CREATE TABLE users (
    id          serial,
    email       text,
    created_at  timestamp
) PARTITION BY RANGE (created_at);

-- 正确：唯一约束包含分区键
CREATE TABLE users_2023_q1 PARTITION OF users
    FOR VALUES FROM ('2023-01-01') TO ('2023-04-01');

-- 在主表上创建唯一约束
ALTER TABLE users
    ADD CONSTRAINT unique_email_created
    UNIQUE (email, created_at);
```

## 高级特性

### 1. 声明式分区（PostgreSQL 10+）

```sql
-- 现代分区方式（推荐）
CREATE TABLE measurement (
    city_id     int not null,
    logdate     date not null,
    peaktemp    int,
    unitsales   int
) PARTITION BY RANGE (logdate);
```

### 1. 分区表继承（PostgreSQL 10 之前）

不推荐使用这一分区方式，太复杂、维护困难。

```sql
-- 传统分区方式（不推荐用于新项目）
CREATE TABLE measurement (
    city_id     int not null,
    logdate     date not null,
    peaktemp    int,
    unitsales   int
);

CREATE TABLE measurement_2023_01 () INHERITS (measurement);

-- 添加约束
ALTER TABLE measurement_2023_01
    ADD CONSTRAINT measurement_2023_01_logdate_check
    CHECK (logdate >= '2023-01-01' AND logdate < '2023-02-01');

-- 创建触发器自动路由到正确分区
CREATE OR REPLACE FUNCTION measurement_insert_trigger()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.logdate >= '2023-01-01' AND NEW.logdate < '2023-02-01' THEN
        INSERT INTO measurement_2023_01 VALUES (NEW.*);
    ELSE
        RAISE EXCEPTION 'Date out of range';
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;
```



### 3. 混合分区策略

```sql
-- 复合分区：先按时间分区，再按地区子分区
CREATE TABLE orders (
    order_id    serial,
    customer_id int,
    region      text,
    order_date  date,
    amount      numeric
) PARTITION BY RANGE (order_date);

-- 创建月度分区
CREATE TABLE orders_2023_01 PARTITION OF orders
    FOR VALUES FROM ('2023-01-01') TO ('2023-02-01')
    PARTITION BY LIST (region);

-- 在月度分区内创建地区子分区
CREATE TABLE orders_2023_01_na PARTITION OF orders_2023_01
    FOR VALUES IN ('USA', 'Canada', 'Mexico');

CREATE TABLE orders_2023_01_eu PARTITION OF orders_2023_01
    FOR VALUES IN ('UK', 'Germany', 'France');
```

## 工具和扩展

### 1. pg_partman 扩展

```sql
-- 安装扩展
CREATE EXTENSION pg_partman;

-- 创建分区管理
SELECT partman.create_parent(
    p_parent_table => 'public.measurement',
    p_control => 'logdate',
    p_type => 'range',
    p_interval => '1 month',
    p_premake => 3
);

-- 自动维护分区
SELECT partman.run_maintenance();
```

### 2. 分区监控查询

```sql
-- 查看分区表信息
SELECT
    n.nspname as schema_name,
    c.relname as table_name,
    c.relkind as table_type,
    pg_size_pretty(pg_total_relation_size(c.oid)) as size
FROM pg_class c
JOIN pg_namespace n ON c.relnamespace = n.oid
WHERE c.relispartition OR c.relkind = 'p'
ORDER BY pg_total_relation_size(c.oid) DESC;

-- 查看分区边界
SELECT
    n.nspname as schema_name,
    c.relname as partition_name,
    pg_get_expr(c.relpartbound, c.oid) as partition_bounds
FROM pg_class c
JOIN pg_namespace n ON c.relnamespace = n.oid
WHERE c.relispartition
ORDER BY partition_name;
```

## 总结

表分区是 PostgreSQL 中处理大规模数据的重要技术。选择合适的分区策略和分区键对性能至关重要：

- **时间序列数据**：使用范围分区按时间划分
- **地理分布数据**：使用列表分区按地区划分
- **需要均匀分布**：使用哈希分区
- **复杂数据模式**：考虑混合分区策略

合理使用分区可以显著提升查询性能、简化数据维护，并为数据管理提供更大的灵活性。
