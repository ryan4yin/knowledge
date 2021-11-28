
## Envoy Sidecar 管理员 API

登入 Pod 的 shell 中，可以通过如下命令，访问 Envoy 的管理员 API：

```shell
# 查看所有 管理员 api
curl localhost:15000/help

# 查看动态集群配置，内容相当多。。还没搞明白
curl localhost:15000/config_dump?resource=dynamic_active_clusters

# 查看静态监听配置，内容相当多。。还没搞明白
curl localhost:15000/config_dump?resource=static_listeners

```

官方文档：[Administration interface - Enovy Docs](https://www.envoyproxy.io/docs/envoy/latest/operations/admin#)


## [EnvoyFilter](https://istio.io/latest/docs/reference/config/networking/envoy-filter/)

可以通过 Istio 提供的 EnvoyFilter 自定义 Envoy 的配置。


## 关闭 Sidecar 注入会导致什么现象？

有部分服务，业务方为了省钱，就通过注解 `sidecar.istio.io/inject: 'false'` 把 Sidecar 关掉了。
这会造成一些与预期不一致的现象。

首先明确两点：

- Istio 在客户端执行所有的负载均衡、流量切分逻辑
  - 对于从网关进来的请求，Istio 直接在 IngressGateway 上执行负载均衡、流量切分逻辑。因此服务关闭 Sidecar 也没啥影响。
  - 对于服务间调用，调用方就必须注入了 Sidecar，否则 Istio 的流量切分、负载均衡等逻辑都会失效。
- Istio 的监控指标，依赖于客户端与服务端两个 Sidecar 之间的信息沟通。
  - 对于从网关进来的请求，如果服务端关闭了 Sidecar 注入，IngressGateway 就无法获知服务端信息，将无法生成监控指标。
  - 对于服务间调用
    - 如果客户端关闭了 Sidecar，服务端会生成 `source_workload=unknown` 的监控指标。
    - 如果服务端关闭了 Sidecar，那跟网关调用一样，将无法生成监控指标。
    - 两边都关掉了 Sidecar，那显然也不会有任何指标...


## Istio 数据面性能优化

待续


## 参考

- [Istio数据面性能测试与优化](https://penglei.github.io/post/latency-optimization-for-istio-proxy-based-on-envoy/)
- [深入了解服务网格数据平面性能和调优 - 文章](https://cloud.tencent.com/developer/article/1685873)
- [深入了解服务网格数据平面性能和调优 - 视频](https://v.qq.com/x/page/v3137ax6zss.html)
