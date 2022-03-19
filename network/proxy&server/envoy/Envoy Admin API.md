## Envoy 管理员 API

如果 Admin API 配置了监听地址为 `0.0.0.0:15000`，可以直接通过浏览器访问 `<ip-addr>:15000`。
这是一个导航页，列出了 Admin 的各种 API 接口。

在命令行中，可以通过如下命令，访问 Envoy 的管理员 API：

```shell
# 查看所有 Admin api
curl localhost:15000/help

# 查看动态集群配置
curl localhost:15000/config_dump?resource=dynamic_active_clusters

# 查看静态监听配置
curl localhost:15000/config_dump?resource=static_listeners

# 查看当前的 clusters 信息（有哪些 endpoints，是否 health，权重，监控指标等）
curl localhost:15000/clusters?format=json

# 查看当前的 listeners 信息
curl localhost:15000/clusters?format=json

# prometheus 指标接口
curl localhost:15000/stats/prometheus

# Envoy 的其他运行时信息
curl localhost:15000/server_info
```

官方文档：[Administration interface - Enovy Docs](https://www.envoyproxy.io/docs/envoy/v1.21.1/operations/admin#)


