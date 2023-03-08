# Border Gateway Protocol

边界网关协议（英语：Border Gateway Protocol，缩写：BGP）是互联网上一个核心的**去中心化自治路由协议**。它通过维护IP路由表或‘前缀’表来实现自治系统（AS）之间的可达性，属于矢量路由协议。BGP不使用传统的内部网关协议（IGP）的指标，而使用基于路径、网络策略或规则集来决定路由。因此，它更适合被称为矢量性协议，而不是路由协议。

大多数互联网服务提供商必须使用BGP来与其他ISP创建路由连接（尤其是当它们采取多宿主连接时）。因此，即使大多数互联网用户不直接使用它，但是与7号信令系统相比，即通过PSTN的跨供应商核心响应设置协议，BGP仍然是互联网最重要的协议之一。特大型的私有IP网络也可以使用BGP。例如当需要将若干个大型的开放最短路径优先（OSPF）网络进行合并，而OSPF本身又无法提供这种可扩展性时。使用BGP的另一个原因是其能为多宿主的单个ISP（RFC 1998）或多个ISP网络提供更好的冗余网络。

>比如 Kubernetes 的众多网络实现，都使用了 BGP 协议。详见 [kubernetes 如何将服务暴露到外部](/kubernetes/kubernetes%20如何将服务暴露到外部.md)

待续

## 参考

- [Border Gateway Protocol -Wiki](https://zh.wikipedia.org/wiki/%E8%BE%B9%E7%95%8C%E7%BD%91%E5%85%B3%E5%8D%8F%E8%AE%AE)
- [BGP漫谈](https://zhuanlan.zhihu.com/p/25433049)
- [EBGP vs IBGP](https://zhuanlan.zhihu.com/p/31766603)
