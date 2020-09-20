# K8s Job 

Job 这里需要注意的一个点，是 `spec.template.spec.restartPolicy` 和 `.spec.backoffLimit`。它们都是失败重试机制的一部分。

先说 `spec.template.spec.restartPolicy`，Job 中该参数只能在下列两个选项中二选一:

1. 当 `.spec.template.spec.restartPolicy = "OnFailure"` 时，Pod 会留在原地，Job 重试时会原地重新启动 Pod。
2. 当 `.spec.template.spec.restartPolicy = "Never"` 时，Pod 会转变到 Failed 状态（单容器的情况下）。Job 重试时会新建 Pod 执行任务！

而 `.spec.backoffLimit` 则是一个用于负责控制 Job 重试次数的参数，默认情况下它的值为 `6`。

如果你设置了 `restartPolicy = "OnFailure"`，那么 Pod 将在达到 `backoffLimit` 重启次数时状态将转变成 Terminating，结果就是容器没了，日志也没了。
为了保存日志，方便后续分析问题，可以使用如下两种方案之一：

1. 使用日志系统（比如 EFK）
1. 在测试阶段将 `restartPolicy` 设为 `Never`，这种情况下 Job 重试会新建 Pod，所有的历史 Pod 都会保留。

最后还有一个 `.spec.activeDeadlineSeconds` 参数值得注意，它指定了任务的超时时间，只要任务超过该时间，就一定会被强制停止！谨慎使用。

## CronJob

1. **只应该使用 CronJob 运行幂等的任务！（类比 HTTP 的 PUT 方法）**因为 k8s 不能保证 CronJob 只被运行一次。
   - CronJob 创建 Job 对象，每个 Job 的执行次数**大约**为一次。 我们之所以说 “大约”，是因为在某些情况下，可能会创建两个 Job，或者不会创建任何 Job。 我们试图使这些情况尽量少发生，但不能完全杜绝。
   - 如果您不指定 startingDeadlineSeconds 值，则 CronJob 永远不会超时。这可能会导致同一个 CronJob 同时运行多次。
1. 可通过 `spec.concurrencyPolicy` 设置禁止任务并行执行。
3. 如果未能在调度时间内创建 CronJob，则计为「missed」错过调度时间。 
   1. 例如，如果 concurrencyPolicy 被设置为 Forbid，并且当前有一个调度仍在运行的情况下， 试图调度的 CronJob 将被计算为错过。
   2. 如果「错过次数」超过 100 次，Cronjob 将报错并停止工作。
4. `.spec.suspend` 可用于临时挂起 Cronjob，让它不生效。
2. 可通过 `.spec.startingDeadlineSeconds` 设置任务的调度超时时间。在这个时间段内（比如 200 秒内） Job 可以被多次重试直到“成功被调度”。
   1. 如果设置了这个参数，Cronjob 将只统计 startingDeadlineSeconds（如 200 秒）内的 CronJob「错过次数」，以此判断是否停止 Cronjob.
3. 通过 `.spec.jobTemplate.spec.activeDeadlineSeconds`，可以设置 Job 的超时时间，超时的任务会被强制停止！谨慎使用。

如果不能接受上面提到的这些 CronJob 的问题，可以考虑修改代码，让容器自己常驻后台，自行处理定时执行的任务。
这样因为 Pod 常驻后台，就成了一个 Deployment 了，也就不受不可靠的 Cronjob 影响。
任务的超时、并发等问题，都可以在自己的代码中去处理，更灵活也更复杂。

## 参考

- [Jobs - Run to Completion - Kubernetes](https://kubernetes.io/docs/concepts/workloads/controllers/jobs-run-to-completion/)
- [CronJob - Kubernetes](https://kubernetes.io/zh/docs/concepts/workloads/controllers/cron-jobs/)