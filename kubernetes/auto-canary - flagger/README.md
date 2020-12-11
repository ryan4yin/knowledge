# [Flagger](https://github.com/weaveworks/flagger)


Flagger 是一个 Kubernetes 上的渐进式交付 Operator，可以根据监控指标进行自动化的金丝雀发布、A/B 测试、蓝/绿发布等。

Flagger 可以和 fluxcd 集成，实现整个部署流程的自动化。


## 一、部署 Flagger

```shell
helm repo add flagger https://flagger.app
# 查看 flagger 版本号
helm search repo flagger/flagger -l | head
# 下载并解压 chart
helm pull flagger/flagger --untar --version 1.2.0

# 查看生成出的 kubernetes yaml 内容
helm template ./flagger --namespace flagger -f custom-values.yaml > flagger-all.yaml

# 使用自定义的 cutome-values.yaml 进行部署（helm3）
kubectl create ns flagger
helm upgrade --install \
  --namespace flagger \
  -f custom-values.yaml \
  flagger \
  ./flagger
```


## 二、Prometheus 接入

### 1. metricsServer

metricsServer 是 flagger 默认的 Prometheus 地址，但是目前好像只有内置指标有用到这个配置项。

然而目前 flagger 只内置了两个指标(request-success-rate/request-duration)。
自定义指标 MetricTemplate 要求必须指定 Prometheus 等指标服务器的地址。

所以如果你没有用到内置指标，这个属性好像就没什么作用。

### 2. 使用 Prometheus 进行灰度分析

除了查询监控指标用于判断外，flagger pod 自身也导出了当前灰度状态与权重相关的 Prometheus 指标，可用于做进一步的灰度分析。

flagger 默认的 `podAnnotations` 配置中，包含了 `prometheus` 的抓取注解，这样 prometheus 就会自动抓取它的灰度数据。

可以按照官方提供的方法，部署 grafana 面板查看灰度信息：

- flagger 自动灰度工具: https://docs.flagger.app/usage/monitoring
  - 官方文档要求部署独立的 grafana，但是你也可以将官方的 dashboard 配置文件导入已存在的 grafana.
  - 官方提供的 dashboard 配置文件：https://github.com/weaveworks/flagger/tree/master/charts/grafana/dashboards


## 二、结合 Istio 进行灰度发布(Canary)

Flagger 通过 Canary 资源来声明灰度发布策略，示例如下：

```yaml
apiVersion: flagger.app/v1beta1
kind: Canary
metadata:
  name: podinfo
  namespace: test
spec:
  # deployment reference
  targetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: podinfo
  # the maximum time in seconds for the canary deployment
  # to make progress before it is rollback (default 600s)
  progressDeadlineSeconds: 60
  # HPA reference (optional)
  autoscalerRef:
    apiVersion: autoscaling/v2beta2
    kind: HorizontalPodAutoscaler
    name: podinfo
  service:
    # 服务端口号，注意，只支持一个端口！
    port: 9898
    # container port number or name (optional)
    targetPort: 9898
    # 端口使用的协议，只支持两种: http/grpc
    portName: http
    # 自动发现服务端口，这会将 Deployment 中的所有端口添加到 Service 中
    # 但是既然只添加到 Service 中，不往 VirtualService 中加，也就意味着这些端口不会参与灰度
    portDiscovery: true
    # Istio gateways (optional)
    gateways:
    # 在网格内进行灰度（对内）
    - mesh
    # 在网关层进行灰度（对外）
    - public-gateway.istio-system.svc.cluster.local
    # Istio virtual service host names (optional)
    hosts:
    # 对内的 host
    - podinfo.default.svc.cluster.local
    # 对外的 host
    - app.example.com
    # Istio traffic policy (optional)
    trafficPolicy:
      tls:
        # use ISTIO_MUTUAL when mTLS is enabled
        mode: DISABLE
    # Istio 重试策略（可选），请慎用！一定要确保微服务只有幂等的 HTTP/GRPC 接口，才能使用重试！
    # 否则有可能导致业务逻辑混乱！！！
    retries:
      attempts: 3
      perTryTimeout: 1s
      retryOn: "gateway-error,connect-failure,refused-stream"
  # 灰度状态分析，flagger 通过它自动判断是要继续灰度，还是出了问题应该回退。
  analysis:
    # schedule interval (default 60s)
    interval: 1m
    # max number of failed metric checks before rollback
    threshold: 5
    # max traffic percentage routed to canary
    # percentage (0-100)
    maxWeight: 50
    # canary increment step
    # percentage (0-100)
    stepWeight: 10
    metrics:
    - name: request-success-rate
      # minimum req success rate (non 5xx responses)
      # percentage (0-100)
      thresholdRange:
        min: 99
      interval: 1m
    - name: request-duration
      # maximum req duration P99
      # milliseconds
      thresholdRange:
        max: 500
      interval: 30s
    # 回调，可用于实现 钉钉告警等
    webhooks:
      - name: acceptance-test
        type: pre-rollout
        url: http://flagger-loadtester.test/
        timeout: 30s
        metadata:
          type: bash
          cmd: "curl -sd 'test' http://podinfo-canary:9898/token | grep token"
      - name: load-test
        url: http://flagger-loadtester.test/
        timeout: 5s
        metadata:
          cmd: "hey -z 1m -q 10 -c 2 http://podinfo-canary.test:9898/"
```

可以看到上述配置中涉及到了如下几个资源引用：

1. Deployment
2. HPA
3. istio gateway: 在 spec.service.gateways 中引用了 istio gateway

也就是说我们现在只需要手动管理这三个资源了，而下列的资源将由 flagger 自动生成并管理：

1. Service
2. Istio DestinationRule
3. Istio VirtualService


灰度流程中，Flagger 将被引用的 Deployment 和 HPA 看做「金丝雀版本(canary)」，而「主版本(primary)」则由 Flagger 自动生成。

Flagger 会监控 Deployment，一有更新就进入灰度流程，将流量逐渐从「主版本」切换到「金丝雀版本」。
切换过程中两个 Deployment 的扩缩容由 HPA 管控，因此只要 HPA 和灰度速率设置地恰当，
在切换流量的过程中，「主版本」将渐渐缩容，而「金丝雀版本」将渐渐扩容。

待续


### 注意事项

1. 网关只支持南北向流量（用户->网关）的灰度，只有服务网格才支持东西向流量（微服务->微服务）的灰度。
    - 使用 Istio 进行网格内的流量灰度，需要在 Canary 的 `spec.service.gateways` 中添加 `mesh` 表示网格内部流量，同时 `spec.service.hosts` 中也得添加上内部 Service 的名称。
1. 通过 Canary 的 `spec.service.trafficPolicy.tls.mode` 可以强制微服务使用 mtls 双向认证。
1. Flagger 可以自定义 MetricTemplate，支持设定 prometheus 地址，通过 PromQL 计算指标。
    - 比如通过 Istio 在网格内灰度一个 gRPC 服务，就需要通过 PromQL 从 Prometheus 中查询 Istio 提供的 gRPC 状态码等指标。
1. Flagger 对多端口的支持有些问题，`spec.service.portDiscovery: true` 只能智能将识别到的 containerPort 添加到 `Service` 中。但是 `VirtualService` 的灰度端口只能是 `spec.service.port` 指定的端口号！别的端口不会被添加到 VirtualService 中，也就不会被灰度！
2. `spec.service.portName` 默认是 `http`，如果灰度 `grpc` 端口，必须要将这个参数设为 `grpc`！！！
  - flagger 只支持灰度 http/grpc 协议！
1. Flagger 的灰度是滚动更新，而且会滚动更新两次！v1-primary ->(灰度) v2-canary ->(改名) v2-primary


## 问题：Flagger 的灰度过程中 Pods 数量会如何变化？

从官方的示意图看，Pods 数量可能会翻倍。。。这在副本数比较多的情况下，可能很消耗资源。

灰度过程中有 HPA 管着问题倒不大，但是在灰度完成后，


## 相关文档

- [Flagger Docs - How it works](https://docs.flagger.app/usage/how-it-works)
