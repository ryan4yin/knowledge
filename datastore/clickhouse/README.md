# ClickHouse 实战教程

欢迎来到 ClickHouse 实战教程！ClickHouse 是世界上最快的开源列式分析型数据库，专为实时数据处理和分析而设计。本教程专注于实战应用，帮助你掌握 ClickHouse 的核心技能。

## 教程路径

### 🚀 [快速入门](quickstart/README.md)
- 5 分钟上手 ClickHouse
- Docker 快速部署
- 第一个分析查询

### 🏗️ [架构与模式设计](schema-design/README.md)
- ClickHouse 存储原理
- 数据建模最佳实践
- 分区和排序键设计
- 表引擎选择指南

### ⚡ [MergeTree 深度解析](merge-tree-engine/README.md)
- MergeTree 系列引擎详解
- 数据分区策略
- 主键设计原则
- TTL 和数据生命周期管理

### 🎯 [性能调优实战](performance-tuning/README.md)
- 查询优化技巧
- 写入性能优化
- 内存管理
- 配置参数调优

### 📊 [实时分析案例](realtime-analytics/README.md)
- 用户行为分析
- 监控指标处理
- 日志分析实战
- 实时看板构建

### 🌐 [集群部署与管理](clustering/README.md)
- 分布式集群搭建
- 数据分片策略
- 复制和高可用
- 负载均衡

### 📈 [监控与运维](monitoring/README.md)
- 系统监控指标
- 日志分析
- 故障排查
- 性能基准测试

### 💡 [最佳实践与案例](best-practices/README.md)
- 生产环境部署经验
- 常见陷阱和解决方案
- 大厂案例分析
- 性能调优模板

## 为什么选择 ClickHouse？

### 🚀 极致性能
- **查询速度**: 单节点处理速度可达 1-10 GB/s
- **实时插入**: 支持每秒百万级记录写入
- **压缩比**: 列式存储带来 5-10 倍压缩比

### 📊 分析场景完美匹配
- **列式存储**: 分析查询性能极佳
- **向量化执行**: 充分利用现代 CPU
- **预计算**: 物化视图支持实时聚合

### 🔄 实时处理
- **实时写入**: 无锁插入，高并发支持
- **增量计算**: 支持流式数据处理
- **实时查询**: 秒级响应复杂分析

### 📈 海量数据
- **PB 级扩展**: 线性扩展到 PB 级数据
- **分布式架构**: 原生分布式设计
- **高可用**: 自动故障转移

## 典型应用场景

### 🎯 用户行为分析
```sql
-- 实时统计用户活跃度
SELECT
    toStartOfHour(event_time) as hour,
    countDistinct(user_id) as active_users,
    count() as total_events
FROM events
WHERE event_date >= today()
GROUP BY hour
ORDER BY hour DESC;
```

### 📊 监控指标分析
```sql
-- 服务监控指标趋势
SELECT
    service_name,
    quantile(0.50)(response_time) as p50,
    quantile(0.95)(response_time) as p95,
    quantile(0.99)(response_time) as p99
FROM metrics
WHERE timestamp >= now() - INTERVAL 1 HOUR
GROUP BY service_name;
```

### 📈 业务数据分析
```sql
-- 销售漏斗分析
SELECT
    date,
    uniqExact(user_id) as visitors,
    uniqExactIf(user_id, action = 'add_to_cart') as cart_adds,
    uniqExactIf(user_id, action = 'purchase') as purchases,
    purchases / visitors * 100 as conversion_rate
FROM events
WHERE action IN ('visit', 'add_to_cart', 'purchase')
GROUP BY date
ORDER BY date DESC;
```

## 快速体验

### 使用 Docker 启动
```bash
# 启动 ClickHouse 服务
docker run -d --name clickhouse-server \
  -p 8123:8123 -p 9000:9000 \
  clickhouse/clickhouse-server

# 连接客户端
docker exec -it clickhouse-server clickhouse-client

# 测试查询
SELECT 'Hello ClickHouse!' as greeting;
```

### HTTP 接口体验
```bash
# 通过 HTTP 接口查询
curl "http://localhost:8123/?query=SELECT%20version()"

# 插入数据
curl -X POST "http://localhost:8123/" \
  --data "INSERT INTO test.table VALUES (1, 'test'), (2, 'data')"
```

## 学习路径建议

### 初学者（第1-2周）
1. 熟悉基本概念和安装
2. 掌握基础查询语法
3. 理解表引擎基本使用
4. 完成简单分析案例

### 进阶用户（第3-4周）
1. 深入理解 MergeTree 引擎
2. 掌握分区和排序键设计
3. 学习性能调优技巧
4. 构建实时分析系统

### 专家级（第1-2个月）
1. 集群部署和管理
2. 复杂查询优化
3. 生产环境运维
4. 大规模数据处理

## 核心概念速览

### 表引擎
- **MergeTree**: 主引擎，支持分区和索引
- **ReplacingMergeTree**: 去重功能
- **AggregatingMergeTree**: 聚合功能
- **ReplicatedMergeTree**: 副本功能

### 数据类型
- **数值型**: UInt8/16/32/64, Int8/16/32/64, Float32/64
- **字符串型**: String, FixedString
- **时间型**: Date, DateTime, DateTime64
- **特殊型**: UUID, IPv4/IPv6, Array, Tuple, Nested

### 索引
- **主键**: 排序键，决定物理存储顺序
- **跳数索引**: 加速查询条件过滤
- **二级索引**: 在 MergeTree 中支持

## 社区与支持

- [官方文档](https://clickhouse.com/docs/)
- [GitHub 仓库](https://github.com/ClickHouse/ClickHouse)
- [中文社区](https://github.com/ClickHouse/clickhouse-docs-cn)
- [在线体验](https://play.clickhouse.com/)

---

开始你的 ClickHouse 实战之旅吧！从快速入门开始，逐步深入到高级优化和生产部署。