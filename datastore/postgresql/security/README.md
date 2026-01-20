# PostgreSQL 用户与权限管理

PostgreSQL 提供了强大的安全模型，包括用户（角色）管理、权限控制和访问控制。本章节详细介绍 PostgreSQL 的安全机制和最佳实践。

## 角色与用户管理

### 0. Role 跟 User

在现代 PostgreSQL 中，User（用户）和 Role（角色）在底层本质上是同一个东西。

简单来说：**Role 是核心概念，而 User 只是一个带有「登录权限」的 Role**。

### 1. 创建角色和用户

```sql
-- 创建角色（不包含 LOGIN 属性时是组角色）
CREATE ROLE readonly_role;
CREATE ROLE admin_role;

-- 创建用户（包含 LOGIN 属性）
CREATE USER app_user WITH PASSWORD 'secure_password123';
CREATE USER analytics_user WITH PASSWORD 'analytics_pass' CREATEDB CREATEROLE;

-- 创建具有特定权限的用户
CREATE USER report_user WITH
    PASSWORD 'report_pass',
    CONNECTION LIMIT 10,
    VALID UNTIL '2024-12-31';

-- 使用角色继承
CREATE ROLE app_developer;
CREATE USER dev1 WITH PASSWORD 'dev1_pass' IN ROLE app_developer;
CREATE USER dev2 WITH PASSWORD 'dev2_pass' IN ROLE app_developer;
```

### 2. 用户属性管理

```sql
-- 修改用户密码
ALTER USER app_user WITH PASSWORD 'new_secure_password';

-- 设置连接限制
ALTER USER analytics_user WITH CONNECTION LIMIT 5;

-- 设置密码过期时间
ALTER USER app_user VALID UNTIL '2024-06-30';

-- 启用/禁用用户
ALTER USER app_user WITH NOLOGIN;   -- 禁用
ALTER USER app_user WITH LOGIN;     -- 启用

-- 重命名用户
ALTER USER old_name RENAME TO new_name;

-- 设置超级用户权限
ALTER USER admin_user WITH SUPERUSER;

-- 撤销超级用户权限
ALTER USER admin_user WITH NOSUPERUSER;
```

### 3. 查看用户信息

```sql
-- 查看所有角色
SELECT rolname, rolsuper, rolcreaterole, rolcreatedb, rolcanlogin
FROM pg_roles
ORDER BY rolname;

-- 查看用户会话信息
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

-- 查看用户权限
SELECT
    r.rolname,
    r.rolsuper,
    r.rolinherit,
    r.rolcreaterole,
    r.rolcreatedb,
    r.rolcanlogin,
    r.rolconnlimit,
    r.rolpassword,
    r.rolvaliduntil
FROM pg_roles r
WHERE r.rolname = 'app_user';
```

## 数据库权限管理

### 1. 对象权限类型

```sql
-- 表权限
GRANT SELECT, INSERT, UPDATE, DELETE ON orders TO app_user;
GRANT ALL PRIVILEGES ON products TO admin_user;
GRANT SELECT ON sensitive_data TO readonly_role;

-- 序列权限
GRANT USAGE, SELECT ON sequence_name TO app_user;

-- 模式权限
GRANT USAGE ON SCHEMA public TO app_user;
GRANT CREATE ON SCHEMA app_schema TO app_developer;
GRANT ALL ON SCHEMA analytics_schema TO analytics_user;

-- 数据库权限
GRANT CONNECT ON DATABASE myapp TO app_user;
GRANT CREATE ON DATABASE myapp TO app_developer;
GRANT TEMPORARY ON DATABASE myapp TO app_user;

-- 函数权限
GRANT EXECUTE ON FUNCTION calculate_discount(numeric, numeric) TO app_user;
GRANT ALL ON ALL FUNCTIONS IN SCHEMA public TO app_developer;
```

### 2. 权限撤销

```sql
-- 撤销表权限
REVOKE INSERT, UPDATE, DELETE ON orders FROM app_user;
REVOKE ALL ON products FROM admin_user;

-- 撤销模式权限
REVOKE CREATE ON SCHEMA app_schema FROM app_developer;

-- 撤销数据库权限
REVOKE CONNECT ON DATABASE myapp FROM old_user;

-- 撤销角色
REVOKE app_role FROM user1;
```

### 3. 默认权限设置

```sql
-- 设置默认权限（PostgreSQL 9.3+）
ALTER DEFAULT PRIVILEGES IN SCHEMA public
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO app_user;

ALTER DEFAULT PRIVILEGES IN SCHEMA public
GRANT USAGE, SELECT ON SEQUENCES TO app_user;

-- 为未来创建的对象设置权限
ALTER DEFAULT PRIVILEGES
FOR USER admin_user
IN SCHEMA public
GRANT ALL ON TABLES TO admin_user;
```

## 角色继承与组管理

### 1. 角色层次结构

```sql
-- 创建基础角色
CREATE ROLE basic_access;
CREATE ROLE read_write;
CREATE ROLE admin_access;

-- 设置角色继承
GRANT basic_access TO read_write;
GRANT read_write TO admin_access;

-- 创建用户并分配到角色
CREATE USER web_user WITH PASSWORD 'web_pass' IN ROLE basic_access;
CREATE USER app_user WITH PASSWORD 'app_pass' IN ROLE read_write;
CREATE USER admin_user WITH PASSWORD 'admin_pass' IN ROLE admin_access;

-- 为基础角色分配权限
GRANT CONNECT ON DATABASE myapp TO basic_access;
GRANT USAGE ON SCHEMA public TO basic_access;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO basic_access;

-- 为读写角色分配额外权限
GRANT INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO read_write;
GRANT USAGE ON ALL SEQUENCES IN SCHEMA public TO read_write;
```

### 2. 角色继承管理

```sql
-- 查看角色继承关系
SELECT
    r1.rolname as role,
    r2.rolname as member_of,
    r2.rolinherit as inheritable
FROM pg_auth_members m
JOIN pg_roles r1 ON m.roleid = r1.oid
JOIN pg_roles r2 ON m.member = r2.oid
ORDER BY r1.rolname, r2.rolname;

-- 防止权限传播
ALTER ROLE read_write NOINHERIT;
-- 用户需要手动 SET ROLE read_write 来获得该角色权限

-- 创建非继承角色用于特定任务
CREATE ROLE task_executor NOINHERIT;
GRANT task_executor TO app_user;
-- app_user 需要显式 SET ROLE task_executor 来使用该角色权限
```

## 行级安全策略 (RLS)

### 1. 启用行级安全

```sql
-- 创建测试表
CREATE TABLE employees (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    department VARCHAR(50) NOT NULL,
    salary NUMERIC(10,2),
    manager_id INTEGER REFERENCES employees(id)
);

-- 插入测试数据
INSERT INTO employees (name, department, salary, manager_id)
VALUES
    ('John Doe', 'IT', 80000, NULL),
    ('Jane Smith', 'IT', 70000, 1),
    ('Bob Johnson', 'HR', 75000, NULL),
    ('Alice Brown', 'HR', 65000, 3);

-- 启用行级安全
ALTER TABLE employees ENABLE ROW LEVEL SECURITY;
```

### 2. 创建安全策略

```sql
-- 策略1：用户只能查看和修改自己部门的信息
CREATE POLICY dept_policy ON employees
FOR ALL
USING (department = current_setting('app.current_department')::TEXT);

-- 策略2：经理可以查看所有员工信息
CREATE POLICY manager_policy ON employees
FOR SELECT
USING (
    id IN (
        SELECT manager_id FROM employees WHERE manager_id IS NOT NULL
    ) OR id = current_setting('app.current_user_id')::INTEGER
);

-- 策略3：用户只能更新自己的记录
CREATE POLICY self_update_policy ON employees
FOR UPDATE
USING (id = current_setting('app.current_user_id')::INTEGER);

-- 策略4：只有管理员可以删除记录
CREATE POLICY admin_delete_policy ON employees
FOR DELETE
USING (pg_has_role(current_user, 'admin_role', 'MEMBER'));
```

### 3. 使用行级安全

```sql
-- 在应用中设置会话参数
SET app.current_department = 'IT';
SET app.current_user_id = '1';

-- 查看当前用户可见的数据
SELECT * FROM employees;

-- 切换到另一个用户
SET app.current_department = 'HR';
SET app.current_user_id = '3';

-- 再次查询，看到不同的数据
SELECT * FROM employees;

-- 查看当前激活的策略
SELECT * FROM pg_policies WHERE tablename = 'employees';
```

### 4. 动态安全策略

```sql
-- 基于用户角色的动态策略
CREATE POLICY dynamic_policy ON sensitive_data
FOR SELECT
USING (
    CASE
        WHEN pg_has_role(current_user, 'admin_role', 'MEMBER') THEN true
        WHEN pg_has_role(current_user, 'manager_role', 'MEMBER') THEN department = (
            SELECT department FROM users WHERE username = current_user
        )
        WHEN pg_has_role(current_user, 'user_role', 'MEMBER') THEN user_id = (
            SELECT id FROM users WHERE username = current_user
        )
        ELSE false
    END
);

-- 基于时间的策略（例如：工作时间才能访问）
CREATE POLICY time_based_policy ON work_orders
FOR SELECT
USING (
    EXTRACT(HOUR FROM CURRENT_TIMESTAMP) BETWEEN 9 AND 17
    AND EXTRACT(DOW FROM CURRENT_TIMESTAMP) BETWEEN 1 AND 5  -- 周一到周五
);
```

## 认证方法配置

### 1. pg_hba.conf 配置

```bash
# pg_hba.conf 文件格式
# TYPE    DATABASE        USER            ADDRESS                 METHOD

# 本地连接使用 peer 认证
local    all             postgres                                peer

# 本地连接使用密码认证
local    all             all                                     md5

# IPv4 本地连接
host     all             all             127.0.0.1/32            md5

# 内网连接
host     myapp           app_user        10.0.0.0/8              md5
host     analytics       analytics_user  192.168.1.0/24          md5

# SSL 连接
hostssl myapp            app_user        0.0.0.0/0               md5 clientcert=1

# 管理员连接
host     all             admin_user      192.168.1.100/32        md5

# 复制连接
host     replication     replicator      192.168.1.101/32        md5
```

### 2. 认证方法类型

```bash
# 信任认证（不安全，仅用于开发环境）
local   all     all     trust

# 密码认证
local   all     all     md5      # MD5 哈希
local   all     all     scram-sha-256  # 更安全的密码哈希

# LDAP 认证
host    all     all     0.0.0.0/0   ldap ldapserver=ldap.example.com ldapprefix="uid=" ldapsuffix=",ou=users,dc=example,dc=com"

# PAM 认证
host    all     all     0.0.0.0/0   pam pamservice=postgresql

# Kerberos 认证
host    all     all     0.0.0.0/0   gss include_realm=0 krb_realm=EXAMPLE.COM

# 证书认证
hostssl all     all     0.0.0.0/0   cert clientcert=1
```

## 审计与监控

### 1. 审计日志配置

```sql
-- 安装 pgaudit 扩展
CREATE EXTENSION IF NOT EXISTS pgaudit;

-- postgresql.conf 配置
shared_preload_libraries = 'pgaudit'

# 基本审计配置
pgaudit.log = 'all'                           # 记录所有操作
pgaudit.log_catalog = off                     # 不记录系统表操作
pgaudit.log_parameter = on                    # 记录参数
pgaudit.log_relation = on                     # 记录关系操作
pgaudit.log_statement = 'all'                 # 记录所有语句
pgaudit.log_level = log                       # 日志级别

# 按类型过滤
pgaudit.log = 'read, write, ddl, role, misc'  # 指定要审计的操作类型
pgaudit.role = 'audit_role'                   # 审计角色
```

### 2. 对象级审计

```sql
-- 监控特定表的所有操作
ALTER TABLE sensitive_data SET (pgaudit.log_relation = on);

-- 监控特定用户的操作
ALTER ROLE app_user SET pgaudit.log = 'read, write';
ALTER ROLE admin_user SET pgaudit.log = 'all';

-- 查看审计日志示例
-- AUDIT: SESSION,1,1,READ,SELECT,TABLE,public.users,SELECT * FROM users WHERE id = 1;
-- AUDIT: SESSION,1,1,WRITE,INSERT,TABLE,public.orders,INSERT INTO orders (customer_id, total) VALUES (1, 100);
```

### 3. 安全监控查询

```sql
-- 监控失败的登录尝试
SELECT
    datname as database,
    usename as username,
    application_name,
    client_addr,
    backend_start
FROM pg_stat_activity
WHERE state = 'idle' AND backend_start < NOW() - INTERVAL '1 hour';

-- 查看用户权限
SELECT
    grantee,
    table_schema,
    table_name,
    privilege_type,
    is_grantable
FROM information_schema.role_table_grants
WHERE table_schema NOT IN ('information_schema', 'pg_catalog');

-- 查看当前用户权限
SELECT
    schemaname,
    tablename,
    has_table_privilege(current_user, schemaname||'.'||tablename, 'SELECT') as can_select,
    has_table_privilege(current_user, schemaname||'.'||tablename, 'INSERT') as can_insert,
    has_table_privilege(current_user, schemaname||'.'||tablename, 'UPDATE') as can_update,
    has_table_privilege(current_user, schemaname||'.'||tablename, 'DELETE') as can_delete
FROM pg_tables
WHERE schemaname NOT IN ('information_schema', 'pg_catalog');
```

## 加密与数据保护

### 1. 传输加密

```bash
# postgresql.conf SSL 配置
ssl = on
ssl_cert_file = 'server.crt'
ssl_key_file = 'server.key'
ssl_ca_file = 'root.crt'
ssl_crl_file = 'root.crl'

# 要求客户端使用 SSL
# pg_hba.conf
hostssl all     all     0.0.0.0/0   md5
```

### 2. 数据加密

```sql
-- 安装 pgcrypto 扩展
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- 密码哈希存储
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    salt VARCHAR(64) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 插入用户（使用安全密码哈希）
INSERT INTO users (username, password_hash, salt)
VALUES (
    'john_doe',
    crypt('password123', gen_salt('bf', 12)),
    'generated_salt'
);

-- 验证密码
SELECT * FROM users
WHERE username = 'john_doe'
AND password_hash = crypt('entered_password', password_hash);

-- 敏感数据加密存储
CREATE TABLE sensitive_documents (
    id SERIAL PRIMARY KEY,
    document_name VARCHAR(255),
    encrypted_content BYTEA,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 加密插入数据
INSERT INTO sensitive_documents (document_name, encrypted_content)
VALUES (
    'secret_file.txt',
    pgp_sym_encrypt('This is secret content', 'encryption_key')
);

-- 解密查询数据
SELECT
    document_name,
    pgp_sym_decrypt(encrypted_content, 'encryption_key') as content
FROM sensitive_documents;
```

### 3. 列级加密

```sql
-- 创建加密函数
CREATE OR REPLACE FUNCTION encrypt_sensitive_data(data TEXT, key TEXT)
RETURNS TEXT AS $$
BEGIN
    RETURN encode(pgp_sym_encrypt(data, key), 'base64');
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE OR REPLACE FUNCTION decrypt_sensitive_data(encrypted_data TEXT, key TEXT)
RETURNS TEXT AS $$
BEGIN
    RETURN pgp_sym_decrypt(decode(encrypted_data, 'base64'), key);
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 使用加密函数
INSERT INTO customer_profiles (
    name,
    encrypted_ssn,
    encrypted_credit_card
) VALUES (
    'John Doe',
    encrypt_sensitive_data('123-45-6789', 'ssn_key'),
    encrypt_sensitive_data('4111-1111-1111-1111', 'cc_key')
);
```

## 安全最佳实践

### 1. 权限最小化原则

```sql
-- 创建应用专用用户
CREATE USER app_readonly WITH PASSWORD 'readonly_pass';
CREATE USER app_readwrite WITH PASSWORD 'readwrite_pass';
CREATE USER app_admin WITH PASSWORD 'admin_pass';

-- 分配最小必要权限
GRANT CONNECT ON DATABASE myapp TO app_readonly;
GRANT USAGE ON SCHEMA public TO app_readonly;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO app_readonly;

GRANT CONNECT ON DATABASE myapp TO app_readwrite;
GRANT USAGE ON SCHEMA public TO app_readwrite;
GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA public TO app_readwrite;
GRANT USAGE ON ALL SEQUENCES IN SCHEMA public TO app_readwrite;
```

### 2. 定期安全审计

```sql
-- 创建安全审计脚本
CREATE OR REPLACE FUNCTION security_audit()
RETURNS TABLE (
    username TEXT,
    privilege_type TEXT,
    object_type TEXT,
    object_name TEXT
) AS $$
BEGIN
    -- 检查过高的权限
    RETURN QUERY
    SELECT
        r.rolname as username,
        'SUPERUSER' as privilege_type,
        'ROLE' as object_type,
        r.rolname as object_name
    FROM pg_roles r
    WHERE r.rolsuper = true
    AND r.rolname != 'postgres';

    -- 检查不安全的密码
    RETURN QUERY
    SELECT
        r.rolname as username,
        'WEAK_PASSWORD' as privilege_type,
        'ROLE' as object_type,
        r.rolname as object_name
    FROM pg_roles r
    WHERE r.rolpassword = 'md506a96ed828f2f643a87f70b9079246e8a35755e'
    AND r.rolname != 'postgres'; -- 默认密码

END;
$$ LANGUAGE plpgsql;

-- 运行安全审计
SELECT * FROM security_audit();
```

### 3. 连接安全

```sql
-- 限制连接数
ALTER USER app_user WITH CONNECTION LIMIT 10;

-- 设置密码策略
CREATE EXTENSION IF NOT EXISTS passwordcheck;
-- postgresql.conf 中配置
-- passwordcheck.enable = on
-- passwordcheck.min_length = 8
-- passwordcheck.require_alpha = on
-- passwordcheck.require_numeric = on

-- 设置会话超时
ALTER USER app_user WITH VALID UNTIL '2024-12-31';
SET session_timeout = '30min';
SET idle_in_transaction_session_timeout = '15min';
```

通过合理的用户和权限管理，可以确保 PostgreSQL 数据库的安全性和数据的完整性。
