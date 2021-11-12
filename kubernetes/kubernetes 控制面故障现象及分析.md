# kubernetes 控制面故障现象及分析

当 Kubernetes 的控制面出现故障时，往往会导致集群出现各种奇怪的现象。

这里记录下我遇到过的，以及测试过的种种控制面故障造成的异常。供以后排查问题时参考。


## 为 Kubernetes 控制面添加监控与告警

如前所述，控制面故障造成的种种异常，往往非常不直观。
你可能太过相信集群控制面，导致你根本想不到这个问题可能是控制面故障导致的。

可以考虑维护一套控制面的监控告警机制。

对于 AWS EKS，控制面的 pod 对我们而言是不可见的，不过可以使用如下命令检查控制面的状态：

```shell
kubectl get componentstatuses
```

而对于使用 kubeadm 自建的集群，直接检查控制面 pod 的状态即可：

```
kubectl get pod -n kube-system | grep kube-apiserver
kubectl get pod -n kube-system | grep etcd
kubectl get pod -n kube-system | grep kube-controller-manager
kubectl get pod -n kube-system | grep kube-scheduler
```

## kube-apiserver 故障

如果 kube-apiserver 发生故障，最明显的现象应该是：kubectl 命令无法使用了，各种与 apiserver 沟通的 controller 也将不断报错。

这个现象还是很明显的。


## etcd 故障

对于托管版的集群而言，如果挂掉少于 1/2 的节点，对我们并没有影响，云服务商也会自行处理恢复。

对于自建集群且使用 static pod 运行的 etcd，可以直接通过 kubectl 观测到所有 etcd 实例的状态。

如果挂掉超过一半节点，所有集群数据将无法再更新，集群会彻底锁住，直到可用节点数超过 1/2


## kube-controller-manager 故障

kube-controller-manager 包含了一组 kubernetes 集群内置的控制器，如：

- 节点控制器（Node Controller）: 负责在节点出现故障时进行通知和响应
- Deployment Controller / Daemon Controller / StatefulSet Controller / RelicaSet
- Horizontal Pod Autoscaler: 负责 Pods 的动态伸缩
- 任务控制器（Job Controller + CronJob Controller）: 监测代表一次性任务的 Job 对象，然后创建 Pods 来运行这些任务直至完成
- 端点控制器（Endpoints Controller）: 填充端点(Endpoints)对象(即加入 Service 与 Pod)
-  Namespace Controller
- 服务帐户和令牌控制器（Service Account & Token Controllers）: 为新的命名空间创建默认帐户和 API 访问令牌
- ...

因此，如果 kube-controller-manager 发生故障，可能产生的现象有：

1. 节点的服务器已经被终止，但是 Kuberntes 里还显示 node 为 Ready 状态，不会更新为 NotReady.
2. 被删除的 Pods 可能会卡在 Terminating 状态，只有强制删除才能删除掉它们。并且确认 Pod 没有 `metadata.finalizers` 属性
3. HPA 的动态伸缩功能失效
4. ...

如果这些现象同时发生，就要怀疑是否是 kube-controller-manager 出问题了.

我们有实际遇到过 AWS EKS 的 controller-manager 故障，导致集群出现上述异常。在花了大量时间后，最终通过如下命令确认是托管的 EKS controller-manager 故障：

```shell
$ kubectl get componentstatuses
Warning: v1 ComponentStatus is deprecated in v1.19+
NAME                 STATUS      MESSAGE                                                                                       ERROR
controller-manager   Unhealthy   Get "http://127.0.0.1:10252/healthz ": dial tcp 127.0.0.1:10252: connect: connection refused
scheduler            Healthy     ok
etcd-0               Healthy     {"health":"true"}
```

由 aws 工程师内部提工单，手动处理后，才恢复。故障时间持续了超过 12 小时。
而且完全没感知到 EKS 控制平面的异常，花了大量时间排查上述的表面现象。

## kube-scheduler 故障

kube-scheduler 主要负责 Pod 的调度，将刚创建的 Pods，根据各种策略，调度到合适的节点上去。

因此它如果出现故障，可能会导致 Pod 调度失败。如果出现类似的错误，就要怀疑是否是 kube-scheduler 故障...
