# [分片(Sharding)](https://docs.mongodb.com/manual/sharding/)

副本集通过 Raft 算法保证 MongoDB 的高可用。而分片则是将数据拆分到不同的副本集上，提升 MongoDB 总体的
性能。

这类似磁盘阵列中的 RAID10.

## 一、部署

> 以下部署流程只适合开发/测试环境，不保证稳定性。

分片的 MongoDB 集群组件比较多，部署起来比较麻烦。

可以考虑使用 docker-compose 在单机上部署分片 MongoDB，或者最简单的，使用 k8s+helm 一行命令部署：

```shell
helm repo add bitnami https://charts.bitnami.com/bitnami
# 查看 mongo-sharded 版本号
helm search repo bitnami/mongodb-sharded -l | head
# 下载并解压 chart，目的是方便 gitops 版本管理
helm pull bitnami/mongodb-sharded --untar --version 1.6.5
# 安装 mongo-sharded
helm upgrade --install mongo-sharded ./mongodb-sharded
```

如果需要自定义集群调度、分片数量等参数，请新建一个 `custom-values.yml` 文件，然后从
`./mongodb-sharded/Values.yml` 中将你需要修改的属性拷贝过去，再进行修改。

最后使用如下命令进行部署：

```shell
# 使用自定义属性安装或升级 mongo-sharded
helm upgrade --install mongo-sharded -f custom-values.yaml ./mongodb-sharded
```

### 二、测试可用性

使用 python 测试 mongo 分片集群的可用性

```python
from pymongo import MongoClient

# 使用账号密码连接分片集群
client = MongoClient("mongo-sharded.db.local", 27017, username="root", password="<your-password>")
# 也可以通过一个 URI 设置好所有的连接参数
# client = MongoClient("mongodb://root：<password>@<mongo1>:<port1>,<mongo2>:<port2>,<mongo3>:<port3>/admin")
client.list_database_names()

# 测试插入数据
test_db = client.test_db
test_collection = test_db.test_collection
test_collection.insert({
    "author": "Mike",
    "phone": "15000000001",
})
```

用户连接分片集群的方式跟连接单例Mongo完全类似，区别在于用户可以配置多个 mongos 的地址。所有 mongos
的地位和功能完全对等，而且都是无状态应用，可以任意扩容。

## 三、 Mongo 分片集群架构介绍

待续
