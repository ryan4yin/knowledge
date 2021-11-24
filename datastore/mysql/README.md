# MySQL

## 部署方案

这里讨论三种部署方案：

1. 普通的单机部署(normal)
2. 单机内存数据库(in-memory)：适合用于测试的高速 MySQL 数据库，数据保存在内存中因而速度快。
3. 使用 kubernetes 部署分布式的 MySQL 集群：参见 [mysql cluster -vitess](./mysql%20cluster%20-%20vitess/README.md)

### 参考

- [mysql - Docker Official Images](https://hub.docker.com/_/mysql/)

## 设置账号密码

- [mysql 用户管理和权限设置](https://www.cnblogs.com/fslnet/p/3143344.html)

### 1. 给 root 账号设置密码（适合开发环境，对安全性要求不高的场景）

启用 root 账户远程登录，并且设置密码：
```sql
GRANT ALL PRIVILEGES ON *.* TO 'root'@'%' IDENTIFIED BY '<your-password>';
FLUSH PRIVILEGES;
```

内网开发环境的 mysql，可以关掉 root 账户的密码验证功能（**危险操作！另外很多应用都不支持使用空密码连接 MySQL！**）：

```sql
# 使本机访问 mysql 不需要密码
GRANT ALL PRIVILEGES ON *.* TO 'root'@'localhost'
# 使远程访问 mysql 也不需要密码
GRANT ALL PRIVILEGES ON *.* TO 'root'@'%' 
FLUSH PRIVILEGES;
```

### 2. 添加受限用户（安全性高）并设置密码

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
# 给远程用户 test 授予 testdb 中所有表的**只读**权限
GRANT SELECT ON testdb.* TO 'test'@'%'
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

## 运行 SQL 脚本

使用 mysqldump 备份数据为 sql 文件：

```shell
mysqldump --all-databases --user=root --password="$MYSQL_ROOT_PASSWORD" > /some/path/on/your/host/all-databases.sql
```

将 sql 文件还原到数据库：

```shell
# 1. 直接运行某个 sql 文件
mysql --database="databasename" --user="username" --password="yourpassword" < "/path/to/xxx.sql"
# 2. 在 mysql shell 里运行 sql 文件
$ mysql -u root -p
mysql> USE mydb;
mysql> source /path/to/xxx.sql
```

在 mysql 容器中执行备份还原：

```shell
# 备份单个数据库
mysqldump -uroot -p"$MYSQL_ROOT_PASSWORD" -h <host> my_db  > my_db.sql

# 备份
docker exec some-mysql sh -c 'exec mysqldump --all-databases -uroot -p"$MYSQL_ROOT_PASSWORD"' > /some/path/on/your/host/all-databases.sql

# 还原
docker exec -i some-mysql sh -c 'exec mysql -uroot -p"$MYSQL_ROOT_PASSWORD"' < /some/path/on/your/host/all-databases.sql
```

## SQL 语句分析

- [MySQL Explain 详解](https://www.cnblogs.com/xuanzhi201111/p/4175635.html)
- [技术经理：求求你，别再乱改数据库连接池的大小了！](https://mp.weixin.qq.com/s/n1iE63B0N-vsXnro_NZzJw)
