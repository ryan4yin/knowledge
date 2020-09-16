
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

## Istio 数据面性能优化

待续

## 参考

- [Istio数据面性能测试与优化](https://penglei.github.io/post/latency-optimization-for-istio-proxy-based-on-envoy/)

