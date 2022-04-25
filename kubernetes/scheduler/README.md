# Scheduler

## descheduler

集群随着时间的推移，不可避免地总有一些资源的分布会变得不符合期望，descheduler 会找到可以优化的 pod 并驱逐它们，使它们被重新调度到期望的位置上。

[descheduler](https://github.com/kubernetes-sigs/descheduler) 有非常多种部署方式，个人觉得 cronjob 可能是比较通用的一种解决方案。

官方提供的部署方法：

```shell
kubectl create -f kubernetes/base/rbac.yaml
kubectl create -f kubernetes/base/configmap.yaml
kubectl create -f kubernetes/cronjob/cronjob.yaml
```

其中的 `kubernetes/base/configmap.yaml` 这个 configmap 就保存了 deschudler 的所有配置。
descheduler 的所有配置变更，都是直接修改此文件。

descheduler 支持如下几种策略：

### RemoveDuplicates:

此策略尽量确保每个节点上，只有同一个 Replicaset/StatefulSet 的一个实例。如果有多个，就驱逐掉多余的实例。
从而确保同一个 ReplicaSet/StatefulSet 的实例尽量分布在不同节点上，提升高可用性

### HighNodeUtilization

此策略识别出所有资源用量低于某个阈值的节点，并尝试驱逐上面的所有 pods，使其能够被回收。

此策略必须与 kube-scheduler 或其他调度器的 `MostAllocated` 一起使用，否则即使 pod 被驱逐，仍然会无法回收对应的节点。

我遇到一个使用此策略的场景，是使用 aws karpenter 进行扩缩容后，发现集群低峰期实例数多了很多，原因是 karpenter(目前是 0.8.2) 只支持两种缩容策略：缩容空节点、缩容运行时长超过阈值的节点。但是不支持「**缩容资源使用率低的节点**」！相关 issue: https://github.com/kubernetes-sigs/descheduler/issues/749

但是实际使用后发现还是有问题，要改调度器的调度策略这就很不对劲啊...目前正在等待 aws karpenter 支持这个功能。



## volcano

[volcano](https://github.com/volcano-sh/volcano) 是一个专为 AI/Data 等计算密集型任务打造的调度器，支持多种调度策略。

它支持多种调度策略：

- gang scheduler: 在并发系统中，将多个相关联的进程调度到不同处理器上同时运行的策略。
  - 最主要的原则是保证所有相关联的进程能够同时启动，防止因部分进程未启动而导致整个关联进程组一直阻塞。
  - 这种导致阻塞的部分异常进程，称之为「碎片（fragement）」
  - gang scheduler 完全不允许碎片存在，也就是「All or Nothing」.
  - 主要应用场景：很多数据计算类的离线作业具有组合调度的特点，即要求所有的子任务都能够成功创建后，整个作业才能正常运行。


相关文档：

- [Volcano架构设计与原理解读](https://bbs.huaweicloud.com/blogs/detail/239645)
- [进击的Kubernetes调度系统（二）：支持批任务的Coscheduling/Gang scheduling](https://developer.aliyun.com/article/766275): 这里提到了 volcano 的一些缺陷
  - 单点问题，volcano 出问题可能会导致 pod 无法调度
  - 增加维护成本
  - 多 scheduler 共存可能会出现策略冲突


## Scheduler Framework

- [scheduler-plugins](https://github.com/kubernetes-sigs/scheduler-plugins)
- [Scheduler Framework 研读 (scheduler 02)](https://zhuanlan.zhihu.com/p/347816064)

