
# [分片(Sharding)](https://docs.mongodb.com/manual/sharding/)

副本集通过 Raft 算法保证 MongoDB 的高可用。
而分片则是将数据拆分到不同的副本集上，提升 MongoDB 总体的性能。

这类似磁盘阵列中的 RAID10.


## 部署

分片的 MongoDB 集群组件比较多，部署起来比较麻烦。

### 一、测试/开发环境

可以考虑使用 docker-compose 在单机上部署分片 MongoDB，
或者最简单的，使用 k8s+helm 一行命令部署：

```shell
helm repo add bitnami https://charts.bitnami.com/bitnami
# 下载并解压 mongo-sharded chart
helm pull bitnami/mongodb-sharded --untar
# 安装 mongo-sharded
helm upgrade --install mongo-sharded ./mongodb-sharded
```

如果需要自定义集群调度、分片数量等参数，请新建一个 `custom-values.yml` 文件，
然后从 `./mongodb-sharded/Values.yml` 中将你需要修改的属性拷贝过去，再进行修改。

最后使用如下命令进行部署：

```shell
# 使用自定义属性安装或升级 mongo-sharded
helm upgrade --install mongo-sharded -f custom-values.yaml ./mongodb-sharded
```

### 二、生产环境

建议二进制方式部署，或者购买云服务。


### 三、测试可用性

使用 python 测试 mongo 分片集群的可用性

```python3
from pymongo import MongoClient
client = MongoClient("mongo-sharded.db.local", 27017, username="root", password="")
client.list_database_names()
```
