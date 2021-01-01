# Service Mesh

一句话介绍：服务网格接管集群内的所有流量，实现方式是在每个 Pod 中注入一个 Sidecar 容器（envoy）做网络代理。


服务网格的优势：

1. 流量控制
   1. 流量切分与流量镜像。
   2. 东西向与南北向流量的四/七层负载均衡。
   1. 请求自动重试、故障注入。
   2. Rewrite HTTP URIs and Authority(HOST) headers
2. 观察：集群内流量的可观察性，提供丰富的流量监控能力。
3. 安全：东西向与南北向流量的 mTLS 加密，JWT 鉴权。

## 一、Istio

> 永远推荐使用 Operator 进行有状态应用的部署！使用 helm 或者官方客户端(如 istioctl)部署 Operator.

>当前针对的 Istio 版本：1.7.x

### 1. 简单部署

使用 istioctl 部署 istio:
```shell
# 示例1：只部署 istiod 和 ingressgateway
istioctl manifest apply --set profile=default

# 示例2：只部署 istiod 和 ingressgateway，并且从内网的容器镜像仓库拉镜像 
istioctl manifest apply --set profile=default --set hub=registry.svc.local
```

这种方式适合自定义参数比较少，而且只是临时测试的情形。

其中 `profile` 的选择，参见 [Installation Configuration Profiles - Istio Docs](https://istio.io/latest/docs/setup/additional-setup/config-profiles/).

生产/测试环境建议使用 `default`，开发环境/试用 istio 建议使用 `demo`。


#### 1.1 自定义部署（推荐方式）

可以通过 [istio-operator-values.yaml](./istio-operator-values.yaml) 配置文件进行自定义部署：

```shell
# istioctl 1.5+
istioctl manifest apply -f istio-operator-values.yaml

# istioctl 1.7+
istioctl install -f istio-operator-values.yaml
```

通过 [istio-operator-values.yaml](./istio-operator-values.yaml)，可以自定义 k8s 资源定义（节点选择器、HPA、资源预留与限制等等）、istio 组件本身的设置等等。而且可以直接保存在 git 仓库里，方便迭代、自动化部署。

可以通过 `istioctl profile dump demo` 查看完整的 IstioOperator 配置，作为编写 [istio-operator-values.yaml](./istio-operator-values.yaml) 的参考。

更多自定义部署的信息，参见官方文档 [istioctl: configure-component-settings](https://istio.io/docs/setup/install/istioctl/#configure-component-settings)


#### 1.2 升级与删除

滚动升级 istio:

```shell
# 还未测试成功
istioctl upgrade -f istio-operator-values.yaml
```

删除 istio：

```shell
# 格式如下：
istioctl manifest generate <your original installation options> | kubectl delete -f -
# 示例一：使用 --set 指定自定义参数
istioctl manifest generate --set profile=default | kubectl delete -f -
# 示例二：使用 istiooperator 配置指定自定义参数
istioctl manifest generate -f istio-operator-values.yaml | kubectl delete -f -

# istioctl 1.7+ 提供更简单的命令
istioctl x uninstall -f istio-operator-values.yaml
```

#### 1.3 查看与动态修改 Istio 配置

部署完成后，Istio 的配置将会以 configmap 的形式，保存在 istio-system 名字空间中：

1. `istio`: 这个 configmap 包含了 `spec.meshConfig` 的几乎所有内容。
2. `istio-sidecar-injector`: 这个 configmap 包含了 sidecar 的所有配置。

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

配置步骤如下：
1. 部署 Prometheus Operator，步骤参见 [telemetry - kube-prometheus](/telemetry/metrics%20-%20prometheus+grafana/kube-prometheus/README.md)
2. 修改 [istio-operator-values.yaml](./istio-operator-values.yamll)，将 `spec.meshConfig.enablePrometheusMerge` 设为 true.
   1. 启用这项配置后，istio 将在数据层注入 prometheus 相关注解，使 prometheus-operator 开箱即用.
3. `istioctl install -f istio-operator-values.yaml`：通过修改好的配置部署 istio 或更新 istio 配置。



#### Istio 的 Grafana 面板

我们前面部署 Istio 时已经为 Prometheus Operator 创建了 `ServiceMoniter` 抓取规则，没问题的话现在 Prometheus 中已经有 Istio 的数据了。
现在只缺少展示数据的 Grafana 面板。

Prometheus Operator 会自动部署 Grafana 面板，详见 [telemetry - kube-prometheus](/telemetry/metrics%20-%20prometheus+grafana/kube-prometheus/README.md)，但是不包含 Istio 的 Dashboard 配置。


在这个页面中找到最新版本的 Istio Dashboard ID: https://grafana.com/orgs/istio
然后进入 kube-prometheus 的 Grafana 页面，使用 ID 就可一键导入 Istio Dashboard。

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

jaeger-operator 的详细部署流程参见 [/telemetry/tracing - jaeger/README.md](/telemetry/tracing%20-%20jaeger/README.md)


### 5. Kiali 网络拓扑/流量拓扑

>以下部署方案还未完善，待修改

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
   2. 本地测试环境使用 NodePort 暴露出 Web UI 端口。

```shell
kubectl apply -f my-kiali-cr.yaml -n istio-system
```

## 参考

- [servicemesher/istio-handbook](https://github.com/servicemesher/istio-handbook)
- [Why API Management and Service Mesh are Complementary Patterns for Different Use Cases](https://www.cncf.io/blog/2020/03/06/the-difference-between-api-gateways-and-service-mesh/)
- [Mecha：将Mesh进行到底(Dapr)](https://www.servicemesher.com/blog/mecha/)

