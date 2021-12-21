# Scheduler

- [descheduler](https://github.com/kubernetes-sigs/descheduler): 集群随着时间的推移，不可避免地总有一些资源的分布会变得不符合期望，descheduler 会找到可以优化的 pod 并驱逐它们，使它们被重新调度到期望的位置上

- [volcano](https://github.com/volcano-sh/volcano): 专为 AI/Data 等计算密集型任务打造的调度器，支持多种调度策略


## descheduler

待续，反正推荐搞一个。


## volcano

支持多种调度策略：

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

