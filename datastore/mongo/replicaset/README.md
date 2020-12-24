# Mongo 副本集

这里使用 [bitnami/mongodb](https://github.com/bitnami/bitnami-docker-mongodb) 而非 Docker 官方提供的 Mongo 镜像，因为 bitnami/mongo 把一些参数和副本集的功能封装到了环境变量里面，使用起来更方便。

为了让 mongo 副本集能在容器外部网络使用，我对 bitnami/mongo 官方提供的 docker-compose.yml 做了一些修改。

## 部署方法

一个正常 Mongo 的副本集，会使用 Raft 算法选主（和 Etcd 一样），来保证副本集的高可用，因此通常建议使用奇数个节点。

但是 bitnami/mongo 通过设定一些强制性的参数，让我们可以方便地通过环境变量强制某个节点成为主节点。
另一方面我们使用 docker-compose 本来也是单机部署。因此这里副本节点个数就无所谓了。

启动命令：

```shell
# 首先，修改 docker-compose-replicaset.yml 中的 hostname 为宿主机 IP 地址。

# 启动容器
mv docker-compose-replicaset.yml docker-compose.yml
docker-compose up -d
```

如果 mongo 副本集只需要在容器网络内部使用，那可以删除掉所有端口映射，然后使用 [bitnami/mongodb](https://github.com/bitnami/bitnami-docker-mongodb) 官方提供的方法进行快速的副本扩缩容：

```
# 首先，修改 docker-compose-replicaset.yml 中的 hostname 为宿主机 IP 地址。

mv docker-compose-replicaset.yml docker-compose.yml
# 一主三副本
docker-compose up -d --scale mongodb-secondary=3
```

## 特殊：单节点副本集的部署

```shell
# 首先，修改 docker-compose-signle.yml 中的 hostname 为宿主机 IP 地址。

mv docker-compose-signle.yml docker-compose.yml
docker-compose up -d
```


## 测试 mongodb 可用性

可以在容器中使用命令行进入 mongo shell:

```shell
# 如果不需要认证，可以直接进入 shell
mongo shell

# 使用账号密码登录，认证数据库为 admin
mongo shell --authenticationDatabase admin -u root -p password123

# 然后使用如下命令查看副本集状态：
rs.status()
```

使用 python 测试 mongodb 可用性：

```python
from pymongo import MongoClient

# 连接时需要指定副本集为 rs0，pymongo 会自动发现其他所有副本地址。
client = MongoClient("mongo.db.local", 27017, replicaset="rs0")
# 使用账号密码登录
# client = MongoClient(
#     "mongo.db.local",
#     27017, 
#     replicaset="rs0",
#     username='root',
#     password="password123", 
#     authSource='admin',
# )
# 也可以通过一个 URI 设置好所有的连接参数
# client = MongoClient("mongodb://root：<password>@<mongo1>:<port1>,<mongo2>:<port2>,<mongo3>:<port3>/admin?replicaSet=rs0")
print(client.nodes)  # 打印出连接的所有节点
print(client.list_database_names())  # 列出所有 database 名称
print(client.config.list_collections_names())  # 列出 config 的所有 collectioons 名称

# 测试插入数据
test_db = client.test_db
test_collection = test_db.test_collection
test_collection.insert({
    "auther": "Mike",
    "phone": "15000000001",
})
```

