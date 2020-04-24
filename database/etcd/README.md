# [ETCD](https://github.com/etcd-io/etcd)

## 搭建 etcd 集群

可以使用本文件夹中的 `docker-compose.yml` 启动一个多节点的 etcd 测试集群用于学习与测试。
参考了 [docker_practice - Etcd 集群](https://github.com/yeasy/docker_practice/blob/master/etcd/cluster.md)


## Etcd 集群运维需知

1. Etcd 集群的节点数量越多，写入速度越慢。因为 raft 协议要求超过 1/2 的节点写入成功，才算是一次成功的写操作。
   1. 因此通常使用 3/5/7 个 etcd 节点。
2. 集群节点在线数低于 1/2，将无法进行写入，也无法进行读取！！！因为任何对集群的读/写操作，都需要超过 1/2 的节点进行确认/完成写入。
   1. [Etcd 的线性一致读](https://zhuanlan.zhihu.com/p/31050303)

官方运维文档：[etcd 3.4 - operations guide](https://etcd.io/docs/v3.4.0/op-guide)


## Etcd 集群故障恢复

>官方文档：[etcd 3.4 - disaster recovery](https://etcd.io/docs/v3.4.0/op-guide/recovery/)

待续
