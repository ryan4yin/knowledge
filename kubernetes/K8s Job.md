# K8s Job 

Job 这里需要注意的一个点，是 `spec.template.spec.restartPolicy` 和 `.spec.backoffLimit`。它们都是失败重试机制的一部分。

先说 `spec.template.spec.restartPolicy`:

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

CronJob 倒没啥好说的，就记一下 cron 表达式。
还有指定两个保存历史记录个数的参数值得多瞟一眼：``

## 参考

- [Jobs - Run to Completion](https://kubernetes.io/docs/concepts/workloads/controllers/jobs-run-to-completion/)
