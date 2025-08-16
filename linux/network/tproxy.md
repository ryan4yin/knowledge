# tproxy 透明代理

https://www.kernel.org/doc/Documentation/networking/tproxy.txt

## Istio Sidecar 的流量拦截

以 Istio 为例，它默认使用 iptables
REDIRECT 跟 NAT 实现将 inbound/outbound 流量拦截到 sidecar, 但是这种方式会导致 source
IP 被 NAT 后丢失，sidecar 无法获得该地址。

Istio 也支持使用 iptables
TPROXY 透明代理来实现流量拦截，顾名思义，这一拦截行为是透明的，不会修改数据包信息，因此 source
IP 不会丢失。
其主要缺点是，sidecar 会需要 CAP_NET_ADMIN 权限来实现 TPROXY 功能。



