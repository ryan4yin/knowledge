# Kubernetes 中的负载均衡

Kubernetes 集群中有多种流量转发的方法：

1. Service - ClusterIP: 四层负载均衡。群内部使用广泛的一种流量转发方式。
   - 四层负载均衡，主要适合短连接。它均衡不了 tcp 长连接中的七层请求（比如 HTTP/1.1 gRPC 等）。
2. Service - Internal LoadBalancer: 四层/七层的负载均衡。云上环境中的内部负载均衡器，在 LoadBalancer
   类型的 Service 上使用注解可配置。
   1. 这种用法貌似很少见？LoadBalancer 主要还是被用于将服务暴露给外部访问。
3. Istio 服务网格：最灵活，性能损耗也最大的一种负载均衡策略。但是它能实现最丰富的负载均衡策略，甚至
   按比例切分流量。
4. Ingress: 可以在网关层做四/七层的负载均衡。和 Istio 的区别在于：它不支持均衡南北向流量。
5. 底层的网络插件，有可能提供更高级的负载均衡、流量监控等功能。

## 请求亲和性

Kubernetes Service 可以通过设置 `service.spec.sessionAffinity` 为 `ClientIP`，以客户端 IP 地址设置会
话关联。还可以通过设置 `service.spec.sessionAffinityConfig.clientIP.timeoutSeconds` 来修改会话的最大
有效时长.（默认值为 10800 秒，即 3 小时）

如果使用 Istio 服务网格，就可以配置非常智能的请求均衡策略，比如可以按 Header/Cookie/QueryParameter
等 HTTP 属性设置会话关联。详见
[Istio DestinationRule - ConsistentHashLB](https://istio.io/latest/docs/reference/config/networking/destination-rule/#LoadBalancerSettings-ConsistentHashLB)

用途：

1. 微服务-微服务：
   1. 基于 IP 的会话亲和性，主要功能就是用于保持微服务-微服务的会话。
2. 用户-微服务：
   1. 可以在 Istio 服务网格上配置基于 Cookie/Header 的会话关联，提升微服务缓存的利用率。
   2. 利用 Header 进行金丝雀发布（策略路由），只有带有特定 Header 的请求会被转发给测试 Pod。

## 四层负载均衡和七层负载均衡

主要区别在于：

1. 依据第几层的信息进行转发
   1. 第四层：IP 和 端口号
   2. TLS（也被分到第七层）: TLS Client Hello 中的 Host
   3. 第七层：HTTP 中的 Host/Path 等信息
2. 四层负载均衡不查看七层信息，因此它无法负载均衡一个 TCP 长连接中的 HTTP 请求，也无法负载均衡 gRPC
   请求。
   1. 因此在 kubernetes 中直接使用 Service+gRPC，将造成一 Pod 有难，多 Pod 围观的情况。
   2. 七层负载均衡器只负责做 NAT，客户端和服务端是在 TCP 层直连的。
3. 七层负载均衡会查看七层信息，如果客户端通过一个 TCP 连接发送过来多个 HTTP/2 请求，它能够将请求均衡
   到多个后端去。
   1. 七层负载均衡器是分别与客户端、服务端建立 TCP 连接，然后解析客户端发来的七层请求，将请求内容均
      衡发送给后端。
   1. 客户端不是在 TCP 层直连服务端，它只是直连了七层负载均衡器。
4. 四层负载均衡工作在更底层，性能更好，但是能力也更弱。而且客户端直连服务端，服务端抗 DDos 能力弱。
   1. 适合做内部的负载均衡，即客户端可信的情况。
5. 七层负载均衡要处理更多的数据，性能更差。但是：
   1. 它可以在 HTTP 请求粒度上做负载均衡，更智能。
   2. 甚至可以魔改 HTTP 请求内容，或者缓存图片等静态资源（通过 content-type 判断是否静态资源），使用
      gzip 等压缩技术，tls 加密等等。
   3. 抗 DDos 能力强，DDos 作为一种TCP(四层)攻击，只会影响负载均衡器自身，影响不到后端服务器。
   4.

## Kubernetes 集群中的客户端负载均衡

除了使用 Istio 服务网格做集群内的七层负载均衡，还有另一种方法：客户端负载均衡。

也就是使用 Headless Service，让客户端自己去轮询有多少的服务端 Pod，自行与所有 Pod 建立连接，然后自己
在这些连接上做负载均衡。

这种方案性能比 Istio 要高，但是实现复杂。
