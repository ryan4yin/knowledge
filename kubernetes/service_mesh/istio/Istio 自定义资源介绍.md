# Istio 自定义资源介绍

## VirtualService

VirtualService 详细介绍，参见官方文档：[VirtualService Reference - Istio Docs](https://istio.io/latest/docs/reference/config/networking/virtual-service)

### VirtualService 注意事项

1. hosts 属性可以使用 FQDN，也建议使用 FQDN
   1. **VirtualService** 仅使用 `Host` 或者 HTTP/2 的 `:authority`  Header 匹配 自己的 `hosts` 字段，不会考虑请求的目标 IP 地址！
   2. 这意味着你对任意一个 IP 地址发出一个 `Host` 能匹配上某个 virtualservice 的请求，都会被 Envoy 的 VirtualService 拦截并处理！目标 IP 地址会直接被忽略！
   3. 因此，网关层为了透传一个客户端的 host 到服务端，比如 `example.com`，就必须要有一个能匹配得上这个 host 的 virtualservice 才行。
      1. 否则 Istio 将会忽略这些请求，请求当然也能正常被发送到对应的服务，但是就利用不上任何 Istio 的功能了。
2. gateways 列表中的元素有三种可能：
   1. 网格内部流量：`mesh`，这也是默认的 gateway.
   2. 当前名字空间的网关：`<gateway-name>`，直接填网关名称。
   3. 别的名字空间的网关：` <gateway-namespace>/<gateway-name>`，比如 `my-namespace/my-gateway`
      1. gateway 名称不是域名 FQDN！而是使用 `/` 分隔的一个名称！
3. [routes 的匹配顺序](https://istio.io/latest/docs/concepts/traffic-management/#routing-rule-precedence)
   1. Istio 按列表的顺序，从上至下地进行 routes 匹配。也就是说越靠前的规则优先级越高。


