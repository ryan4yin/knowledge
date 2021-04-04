# 服务网格

目前这个领域，最流行的服务代理是 envoy，最流行的服务网格是：

2. istio: 目前全球最流行的服务网格
3. linkerd2: 最初的服务网格的 rust 重构版，比 istio 简单，性能更高。
1. consul: 这个不了解。。
2. dapr: 它给自己的定位是 Multi-Runtime - 一个比服务网格更通用、能力更强的运行时，一个运行时就能提供原本需要多个 Sidecar 实现的能力（如 网络代理，缓存代理，绑定代理）
3. 其他 traefik/kong 等也都推出了功能类似 istio 的服务网格，但是用户少，暂时不做介绍。

然后最近 nginx/kong/traefik 等又推出了一票服务网格实现，慢慢观望吧。。。


## 服务网格的正确形态？

目前主流的服务网格，核心元素有三个：

- 定位: Service Mesh 的定位始终是提供**服务间通讯**的基础设施层，范围包括 HTTP 和 RPC——支持 HTTP1.1/REST，支持 HTTP2/gRPC，支持 TCP 协议。也有一些小的尝试如对 Redis 、 Kafka 的支持。
- 原理: Service Mesh 的工作原理是**原协议转发**，原则上不改变协议内容（通常只是 header 有些小改动）。为了达到零侵入的目标，还引入了 iptables 等流量劫持技术。
- 部署: Service Mesh 支持 Kubernetes 和虚拟机，但都是采用 **Sidecar 模式**部署，没有采用其他方式如 Node 部署、中心化部署。

不过我们现在已经看到了 dapr 这样更通用的 multi-runtime 产品来搅局。

## 我的相关博客

- [使用 Istio 进行 JWT 身份验证（充当 API 网关）](https://ryan4yin.space/posts/use-istio-for-jwt-auth/)


## 其他资料

- [Slime：让Istio服务网格变得更加高效与智能](https://cloudnative.to/blog/netease-slime/)
