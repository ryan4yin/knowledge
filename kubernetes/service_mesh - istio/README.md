# Service Mesh

> 永远推荐使用 Operator 进行有状态应用的部署！使用 helm 或者官方客户端(如 istioctl)部署 Operator.

## 一、Istio

### 1. 简单部署

使用 istioctl 部署 istio:
```shell
# 示例1：只部署 istiod 和 ingressgateway
istioctl manifest apply --set profile=default --set values.prometheus.enabled=false 

# 示例2：只部署 istiod 和 ingressgateway，并且使用内网的 docker hub 缓存
istioctl manifest apply \
  --set profile=default \
  --set values.prometheus.enabled=false \
  --set hub=registry.svc.local > istio-manifest.yaml
```

这种方式适合自定义参数比较少，而且只是临时测试的情形。

其中 `profile` 的选择，参见 [Installation Configuration Profiles - Istio Docs](https://istio.io/latest/docs/setup/additional-setup/config-profiles/).

生产/测试环境建议使用 `default`，开发环境/试用 istio 建议使用 `demo`。


#### 1.1 自定义部署（推荐方式）

可以通过 `istioctl manifest apply -f istio-operator-values.yaml` 进行自定义部署，[istio-operator-values.yaml](./istio-operator-values.yaml) 就在当前文件夹内。

通过 [istio-operator-values.yaml](./istio-operator-values.yaml)，可以自定义 k8s 资源定义（节点选择器、HPA、资源预留与限制等等）、istio 组件本身的设置等等。而且可以直接保存在 git 仓库里，方便迭代、自动化部署。

可以通过 `istioctl profile dump` 查看完整的 IstioOperator 配置，作为编写 [istio-operator-values.yaml](./istio-operator-values.yaml) 的参考。

更多自定义部署的信息，参见官方文档 [istioctl: configure-component-settings](https://istio.io/docs/setup/install/istioctl/#configure-component-settings)


#### 1.2 升级与删除

滚动升级 istio:

```shell
# TODO 我使用此命令从 1.5.0 升级到 1.5.2 时一直卡住，没升级成功。
# 最后只好先删除掉 1.5.0 然后重新安装 1.5.2
istioctl upgrade -f istio-operator-values.yaml
```

删除 istio：

```shell
# 格式如下：
istioctl manifest generate <your original installation options> | kubectl delete -f -
# 示例一：使用 --set 指定自定义参数
istioctl manifest generate --set profile=default --set values.prometheus.enabled=false | kubectl delete -f -
# 示例二：使用 istiooperator 配置指定自定义参数
istioctl manifest generate -f istio-operator-values.yaml | kubectl delete -f -
```

### 2. 部署应用

#### 2.1 [Sidecar 注入](https://istio.io/latest/docs/setup/additional-setup/sidecar-injection/)

启动 Sidecar 自动注入：

```shell
kubectl label namespace default istio-injection=enabled
```

对某些不需要 Sidecar 的应用（如某些 Job/CronJob），可以在 Pod 模板上添加注解以禁止 Sidecar 注入：

```yaml
metadata:
  annotations:
    sidecar.istio.io/inject: "false"
```

### 3. 监控：istioctl + prometheus-operator

Istio 官方推荐在集群外部使用 [Prometheus Operator](https://github.com/coreos/prometheus-operator) 等工具搭建生产级别的 Prometheus 集群，然后和 Istio 默认部署的 Prometheus 组成联邦。
Istio Prometheus 只保存 6h 的数据，而外部的 Prometheus 可以将数据保存相当长的一段时间，并且提供自定义的 Grafana 面板。

另一种方案是部署 Istio 时不部署它自带的 Prometheus+Grafana，直接使用 [Prometheus Operator](https://github.com/coreos/prometheus-operator) 部署的监控系统进行监控。

配置步骤如下：
1. 部署 [Prometheus Operator](https://github.com/coreos/prometheus-operator)。
2. 修改 [istio-operator-values.yaml](./istio-operator-values.yamll)。最后几行 prometheus/prometheusOperator 相关的配置就是需要添加的内容。
  - 这一步实际做的是：关闭 Istio 自带的 Prometheus，改为创建 prometheusOperator 的自定义资源（`ServiceMonitor`）
  - prometheusOperator 如果默认就监控了 `istio-system` 这个名字空间，它就会根据 `ServiceMonitor` 的内容采集 Istio 数据。
3. `istioctl manifest apply -f istio-operator-values.yaml`：通过修改好的配置部署 istio 或更新 istio 配置。



#### Istio 的 Grafana 面板

Prometheus Operator 会自动部署 Grafana 面板，详见 [prometheus+grafana](/telemetry/prometheus+grafana/README.md)

再者我们前面部署 Istio 时已经为 Prometheus Operator 创建了 `ServiceMoniter` 抓取规则，没问题的话现在 Prometheus 中已经有 Istio 的数据了。
现在只缺少展示数据的 Grafana 面板。

Istio 官方有提供 Grafana 面板：https://grafana.com/orgs/istio，在这个页面上找到面板的 ID，
然后进入集群的 Grafana 页面中，使用 ID 就可一键导入 Istio 面板。

### 4. 链路追踪（Istio + Jaeger + OpenTelemetry）

>OpenTracing 只支持跟踪 HTTP/GRPC 调用，而 Opencensus 提供了自定义指标的功能，使我们能跟踪任意自定义指标（比如 mysql 调用、redis 调用，甚至任意本地方法调用）。
现在上述两个开放标准已经合二为一：[OpenTelemetry](https://github.com/open-telemetry).

Istio 链路追踪说是可以减少链路追踪对应用层的侵入，应用本身只需要转发一下 trace headers 就行，sidecar(也就是 envoy) 会自动帮你:

1. 生成 span(b3) 并添加到 http/grpc headers 中
2. 收集 http/grpc headers 中的 spans
3. 对 spans 进行采样
4. 将 spans 发送到指定的后端（使用 zipkin 协议）

但是实际调研后，发现上述流程的核心是 HTTP Headers，因此基本上只能支持 HTTP/gRPC 协议。
而 mysql/redis/message_queue 等都是使用的专有协议，Sidecar 或者我们的应用本身，都没有办法往这些流量中添加额外的链路信息。

因此使用服务网格进行链路追踪，只能满足我们的一小部分需求。对于 mysql/redis/mq 等非 http 协议的调用，还是必须由我们的应用自身来完成 span 的生成、收集、采样、上报。

这种情况下，如果要使用 Istio 的链路追踪，那就得根据流量类型进行上报了：

1. HTTP/gRPC: 由 Istio(Envoy) 进行上报
2. MySQL/Redis 等协议：由应用自身进行采集上报。

其实就只是拆出了一部分链路追踪的功能给 Istio 做了，另一部分还得自己处理。
具体实现还没仔细验证，我怀疑会比「不使用 Istio 链路追踪」更复杂也说不定。

#### 部署 jaeger operator

生产环境不建议部署 Istio 提供的 jaeger，它是一个 fat 容器（all in one），建议自己使用 [jaeger operator](https://github.com/jaegertracing/jaeger-operator) 进行部署。

如果打算使用 Istio 的链路追踪，那么 jaeger 需要开启 zipkin 协议支持，并且修改 istio 的 `values.global.tracer.zipkin.address` 指向 jager 的 zipkin 端口。

否则就和 Istio 没啥关系了，应用自身向 jaeger-agent(udp) 或者 jaeger-collector(http/grpc) 上报追踪数据。

部署流程参见 [/telemetry/jaeger/README.md](/telemetry/jaeger/README.md)


### 5. Kiali 网络拓扑/流量拓扑

从 Istio 1.7 开始，Istioctl 不再安装 kiali，推荐使用 helm 部署最新稳定版的 kiali.

首先安装 helm-operator:

```shell
# 下载 flux 的 charts，我们需要修改其中一些配置
helm repo add kiali https://kiali.org/helm-charts
# 查看历史版本
helm search repo kiali/kiali-operator -l | head
# 下载并解压 chart
helm pull kiali/kiali-operator --untar --version 1.23.0

# 安装或更新
kubectl create namespace kiali-operator
helm upgrade --install kiali-operator --namespace kiali-operator -f kiali-operator-values.yaml ./kiali-operator

# 卸载
helm uninstall kiali-operator --namespace kiali-operator
```

>和 jaeger-operator 一样，kiali-operator 自身也没几个参数可配置。

operator 有了，现在手动下载并修改 [kiali_cr.yaml](https://github.com/kiali/kiali-operator/blob/master/deploy/kiali/kiali_cr.yaml) 并部署。
kiali-operator 会根据 `kiali_cr.yaml` 的内容，创建/更新/修改 kiali 服务。

需要修改的配置有：

1. prometheus+grafana: kiali 需要从 prometheus 中查询 istio 网格的各项指标。
   1. 我们使用 prometheus operator，需要自定义 prometheus 的 url 为 `http://prometheus-operator-prometheus.monitoring:9090`
   2. kiali 需要使用 grafana 中定义好的 istio 相关 PromQL，因此得自定义 grafana 的 url 为 `http://prometheus-operator-grafana.monitoring:80`
1. jaeger: kiali 还需要查询链路追踪的数据，因此还得配置 jaeger-query　的　api url: `http://jaeger.tracing:80`
1. Web UI 相关：kiali 通过 Web UI 展示网格数据。
   1. `auth`: 测试环境可设置为 `anonymous`，方便测试。

```shell
kubectl apply -f my-kiali-cr.yaml -n istio-system
```
