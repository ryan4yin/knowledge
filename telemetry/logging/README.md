# Logging

kubernetes 集群的日志收集与分析方案，目前主要有两个：

1. EFK: 传统的日志收集与分析方案，用户量巨大。但是比较重，而且吃性能。
2. loki: grafanalab 出品的新一代日志收集方案。参照 Prometheus 的思路给日志打标签，不提供全文检索。

这里提供两种方案的部署，具体的对比参见 loke 官方文档：[Loki/Promtail/Grafana vs EFK](https://grafana.com/docs/loki/latest/overview/comparisons/)


## AIOps - logging

基于日志的 AIOps，暂时不是很了解，待补充。
