# Logging

kubernetes 集群的日志收集与分析方案，目前主要有两个：

1. EFK: 传统的日志收集与分析方案，用户量巨大。但是比较重，而且吃性能。
2. loki: grafanalab 出品的新一代日志收集方案。参照 Prometheus 的思路给日志打标签，不提供全文检索。

这里提供两种方案的部署，具体的对比参见 loke 官方文档：[Loki/Promtail/Grafana vs EFK](https://grafana.com/docs/loki/latest/overview/comparisons/)


## 日志是否落盘

在日志量很大的情况下，日志先写入本地磁盘，再通过 fluentd 等 agent 采集日志，对磁盘 IO 会有很大压力，整体性能不高。

如果遇到这种情况，建议将业务容器的日志组件直接对接日志系统，日志直接用 UDP 协议发送到后端，这样做性能会有一个很大的提升。
但是缺点就是，日志可能会因为网络问题、日志接收端负载等问题发生丢失。另一方面日志就只能通过日志系统查看了，`kubectl log` 将无法查看到任何日志。

## AIOps - logging

基于日志的 AIOps，暂时不是很了解，待补充。
