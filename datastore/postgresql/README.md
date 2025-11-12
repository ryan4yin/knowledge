# PostgreSQL 16 入门教程

欢迎来到 PostgreSQL 16 入门教程！PostgreSQL 是世界上最先进的开源关系型数据库管理系统，以其强大的功能、可扩展性和符合 SQL 标准而闻名。

## 教程内容

### [1. 基本命令](basics/README.md)
- psql 基本操作命令（\l、\c、\d、\dt 等）
- 数据库和表的基本操作
- SQL 基础语法

### [2. 数据类型](data-types/README.md)
- ARRAY 数组类型
- JSONB JSON 二进制类型
- TSRANGE 时间范围类型
- 其他 PostgreSQL 特有数据类型

### [3. 索引类型](indexes/README.md)
- B-Tree 索引
- 哈希索引
- GIN 索引
- GiST 索引
- SP-GiST 索引
- BRIN 索引
- 部分索引和表达式索引

### [4. 表分区](table-partitioning/README.md)
- 范围分区 (RANGE)
- 列表分区 (LIST)
- 哈希分区 (HASH)
- 分区管理和维护
- 查询优化和最佳实践

### [5. 扩展机制](extensions/README.md)
- PostgreSQL 扩展系统介绍
- 常用扩展（PostGIS、pg_stat_statements 等）
- 创建自定义扩展

### [7. 与 MySQL 的区别](mysql-comparison/README.md)
- PostgreSQL 与 MySQL 主要区别速查表
- 迁移指南

### [8. 备份与恢复](backup-recovery/README.md)
- WAL (Write-Ahead Logging) 机制
- 逻辑备份与物理备份
- 时间点恢复

### [9. 插件原理与使用](plugins/README.md)
- 插件工作原理
- 安装与配置常用插件
- 插件开发基础

### [10. 最佳实践](best-practices/README.md)
- 数据库设计原则
- 性能优化建议
- 安全配置

### [11. 常用函数](functions/README.md)
- 字符串函数
- 数值函数
- 日期时间函数
- 窗口函数
- 聚合函数

### [12. 性能优化](performance/README.md)
- 慢查询分析
- 查询计划分析
- 性能调优技巧

### [13. 用户与权限管理](security/README.md)
- 用户管理
- 角色和权限
- 认证方法

### [14. 服务器配置](admin/README.md)
- postgresql.conf 配置
- pg_hba.conf 访问控制
- 连接池配置

### [15. 故障排查](troubleshooting/README.md)
- 常见问题与解决方案
- 日志分析
- 性能监控

### [16. 实践示例](examples/README.md)
- 实际应用场景示例
- SQL 查询示例
- 数据库操作示例

## 快速开始

### 安装 PostgreSQL

#### Ubuntu/Debian
```bash
sudo apt update
sudo apt install postgresql-16 postgresql-contrib-16
```

#### CentOS/RHEL
```bash
sudo dnf install postgresql16-server postgresql16
sudo postgresql-16-setup initdb
sudo systemctl enable postgresql-16
sudo systemctl start postgresql-16
```

#### macOS
```bash
brew install postgresql@16
brew services start postgresql@16
```

### 连接到 PostgreSQL

```bash
# 使用操作系统用户连接
sudo -u postgres psql

# 连接到特定数据库
psql -h localhost -p 5432 -U username -d database_name
```

### 创建数据库和用户

```sql
-- 创建数据库
CREATE DATABASE myapp;

-- 创建用户
CREATE USER myuser WITH PASSWORD 'secure_password';

-- 授权
GRANT ALL PRIVILEGES ON DATABASE myapp TO myuser;
```

## 学习建议

1. **循序渐进**：按照教程顺序逐步学习，先掌握基本命令，再学习高级特性
2. **实践为主**：每个章节都包含实际示例，建议在本地环境中动手操作
3. **查阅官方文档**：PostgreSQL 官方文档是最权威的参考资料
4. **参与社区**：遇到问题时可以到 PostgreSQL 社区寻求帮助

## 参考资源

- [PostgreSQL 16 官方文档](https://www.postgresql.org/docs/16/)
- [PostgreSQL Wiki](https://wiki.postgresql.org/)
- [Planet PostgreSQL](https://planet.postgresql.org/)
- [PostgreSQL 邮件列表](https://www.postgresql.org/list/)

## 许可证

本教程遵循 CC BY-SA 4.0 许可证，欢迎分享和改进。
