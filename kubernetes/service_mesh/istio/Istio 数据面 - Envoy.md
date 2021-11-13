
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

## Istio 数据面性能优化

待续


## 控制数据面 proxy 的启动、终止顺序

### 预先启动 proxy，或者说在 proxy 启动后再启动其他容器

Istio 1.7 新增了一个功能: [delay the application start until after the sidecar is started](https://istio.io/latest/news/releases/1.7.x/announcing-1.7/change-notes/#traffic-management)

通过设置 operator 参数 `values.global.proxy.holdApplicationUntilProxyStarts=true`，就能全局启用此功能，让主容器在 Sidecar 就绪后启动，避免主容器因为网络未就绪而 Crash.

或者在 pod 上添加如下注解也是一样的效果（只在该 pod 上生效）：

```yaml
annotations:
  # https://istio.io/latest/docs/reference/config/istio.mesh.v1alpha1/#ProxyConfig
  proxy.istio.io/config: '{ "holdApplicationUntilProxyStarts": true }'
```

建议：通常只有一启动就需要访问外部网络的服务，会有这个问题，因此我认为应该按需在每个 Pod 上启用此功能，没必要改全局配置。

### 在所有连接全部 Drain 掉后，再关闭 proxy

同样的，
```yaml
annotations:
  # https://istio.io/latest/docs/reference/config/istio.mesh.v1alpha1/#ProxyConfig
  proxy.istio.io/config: |
    terminationDrainDuration: 30s
```


## 参考

- [Istio数据面性能测试与优化](https://penglei.github.io/post/latency-optimization-for-istio-proxy-based-on-envoy/)
- [深入了解服务网格数据平面性能和调优 - 文章](https://cloud.tencent.com/developer/article/1685873)
- [深入了解服务网格数据平面性能和调优 - 视频](https://v.qq.com/x/page/v3137ax6zss.html)
