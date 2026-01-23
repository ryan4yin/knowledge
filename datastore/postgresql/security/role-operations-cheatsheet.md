# PostgreSQL 角色管理快速参考

## 核心概念

```
PostgreSQL Role = User (LOGIN) + Group (NOLOGIN)
                 └─ 实例级别（全局）
                 └─ 权限是数据库级别的（局部）
```

## 快速诊断命令

### 查询角色拥有的对象
```sql
SELECT n.nspname, c.relname, c.relkind
FROM pg_class c
JOIN pg_namespace n ON n.oid = c.relnamespace
JOIN pg_roles r ON r.oid = c.relowner
WHERE r.rolname = 'role_name';
```

### 查询角色被授予的权限
```sql
SELECT * FROM information_schema.role_table_grants
WHERE grantee = 'role_name';
```

### 查询所有依赖（终极探测）
```sql
SELECT db.datname, classid::regclass, objid, deptype
FROM pg_shdepend s
LEFT JOIN pg_database db ON s.dbid = db.oid
WHERE refobjid = (SELECT oid FROM pg_roles WHERE rolname = 'role_name');
```

### 查找受影响的数据库
```sql
SELECT DISTINCT db.datname
FROM pg_shdepend s
JOIN pg_database db ON s.dbid = db.oid
WHERE refobjid = (SELECT oid FROM pg_roles WHERE rolname = 'role_name');
```

## 删除角色四步法

### 1️⃣ 身份继承
```sql
GRANT "target_role" TO "admin_user";
GRANT "recipient_role" TO "admin_user";
```

### 2️⃣ 资产转移
```sql
REASSIGN OWNED BY "target_role" TO "recipient_role";
```

### 3️⃣ 依赖抹除
```sql
DROP OWNED BY "target_role";
```

### 4️⃣ 物理删除
```sql
DROP ROLE "target_role";
```

## 权限授予三级跳

```sql
-- Database 层
GRANT CONNECT ON DATABASE my_db TO user;

-- Schema 层
GRANT USAGE ON SCHEMA public TO user;

-- Object 层
GRANT SELECT, INSERT ON ALL TABLES IN SCHEMA public TO user;
```

## 常用角色管理命令

### 创建角色
```sql
CREATE ROLE readonly_role;
CREATE USER app_user WITH PASSWORD 'secure_pass';
CREATE USER dev_user IN ROLE developer_role;
```

### 修改角色属性
```sql
ALTER USER user_name WITH PASSWORD 'new_pass';
ALTER USER user_name WITH CONNECTION LIMIT 10;
ALTER USER user_name VALID UNTIL '2024-12-31';
ALTER USER user_name WITH NOLOGIN;  -- 禁用
ALTER USER user_name WITH LOGIN;    -- 启用
```

### 角色继承
```sql
GRANT group_role TO user;
REVOKE group_role FROM user;
SET ROLE group_role;  -- 临时切换角色
RESET ROLE;
```

## 常见错误速查

| 错误 | 原因 | 解决方案 |
|------|------|----------|
| `permission denied` | 权限不足 | `GRANT target_role TO current_user` |
| `cannot drop because some objects depend on it` | 拥有对象 | `REASSIGN OWNED` + `DROP OWNED` |
| `role is being used by current user` | 正在使用 | 重新连接数据库 |
| `must be owner of schema` | 默认权限 | `SET ROLE grantor` 后清理 |

## 删除角色检查清单

- [ ] 在所有数据库中执行了 `REASSIGN OWNED`
- [ ] 在所有数据库中执行了 `DROP OWNED`
- [ ] 检查了 `postgres` 数据库
- [ ] 检查了默认权限（Default ACLs）
- [ ] 清理了临时授予的角色继承
- [ ] 验证角色已被删除

## 自动化脚本

使用 `delete-user.sql` 脚本：

```bash
# 修改配置
vim delete-user.sql

# 在每个数据库中执行
for db in $(psql -t -c "SELECT datname FROM pg_database WHERE datistemplate = false"); do
    psql -d $db -f delete-user.sql
done
```

## 最佳实践

1. ✅ 使用角色组（Group Roles）管理权限
2. ✅ 遵循最小权限原则
3. ✅ 定期审计角色权限
4. ✅ 使用自动化脚本减少错误
5. ✅ 文档化权限分配
6. ✅ 删除前先在测试环境验证

## 相关文件

- 📄 [完整角色删除指南](../examples/role-deletion-guide.md)
- 🔧 [删除角色脚本](./delete-user.sql)
- 📚 [用户与权限管理](./README.md)
