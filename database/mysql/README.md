# MySQL

## 设置密码

### 1. 开发环境（对安全性要求不高）

启用 root 账户远程登录，并且设置密码
```sql
GRANT ALL PRIVILEGES ON *.* TO 'root'@'%' IDENTIFIED BY '<your-password>';
FLUSH PRIVILEGES;
```

内网开发环境的 mysql，可以关掉 root 账户的密码验证功能（危险操作！）：

```sql
# 使本机访问 mysql 不需要密码
GRANT ALL PRIVILEGES ON *.* TO 'root'@'localhost'
# 使远程访问 mysql 也不需要密码
GRANT ALL PRIVILEGES ON *.* TO 'root'@'%' 
FLUSH PRIVILEGES;
```

### 2. 添加受限用户（安全性高）

添加用户：
```sql
# 添加本地用户 test，并设置密码
create user 'test'@'localhost' identified by '<your-password>';
# 添加远程用户 test，并设置密码
create user 'test'@'%' identified by '<your-password>';
FLUSH PRIVILEGES;
```

给用户授权：

```sql
# 给本地用户 test 授予 testdb 中所有表的 CRUD 权限。
GRANT ALL PRIVILEGES ON testdb.* TO 'test'@'localhost'
# 给远程用户 test 授予 testdb 中所有表的 CRUD 权限。
GRANT ALL PRIVILEGES ON testdb.* TO 'test'@'%'
FLUSH PRIVILEGES;
```

查看用户与权限：

```sql
# 查看用户
SELECT user,host,authentication_string,plugin FROM mysql.user;
# 查看本地用户 test 的权限
show grants for 'test'@'localhost'; 
```

删除用户与权限：

```sql
DROP USER 'test'@'localhost';
```
