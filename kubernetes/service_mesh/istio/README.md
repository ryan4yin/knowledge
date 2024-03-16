# Service Mesh

一句话介绍：服务网格接管集群内的所有流量，实现方式是在每个 Pod 中注入一个 Sidecar 容器（envoy）做网
络代理。

服务网格的优势：

1. 流量控制
   1. 流量切分与流量镜像。
   2. 东西向与南北向流量的四/七层负载均衡。
   3. 请求自动重试、故障注入。
   4. Rewrite HTTP URIs and Authority(HOST) headers
2. 观察：集群内流量的可观察性，提供丰富的流量监控能力。
3. 安全：东西向与南北向流量的 mTLS 加密，JWT 鉴权。

## Istio 服务网格 - 商业版

> https://istio.io/latest/about/ecosystem/

在使用 Istio 时，尤其是使用多集群等更复杂场景的服务网格时，如果团队的技术能力不足，更好的选择是直接
使用商业版的 Istio，由专业的团队来帮助维护这个核心组件，等技术能力提升上来了，再考虑是否自己来维护。

我了解到的商业版服务网格有：

- [Google Anthos Service Mesh](https://cloud.google.com/service-mesh/docs/overview)
  - Google Cloud 提供的 Istio 服务网格功能，用于在本地或在 Google Cloud 上监控和管理可靠的服务网格。
  - 根据
    [Anthos Support Platforms](https://cloud.google.com/service-mesh/docs/supported-features#supported_platforms)，
    它支持 GKE/裸机/VMware/AWS，其中多集群模式仅支持 GCP/裸机
- [VMware Tanzu Service Mesh](https://tanzu.vmware.com/service-mesh)
  - Multi-cloud and multi-runtime connectivity for distributed applications
  - Visibility and analytics across app end-users, microservices, APIs, and data
- [Tetrate Istio Subscription](https://www.tetrate.io/tetrate-istio-subscription/)
  - Enterprise Istio support from creators of Istio
  - 已在 AWS/GCP/Azure 上测试
- [Solo.io Production Istio Support](https://lp.solo.io/istio-support)
  - We offer support for open source Istio software as part of Gloo Mesh Enterprise.
- [Red Hat OpenShift service mesh](https://www.redhat.com/en/technologies/cloud-computing/openshift/service-mesh)
  - Connect, manage, and observe your microservices-based applications with Red Hat OpenShift®
    Service Mesh, based on the Istio open source project.
- [阿里云 ASM](https://www.aliyun.com/product/cs/servicemesh)/[腾讯云 TCM](https://cloud.tencent.com/product/tcm)
  - 一个统一管理微服务应用流量、兼容 Istio 的托管式平台。
  - 仅支持阿里云/腾讯云

从对 Istio 的贡献上看，Google/RedHat/VMware/Tetrate/Solo 这四家应该都还是比较靠谱的。

## 一、Istio

> 当前针对的 Istio 版本：1.11.x，建议使用 istioctl + 自定义配置文件部署

### 1. 简单部署

使用 istioctl 部署 istio:

```shell
# 示例1：只部署 istiod 和 ingressgateway
istioctl install --set profile=default

# 示例2：只部署 istiod 和 ingressgateway，并且从内网的容器镜像仓库拉镜像
istioctl install --set profile=default --set hub=registry.svc.local
```

这种方式适合自定义参数比较少，而且只是临时测试的情形。

其中 `profile` 的选择，参见
[Installation Configuration Profiles - Istio Docs](https://istio.io/latest/docs/setup/additional-setup/config-profiles/).

> 生产环境建议使用 `minimal`，开发测试环境建议使用 `default`

#### 1.1 自定义部署（推荐方式）

> 建议使用 `minimal` 这个 profile，然后另行部署 Gateways.

可以通过 [istio-operator-values.yaml](./istio-operator-values.yaml) 配置文件进行自定义部署：

```shell
istioctl install -f istio-operator-values.yaml
```

通过 [istio-operator-values.yaml](./istio-operator-values.yaml)，可以自定义 k8s 资源定义（节点选择
器、HPA、资源预留与限制等等）、istio 组件本身的设置等等。而且可以直接保存在 git 仓库里，方便迭代、自
动化部署。

可以通过 `istioctl profile dump default` 查看完整的 IstioOperator 配置，作为编写
[istio-operator-values.yaml](./istio-operator-values.yaml) 的参考。

更多自定义部署的信息，参见官方文档
[istioctl: configure-component-settings](https://istio.io/docs/setup/install/istioctl/#configure-component-settings)

##### 1.2 手动部署 IngressGateways

参见 [Ingress](./Ingress.md) 和 [Egress](./Egress.md)

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
  labels:
    sidecar.istio.io/inject: "false"
```

> 旧的 `sidecar.istio.io/inject` 是添加在 `annotations` 中的，但是已被 `labels` 中的同名标签取代，旧
> 标签已废弃。

### 3. 监控：istioctl + prometheus-operator

Istio 官方推荐在集群外部使用
[prometheus-community/prometheus](https://github.com/prometheus-community/helm-charts/blob/main/charts/prometheus/README.md#scraping-pod-metrics-via-annotations)
等工具搭建生产级别的 Prometheus 集群.

配置步骤如下：

1. 部署
   [prometheus-community/prometheus](https://github.com/prometheus-community/helm-charts/blob/main/charts/prometheus/README.md#scraping-pod-metrics-via-annotations)
2. 将 [istio-operator-values.yaml](./istio-operator-values.yaml)，将
   `spec.meshConfig.enablePrometheusMerge` 设为 true
   1. 修改此参数后，istio 将在数据层注入 prometheus 相关注解，`prometheus-community/prometheus` 会自
      动识别这些注解并抓取指标
3. `istioctl install -f istio-operator-values.yaml`：通过修改好的配置部署 istio 或更新 istio 配置。

#### Istio 的 Grafana 面板

经过前面的部署，我们的 Prometheus 应该已经在通过注解识别到 istio proxy 及控制面的 targets，并开始抓
取指标了。

接下来需要部署 grafana，然后导入 Istio 的 Dashboard 配置，即可查看到 Istio 的状态。

grafana 的 helm chart: https://github.com/grafana/helm-charts/tree/main/charts/grafana

部署好 grafana 后，在这个页面中找到最新版本的 Istio Dashboard ID: https://grafana.com/orgs/istio 然
后进入rafana 页面，使用 ID 就可一键导入 Istio Dashboard.

### 4. HTTP 方法调用级别的链路追踪（Istio + Jaeger + OpenTelemetry）

> Istio Sidecar 只支持 HTTP/GRPC **方法调用级别的链路跟踪**，而 Opencensus 提供了自定义指标的功能，
> 使我们能跟踪任意自定义指标（比如 mysql 调用、redis 调用，甚至任意本地方法调用），但是这样会提升
> sdk 的侵入性。现在上述两个开放标准已经合二为
> 一：[OpenTelemetry](https://github.com/open-telemetry).

Istio 链路追踪说是可以减少链路追踪对应用层的侵入，应用本身只需要转发一下 trace headers 就
行，sidecar(也就是 envoy) 会自动帮你:

1. 生成 span(b3) 并添加到 http/grpc headers 中
2. 收集 http/grpc headers 中的 spans
3. 对 spans 进行采样
4. 将 spans 发送到指定的后端（使用 zipkin 协议）

但是实际调研后，发现上述流程的核心是 HTTP Headers，因此基本上只能支持 HTTP/gRPC 协议。而
mysql/redis/message_queue 等都是使用的专有协议，Sidecar 或者我们的应用本身，都没有办法往这些流量中添
加额外的链路信息。

因此使用服务网格进行链路追踪，只能满足我们的一小部分需求。对于 mysql/redis/mq 等非 http 协议的调用，
还是必须由我们的应用自身来完成 span 的生成、收集、采样、上报。

这种情况下，如果要使用 Istio 的链路追踪，那就得根据流量类型进行上报了：

1. HTTP/gRPC: 由 Istio(Envoy) 进行上报
2. MySQL/Redis 等协议：由应用自身进行采集上报。

其实就只是拆出了一部分链路追踪的功能给 Istio 做了，另一部分还得自己处理。具体实现还没仔细验证，我怀
疑会比「不使用 Istio 链路追踪」更复杂也说不定。

#### 部署 jaeger operator

生产环境不建议部署 Istio 提供的 jaeger，它是一个 fat 容器（all in one），建议自己使用
[jaeger operator](https://github.com/jaegertracing/jaeger-operator) 进行部署。

如果打算使用 Istio 的链路追踪，那么 jaeger 需要开启 zipkin 协议支持，并且修改 istio 的
`values.global.tracer.zipkin.address` 指向 jager 的 zipkin 端口。

否则就和 Istio 没啥关系了，应用自身向 jaeger-agent(udp) 或者 jaeger-collector(http/grpc) 上报追踪数
据。

jaeger-operator 的详细部署流程参见
[/telemetry/tracing - jaeger/README.md](/telemetry/tracing%20-%20jaeger/README.md)

## 参考

- [servicemesher/istio-handbook](https://github.com/servicemesher/istio-handbook)
- [Why API Management and Service Mesh are Complementary Patterns for Different Use Cases](https://www.cncf.io/blog/2020/03/06/the-difference-between-api-gateways-and-service-mesh/)
- [Mecha：将Mesh进行到底(Dapr)](https://www.servicemesher.com/blog/mecha/)
