# CRD+Operator - 复杂有状态应用的管理器

如果需要在 Kubernetes 中部署类似 rook-ceph/istio/mysql-cluster/prometheus-cluster/mongo-cluster 之类的复杂有状态应用，最好的方式就是 CRD+Operator。


## 为什么需要 CRD+Operator

因为 Kubernetes 提供的 StatefulSet 功能太弱了，要部署一个可伸缩的有状态应用，StatefulSet 的功能远远不够。

StatefulSet 只适合用于部署比较简单的有状态应用，比如 [mqtt/emitter](/other/mqtt/README.md)，各副本（Pod）可以简单地通过 Headless Service 互相发现，互相连接。

而对于 Mongo 分片集群、MySQL 集群、rook-ceph 这类组件众多，不同组件功能和地位都不同，启动/初始化流程、扩缩容流程都很复杂的有状态应用，StatefulSet 就无能为力了。

但是数据库的高可用与弹性扩缩容，是企业自建数据库的刚需。
另一方面不止数据库，其他诸如 Istio 这类复杂有状态应用，也面临着同样的问题。

于是 Operator 应运而生，它由 CoreOS 首先提出，现在已经成了 Kubernetes 上部署与管理复杂有状态应用的事实标准。



## 注意事项

使用 operator 时，operator 和 cr 的删除必须遵循如下顺序：

1. 删除 cr，等待 cr 被 operator 完全清理
2. 删除 operator

如果你先删了 operator，将导致 cr 无法完全清理，从而无法被删除！
