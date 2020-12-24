# Telemetry（遥测） - Metrics（指标）、Logging（日志）、Tracing（追踪）

云原生的 Telemetry 源自控制论中的[可观察性 - Observability](https://en.wikipedia.org/wiki/Observability)，其中有一段话：

>In control theory, observability is a measure of how well internal states of a system can be inferred from knowledge of its external outputs.

我们可以通过系统的外部输出来推断系统内部的状态，「可观测性」就被用于衡量这个「内部状态推断」的精确性。
「推断」越是精确便捷，我们就说这个系统的「可观测性」越好。

云原生下有如下三种手段去观察一个云服务：

1. 指标：即监控指标，主要使用 Prometheus 采集，通过 Grafana 进行可视化。
   1. 集群本身也会使用一些指标进行自动伸缩、判断服务、节点是否处于异常状态等。
2. 日志：这是传统应用最重要的问题排查方式，但是在云原生场景下，日志需要被收集，统一处理。
   1. 通过 EFK 等系统，可以对数据进行各种高级的分析：搜索、聚类、特征提取等
3. 链路追踪：微服务架构下问题排查的必要功能。

通过这三种「外部输出」，我们可以推断出微服务内部的状态：资源不足、定位 Bug、性能不够等等。
这三个「外部输出」越精确，那我们就越容易做出正确的推断。


## AIOps

随着 AI 技术应用的推广，AI 技术也渐渐渗透到运维平台，AIOps 即智能运维。

传统的 logging/metrics/tracing 数据使用方式，通常都是靠人工分析出异常特征，然后添加对应的告警规则。
更智能一些的平台还可以配置对应的故障自愈方法。

而 AIOps 则是使用 AI 技术去智能地在 logging/metrics/tracing 进行异常检测(anomaly-detection)，检测到异常后执行对应的故障自愈操作。

这个领域我目前了解还很欠缺，待补充

### AIOps 参考资料

- [Metis - a learnware platform in the field of AIOps](https://github.com/Tencent/Metis)
- [Collection of slides, repositories, papers about AIOps](https://github.com/chenryn/aiops-handbook)
- [awesome-AIOps](https://github.com/linjinjin123/awesome-AIOps)


## telemetry 相关资料

视频:

- [OpenTelemetry Agent and Collector: Telemetry Built-in Into All Service - Steve Flanders & Trask Stalnaker](https://www.youtube.com/watch?v=cHiFSprUqa0&list=PLj6h78yzYM2O1wlsM-Ma-RYhfT5LKq0XC&index=88)

