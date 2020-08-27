# 通用监控方案：Prometheus + Grafana + Altermanager


## Docker 方式部署

这种方式可以部署单机版的一整套监控方案：

- [github - dockprom](https://github.com/stefanprodan/dockprom)

## Kubernetes 监控

两个部署方案，都是基于 [prometheus-operator](https://github.com/prometheus-operator/prometheus-operator)：

- [prometheus-operator helm chart](https://github.com/helm/charts/tree/master/stable/prometheus-operator): 简明快捷地部署一个 prometheus operator。
- [coreos/kube-prometheus](https://github.com/coreos/kube-prometheus): prometheus operator 官方提供的部署方案，使用了 jsonnet，深入学习的话，比 helm 版的要更复杂一些。

上述两个工具部署的 prometheus-operator 都可以和 istio 集成，替换掉 istioctl 自带的 prometheus+grafana，参见 [istioctl + prometheus-operator](/kubernetes/service_mesh/README.md)


## 高可用 Prometheus

由于 Prometheus 本身不支持高可用（就像 MySQL 一样，本身只是一个单机数据库），因此也有专门提供集群版 Prometheus 的工具比较被看好的有：

- [thanos](https://github.com/thanos-io/thanos): Highly available Prometheus setup with long term storage capabilities.
- [VictoriaMetrics](https://github.com/VictoriaMetrics/VictoriaMetrics): 一个相当新的解决方案，支持 PromQL 等多种协议，永久性存储，据说还很快。

还有另外两个 Prometheus 集群方案也可以考虑：

- [m3db](https://github.com/m3db/m3): Distributed TSDB, Aggregator and Query Engine, Prometheus Sidecar, Graphite Compatible, Metrics Platform 
- [cortex](https://github.com/cortexproject/cortex): A horizontally scalable, highly available, multi-tenant, long term Prometheus.



可以通过上述几种高可用部署方式实现 prometheus 数据的聚合（也可用 Prometheus 文档介绍的联邦集群实现）、永久性存储。

## 自定义 Grafana 面板

待续


## 监控数据的汇总、可视化与持久化

常用的手段：集群内部的 prometheus 和集群外部的 prometheus 组建联邦。
内部 prometheus 设置数据保留时间为 24h 甚至更短，外部 prometheus 设置数据保留时间为 1 个月。

多个集群及其他主机的监控数据，都通过联邦汇总到一个外部 prometheus 中，再通过 grafana 提供统一的监控面板。
