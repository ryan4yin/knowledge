# PostgreSQL 角色删除实战指南

本指南通过实际案例演示如何安全删除 PostgreSQL 角色/用户，以及如何处理常见的依赖问题。

## 目录

1. [背景场景](#背景场景)
2. [问题诊断](#问题诊断)
3. [分步清理流程](#分步清理流程)
4. [实战案例](#实战案例)
5. [自动化脚本](#自动化脚本)
6. [故障排查](#故障排查)

---

## 背景场景

### 场景描述

你有一个 PostgreSQL 实例，包含多个数据库：

```sql
SELECT datname FROM pg_database WHERE datistemplate = false;

 datname
----------
 postgres
 app_db
 analytics_db
 user_db
```

你需要删除一个旧的应用用户 `old_app_user`，但是直接删除失败了：

```sql
DROP ROLE old_app_user;
-- ERROR: role "old_app_user" cannot be dropped because some objects depend on it
-- DETAIL:  owner of table app_db.users
-- owner of sequence app_db.users_id_seq
-- privileges for database app_db
```

### 为什么会失败？

PostgreSQL 角色可能在以下情况下存在依赖：

1. **对象所有权**：拥有表、视图、序列、函数等对象
2. **权限授予**：被授予了某些对象的权限
3. **默认权限**：设置了 `ALTER DEFAULT PRIVILEGES` 规则
4. **多数据库依赖**：在多个数据库中都有上述依赖

---

## 问题诊断

### 步骤 1：查询对象所有权

查看该角色拥有哪些对象：

```sql
SELECT
    n.nspname as schema_name,
    c.relname as object_name,
    CASE c.relkind
        WHEN 'r' THEN 'table'
        WHEN 'S' THEN 'sequence'
        WHEN 'v' THEN 'view'
        WHEN 'm' THEN 'materialized view'
        WHEN 'f' THEN 'foreign table'
        ELSE c.relkind::text
    END as object_type
FROM pg_class c
JOIN pg_namespace n ON n.oid = c.relnamespace
JOIN pg_roles r ON r.oid = c.relowner
WHERE r.rolname = 'old_app_user'
ORDER BY n.nspname, c.relname;
```

**输出示例：**

```
 schema_name | object_name     | object_type
-------------+-----------------+-------------
 public      | users           | table
 public      | users_id_seq    | sequence
 public      | audit_log       | table
```

### 步骤 2：查询显式权限授予

查看该角色被授予了哪些权限：

```sql
SELECT
    grantee,
    table_schema,
    table_name,
    privilege_type,
    is_grantable
FROM information_schema.role_table_grants
WHERE grantee = 'old_app_user'
ORDER BY table_schema, table_name;
```

**输出示例：**

```
 grantee      | table_schema | table_name | privilege_type | is_grantable
--------------+--------------+------------+----------------+--------------
 old_app_user | public       | products   | SELECT         | NO
 old_app_user | public       | products   | INSERT         | NO
 old_app_user | public       | orders     | SELECT         | NO
```

### 步骤 3：查询全实例依赖（终极探测）

如果上述查询没有结果，但删除仍然失败，使用系统共享依赖表：

```sql
SELECT
    COALESCE(db.datname, 'global') as database,
    classid::regclass as object_type,
    objid as object_id,
    CASE deptype
        WHEN 'a' THEN 'internal dependency'
        WHEN 'r' THEN 'owned by (dependency on role)'
        WHEN 'n' THEN 'pin dependency'
        WHEN 'x' THEN 'extension'
        ELSE deptype::text
    END as dependency_type
FROM pg_shdepend s
LEFT JOIN pg_database db ON s.dbid = db.oid
WHERE refobjid = (SELECT oid FROM pg_roles WHERE rolname = 'old_app_user')
ORDER BY db.datname, classid::regclass;
```

**输出示例：**

```
 database   | object_type | object_id | dependency_type
------------+-------------+-----------+-----------------
 app_db     | pg_class    |     16420 | owned by (dependency on role)
 app_db     | pg_class    |     16425 | owned by (dependency on role)
 postgres   | pg_namespace |     2200 | owned by (dependency on role)
```

### 步骤 4：查找所有受影响的数据库

确定需要在哪些数据库中执行清理：

```sql
SELECT DISTINCT
    db.datname as database_name
FROM pg_shdepend s
JOIN pg_database db ON s.dbid = db.oid
WHERE refobjid = (SELECT oid FROM pg_roles WHERE rolname = 'old_app_user')
UNION
SELECT 'postgres'::text  -- 总是检查 postgres 数据库
ORDER BY database_name;
```

---

## 分步清理流程

### 准备工作

1. **选择接收资产的角色**

通常选择 `postgres` 超级用户或其他管理员角色作为资产接收方：

```sql
-- 确认接收角色存在
SELECT rolname, rolsuper
FROM pg_roles
WHERE rolname = 'postgres';
```

2. **确认当前用户权限**

确保你有足够的权限执行清理操作：

```sql
SELECT current_user, session_user;
```

### 第一步：身份继承

管理员需要临时获得目标角色的身份，才能处理它的资产：

```sql
-- 假设当前用户是 postgres
GRANT old_app_user TO postgres;
GRANT postgres TO postgres;  -- 确保拥有自己的权限
```

**为什么要这样做？**

- `REASSIGN OWNED` 和 `DROP OWNED` 需要有权限访问目标角色的对象
- 直接操作可能因权限不足而失败
- 通过角色继承，管理员可以"代表"目标角色操作

### 第二步：资产转移

将目标角色拥有的所有对象转移给接收角色：

```sql
-- 在 app_db 数据库中执行
\c app_db

REASSIGN OWNED BY old_app_user TO postgres;
```

**验证转移结果：**

```sql
-- 检查是否还有属于 old_app_user 的对象
SELECT
    n.nspname as schema_name,
    c.relname as object_name
FROM pg_class c
JOIN pg_namespace n ON n.oid = c.relnamespace
JOIN pg_roles r ON r.oid = c.relowner
WHERE r.rolname = 'old_app_user';
-- 应该返回空结果
```

### 第三步：依赖抹除

清理所有权限和默认权限：

```sql
-- 在 app_db 数据库中执行
DROP OWNED BY old_app_user;
```

**这一步做了什么？**

1. 撤销所有显式授予的权限（GRANT）
2. 清理默认权限规则（Default ACLs）
3. 删除该角色在当前数据库的所有依赖记录

**验证清理结果：**

```sql
-- 检查是否还有权限授予
SELECT * FROM information_schema.role_table_grants
WHERE grantee = 'old_app_user';
-- 应该返回空结果
```

### 第四步：在所有数据库中重复

对步骤 2-3 在每个受影响的数据库中执行：

```sql
-- 在 analytics_db 中
\c analytics_db
REASSIGN OWNED BY old_app_user TO postgres;
DROP OWNED BY old_app_user;

-- 在 user_db 中
\c user_db
REASSIGN OWNED BY old_app_user TO postgres;
DROP OWNED BY old_app_user;

-- 在 postgres 数据库中（不要忘记！）
\c postgres
REASSIGN OWNED BY old_app_user TO postgres;
DROP OWNED BY old_app_user;
```

### 第五步：物理删除角色

当所有数据库都清理完成后，删除角色：

```sql
DROP ROLE old_app_user;
```

**成功信息：**

```sql
-- 如果成功，不会有任何输出
-- 可以验证：
SELECT rolname FROM pg_roles WHERE rolname = 'old_app_user';
-- 返回空结果
```

### 第六步：清理身份继承

删除成功后，清理临时授予的权限：

```sql
REVOKE old_app_user FROM postgres;
```

---

## 实战案例

### 案例 1：简单的单数据库清理

**场景：** 用户 `dev_user` 只在 `app_db` 中有一个表。

```sql
-- 步骤 1：检查依赖
SELECT
    n.nspname,
    c.relname,
    c.relkind
FROM pg_class c
JOIN pg_namespace n ON n.oid = c.relnamespace
JOIN pg_roles r ON r.oid = c.relowner
WHERE r.rolname = 'dev_user';

-- 结果：
-- nspname | relname  | relkind
-- ---------+----------+--------
-- public  | test_tbl | r

-- 步骤 2：清理
\c app_db
GRANT dev_user TO postgres;
REASSIGN OWNED BY dev_user TO postgres;
DROP OWNED BY dev_user;
DROP ROLE dev_user;
REVOKE dev_user FROM postgres;
```

### 案例 2：多数据库复杂依赖

**场景：** 用户 `legacy_user` 在 3 个数据库中都有对象和权限。

```sql
-- 步骤 1：查找所有受影响的数据库
SELECT DISTINCT db.datname
FROM pg_shdepend s
JOIN pg_database db ON s.dbid = db.oid
WHERE refobjid = (SELECT oid FROM pg_roles WHERE rolname = 'legacy_user');

-- 结果：
-- datname
-- ----------
-- app_db
-- analytics_db
-- postgres

-- 步骤 2：依次清理每个数据库
\c app_db
GRANT legacy_user TO postgres;
REASSIGN OWNED BY legacy_user TO postgres;
DROP OWNED BY legacy_user;

\c analytics_db
REASSIGN OWNED BY legacy_user TO postgres;
DROP OWNED BY legacy_user;

\c postgres
REASSIGN OWNED BY legacy_user TO postgres;
DROP OWNED BY legacy_user;

-- 步骤 3：删除角色
DROP ROLE legacy_user;
REVOKE legacy_user FROM postgres;
```

### 案例 3：默认权限陷阱

**场景：** 用户 A 为用户 B 设置了默认权限，导致用户 B 删不掉。

```sql
-- 步骤 1：发现默认权限
SELECT
    grantor,
    grantee,
    schema_name,
    default_acl_item_type
FROM information_schema.default_privileges
WHERE grantee = 'user_b';

-- 结果：
-- grantor | grantee | schema_name | default_acl_item_type
-- ---------+---------+-------------+-----------------------
-- user_a  | user_b  | public      | TABLES

-- 步骤 2：获取 user_a 的权限来清理
GRANT user_a TO postgres;
SET ROLE user_a;

-- 步骤 3：撤销默认权限
ALTER DEFAULT PRIVILEGES FOR ROLE user_b
REVOKE ALL ON TABLES FROM user_b;

RESET ROLE;
REVOKE user_a FROM postgres;
```

---

## 自动化脚本

### 使用 delete-user.sql 脚本

将 `delete-user.sql` 复制到你的工作目录并修改配置：

```bash
# 修改脚本中的变量
vim delete-user.sql
# 将 v_old_user 改为 'old_app_user'
# 将 v_target_user 改为 'postgres'
```

然后在每个数据库中执行：

```bash
# 方法 1：使用 psql 命令行
psql -h localhost -U postgres -d app_db -f delete-user.sql
psql -h localhost -U postgres -d analytics_db -f delete-user.sql
psql -h localhost -U postgres -d postgres -f delete-user.sql

# 方法 2：在 psql 交互界面中
\c app_db
\i delete-user.sql

\c analytics_db
\i delete-user.sql

\c postgres
\i delete-user.sql
```

### 批量执行脚本

创建一个 shell 脚本在所有数据库中执行：

```bash
#!/bin/bash
# cleanup-user.sh

ROLE_NAME="old_app_user"
TARGET_USER="postgres"
DB_HOST="localhost"
DB_PORT="5432"

# 获取所有需要清理的数据库
DATABASES=$(psql -h $DB_HOST -p $DB_PORT -U postgres -t -c "
    SELECT DISTINCT datname
    FROM pg_database
    WHERE datistemplate = false
    ORDER BY datname;
")

# 在每个数据库中执行清理脚本
for db in $DATABASES; do
    echo "Cleaning database: $db"
    psql -h $DB_HOST -p $DB_PORT -U postgres -d $db -f delete-user.sql
    echo "---"
done

echo "Cleanup complete!"
```

---

## 故障排查

### 问题 1：权限不足

**错误信息：**
```
ERROR: permission denied for table xxx
```

**解决方案：**

```sql
-- 确保执行了身份继承
GRANT target_role TO current_user;

-- 或者直接使用超级用户
SET ROLE postgres;
```

### 问题 2：角色正在被使用

**错误信息：**
```
ERROR: role "xxx" is being used by current user
```

**解决方案：**

```bash
# 重新连接数据库
\c app_db

# 或者在新的 psql 会话中执行
psql -h localhost -U postgres -d app_db
```

### 问题 3：依赖对象

**错误信息：**
```
ERROR: cannot drop table xxx because other objects depend on it
```

**解决方案：**

```sql
-- 使用 CASCADE 选项
DROP TABLE xxx CASCADE;

-- 或者在 DROP OWNED 时指定 CASCADE
DROP OWNED BY target_role CASCADE;
```

### 问题 4：在某个数据库中找不到依赖

**症状：** 删除仍然失败，但在当前数据库中找不到任何依赖

**解决方案：**

```sql
-- 1. 检查所有数据库
\c postgres
SELECT datname FROM pg_database;

-- 2. 在每个数据库中检查依赖
-- 3. 不要忘记 template0 和 template1（虽然通常不应该有依赖）
```

### 问题 5：默认权限无法清理

**错误信息：**
```
ERROR: must be owner of schema xxx
```

**解决方案：**

```sql
-- 1. 找到设置默认权限的用户
SELECT
    grantor,
    schema_name
FROM information_schema.default_privileges
WHERE grantee = 'target_user';

-- 2. 获取该用户的权限
GRANT grantor_role TO current_user;
SET ROLE grantor_role;

-- 3. 撤销默认权限
ALTER DEFAULT PRIVILEGES
REVOKE ALL ON TABLES FROM target_user;

-- 4. 恢复角色
RESET ROLE;
REVOKE grantor_role FROM current_user;
```

---

## 最佳实践

### 1. 定期审计

```sql
-- 定期检查闲置的角色
SELECT
    rolname,
    rolcreaterole,
    rolcreatedb,
    rolsuper
FROM pg_roles
WHERE rolname NOT IN ('postgres', 'pg_XXX')  -- 排除系统角色
AND NOT EXISTS (
    SELECT 1 FROM pg_stat_activity WHERE usename = pg_roles.rolname
);
```

### 2. 使用角色组

```sql
-- 创建角色组而不是直接授予个人用户
CREATE ROLE app_readonly;
CREATE ROLE app_readwrite;
CREATE ROLE app_admin;

-- 用户加入角色组
CREATE USER alice IN ROLE app_readonly;
CREATE USER bob IN ROLE app_readwrite;

-- 删除用户时只需从角色组移除
REVOKE app_readonly FROM alice;
DROP USER alice;
```

### 3. 文档化权限

```sql
-- 生成权限报告
SELECT
    grantee,
    table_schema,
    table_name,
    string_agg(privilege_type, ', ') as privileges
FROM information_schema.role_table_grants
WHERE table_schema NOT IN ('pg_catalog', 'information_schema')
GROUP BY grantee, table_schema, table_name
ORDER BY grantee, table_schema, table_name;
```

### 4. 使用自动化脚本

- 在生产环境中，使用经过测试的自动化脚本
- 在执行前先在测试环境验证
- 保留操作日志以便审计

---

## 总结

删除 PostgreSQL 角色的关键要点：

1. ✅ **Role 是实例级别的，但权限是数据库级别的**
2. ✅ **必须在每个数据库中清理依赖**
3. ✅ **使用 REASSIGN OWNED 转移所有权**
4. ✅ **使用 DROP OWNED 清理所有权限**
5. ✅ **不要忘记 postgres 数据库**
6. ✅ **注意默认权限（Default ACLs）**
7. ✅ **使用自动化脚本减少人为错误**

通过遵循本指南的流程，你可以安全地删除任何 PostgreSQL 角色，同时避免数据丢失和权限问题。
