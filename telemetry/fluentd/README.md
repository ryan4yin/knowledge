# Fluentd

云原生日志收集器

## 部署到 Kubernetes 中

- [fluent/fluentd-kubernetes-daemonset](https://github.com/fluent/fluentd-kubernetes-daemonset/): Fluentd 官方提供的 daemonset 部署方法，可以方便地通过环境变量配置 Fluentd.
  - 用于日志存储与分析的 ElasticSearch/Kibana 请额外部署。
  - 所有的环境变量：参见 [fluentd-kubernetes-daemonset - fluent.conf](https://github.com/fluent/fluentd-kubernetes-daemonset/blob/master/docker-image/v1.9/debian-elasticsearch7/conf/fluent.conf)

## 「Bug」记录

- [Fluentd 报错：`Worker 0 finished unexpectedly with signal SIGKILL`](https://github.com/fluent/fluentd/issues/2408): 内存不足，增加 `resources.limits.memory` 的值。


## 日志分析 - EFK

数据采集到 ElasticSearch 中，通过 Kibana 面板进行数据分析。
