# AWS - [kubernetes/autoscaler](https://github.com/kubernetes/autoscaler)

autoscaler 是 kubernetes 官方提供的一个节点伸缩组件，支持 AWS.

CA 相比 karpenter 的区别在于，它底层是基于 AWS ASG 伸缩组实现的，因此也能很方便地用上 ASG 的各种特性：

- Spot/OD、多种实例类型混用的 ASG

当然也有些 ASG 特性 CA 目前还不支持：

- 热池：提前扩容一批实例并关机，在需要时可以立即启动并加入集群
  - https://github.com/kubernetes/autoscaler/issues/4005

不过总的来看，karpenter 的特性是比 CA 更多的，或许 karpenter 是更好的选择。


## 参考

- [Cluster Autoscaler on AWS](https://github.com/kubernetes/autoscaler/tree/master/cluster-autoscaler/cloudprovider/aws)


