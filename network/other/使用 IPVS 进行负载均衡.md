# 使用 IPVS 进行负载均衡

>本文需要前置知识：iptables 四表五链的概念，详见 [iptables 及 docker 容器网络分析](https://thiscute.world/posts/iptables-and-container-networks/)

IPVS 是一个高性能的四层负载均衡器，由两部分组成：

- linux 内核模块 ipvs
  - 源码地址：https://github.com/torvalds/linux/tree/master/net/netfilter/ipvs
- 用户层的管理工具 ipvsadm
  - 源码地址：https://git.kernel.org/pub/scm/utils/kernel/ipvsadm/ipvsadm.git/

其中 ipvs 是一个依附于 netfilter 的内核模块（看源码路径也能确认这一点），这也是为啥需要 iptables 作为前置知识的原因。


待续
