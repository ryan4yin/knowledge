# [Envoy](https://github.com/envoyproxy/envoy/)

官方定义：Cloud-native high-performance edge/middle/service proxy

envoy 目前是在云原生社区最流行的网络代理，没有之一。众多的 API 网关和服务网格，都是以它为基础。

不论是为了学习研究，还是需要在生产环境使用基于 Envoy 的服务网格/API 网关，学习 Envoy 都是有必要的。

## 与 Nginx 的异同

### 0. 配置方式

Nginx 与 Envoy 在配置方面的设计目标是不一样的。

Nginx 在 2004 年，那个时候 Web 服务器都是手工配置的，所以 Nginx 设计了专用的语法用于编写配置，主要是方便配置的编写。而且当时也没有动态更新配置的需求，配置更新后手动 reload 一下对管理员而言也不是难事。

而 Envoy 的设计目标是作为微服务的边车代理，并且组成服务网格来代理所有集群流量，这种场景需要非常灵活的动态配置能力。
因此 Envoy 的配置使用了 Json/Yaml 这种解析很方便的配置语法，而且设计重点是配置的模块化，使每部分配置都能单独更新。
这也导致了直接手写配置的话，Envoy 的配置会显得比较臃肿。

但是实际上把 Envoy 的结构理清楚，它的配置还是很好理解的。

### 1. Worker 连接数

Nginx 的配置中需要设定 worker 进程数，以及最大连接数。

而 Envoy 使用非阻塞事件循环编写 worker 代码，因此它不需要太多的线程，也不需要维护太多的连接。
默认情况下 Enovy 使用的线程数等于硬件线程数（即 Linux 逻辑核数），任一 Worker 与每个上游都只会建立一个 HTTP/2 连接，或者维护一个 HTTP/1.1 连接池。

一个 Worker 与每个上游只建立一个 HTTP/2 连接，但因为 HTTP/2 的多路复用等属性，这并不表示 Envoy 的性能一定会比 Nginx 的大量 Workers 差。

Envoy 的线程数是一个很重要的参数，可以通过 `--concurrency` 来修改，一般边缘代理（网关）需要设置更高的线程数（Worker 数），
而内部代理大部分负载都很低，降低线程数可以减少资源浪费，在大型服务网格中这就显得很重要了。


详见 [Envoy threading model](https://blog.envoyproxy.io/envoy-threading-model-a8d44b922310)


### 2. 客户端断开连接

对于 proxy 还在处理数据，连响应 header 都还没返回给客户端的时候，客户端主动了断开连接的情况，
nginx 和 envoy 在内部使用不同的状态码来记录这种情况：

- nginx 使用状态码 `499`
- envoy 则使用状态码 `0`

如果出现这种状态码，通常有以下几种可能：

- 客户端自身问题：客户端收到了 SIGTERM 信号，于是主动关闭了所有连接。
  - 比如你手动终止一个正在高并发压测的 wrk 程序，就可能在 nginx/envoy 上看到 `499`/`0`
- 服务端问题：客户端等了很久没等到响应，于是放弃了等待。
  - 这可能说明服务端处理用的时间太久了。
- 其他网络问题

### 3. HTTP 配置

Nginx 的 http 配置块中，可以在全部或某个 location 上配置 gzip、超时、access_log、rewrite 等功能，还支持使用 if 之类的 DSL，或者运行 lua 脚本。

而在 Envoy 中，所有 HTTP 相关的功能都是使用过滤器实现的，后面会详细讨论。

另外 Envoy 原生支持 json 格式的 access_log, promethus 监控指标，以及分布式链路追踪。

### 3. Upstream

Nginx 的 Upstream 负责在多个 server 之间进行负载均衡，而且不支持动态发现。
Envoy 中与之对应的概念是 Cluster，每个 Cluster 都可以有多个 Endpoints.
Cluster 负责在 Endpoints 之间进行负载均衡，也支持动态发现 Endpoints.


## 参考

- [Envoy 中文指南 - 云原生实验室](https://fuckcloudnative.io/envoy-handbook)
- [服务网格数据面性能深度调优](https://mp.weixin.qq.com/s/sRH-VKJh2izfSJuG7dNhGg)
- [Envoy请求流程源码解析（一）：流量劫持](https://segmentfault.com/a/1190000041456849)
- [Istio 中文指南 - 云原生实验室](https://github.com/yangchuansheng/envoy-handbook)
