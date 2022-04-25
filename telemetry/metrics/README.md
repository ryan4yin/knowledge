# 通用监控方案：Prometheus + Grafana + Altermanager

在监控领域 netdata 是一个非常流行的监控方案，它有非常漂亮的监控面板，用的 CPU 据说也不多，很适合单机监控的场景。

而在集群监控场景中，Node_Exporter + Prometheus + Grafana + Altermanager 是目前云原生社区最流行的开源监控告警方案:

1. Prometheus: 指标暴露、抓取、存储以及告警
   1. expoter: 通常由被抓取目标主动 export 可供抓取的 http metrics endpoint.
   2. 抓取指标：prometheus 根据 `prometheus.yml` 中 `scrape_configs` 的配置，进行指标抓取。
   3. 存储：指标直接存储到本机硬盘中，可以配置指标保留时间。
   4. 告警：alertrules 在 `prometheus.yml` 的 `rule_files` 中配置。
2. Grafana: 指标的展示面板，可以通过 json 配置完全自定义自己的监控面板。
   1. Grafana 也自带一个报警的功能，但是貌似没啥人用（据说很繁琐，而且功能不强）。
3. Altermanager: prometheus 的告警组件，它接收 prometheus 给出的告警，然后通过 web_hook/mail 等方式，将信息发给正确的接收者。
   1. alertmanager 是「联系人」和「prometheus」的一个中间层，用于解耦具体的报警方式。


这套监控系统有两种主流的部署方式：

1. docker-compose 方式：这种方式适合用于监控非 kubernetes 目标，或者用于和集群内部的 prometheus 做联邦集群。
2. helm chart 方式：通过社区提供的 helm chart 部署 prometheus.

详细的内容参见 `dockprom` 和 `Prometheus for Kubernetes`。

## 相关文档

- [prometheus-book - github](https://github.com/yunlzheng/prometheus-book)
- [容器监控方案汇总  - github](https://github.com/yasongxu/container-monitor)
- [这篇文章，让运维监控不再成为你的短板!](https://segmentfault.com/a/1190000020990098)
- [Prometheus在京东开源项目ChubaoFS中的使用](https://developer.jdcloud.com/article/983)