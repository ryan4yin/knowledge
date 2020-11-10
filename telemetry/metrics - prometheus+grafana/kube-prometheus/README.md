
## 二、Kubernetes 监控部署

有两个部署方案，都是基于 [prometheus-operator](https://github.com/prometheus-operator/prometheus-operator)：

- [kube-prometheus-stack helm chart](https://github.com/prometheus-community/helm-charts): 简明快捷地部署一个 prometheus operator + 其他相关应用。
- [coreos/kube-prometheus](https://github.com/coreos/kube-prometheus): prometheus operator 官方提供的部署方案，使用了 jsonnet，深入学习的话，比 helm 版的要更复杂一些。

上述两个工具部署的 prometheus-operator 都可以和 istio 集成，替换掉 istioctl 自带的 prometheus+grafana，参见 [istioctl + prometheus-operator](/kubernetes/service_mesh/README.md)

以 helm 部署为例，部署命令：

```shell
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
# 查看 kube-prometheus-stack 版本号
helm search repo prometheus-community/kube-prometheus-stack -l | head
# 下载并解压 chart
helm pull prometheus-community/kube-prometheus-stack --untar --version 11.1.0

# 使用自定义的 cutome-values.yaml 进行部署（helm3）
kubectl create ns monitoring
helm upgrade --install \
  --namespace monitoring \
  -f custom-values.yaml \
  kube-prometheus-stack \
  ./kube-prometheus-stack
```

## 三、使用 Prometheus

我在 `custom-values.yaml` 中将 grafana/altermanager/prometheus 均通过 NodePort 方式暴露到了外部，可以通过如下端口号访问这三个服务：

1. grafana：30880 端口，账号 admin，密码在 `grafana.adminPassword` 中定义，请进入 `custom-values.yaml` 查看。
1. prometheus: 30090 端口
2. altermanager: 30903 端口


## 四、高可用 Prometheus

由于 Prometheus 本身不支持高可用（就像 MySQL 一样，本身只是一个单机数据库），因此也有专门提供集群版 Prometheus 的工具比较被看好的有：

- [thanos](https://github.com/thanos-io/thanos): Highly available Prometheus setup with long term storage capabilities，prometheus-operator 可以与它结合使用。
- [VictoriaMetrics](https://github.com/VictoriaMetrics/VictoriaMetrics): 一个相当新的解决方案，支持 PromQL 等多种协议，永久性存储，据说还很快。

还有另外两个 Prometheus 集群方案也可以考虑：

- [m3db](https://github.com/m3db/m3): Distributed TSDB, Aggregator and Query Engine, Prometheus Sidecar, Graphite Compatible, Metrics Platform，由 Uber 开源
- [cortex](https://github.com/cortexproject/cortex): A horizontally scalable, highly available, multi-tenant, long term Prometheus. 和 Thanos 类似，但是 Thanos 据说更简单，因此更受欢迎些。



可以通过上述几种高可用部署方式实现 prometheus 数据的聚合（也可用 Prometheus 文档介绍的联邦集群实现）、永久性存储。


## 指标抓取配置：PodMonitor/ServiceMonitor

>详见 [prometheus-operator - customresourcedefinitions](https://github.com/prometheus-operator/prometheus-operator#customresourcedefinitions)

docker 方式部署的 prometheus，它的抓取配置直接写在 `prometheus.yml` 的 `scrape_configs` 里面，
而 prometheus-operator，则通过自定义资源(CR) PodMonitor/ServiceMonitor 来进行抓取配置。



## 监控数据的汇总、可视化与持久化

常用的手段：集群内部的 prometheus 和集群外部的 prometheus 组建联邦。
内部 prometheus 设置数据保留时间为 24h 甚至更短，外部 prometheus 设置数据保留时间为 1 个月。

多个集群及其他主机的监控数据，都通过联邦汇总到一个外部 prometheus 中，再通过 grafana 提供统一的监控面板。

