# Istio 使用说明


## VirtualService

VirtualService 详细介绍，参见官方文档：[VirtualService Reference - Istio Docs](https://istio.io/latest/docs/reference/config/networking/virtual-service)

### VirtualService 注意事项

1. hosts 属性可以使用 FQDN，也建议使用 FQDN
2. gateways 列表中的元素有三种可能：
   1. 网格内部流量：`mesh`，这也是默认的 gateway.
   1. 当前名字空间的网关：`<gateway-name>`，直接填网关名称。
   1. 别的名字空间的网关：` <gateway-namespace>/<gateway-name>`，比如 `my-namespace/my-gateway`
      1. gateway 名称不是域名 FQDN！而是使用 `/` 分隔的一个名称！
3. [routes 的匹配顺序](https://istio.io/latest/docs/concepts/traffic-management/#routing-rule-precedence)
   1. Istio 按列表的顺序，从上至下地进行 routes 匹配。也就是说越靠前的规则优先级越高。

### 监控中出现 503 可能的原因

通过 istio 监控指标，能看到 503 对应的 [RESPONSE_FLAG](https://www.envoyproxy.io/docs/envoy/latest/configuration/observability/access_log/usage#config-access-log-format-response-flags)，它给出了 503 更详细的原因。


#### 案例一 - 应用程序雪崩

应用程序雪崩，线程池跑满，所有请求全部没响应。这会在 istio 中导致大量的 0 状态码和 503 状态码。

通过 prometheus 监控能够查到所有 503 响应的 RESPONSE_FLAG 都是 URX，0 状态码则是客户端等太久不耐烦了，主动断开连接。

要进一步验证的话，在容器里直接 curl 容器的任何 http path 也是会卡住的（即使是 404），因为压力太大，所有线程都卡住了，cpu/mem 等指标也会无法采集。

这种情况应该从应用程序或者流量切量上找原因，为啥会雪崩，如何去做熔断限流、或者缓慢切量，以避免雪崩或者恢复服务。
