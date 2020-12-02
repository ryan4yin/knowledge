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


## Kubernetes CronJob 存在的问题（摘抄）

自开始将这些重复的计划任务移至Kubernetes以来，我们发现开箱即用地使用CronJob，导致开发人员和平台团队都遇到了很多个痛点，这些痛点抵消了收益和成本。为了节省开支，我们最初选择了Kubernetes CronJob。但我们很快意识到，我们的开发人员和平台团队都没有配备必要的工具来操作和理解CronJobs复杂的生命周期。

Lyft的开发人员在尝试操作和调试其Kubernetes CronJobs时遇到了许多问题和投诉，例如：

- “为什么我的cron不运行？”
- “我认为我的cron停止了运行。我如何知道我的cron是否正在运行？”
- “我不知道cron不在运行，我只是以为它在运行！”
- “我该如何补救X失败的Cron？我不能只是自己输入和运行命令。”
- “你能解释一下为什么这个Cron似乎错过了X和Y [时间段]之间的一些时间表吗？”
- “我们有X（大量）corn，每个corn都有自己的警报，维护它们实在是非常乏味/痛苦。”
- “这乱七八糟的一堆 Job、Pod、Sidecar 都是干啥的？”

作为平台团队，我们没有能力回答以下问题：

- 我们如何量化Kubernetes Cron平台的性能特征？
- 在我们的Kubernetes环境中加入更多CronJobs有什么影响？
- 与单租户Unix cron相比，运行多租户Kubernetes CronJobs的性能如何？
- 我们如何开始定义与客户沟通的服务水平目标（SLO）？
- 作为平台运营商，我们要监视什么并发出警报，以确保在不影响客户的情况下迅速解决平台范围的问题？
- 
调试CronJob故障并不是一件容易的事，并且通常需要对故障发生的位置以及寻找证据的位置进行直观了解。有时，很难找到这些证据，例如cronjobcontroller仅以高详细日志级别记录的日志。或者，这些痕迹只是在特定时间段后消失，使调试变成“打地鼠”游戏。例如CronJob，Job和Pod对象本身上的Kubernetes Events，默认情况下仅保留一小时。这些方法都不容易使用，而且考虑到平台上越来越多 CronJobs，这些方法的伸缩性也不怎么好。

另外，有时当CronJob错过了太多运行时段，Kubernetes只会**退出**，需要有人手动给 CronJob「松绑」。在实际使用中，这种情况发生的频率比您想像的要高，并且每次手动修复都变得很痛苦。

### 解决方法

痛点在于 Cronjob：

1. 没有方便可靠的监控告警方案，有些错误被会静默处理，无法主动报警。
2. 调度失败次数太多，将需要手动处理。

目前 Lyft 是自己搞了一套自定义的方案，而我公司这边，是暂时自己把我们的 Cronjobs 改造成了死循环，通过 Deployment 调度，通过日志关键字(Error/Fail)来设置告警...

官方目前有个 EAP，计划重写 Cronjob Controller，添加指标支持，改善性能: [KEP-19: Graduate CronJob to stable](https://github.com/kubernetes/enhancements/blob/master/keps/sig-apps/19-Graduate-CronJob-to-Stable/README.md)

该计划打算在 1.20 中推出 Alpha 版本，在 1.21 中进入 Beta 阶段.


## 参考

- [Jobs - Run to Completion - Kubernetes](https://kubernetes.io/docs/concepts/workloads/controllers/jobs-run-to-completion/)
- [CronJob - Kubernetes](https://kubernetes.io/zh/docs/concepts/workloads/controllers/cron-jobs/)
- [How we learned to improve Kubernetes CronJobs at Scale (Part 1 of 2) - Lyft](https://eng.lyft.com/improving-kubernetes-cronjobs-at-scale-part-1-cf1479df98d4)
- [我们如何学会大规模改善Kubernetes CronJobs（第2部分，共2部分） - Lyft](https://zhuanlan.zhihu.com/p/305040921)
