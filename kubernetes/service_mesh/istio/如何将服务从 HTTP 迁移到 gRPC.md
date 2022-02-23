# 如何将服务从 HTTP 迁移到 gRPC

## 一、Istio 对 HTTP/gRPC 双协议的支持调研

### 1. 监控能力

Istio Sidecar 暴露出的 `istio_requests_total` 同时提供 HTTP/gRPC 监控指标。

监控这里需要注意的，应该是 gRPC 使用了自定义的状态码，而不是 HTTP 的 200/4xx/5xx. 需要重新考虑如何计算可用率，哪些状态码跟基础设施有关（在 HTTP 中这通常是 502/503/504）、哪些状态码跟业务服务有关。

监控配置详见 [Istio 监控指标](./Istio%20监控指标.md)

### 2. 负载均衡能力

因为 gRPC 通常是指 gRPC over HTTP/2，而此协议的请求/响应的负载均衡方法跟 HTTP/2 是完全一致的（**未确认哈，猜的**）。
因此 gRPC 可以完全复用 HTTP/2 的负载均衡实现，两者表现应该是一致的。


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

上面的 VirtualService 配置省略了端口配置，但是 Istio 能够从服务的 Service 中的 `port` 及 `targetPort` 推断出对应的端口，因此能正确处理多端口的请求转发、切量及其他逻辑。
该 VirtualService 的等价配置如下：

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

### 4. 其他故障注入等能力

也跟流量切分一样，可直接通过端口 `match` 来分别对 HTTP/gRPC 端口进行操作。
或者不使用 `match`，直接同步操作 HTTP/gRPC.



## 二、HTTP 到 gRPC 的迁移方案

1. 首先更新下游服务，使下游服务同时支持 HTTP-8080 以及 gRPC-9090 两种协议，两个端口
2. 更新下游服务的 Service 及 Deployment 配置，添加新的 gRPC - 9090 端口
3. 接下来对上游服务进行灰度，旧版本使用 HTTP-8080 请求下游，新版本使用 gRPC-9090 请求下游
4. 缓慢将上游服务的流量切到新版本上，观察上游服务稳定性及 gRPC 监控状况，初期这个时间可以持续很多天
5. 确认无误后将上游服务完全切换到新版本，删除旧版本服务。这样就完成了 HTTP 到 gRPC 协议的迁移


## 三、HTTP 到 gRPC 的测试代码

如下两套测试用的微服务，可用于测试前面提到的各项 Istio 核心功能：负载均衡、流量切分、监控指标等。

- https://github.com/drhelius/grpc-demo: 这套简单的微服务，所有服务都通过 grpc-gateway 同时支持了 HTTP/gRPC 两种协议，稍微改改代码就可用于进行 HTTP 到 gRPC 的协议迁移测试。
- https://github.com/GoogleCloudPlatform/microservices-demo: 这是 Google 提供的一套功能验证与演示服务，内部全部使用 gRPC 协议，复杂程度应该算是刚好够用。


