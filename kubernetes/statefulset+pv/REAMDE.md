# StatefulSet + PV

对于大多数单节点的有状态应用，比如各类单节点数据库 MySQL/Mongo/ElasticSearch/Redis，
都可以简单地使用 StatefulSet+PV 进行部署。

>如果你是测试环境，不需要考虑数据丢失的问题，甚至可以考虑直接使用 EmptyDir+Deployment 进行部署，或者干脆不用数据卷映射（数据直接放在容器数据层中）。

但是一但从单节点上升到集群，状态就可能变得很复杂，这时就需要借助 [CRD+Operator](../crd+operator%20-%20stateful%20app/README.md) 来完成集群的部署与状态管理了。

