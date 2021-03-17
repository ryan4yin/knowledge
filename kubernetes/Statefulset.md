# StatefulSet

对于大多数单节点的有状态应用，比如各类单节点数据库 MySQL/Mongo/ElasticSearch/Redis，
都可以简单地使用 StatefulSet+volumeClaimTemplates 进行部署。

>如果你是测试环境，不需要考虑数据丢失的问题，甚至可以考虑直接使用 EmptyDir+Deployment 进行部署，或者干脆不用数据卷映射（数据直接放在容器数据层中）。

但是一但从单节点上升到集群，状态就可能变得很复杂，StatefulSet 提供的功能仍然是非常不足的。
这时就需要借助 [CRD+Operator](../crd+operator%20-%20stateful%20app/README.md) 来完成集群的部署与状态管理了。


## StatefulSet or Deployment?

如果我们考虑多个 Pod 共用一个 PV 的情况，就比如多个 nginx Pod 挂载同一个 `/usr/share/nginx/html` 的 PV，然后都可以读写这个 PV。
这种情况下，好像就没必要使用 StatefulSet+volumeClaimTemplates，Deployment+PVC 就完全够用了，因为这类应用程序根本不需要 StatefulSet 提供的功能——稳定的唯一标识符、有序扩缩容。

StatefulSet 适合不同 Pod 使用不同 PV 的情况，
