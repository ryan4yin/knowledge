# 节点维护与Pod中断预算

在我们通过 `kubectl drain` 将某个节点上的容器驱逐走的时候，
kubernetes 会依据 Pod 的「PodDistruptionBuget」来进行 Pod 的驱逐。

如果不设置任何明确的 PodDistruptionBuget，Pod 将会被直接杀死，然后在别的节点重新调度，**这可能导致服务中断！**



