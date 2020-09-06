# [Flagger](https://github.com/weaveworks/flagger)


Flagger 是一个 Kubernetes 上的渐进式交付 Operator，可以根据监控指标进行自动化的金丝雀发布、A/B 测试、蓝/绿发布等。

Flagger 可以和 fluxcd 集成，实现整个部署流程的自动化。


## 部署 Flagger

```shell
helm repo add flagger https://flagger.app
# 查看 flagger 版本号
helm search repo flagger/flagger -l | head
# 下载并解压 chart
helm pull flagger/flagger --untar --version 1.1.0

# 使用自定义的 cutome-values.yaml 进行部署（helm3）
kubectl create ns flagger
helm upgrade --install \
  --namespace flagger \
  -f custome-values.yaml \
  flagger \
  ./flagger
```

## 注意事项

1. 网关只支持南北向流量（用户->网关）的灰度，只有服务网格才支持东西向流量（微服务->微服务）的灰度。
    - 使用 Istio 进行网格内的流量灰度，需要在 Canary 的 `spec.service.gateways` 中添加 `mesh` 表示网格内部流量，同时 `spec.service.hosts` 中也得添加上内部 Service 的名称。
1. 通过 Canary 的 `spec.service.trafficPolicy.tls.mode` 可以强制微服务使用 mtls 双向认证。
1. Flagger 可以自定义 MetricTemplate，支持设定 prometheus 地址，通过 PromQL 计算指标。
    - 比如通过 Istio 在网格内灰度一个 gRPC 服务，就需要通过 PromQL 从 Prometheus 中查询 Istio 提供的 gRPC 状态码等指标。
1. Flagger 对多端口的支持有些问题，`spec.service.portDiscovery: true` 只能智能将识别到的 containerPort 添加到 `Service` 中。但是 `VirtualService` 的灰度端口只能是 `spec.service.port` 指定的端口号！别的端口不会灰度！
2. `spec.service.portName` 默认是 `http`，如果灰度 `grpc` 端口，必须要将这个参数设为 `grpc`！！！
  - flagger 只支持灰度 http/grpc 协议！
