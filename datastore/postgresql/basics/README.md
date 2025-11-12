# PostgreSQL psql 常用命令

本章节介绍 PostgreSQL 交互式终端 psql 的常用元命令（以反斜杠 `\` 开头的命令）。

> 另外第三方客户端 pgcli 也挺流行。

## 常用数据库命令

### `\l` - 列出数据库
```bash
# 列出所有数据库
\l

# 带详细信息（包括大小）
\l+
```

### `\c` - 连接数据库
```bash
# 连接到指定数据库
\c myapp

# 连接指定数据库和用户
\c myapp myuser
```

## 常用表命令

### `\d` - 查看表结构
```bash
# 查看指定表结构
\d users

# 查看所有表
\dt

# 查看表的详细信息（包括索引）
\d+ users
```

### `\du` - 查看用户角色
```bash
# 列出所有用户角色
\du

# 查看用户的详细信息
\du+
```

## 实用命令

### `\x` - 扩展显示模式
```bash
# 切换扩展显示（每列一行显示）
\x

# 扩展模式输出示例：
-[ RECORD 1 ]-
id        | 1
name      | John Doe
email     | john@example.com
```

### `\copy` - 数据导入导出
```bash
# 从 CSV 文件导入数据
\copy users FROM 'users.csv' WITH CSV HEADER;

# 导出数据到 CSV 文件
\copy users TO 'users_backup.csv' WITH CSV HEADER;
```

### `\h` - SQL 帮助
```bash
# 显示 SQL 命令帮助
\h CREATE TABLE
\h SELECT
```

### 实用技巧

1. **Tab 自动补全**：输入表名或命令前几个字符后按 Tab 键
2. **命令历史**：使用上下箭头键浏览历史命令
3. **退出**：`\q` 退出 psql
4. **执行文件**：`\i script.sql` 执行 SQL 文件
