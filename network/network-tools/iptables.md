# [Iptables](https://www.netfilter.org/projects/iptables/index.html)

>本文描述的 iptables 仅作用于 ipv4 网络，对 ipv6 请查看 ip6tables 相关文档

iptables 提供了包过滤、NAT 以及其他的包处理能力，iptables 应用最多的两个场景是 firewall 和 NAT

iptables 及新的 nftables 都是基于 netfilter 开发的，是 netfilter 的子项目。

但是 eBPF 社区目前正在开发旨在取代 netfilter 的新项目 bpfilter，他们的目标之一是兼容 iptables/nftables 规则，让我们拭目以待吧。

>吐槽：感觉 iptables 好复杂啊

## 概念 - 四表五链

详细的说明参见 [iptables详解（1）：iptables概念](https://www.zsythink.net/archives/1199)，这篇文章写得非常棒！

我这里就转载下其中总结性的一张图：

![iptables-chains](./_imgs/iptables-chains.png)


## 常用命令



## 参考

- [iptables详解（1）：iptables概念](https://www.zsythink.net/archives/1199)

