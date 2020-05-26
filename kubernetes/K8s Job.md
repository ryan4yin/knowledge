# K8s Job 

Job 这里需要注意的一个点，是 `spec.template.spec.restartPolicy` 和 `.spec.backoffLimit`。它们都是失败重试机制的一部分。

先说 `spec.template.spec.restartPolicy`，Job 中该参数只能在下列两个选项中二选一:

1. 当 `.spec.template.spec.restartPolicy = "OnFailure"` 时，Pod 会留在原地，而容器会被原地重新启动。
2. 当 `.spec.template.spec.restartPolicy = "Never"` 时，Pod 会留在原地，容器不会重启。而 Pod 会转变到 Failed 状态（单容器的情况下）。

而 `.spec.backoffLimit` 则是一个用于负责控制 Job 重试次数（pod 的 restart/failed 总数？）的参数，默认情况下它的值为 `6`。
当 Pod 失败时，Job 会自动建立一个新的 Pod。但是每次重试的时间间隔是指数级增长的。

如何你设置了 `restartPolicy = "OnFailure"`，那么 Pod 将在达到 `backoffLimit` 时被 Terminating，结果就是容器没了，日志也没了。
为了保存日志，方便后续分析问题，可以使用如下两种方案之一：

1. 使用日志系统（比如 EFK）
1. 在测试阶段将 `restartPolicy` 设为 `Never`

最后还有一个 `.spec.activeDeadlineSeconds` 参数值得注意，它指定了任务的超时时间，只要任务超过该时间，就一定会被强制停止！

## CronJob

1. **只应该使用 CronJob 运行幂等的任务！（类比 HTTP 的 PUT 方法）**因为 k8s 不能保证 CronJob 只被运行一次。
   - CronJob 创建 Job 对象，每个 Job 的执行次数**大约**为一次。 我们之所以说 “大约”，是因为在某些情况下，可能会创建两个 Job，或者不会创建任何 Job。 我们试图使这些情况尽量少发生，但不能完全杜绝。
   - 如果您不指定 startingDeadlineSeconds 值，则 CronJob 永远不会超时。这可能会导致同一个 CronJob 同时运行多次。



## 参考

- [Jobs - Run to Completion - Kubernetes](https://kubernetes.io/docs/concepts/workloads/controllers/jobs-run-to-completion/)
- [CronJob - Kubernetes](https://kubernetes.io/zh/docs/concepts/workloads/controllers/cron-jobs/)