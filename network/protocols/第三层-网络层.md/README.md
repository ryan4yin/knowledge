# 第三层网络层（The Network Layer）

>网络基础太薄弱，这部分可能有错误。。

1. 主机或路由器接入 IP 网络的边界，被称为接口(Interface)。接口可以对应一个物理的网线端口，也可以是虚拟的。
   1. IP 协议要求每个接口都必须有一个 IP 地址。（也可以多个？）
   2. 主机或路由器的 IP 地址，就是它的接口的 IP 地址。
   3. 物理端口，和接口通常是一一对应的。但是接口可以虚拟。一台单物理端口的物理主机可以通过接口虚拟化技术，获得多个 IP 地址。
   4. 接口的 IP 地址必须属于它所在的网段。


### IPV4

IPV4 通过

### IPv6

>[全球 IPv6 部署现状](http://stats.labs.apnic.net/ipv6/)



## 问题：像各大 DNS 服务提供商，它们的 IP 地址都是固定的，不会有单点问题么？

所有的数据中心(Internet Data Center, IDC)，都应用了很多我们不了解的网络高可用(HA)与负载均衡(LB)技术，
固定的 IP 地址并不是说只能对应到一台物理路由器/主机，甚至不一定只对应一根物理网线：

1. 七层负载均衡(HTTP)：在应用层，查看 HTTP 请求头，判断数据要发送到哪类具体的后端服务器（后端可以是容器、虚拟机或物理机）。
1. 四层负载均衡(TCP)：在传输层，通过查看 IP+Port，判断数据要转发到哪类后端服务器。
2. 三层网络层负载均衡/高可用(IP): 
   1. [keepalived](https://github.com/acassen/keepalived) 使用 [VRRP](https://en.wikipedia.org/wiki/Virtual_Router_Redundancy_Protocol) 实现高可用， vrrp 协议将多个运行着把多个运行着VRRP协议的物理路由器抽象成一个虚拟路由器，物理路由器会通过 VRRP 协议选主，这样能保证虚拟路由器高可用。
   2. kubernetes 的 bare-metal loadbalancer 实现 [metallb](https://github.com/metallb/metallb)/[porter](https://github.com/kubesphere/porter) 利用 BGP 与 ECMP 在网络层实现负载均衡与高可用。
3. 二层链路聚合(MAC): 将多条物理链路虚拟成一条逻辑链路，可以实现链路的高可用，同时也能提升链路带宽(逻辑链路的带宽是所有物理链路带宽的叠加)。


## 参考

- [IPv6，到底是什么？](https://zhuanlan.zhihu.com/p/36542469)


