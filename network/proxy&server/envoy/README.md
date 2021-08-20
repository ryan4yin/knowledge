# [Envoy](https://github.com/envoyproxy/envoy/)

官方定义：Cloud-native high-performance edge/middle/service proxy

envoy 目前是在云原生社区最流行的网络代理，没有之一。众多的 API 网关和服务网格，都是以它为基础。

不论是为了学习研究，还是需要在生产环境使用基于 envoy 的服务网格/API 网关，学习 envoy 都是有必要的（否则生产环境出了问题就抓瞎了...）

## 与 Nginx 的异同

### 1. Worker 连接数

Nginx 的配置中需要设定 worker 进程数，以及最大连接数。

而 Envoy 使用非阻塞实事件循环编写 worker 代码，因此它不需要太多的线程，也不需要维护太多的连接。
默认情况下 Enovy 使用的线程数等于硬件线程数（即 Linux 逻辑核数），任一 Worker 与每个上游都只会建立一个 HTTP/2 连接。

一个 Worker 与一个上游只建立一个 HTTP/2 连接，但因为 HTTP/2 的多路复用等属性，这并不表示 Envoy 的性能一定会比 Nginx 的大量 Workers 差。

Envoy 的线程数是一个很重要的参数，可以通过 `--concurrency` 来修改，一般边缘代理（网关）需要设置更高的线程数（Worker 数），
而内部代理大部分负载都很低，降低线程数可以减少资源浪费，在大型服务网格中这就显得很重要了。


详见 [Envoy threading model](https://blog.envoyproxy.io/envoy-threading-model-a8d44b922310)


## 参考

- [Envoy 中文指南 - 云原生实验室](https://fuckcloudnative.io/envoy-handbook)


