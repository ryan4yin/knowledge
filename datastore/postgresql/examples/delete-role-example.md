# 角色删除操作示例

本文件展示如何使用 PostgreSQL 角色删除脚本的实际操作流程。

## 准备工作

### 1. 设置测试环境

```sql
-- 创建测试数据库
CREATE DATABASE test_cleanup;

-- 创建测试角色
CREATE USER old_user WITH PASSWORD 'old_pass';
CREATE USER admin_user WITH PASSWORD 'admin_pass' SUPERUSER;

-- 创建测试表
\c test_cleanup
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    email VARCHAR(100)
);

-- 将表的所有权给 old_user
ALTER TABLE users OWNER TO old_user;
ALTER SEQUENCE users_id_seq OWNER TO old_user;

-- 授予一些权限
GRANT SELECT ON users TO old_user;
GRANT USAGE ON SCHEMA public TO old_user;
```

### 2. 设置默认权限（制造困难）

```sql
-- 切换到 old_user 来设置默认权限
SET ROLE old_user;

-- 设置默认权限
ALTER DEFAULT PRIVILEGES
FOR ROLE admin_user
GRANT SELECT ON TABLES TO admin_user;

-- 恢复角色
RESET ROLE;
```

## 查询当前状态

### 检查对象所有权

```sql
SELECT
    n.nspname as schema,
    c.relname as object,
    c.relkind as type,
    r.rolname as owner
FROM pg_class c
JOIN pg_namespace n ON n.oid = c.relnamespace
JOIN pg_roles r ON r.oid = c.relowner
WHERE r.rolname = 'old_user';
```

**输出：**
```
 schema | object        | type | owner
--------+---------------+------+---------
 public | users         | r    | old_user
 public | users_id_seq  | S    | old_user
```

### 检查权限授予

```sql
SELECT * FROM information_schema.role_table_grants
WHERE grantee = 'old_user';
```

### 检查共享依赖

```sql
SELECT
    db.datname,
    classid::regclass,
    objid,
    deptype
FROM pg_shdepend s
LEFT JOIN pg_database db ON s.dbid = db.oid
WHERE refobjid = (SELECT oid FROM pg_roles WHERE rolname = 'old_user');
```

## 执行删除操作

### 方式一：手动执行

```sql
-- 步骤 1：身份继承
GRANT old_user TO admin_user;
GRANT admin_user TO admin_user;

-- 步骤 2：资产转移
REASSIGN OWNED BY old_user TO admin_user;

-- 步骤 3：依赖抹除
DROP OWNED BY old_user;

-- 步骤 4：物理删除
DROP ROLE old_user;

-- 步骤 5：清理身份继承
REVOKE old_user FROM admin_user;
```

### 方式二：使用 delete-user.sql

```bash
# 修改脚本配置
vim ../security/delete-user.sql
# 修改：v_old_user := 'old_user'
# 修改：v_target_user := 'admin_user'

# 执行脚本
psql -d test_cleanup -f ../security/delete-user.sql
```

**脚本输出：**
```
================================================
开始清理角色: old_user
当前数据库: test_cleanup
================================================
✓ 已获取角色身份权限
✓ 已转移当前数据库中的所有资产
✓ 已抹除当前数据库中的所有权限依赖
================================================
✓✓✓ 角色 old_user 已被彻底删除！
================================================
✓ 已清理临时身份继承关系
```

## 验证结果

### 检查角色是否已删除

```sql
SELECT rolname FROM pg_roles WHERE rolname = 'old_user';
```

**预期输出：空结果**

### 检查表的所有权

```sql
SELECT
    c.relname as table_name,
    r.rolname as owner
FROM pg_class c
JOIN pg_roles r ON r.oid = c.relowner
WHERE c.relname = 'users';
```

**输出：**
```
 table_name | owner
-----------+-----------
 users     | admin_user
```

### 验证表仍然可用

```sql
-- 测试表是否正常工作
INSERT INTO users (name, email) VALUES ('Test User', 'test@example.com');
SELECT * FROM users;
```

## 清理测试环境

```sql
-- 删除测试表
DROP TABLE users;

-- 删除测试数据库
DROP DATABASE test_cleanup;

-- 删除测试角色
DROP USER admin_user;
```

## 多数据库场景示例

### 创建多数据库测试环境

```sql
-- 创建多个数据库
CREATE DATABASE db1;
CREATE DATABASE db2;
CREATE DATABASE db3;

-- 在每个数据库中创建对象
\c db1
CREATE TABLE db1_table (id SERIAL);
ALTER TABLE db1_table OWNER TO old_user;

\c db2
CREATE TABLE db2_table (id SERIAL);
ALTER TABLE db2_table OWNER TO old_user;
GRANT SELECT ON db2_table TO old_user;

\c db3
CREATE VIEW db3_view AS SELECT 1;
ALTER VIEW db3_view OWNER TO old_user;
```

### 查找所有受影响的数据库

```sql
\c postgres

SELECT DISTINCT db.datname
FROM pg_shdepend s
JOIN pg_database db ON s.dbid = db.oid
WHERE refobjid = (SELECT oid FROM pg_roles WHERE rolname = 'old_user')
ORDER BY db.datname;
```

**输出：**
```
 datname
--------
 db1
 db2
 db3
 postgres
```

### 在每个数据库中执行清理

```bash
# 方法 1：手动逐个执行
psql -d postgres -c "REASSIGN OWNED BY old_user TO postgres; DROP OWNED BY old_user;"
psql -d db1 -c "REASSIGN OWNED BY old_user TO postgres; DROP OWNED BY old_user;"
psql -d db2 -c "REASSIGN OWNED BY old_user TO postgres; DROP OWNED BY old_user;"
psql -d db3 -c "REASSIGN OWNED BY old_user TO postgres; DROP OWNED BY old_user;"

# 方法 2：使用循环
for db in postgres db1 db2 db3; do
    echo "Cleaning database: $db"
    psql -d $db -c "REASSIGN OWNED BY old_user TO postgres; DROP OWNED BY old_user;"
done

# 方法 3：使用脚本
for db in postgres db1 db2 db3; do
    echo "Cleaning database: $db"
    psql -d $db -f delete-user.sql
done
```

### 最终删除角色

```sql
\c postgres
DROP ROLE old_user;
```

## 故障排查示例

### 问题：权限不足

```sql
-- 错误信息
-- ERROR: permission denied for table users

-- 解决方案：确保有足够的权限
GRANT old_user TO current_user;
SET ROLE old_user;
-- 执行操作
RESET ROLE;
```

### 问题：默认权限无法清理

```sql
-- 查询默认权限
SELECT
    grantor,
    grantee,
    schema_name
FROM information_schema.default_privileges
WHERE grantee = 'old_user';

-- 输出：
-- grantor  | grantee   | schema_name
-- ----------+-----------+-------------
-- old_user | admin_user | public

-- 解决方案：获取 grantor 的权限
GRANT old_user TO postgres;
SET ROLE old_user;

-- 撤销默认权限
ALTER DEFAULT PRIVILEGES
REVOKE ALL ON TABLES FROM admin_user;

-- 恢复角色
RESET ROLE;
REVOKE old_user FROM postgres;
```

## 总结

1. ✅ 角色删除必须在每个数据库中执行
2. ✅ 使用 `REASSIGN OWNED` 转移所有权
3. ✅ 使用 `DROP OWNED` 清理所有依赖
4. ✅ 不要忘记 `postgres` 数据库
5. ✅ 注意默认权限（Default ACLs）
6. ✅ 使用自动化脚本简化操作

通过这个示例，你应该能够安全地删除任何 PostgreSQL 角色。
