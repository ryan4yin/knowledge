# ElasticSearch+Fluentd+Kibana 日志分析系统

云原生日志收集器

## 部署 Fluentd

- [fluent/fluentd-kubernetes-daemonset](https://github.com/fluent/fluentd-kubernetes-daemonset/):
  Fluentd 官方提供的 daemonset 部署方法，可以方便地通过环境变量配置 Fluentd.
  - 用于日志存储与分析的 ElasticSearch/Kibana 请额外部署。
  - 所有的环境变量：参见
    [fluentd-kubernetes-daemonset - fluent.conf](https://github.com/fluent/fluentd-kubernetes-daemonset/blob/master/docker-image/v1.9/debian-elasticsearch7/conf/fluent.conf)

## Fluentd「Bug」记录

- [Fluentd 报错：`Worker 0 finished unexpectedly with signal SIGKILL`](https://github.com/fluent/fluentd/issues/2408):
  内存不足，增加 `resources.limits.memory` 的值。

## ElasticSearch + Kibana

参见 [/database/elasticsearch/README.md](/database/elasticsearch/README.md)

## 日志的常见分析手段

1. 日志聚类：智能聚类可以让日志更清晰明了。
2. 时序分析：某段时间日志激增？
3. 交互式分析：关键字查询等，需要高效的搜索语法。

## 参考

- [最佳日志实践（v2.0）](https://zhuanlan.zhihu.com/p/27363484)
- [阿里 PB 级 Kubernetes 日志平台建设实践](https://www.infoq.cn/article/HiIxh-8o0Lm4b3DWKvph)
- [智能日志分析 - 阿里云日志服务](https://zhuanlan.zhihu.com/aliyunlog)
- [日志记录规范总结](http://jalan.space/2019/05/09/2019/logging-best-pratices/)
- [Kubernetes Ingress 日志分析与监控的最佳实践](https://my.oschina.net/u/1464083/blog/3028522)
