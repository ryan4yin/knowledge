# 服务网格

目前这个领域，最流行的服务代理是 envoy，最流行或者最有前景的服务网格是：

1. istio: 目前全球最流行的服务网格，功能强大，但是相对的也更复杂。
2. linkerd2: 最初的服务网格的 rust 重构版，比 istio 简单，流控功能没那么强，但是性能更高。
   - 但是它的数据平面可拓展性比较差，没有良好的插件机制，没有 envoy 灵活。
3. dapr: 它给自己的定位是 Multi-Runtime - 一个比服务网格更通用、能力更强的运行时，一个运行时就能提供原本需要多个 Sidecar 实现的能力（如 网络代理，缓存代理，绑定代理）

其他还有一些名气小一点的服务网格可供参考，但是目前都不推荐选用：

1. consul: 一个服务注册中心，好像也能用 envoy 搭建服务网格，不过功能不强。
2. [traefik mesh](https://github.com/traefik/mesh): 一个轻量级的，Node 模式部署的服务网格，好像目前不支持 TLS 加密
3. [kuma](https://github.com/kumahq/kuma): 由 Kong 基于 Envoy 开发的一个服务网格，
4. [osm](https://github.com/openservicemesh/osm): 微软开源的一个基于 Envoy 的服务网格，好像主要面向 Azure 用户，而且项目还在一个非常早期的阶段。


在选用服务网格产品时，要以自己的痛点为核心，再结合性能、易用性、复杂度来综合考量。
不是说功能最强大的 Istio 就是银弹，功能相对弱一些的 Linkerd2 或许就会是更好的选择，或者说直接自研。

## 服务网格的正确形态？

目前主流的服务网格，核心元素有三个：

- 定位: Service Mesh 的定位始终是提供**服务间通讯**的基础设施层，范围包括 HTTP 和 RPC——支持 HTTP1.1/REST，支持 HTTP2/gRPC，支持 TCP 协议。也有一些小的尝试如对 Redis 、 Kafka 的支持。
- 原理: Service Mesh 的工作原理是**原协议转发**，原则上不改变协议内容（通常只是 header 有些小改动）。为了达到零侵入的目标，还引入了 iptables 等流量劫持技术。
- 部署: Service Mesh 支持 Kubernetes 和虚拟机，但都是采用 **Sidecar 模式**部署，没有采用其他方式如 **Node 模式部署**。
    - Sidecar 模式的性能损耗还是太大了，有些难以接受，所以现在也有一些 **Node 模式**部署的尝试，traefik mesh 就是 Node 模式，dapr 也支持 node 模式。
    - linkerd2 走的路则是做轻量的 sidecar，并且使用 rust 这类高效语言来实现。

不过我们现在已经看到了 dapr 这样更通用的 multi-runtime 产品来搅局。


## 一些问题的解答

### 为何流量分配的配置通常只支持百分比/权重？不支持精确性的灰度？

因为百分比/权重灰度就完全够用了。

曾有人说「预热功能可能会需要精确性的灰度，避免因为流量变动而预热时的请求数也发生变动，为何 Istio 等一众工具都不支持呢？」

确实，精确性的灰度，能确保它足够精确，绝对不会因为流量波动而在预热阶段过载。
但是实际上我们可以通过设置一个非常小的权重来降低预热阶段的风险。

我想你的服务不应该会在 1/100000 的比值下仍然被打垮，否则你应该考虑后端的设计问题了。

或者如果你真的有如此高的 RPS，那你的团队应该完全有能力自己写流量分配组件了。

## 我的相关博客

- [使用 Istio 进行 JWT 身份验证（充当 API 网关）](https://ryan4yin.space/posts/use-istio-for-jwt-auth/)
- [API Gateway vs Service Mesh](https://www.cnblogs.com/kirito-c/p/12394038.html)

## 其他资料

- [Slime：让Istio服务网格变得更加高效与智能](https://cloudnative.to/blog/netease-slime/)
- [基于 Apache APISIX 的下一代微服务架构](https://www.upyun.com/tech/article/512/%E5%9F%BA%E4%BA%8E%20Apache%20APISIX%20%E7%9A%84%E4%B8%8B%E4%B8%80%E4%BB%A3%E5%BE%AE%E6%9C%8D%E5%8A%A1%E6%9E%B6%E6%9E%84.html)
- [Service Mesh Comparison](https://servicemesh.es/)
