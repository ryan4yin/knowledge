# SQLite 入门教程

SQLite 是一个轻量级的嵌入式关系型数据库，广泛用于移动应用、桌面应用和小型 Web 应用。本教程帮助你快速掌握 SQLite 的使用。

## 为什么选择 SQLite？

### 🚀 核心优势
- **零配置**：无需安装和配置，开箱即用
- **轻量级**：单文件数据库，内存占用极小
- **嵌入式**：直接集成到应用程序中
- **跨平台**：支持所有主流操作系统
- **事务支持**：完整的 ACID 事务特性
- **SQL 标准**：兼容大部分 SQL-92 标准

### 🎯 适用场景
- 移动应用 (Android/iOS)
- 桌面应用
- 小型 Web 应用后端
- 数据分析原型
- 测试和开发环境
- IoT 设备数据存储

## 快速开始

### 安装和配置

#### Windows
```bash
# 下载 SQLite 工具
# https://sqlite.org/download.html

# 使用 Chocolatey 安装
choco install sqlite

# 使用 Scoop 安装
scoop install sqlite
```

#### macOS
```bash
# 使用 Homebrew 安装
brew install sqlite

# 使用 MacPorts 安装
sudo port install sqlite3
```

#### Linux (Ubuntu/Debian)
```bash
# 使用 apt 安装
sudo apt update
sudo apt install sqlite3

# 使用 yum 安装 (CentOS/RHEL)
sudo yum install sqlite3
```

### 第一个数据库

```bash
# 创建并连接到数据库
sqlite3 myapp.db

# 查看帮助
.help

# 退出
.quit
```

## 基本操作

### 数据库管理

```sql
-- 查看当前数据库文件
.database

-- 查看所有表
.tables

-- 查看表结构
.schema users

-- 查看特定表结构
.schema products

-- 查看创建表的 SQL 语句
.schema users CREATE TABLE

-- 列出数据库的设置信息
.show
```

### 表操作

```sql
-- 创建表
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    age INTEGER CHECK (age >= 0),
    status TEXT DEFAULT 'active'
);

-- 创建带复合键的表
CREATE TABLE user_scores (
    user_id INTEGER,
    game_id INTEGER,
    score INTEGER,
    played_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, game_id),
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- 修改表结构
ALTER TABLE users ADD COLUMN phone TEXT;
ALTER TABLE users RENAME COLUMN phone TO phone_number;
ALTER TABLE users DROP COLUMN phone_number;

-- 删除表
DROP TABLE user_scores;
```

### 数据操作

```sql
-- 插入单条记录
INSERT INTO users (name, email, age)
VALUES ('张三', 'zhangsan@example.com', 25);

-- 插入多条记录
INSERT INTO users (name, email, age) VALUES
('李四', 'lisi@example.com', 30),
('王五', 'wangwu@example.com', 28);

-- 使用 DEFAULT 值
INSERT INTO users (name, email) VALUES ('赵六', 'zhaoliu@example.com');

-- 更新数据
UPDATE users SET age = 26 WHERE id = 1;
UPDATE users SET email = 'newemail@example.com', age = age + 1 WHERE id = 2;

-- 删除数据
DELETE FROM users WHERE id = 3;
DELETE FROM users WHERE created_at < '2023-01-01';

-- 清空表（保留表结构）
DELETE FROM users;
```

### 查询操作

```sql
-- 基本查询
SELECT * FROM users;
SELECT name, email FROM users WHERE age > 25;

-- 条件查询
SELECT * FROM users WHERE age BETWEEN 20 AND 30;
SELECT * FROM users WHERE name LIKE '张%';
SELECT * FROM users WHERE email IN ('zhangsan@example.com', 'lisi@example.com');

-- 排序
SELECT * FROM users ORDER BY age DESC;
SELECT * FROM users ORDER BY name ASC, age DESC;

-- 限制结果数量
SELECT * FROM users LIMIT 5;
SELECT * FROM users ORDER BY age DESC LIMIT 3;

-- 聚合查询
SELECT COUNT(*) as total_users FROM users;
SELECT COUNT(DISTINCT age) as distinct_ages FROM users;
SELECT AVG(age) as avg_age FROM users;
SELECT MAX(age) as max_age, MIN(age) as min_age FROM users;
SELECT COUNT(*) as users, AVG(age) as avg_age FROM users GROUP BY status;

-- 子查询
SELECT * FROM users
WHERE age > (SELECT AVG(age) FROM users);
```

## 数据类型详解

### 数值类型

```sql
-- 整数类型
CREATE TABLE numbers (
    tiny_int TINYINT,           -- 1 byte: -128 到 127
    small_int SMALLINT,         -- 2 bytes: -32768 到 32767
    medium_int MEDIUMINT,       -- 3 bytes: -8388608 到 8388607
    int INTEGER,                -- 4 bytes: -2147483648 到 2147483647
    big_int BIGINT              -- 8 bytes: -9223372036854775808 到 9223372036854775807
);

-- 浮点类型
CREATE TABLE measurements (
    float_val FLOAT,             -- 4 bytes: 单精度浮点数
    double_val DOUBLE,           -- 8 bytes: 双精度浮点数
    real_val REAL                -- 8 bytes: 双精度浮点数 (别名)
);

-- 自动递增
CREATE TABLE auto_increment_test (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT
);
```

### 字符串类型

```sql
CREATE TABLE text_examples (
    title TEXT,                  -- 可变长度字符串
    description TEXT(100),        -- 带长度限制
    content BLOB,               -- 二进制大对象
    fixed_char CHAR(10),         -- 固定长度字符串
    note STRING                  -- TEXT 的别名
);

-- 插入示例
INSERT INTO text_examples (title, description, note)
VALUES ('SQLite 入门', 'SQLite 数据库教程', '轻量级数据库');
```

### 日期时间类型

```sql
CREATE TABLE time_examples (
    id INTEGER PRIMARY KEY,
    date_created DATE,           -- YYYY-MM-DD
    time_created TIME,           -- HH:MM:SS
    datetime_created DATETIME,    -- YYYY-MM-DD HH:MM:SS
    timestamp TIMESTAMP,         -- Unix 时间戳
    current_time DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 日期时间函数
SELECT CURRENT_DATE;              -- 当前日期
SELECT CURRENT_TIME;              -- 当前时间
SELECT CURRENT_TIMESTAMP;         -- 当前时间戳
SELECT datetime('now');           -- 当前日期时间
SELECT date('now');                -- 当前日期
SELECT time('now');                -- 当前时间
SELECT strftime('%Y-%m', '2023-12-25'); -- 日期格式化
```

## 约束和索引

### 约束

```sql
-- 创建带约束的表
CREATE TABLE products (
    id INTEGER PRIMARY KEY,                    -- 主键约束
    name TEXT NOT NULL,                           -- 非空约束
    price REAL CHECK (price >= 0),              -- 检查约束
    category TEXT DEFAULT 'uncategorized',       -- 默认值
    sku TEXT UNIQUE,                              -- 唯一约束
    stock INTEGER DEFAULT 0,                     -- 默认值
    FOREIGN KEY (category) REFERENCES categories(id) -- 外键约束
);

-- 添加约束
ALTER TABLE products ADD CONSTRAINT positive_price
CHECK (price >= 0);
```

### 索引

```sql
-- 创建索引
CREATE INDEX idx_users_name ON users(name);
CREATE INDEX idx_users_age ON users(age);
CREATE UNIQUE INDEX idx_users_email ON users(email);

-- 复合索引
CREATE INDEX idx_users_age_status ON users(age, status);

-- 查看索引
PRAGMA index_list(products);

-- 查看索引信息
PRAGMA index_info(idx_users_name);

-- 删除索引
DROP INDEX idx_users_name;
```

## 事务处理

### 基本事务

```sql
-- 开启事务
BEGIN TRANSACTION;

-- 执行多个 SQL 语句
UPDATE accounts SET balance = balance - 100 WHERE id = 1;
UPDATE accounts SET balance = balance + 100 WHERE id = 2;

-- 检查结果
SELECT * FROM accounts WHERE id IN (1, 2);

-- 提交事务
COMMIT;

-- 或者回滚事务
ROLLBACK;
```

### 事务隔离级别

```sql
-- SQLite 默认使用 SERIALIZABLE 隔离级别
PRAGMA read_uncommitted = 0;  -- 0: off, 1: on (默认关闭)
PRAGMA read_committed = 1;      -- 0: off, 1: on (默认开启)
PRAGMA write_aware_locking = 1;    -- 0: off, 1: on (默认开启)

-- 查看当前设置
PRAGMA compile_options;
```

## 触发器和视图

### 触发器

```sql
-- 创建触发器日志表
CREATE TABLE audit_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    table_name TEXT,
    operation TEXT,
    old_data TEXT,
    new_data TEXT,
    changed_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 创建 AFTER INSERT 触发器
CREATE TRIGGER audit_user_insert
AFTER INSERT ON users
FOR EACH ROW
BEGIN
    INSERT INTO audit_log (table_name, operation, new_data)
    VALUES ('users', 'INSERT', json_object('name', NEW.name, 'email', NEW.email));
END;

-- 创建 BEFORE UPDATE 触发器
CREATE TRIGGER audit_user_update
BEFORE UPDATE ON users
FOR EACH ROW
BEGIN
    INSERT INTO audit_log (table_name, operation, old_data, new_data)
    VALUES ('users', 'UPDATE',
           json_object('name', OLD.name, 'email', OLD.email),
           json_object('name', NEW.name, 'email', NEW.email));
END;
```

### 视图

```sql
-- 创建视图
CREATE VIEW user_summary AS
SELECT
    id,
    name,
    email,
    age,
    status,
    CASE
        WHEN age < 25 THEN 'Young'
        WHEN age < 35 THEN 'Adult'
        ELSE 'Senior'
    END as age_group
FROM users;

-- 查询视图
SELECT * FROM user_summary WHERE age_group = 'Adult';

-- 创建只读视图
CREATE READONLY VIEW active_users AS
SELECT * FROM users WHERE status = 'active';
```

## 高级功能

### 窗口函数 (SQLite 3.25+)

```sql
-- 创建测试数据
CREATE TABLE sales (
    id INTEGER PRIMARY KEY,
    sales_date DATE,
    product TEXT,
    amount REAL,
    region TEXT
);

INSERT INTO sales VALUES
(1, '2023-12-01', 'Product A', 100.00, 'North'),
(2, '2023-12-02', 'Product A', 150.00, 'North'),
(3, '2023-12-02', 'Product B', 80.00, 'South'),
(4, '2023-12-03', 'Product A', 200.00, 'East'),
(5, '2023-12-03', 'Product B', 120.00, 'East');

-- 窗口函数查询
SELECT
    sales_date,
    product,
    amount,
    SUM(amount) OVER (PARTITION BY product ORDER BY sales_date) as running_total,
    AVG(amount) OVER (PARTITION BY product ORDER BY sales_date
                     ROWS BETWEEN 2 PRECEDING AND 2 FOLLOWING) as moving_avg,
    ROW_NUMBER() OVER (PARTITION BY region ORDER BY amount DESC) as rank_in_region
FROM sales
ORDER BY sales_date, product;
```

### JSON 支持 (SQLite 3.38+)

SQLite 3.38+ 引入了原生的 JSON 数据类型，3.45 引入了类似 PostgreSQL 的 JSONB 二进制格式，JSON 相关操作系统大幅提升。

```sql
-- 创建 JSON 数据表
CREATE TABLE json_data (
    id INTEGER PRIMARY KEY,
    metadata JSON,
    config JSONB DEFAULT '{}',
    tags JSON DEFAULT '[]'
);

-- 插入 JSON 数据
INSERT INTO json_data VALUES
(1, '{"name": "John", "age": 30, "skills": ["JavaScript", "Python"]}',
   '{"theme": "dark", "notifications": true}',
   '["database", "sql", "nosql"]'),
(2, '{"name": "Jane", "age": 25, "skills": ["Python", "Java"]}',
   '{"theme": "light", "notifications": false}',
   '["web", "frontend", "backend"]');

-- JSON 路径查询函数
SELECT
    id,
    json_extract(metadata, '$.name') as name,
    json_extract(metadata, '$.age') as age,
    json_extract(metadata, '$.skills') as skills,
    json_extract(metadata, '$.skills[0]') as primary_skill,
    json_array_length(json_extract(metadata, '$.skills')) as skill_count
FROM json_data;

-- JSONB 提供了更高效的 JSON 存储
SELECT
    id,
    json_extract(config, '$.theme') as theme,
    json_extract(config, '$.notifications') as notifications
FROM json_data;

-- JSON 数组操作
SELECT
    id,
    json_extract(tags, '$[0]') as first_tag,
    json_extract(tags, '$[#-1]') as last_tag,
    json_array_length(tags) as tag_count
FROM json_data;

-- JSON 条件查询
SELECT * FROM json_data
WHERE json_extract(metadata, '$.age') > 25;

-- JSON 操作符
SELECT
    metadata ->> '$.name' as name,           -- SQLite 3.38+ 新语法
    metadata ->> '$.skills[0]' as skill,
    json_extract(metadata, '$.age') as age   -- 传统的 json_extract 仍然有效
FROM json_data;

-- JSON 比较操作
SELECT * FROM json_data
WHERE metadata ->> '$.skills' json '["JavaScript", "Python"]';  -- 数组包含
```

### JSON 存储和性能

```sql
-- JSON vs JSONB 性能比较
CREATE TABLE json_performance (
    id INTEGER PRIMARY KEY,
    json_data JSON,
    jsonb_data JSONB
);

-- 查看存储效率
PRAGMA table_info(json_performance);

-- JSON 类型存储文本形式，便于读取但占用更多空间
-- JSONB 类型存储二进制形式，更紧凑但需要转换

-- JSON 验证
SELECT json_valid('{"name": "test"}');  -- 返回 1
SELECT json_valid('invalid json');    -- 返回 0
```

### JSON 与文本数据类型对比

```sql
-- SQLite JSON 类型与传统 TEXT 类型的区别

-- 1. 自动解析和验证
CREATE TABLE comparison_table (
    id INTEGER PRIMARY KEY,
    json_field JSON,           -- 自动验证 JSON 格式
    text_field TEXT            -- 纯文本存储，无验证
);

INSERT INTO comparison_table VALUES
(1, '{"name": "test", "age": 30}', '{"name": "test", "age": "invalid json"}');  -- 第一个会成功，第二个也会成功，但 json 字段可能无法索引

-- 2. 索引支持
-- SQLite 可以为 JSON 字段中的路径创建表达式索引
CREATE INDEX idx_json_name ON json_data ((metadata ->> '$.name'));

-- 3. 查询性能
-- JSON 字段支持高效的路径查询
-- TEXT 字段需要使用 json_extract 函数，可能较慢

-- 4. 数据完整性
-- JSON 字段确保存储的是有效 JSON
-- TEXT 字段可以存储任意文本
```

### 高级 JSON 功能

```sql
-- JSON 构造函数
SELECT
    json_object(
        'name', 'John',
        'age', 30,
        'skills', json_array('SQL', 'NoSQL')
    ) as user_json;

-- JSON 聚合
SELECT
    json_patch(
        '{"name": "John", "age": 30}',
        '{"age": 35, "active": true}'
    ) as updated_json;

-- JSON 路径检查
SELECT
    json_typeof(json_extract(metadata, '$.age')) as age_type,
    json_extract(metadata, '$.nonexistent') as missing_field
FROM json_data;

-- JSON 深度遍历 (SQLite 3.38.2+)
-- 注意：SQLite 对复杂 JSON 遍历的支持有限
-- 对于复杂的 JSON 操作，建议在应用层处理
```

### 使用建议

```sql
-- 选择合适的 JSON 类型：
-- 1. 结构化的 JSON 数据：使用 JSON 类型
-- 2. 频繁查询的 JSON 字段：考虑 JSONB
-- 3. 大型 JSON 文档：在应用层处理

-- 性能优化提示：
-- 1. 避免过深的 JSON 嵌套
-- 2. 为常用查询路径创建表达式索引
-- 3. 对于复杂 JSON 操作，考虑应用层处理
```

### FTS (全文搜索)

```sql
-- 创建 FTS 虚拟表
CREATE VIRTUAL TABLE documents_fts USING fts5(
    title TEXT,
    content TEXT,
    tags TEXT
);

-- 插入数据
INSERT INTO documents_fts (title, content, tags)
VALUES ('SQLite Tutorial', 'Learn SQLite database', 'database,tutorial'),
('JavaScript Guide', 'Modern JavaScript', 'javascript,web');

-- 全文搜索
SELECT title, snippet(documents_fts, 0, '<b>', '</b>', '...', 2) as content_snippet
FROM documents_fts
WHERE documents_fts MATCH 'sqlite OR database';

-- 查询匹配详情
SELECT highlight(documents_fts, 1, '<mark>', '</mark>') as highlighted_content
FROM documents_fts
WHERE documents_fts MATCH 'tutorial';
```

## 性能优化

### 查询优化技巧

```sql
-- 使用 EXPLAIN QUERY PLAN 查看执行计划
EXPLAIN QUERY PLAN SELECT * FROM users WHERE age > 25;

-- 使用 ANALYZE 分析查询性能
EXPLAIN QUERY PLAN SELECT * FROM users WHERE age > 25;

-- 避免全表扫描
CREATE INDEX idx_users_age ON users(age);  -- 为查询字段创建索引

-- 使用 LIMIT 限制结果
SELECT * FROM large_table ORDER BY created_at DESC LIMIT 100;

-- 使用 EXISTS 替代 IN
SELECT u.* FROM users u
WHERE EXISTS (SELECT 1 FROM orders o WHERE o.user_id = u.id);

-- 使用批量插入
INSERT INTO users (name, email, age) VALUES
('User1', 'user1@example.com', 25),
('User2', 'user2@example.com', 30);
```

### 配置优化

```sql
-- 性能相关设置
PRAGMA journal_mode = WAL;                    -- 使用 WAL 模式
PRAGMA synchronous = NORMAL;                 -- 平衡性能和安全性
PRAGMA cache_size = 10000;                    -- 缓存大小 (页数)
PRAGMA temp_store = MEMORY;                  -- 临时表存储在内存
PRAGMA mmap_size = 268435456;               -- 内存映射大小

-- 查看当前设置
PRAGMA journal_mode;
PRAGMA synchronous;
PRAGMA cache_size;

-- 启用外键约束
PRAGMA foreign_keys = ON;

-- 启用自动清理
PRAGMA auto_vacuum = INCREMENTAL;
PRAGMA incremental_vacuum = 100000;
```

## 实用工具和命令

### SQLite 命令行工具

```bash
# 启动 SQLite
sqlite3 mydb.db

# 导入 SQL 文件
sqlite3 mydb.db < schema.sql

# 导出数据库
sqlite3 mydb.db .dump > backup.sql

-- 导出特定表
sqlite3 mydb.db ".dump users" > users_backup.sql

-- 导出为 CSV
.mode csv
.headers on
.output users.csv
SELECT * FROM users;

-- 执行 SQL 文件
sqlite3 mydb.db ".read queries.sql"

-- 查看表结构
.schema
.schema users

-- 查看所有索引
.indices

-- 查看触发器
.triggers

-- 查看视图
.views

# 退出
.quit
```

### 数据库维护

```sql
-- 分析表统计信息
ANALYZE users;

-- 重建表（优化存储）
VACUUM users;

-- 压缩数据库
VACUUM;

-- 检查数据库完整性
PRAGMA integrity_check;

-- 优化数据库
PRAGMA optimize;

-- 查看数据库信息
PRAGMA table_info(users);
PRAGMA foreign_key_list(users);
PRAGMA index_list(users);
```

## Python 集成

### 使用 sqlite3 模块

```python
import sqlite3
from datetime import datetime

# 连接数据库
conn = sqlite3.connect('myapp.db')
cursor = conn.cursor()

# 创建表
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
''')

# 插入数据
users = [
    ('Alice', 'alice@example.com'),
    ('Bob', 'bob@example.com'),
    ('Charlie', 'charlie@example.com')
]

cursor.executemany(
    'INSERT INTO users (name, email) VALUES (?, ?)', users
)

# 查询数据
cursor.execute('SELECT * FROM users')
users = cursor.fetchall()

for user in users:
    print(f"ID: {user[0]}, Name: {user[1]}, Email: {user[2]}")

# 提交事务
conn.commit()

# 关闭连接
conn.close()
```

### 使用 SQLAlchemy

```python
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

# 创建模型
class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.now)

# 创建连接
engine = create_engine('sqlite:///myapp.db')
Base.metadata.create_all(engine)

# 创建会话
Session = sessionmaker(bind=engine)
session = Session()

# 添加数据
user = User(name='Alice', email='alice@example.com')
session.add(user)
session.commit()

# 查询数据
users = session.query(User).all()
for user in users:
    print(f"{user.name}: {user.email}")

session.close()
```

## 常见问题和解决方案

### 常见错误

```sql
-- 错误: "table already exists"
-- 解决：使用 IF NOT EXISTS
CREATE TABLE IF NOT EXISTS users (...)

-- 错误: "UNIQUE constraint failed"
-- 解决：插入前检查或使用 INSERT OR REPLACE
INSERT OR REPLACE INTO users (id, name, email) VALUES (1, 'Alice', 'alice@example.com');

-- 错误: "no such table"
-- 解决：检查表名是否正确，或先创建表
.tables

-- 错误: "foreign key constraint failed"
-- 解决：确保引用的记录存在
PRAGMA foreign_keys = ON;  -- 启用外键检查
```

### 性能问题

```sql
-- 问题：查询速度慢
-- 解决：
-- 1. 添加索引
CREATE INDEX idx_users_email ON users(email);

-- 2. 优化查询
SELECT id, name FROM users WHERE status = 'active'  -- 只选择需要的列

-- 3. 使用 EXPLAIN 分析执行计划
EXPLAIN QUERY PLAN SELECT * FROM users WHERE name = 'Alice';

-- 4. 使用 LIMIT 限制结果
SELECT * FROM large_table ORDER BY created_at DESC LIMIT 100;
```

## 学习资源

### 官方文档
- [SQLite 官方文档](https://sqlite.org/docs.html)
- [SQLite 语言规范](https://sqlite.org/lang.html)
- [SQLite 命令行工具](https://sqlite.org/cli.html)

### 推荐工具
- **DB Browser for SQLite**: 图形化数据库管理工具
- **SQLiteStudio**: 跨平台 SQLite 管理工具
- **SQLiteStudio**: 免费的 SQLite 数据库管理工具

### 学习路径
1. **基础入门**: 安装配置、基本SQL语法
2. **进阶使用**: 索引、事务、触发器
3. **性能优化**: 查询优化、配置调整
4. **应用集成**: Python、Java、JavaScript 集成
5. **高级特性**: FTS、JSON、窗口函数

通过这个教程，你已经掌握了 SQLite 的核心概念和使用方法。继续实践和探索更高级的功能，将帮助你成为 SQLite 数据库专家！
