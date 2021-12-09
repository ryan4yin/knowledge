# 服务网格

目前这个领域，最流行的服务代理是 envoy，最流行或者最有前景的服务网格是：

1. [istio](https://github.com/istio/istio): 目前全球最流行的服务网格，功能强大，但是相对的也更复杂。
   1. 文档非常详细
2. [linkerd2](https://github.com/linkerd/linkerd2): 最初的服务网格的 rust 重构版，比 istio 简单，流控功能没那么强，但是性能更高。
   - 但是它的数据平面可拓展性比较差，没有良好的插件机制，没有 envoy 灵活。（如果你没有强烈的扩展需求，这一点倒是可以忽略）
   - 文档感觉比较简略，不如 istio.

其他还有一些名气小一点的服务网格可供参考，但是目前都不推荐选用：

1. [kuma](https://github.com/kumahq/kuma): 由 Kong 基于 Envoy 开发的一个服务网格
2. [osm](https://github.com/openservicemesh/osm): 微软开源的一个基于 Envoy 的服务网格，完全基于服务网关接口 SMI 规范开发，使用上比 istio 简单很多，但是仍然功能仍然不够完善，not production-ready.
3. apisix 等基于 nginx/openresty 的技术，也在向这个方向发展
   - 它们的优势大概有：nginx 的「高性能」与「可扩展性」，以及企业能沿用上企业曾经在 nginx 领域多年的历史积累（坑都踩过了）。

以及一些昙花一现，不再活跃的服务网格项目，如 traefik mesh、rancher rio

在选用服务网格产品时，要以自己的痛点为核心，再结合**性能**、**可拓展性**、**复杂度**几个方案来综合考量。

如果选择 envoy 阵营，目前不二选择就是 istio.
如果需要更轻量，目前最佳的选择应该也只有 linkerd2.
如果希望呆在原来的舒适区，继续使用 openresty，那估计得选择自研.


## 性能对比

### 1. [Istio 1.8.3 - 1.11.4](https://istio.io/v1.11/docs/ops/deployment/performance-and-scalability/)

The Istio load tests mesh consists of **1000 services and 2000 sidecars with 70,000 mesh-wide requests per second**. After running the tests using Istio 1.11.4, we get the following results:

- The Envoy proxy uses **0.35 vCPU** and **40 MB** memory per **1000 requests per second** going through the proxy.
- Istiod uses **1 vCPU** and **1.5 GB** of memory.
- The Envoy proxy adds **2.65 ms** to the **90th percentile latency**.

### 2. [Linkerd2](https://linkerd.io/2021/05/27/linkerd-vs-istio-benchmarks/)

Linkerd2 的测试方式看起来跟 istio 有些不同，不过得出的结论显然是: linkerd2-proxy 性能继续吊打 envoy.

## 功能对比（Istio vs Linkerd2）

核心能力：

- [x] 负载均衡 - 目前打平（常用算法都支持、貌似都不支持 slow_start 模式）
- [x] 观测指标 - 暂时平手（不清楚 Istio 的 flags 在 Linkerd2 这边有没有对应参数）
- [x] 链路追踪 - 算平手，都支持 jaeger，而且都只能做到 RPC 调用级别的链路追踪
- [x] 流量切分 - weight_total 至少 1000 - Linkerd2 > Istio, 因为 Istio 有限制必须为 100
   - 都支持 pathRegex、method、headers
   - istio 支持更多的参数：params/schema/uriPrefix/ignoreUriCase/withoutHeaders/rewrite 等，而且支持忽略 URI 大小写、流量镜像 mirror
   - Linkerd2 官方建议搞个 nginx pod 做流量镜像（毕竟只在测试时用嘛，搞个 nginx 确实能满足需求），其他参数估计也是觉得没必要支持，完全可以在 Gateway 上做 hhh
- [x] 性能 - Linderd2 << Istio
- [x] 文档 - Istio == Linkerd2，Istio 的文档感觉条理更清晰，Linkerd2 的文档稍显简略了。
- [x] 流控能力（限流限并发） - Istio > Linkerd2，Linkerd 不提供此能力
  - [Add support for rate limiting - Linkerd2](https://github.com/linkerd/linkerd2/issues/4649)
- [ ] 流量拓扑图，配合流量监测能力 - Istio 有 Kiali 比较强大，Linkerd2 的 Dashboard 尚且不清楚是否同样牛逼。
- [x] 易用性 - Linkerd2 >> Istio，Istio 和 Envoy 两个东西的配置都比 Linkerd2 复杂...

以及另外一些看起来需求不强烈的功能：

- [x] 可拓展性 - Istio Envoy 的 wasm 略胜一筹
- [x] 故障注入 - Istio >> Linkerd2
  - 搞故障演练时估计用的到，但是我们还从没做过故障演练...
  - Istio 这方面支持比较完善，Linkerd2 建议直接跑个 nginx 当故障注入器，然后把流量切过去 hhh
- [x] 服务间的访问控制 - 貌似都做得还行
- [x] jwt认证授权 - Istio >> Linkerd2
  - Linkerd2 貌似没这功能，估计是建议在网关上搞
- [x] 修改请求/响应 - Istio > Linkerd2
  - Linkerd2 貌似没这能力，估计是建议在网关上搞
- [x] EgressGateway - Istio >> Linkerd2
  - Linkerd2 没这功能

目前来看，Istio 是全家桶，啥功能它都有，目前的缺陷就是：

- 权重限制为 100 有点不够用
- slow_start 还没支持，对缓存有依赖的服务扩容不太平滑
- 性能问题

而 Linkerd 的优势就是高性能、易用，但是很多功能都被砍掉了，有必要配合其他的 Gateway 组件使用，它的缺陷有：

- 用的人相对较少，不确定坑有多少
- slow_start 还没支持，对缓存有依赖的服务扩容不太平滑
- 不支持限流限并发，这个感觉在网格内还是有需要的，如果有微服务发疯，能起到隔离的作用...
- 不处理南北向的网关流量，认证授权、rewrite，这些都建议在 Gateway 上搞...

## 服务网格的正确形态？

目前主流的服务网格，核心元素有三个：

- 定位: Service Mesh 的定位始终是提供**服务间通讯+监测**的基础设施层，范围包括 HTTP 和 RPC ——支持 HTTP1.1/REST，支持 HTTP2/gRPC，支持 TCP 协议。也有一些小的尝试如对 Redis 、 Kafka 的支持。
- 原理: Service Mesh 的工作原理是**原协议转发**，原则上不改变协议内容（通常只是 header 有些小改动）。为了达到零侵入的目标，还引入了 iptables 等流量劫持技术。
- 部署: Service Mesh 支持 Kubernetes 和虚拟机，但都是采用 **Sidecar 模式**部署，没有采用其他方式如 **Node 模式部署**。
    - Sidecar 模式的性能损耗还是太大了，有些难以接受，所以现在也有一些 **Node 模式**部署的尝试，traefik mesh 就是 Node 模式，dapr 也支持 node 模式。
    - linkerd2 走的路则是做**轻量的 sidecar**，并且使用 rust 这类高效语言来实现。

不过我们现在也看到了 dapr 这样更通用的 multi-runtime 产品，以及 Proxyless Service Mesh.

## 我的相关博客

- [使用 Istio 进行 JWT 身份验证（充当 API 网关）](https://ryan4yin.space/posts/use-istio-for-jwt-auth/)
- [API Gateway vs Service Mesh](https://www.cnblogs.com/kirito-c/p/12394038.html)

## 其他资料

- [Proxyless Service Mesh在百度的实践与思考](https://mp.weixin.qq.com/s/8T7XI6jQfZunwVYDaDHvLw)
- [Slime：让Istio服务网格变得更加高效与智能](https://cloudnative.to/blog/netease-slime/)
- [基于 Apache APISIX 的下一代微服务架构](https://www.upyun.com/tech/article/512/%E5%9F%BA%E4%BA%8E%20Apache%20APISIX%20%E7%9A%84%E4%B8%8B%E4%B8%80%E4%BB%A3%E5%BE%AE%E6%9C%8D%E5%8A%A1%E6%9E%B6%E6%9E%84.html)
- [Service Mesh Comparison](https://servicemesh.es/)
