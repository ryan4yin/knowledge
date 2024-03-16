# 如何将服务从 HTTP 迁移到 gRPC

## 一、Istio 对 HTTP/gRPC 双协议的支持调研

### 1. 监控能力

Istio Sidecar 暴露出的 `istio_requests_total` 同时提供 HTTP/gRPC 监控指标。

监控这里需要注意的，应该是 gRPC 使用了自定义的状态码，而不是 HTTP 的 200/4xx/5xx. 需要重新考虑如何计
算可用率，哪些状态码跟基础设施有关（在 HTTP 中这通常是 502/503/504）、哪些状态码跟业务服务有关。

另外还需要注意指标是 source 侧的还是 destination 侧的，在 destination 侧不健康的情况下，destination
的指标会直接降到 0，但是按可用率计算仍然是 100%. 如果监控没有 source 侧的指标告警或者 QPS 剧烈波动的
告警，可能会因为外层服务触发了 fallback 机制返回了旧数据，导致告警系统完全检测不到问题！

监控配置详见 [Istio 监控指标](./Istio%20监控指标.md)

### 2. 负载均衡能力

因为 gRPC 通常是指 gRPC over HTTP/2，而此协议的请求/响应的负载均衡方法跟 HTTP/2 是完全一致的（**未确
认哈，猜的**）。因此 gRPC 可以完全复用 HTTP/2 的负载均衡实现，两者表现应该是一致的，实际测试也发现两
种协议的切量及负载均衡都很精确。

但是有一个区别：HTTP 服务通常都会维护自己的 HTTP 连接池，从经验上看添加 Istio Sidecar 对 HTTP 负载均
衡能力的影响不大。而 gRPC 协议使用了 HTTP/2 的多路复用等特性，通常不会维护连接池。在 EKS 中的最佳实
践是借助 Istio Sidecar 进行 gRPC 负载均衡，这种情况下去掉 Sidecar 会直接导致 gRPC 负载均衡能力失效！

### 3. 流量切分能力

可以使用如下配置，直接同步处理 HTTP/gRPC 两个端口及协议的流量切分：

```yaml
apiVersion: v1
kind: Service
metadata:
  labels:
    app: product
  name: product
  namespace: default
spec:
  ports:
    - name: grpc
      port: 9090
      protocol: TCP
      targetPort: 9090
    - name: http
      port: 8080
      protocol: TCP
      targetPort: 8080
  selector:
    app: product
  sessionAffinity: None
  type: ClusterIP
---
apiVersion: networking.istio.io/v1alpha3
kind: DestinationRule
metadata:
  name: product
spec:
  host: product
  # 定义了两个 subset
  subsets:
    - labels:
        version: v1
      name: v1
    - labels:
        version: v2
      name: v2
---
apiVersion: networking.istio.io/v1alpha3
kind: VirtualService
metadata:
  name: product
spec:
  hosts:
    - product
  gateways:
    - mesh
  http:
    - route:
        - destination:
            host: product
            subset: v1
          weight: 80
        - destination:
            host: product
            subset: v2
          weight: 20
---
# 省略了 product 服务的 Deployment 配置
```

上面的 VirtualService 配置省略了端口配置，但是 Istio 能够从服务的 Service 中的 `port` 及
`targetPort` 推断出对应的端口，因此能正确处理多端口的请求转发、切量及其他逻辑，这些逻辑会（几乎）同
时应用在 HTTP/gRPC 两个协议上。该 VirtualService 的等价配置如下：

```yaml
apiVersion: networking.istio.io/v1alpha3
kind: VirtualService
metadata:
  name: product
spec:
  hosts:
    - product
  gateways:
    - mesh
  http:
    # grpc 协议的切量逻辑
    - match:
        - port: 9090
      route:
        - destination:
            host: product
            subset: v1
            port:
              number: 9090
          weight: 80
        - destination:
            host: product
            subset: v2
            port:
              number: 9090
          weight: 20
    # http 协议的切量逻辑
    - match:
        - port: 8080
      route:
        - destination:
            host: product
            subset: v1
            port:
              number: 8080
          weight: 80
        - destination:
            host: product
            subset: v2
            port:
              number: 8080
          weight: 20
```

### 4. 网关层转发配置

如果一个服务既有对外提供 HTTP 服务，也有对集群内提供 gRPC 服务，迁移的时候需要做些额外的修改。

比如服务 product 原来的网关层配置为：

```yaml
apiVersion: networking.istio.io/v1alpha3
kind: Gateway
metadata:
  name: test-gateway
spec:
  selector:
    istio: test-ingress-gateway
  servers:
    - port:
        number: 8080
        name: http
        protocol: HTTP
      hosts:
        - product.test.com
---
apiVersion: networking.istio.io/v1alpha3
kind: VirtualService
metadata:
  name: product.test.com
spec:
  hosts:
    - product.test.com
  gateways:
    - test-gateway
  http:
    - match:
        - uri:
            prefix: /
      route:
        - destination:
            host: product
```

上述配置未明确指定要将外部请求转发到 product 的哪个端口，在 product 服务只有一个 HTTP-8080 端口
时，Istio 会默认使用该端口，因此是没问题的。

但是在为 product 服务添加了 gRPC-9090 端口后，Istio 就无法判断该使用哪个端口了，这会导致从网关进来的
所有请求都返回 503！

解决方法是明确指定要转发的端口地址：

```yaml
---
apiVersion: networking.istio.io/v1alpha3
kind: VirtualService
metadata:
  name: product.test.com
spec:
  hosts:
    - product.test.com
  gateways:
    - test-gateway
  http:
    - match:
        - uri:
            prefix: /
      route:
        - destination:
            host: product
            port:
              number: 8080
```

### 5. 其他故障注入等能力

也跟流量切分一样，可直接通过端口 `match` 来分别对 HTTP/gRPC 端口进行操作。或者不使用 `match`，直接同
步操作 HTTP/gRPC.

## 二、HTTP 到 gRPC 的迁移方案

通过上面的各种能力对比，可以看到 Istio 对 gRPC 的支持跟 HTTP 是高度兼容的，大部分配置都不需要做任何
修改，直接添加一个 gRPC 端口，这些配置就能同时应用在 gRPC/HTTP 两个协议上。

1. 首先更新下游服务，使下游服务同时支持 HTTP-8080 以及 gRPC-9090 两种协议，两个端口
2. 服务的健康检查，可以仍然沿用原 HTTP 的 health check
3. 更新下游服务的 Service 及 Deployment 配置，添加新的 gRPC - 9090 端口
4. 接下来对上游服务进行灰度，旧版本使用 HTTP-8080 请求下游，新版本使用 gRPC-9090 请求下游。或者通过
   请求参数来控制使用的协议。
5. 缓慢将上游服务的流量切到新版本上，观察上游服务稳定性及 gRPC 监控状况，初期这个时间可以持续很多天
6. 确认无误后将上游服务完全切换到新版本，删除旧版本服务。这样就完成了 HTTP 到 gRPC 协议的迁移
7. 先以 0 状态码为成功，其他为失败，

## 三、HTTP 到 gRPC 的测试代码

如下两套测试用的微服务，可用于测试前面提到的各项 Istio 核心功能：负载均衡、流量切分、监控指标等。

- https://github.com/drhelius/grpc-demo: 这套简单的微服务，所有服务都通过 grpc-gateway 同时支持了
  HTTP/gRPC 两种协议，稍微改改代码就可用于进行 HTTP 到 gRPC 的协议迁移测试。
- https://github.com/GoogleCloudPlatform/microservices-demo: 这是 Google 提供的一套功能验证与演示服
  务，内部全部使用 gRPC 协议，复杂程度应该算是刚好够用。

## 四、实际效果

我跟推荐系统的大佬一起将核心服务 ternsorflow/serving 从 HTTP 切换到 gRPC 后，效果立竿见影：服务流量
下降 70%，延迟下降 30% ~ 50% 此外我们在 gRPC 上添加了 gzip 后，服务流量还能再降 70%+，两项优化结合，
流量能降到原来的 10% 以下。

上述两项优化对服务的性能影响很小，可以说是付出了很小的代价，大大提升了服务性能，同时降低了大量的 AWS
跨区流量成本。
