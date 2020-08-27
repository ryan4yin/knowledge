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