# Service Mesh

## 一、Istio

### 1. 部署

使用 istioctl 部署 istio:
```shell
# 示例1：只部署 istiod 和 ingressgateway
istioctl manifest apply --set profile=default --set values.prometheus.enabled=false 

# 示例2：只部署 istiod 和 ingressgateway，并且使用内网的 docker hub 缓存
istioctl manifest apply \
  --set profile=default \
  --set values.prometheus.enabled=false \
  --set hub=registry.xxx.local > istio-manifest.yaml
```

这种方式适合自定义参数比较少，而且只是临时测试的情形。

#### 1.1 自定义部署（推荐方式）

可以通过 `istioctl manifest apply -f custom-operator.yml` 进行自定义部署，[custom-operator.yml](./custom-operator.yml) 就在当前文件夹内。

通过 [custom-operator.yml](./custom-operator.yml)，可以自定义 k8s 资源定义（节点选择器、HPA、资源预留与限制等等）、istio 组件本身的设置等等。而且可以直接保存在 git 仓库里，方便迭代、自动化部署。

可以通过 `istioctl profile dump` 查看完整的 IstioOperator 配置，作为编写 [custom-operator.yml](./custom-operator.yml) 的参考。

更多自定义部署的信息，参见官方文档 [istioctl: configure-component-settings](https://istio.io/docs/setup/install/istioctl/#configure-component-settings)


#### 1.2 升级与删除

滚动升级 istio:

```shell
# TODO 我使用此命令从 1.5.0 升级到 1.5.2 时一直卡住，没升级成功。
# 最后只好先删除掉 1.5.0 然后重新安装 1.5.2
istioctl upgrade -f custom-operator.yml
```

删除 istio：

```shell
# 格式如下：
istioctl manifest generate <your original installation options> | kubectl delete -f -
# 示例一：使用 --set 指定自定义参数
istioctl manifest generate --set profile=default --set values.prometheus.enabled=false | kubectl delete -f -
# 示例二：使用 istiooperator 配置指定自定义参数
istioctl manifest generate -f custom-operator.yml | kubectl delete -f -
```

### 2. 监控：istioctl + prometheus-operator

部署 Istio 时可以不部署它自带的 Prometheus+Grafana，而是使用以 [kube-prometheus](https://github.com/coreos/kube-prometheus) 部署的监控系统进行监控。
但是需要通过 [custom-operator.yml](./custom-operator.yml) 设定额外的配置。



#### Grafana 面板

Istio 官方提供的 Grafana 面板：https://grafana.com/orgs/istio

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


### 5. Kiali 网络拓扑/流量拓扑

待续
