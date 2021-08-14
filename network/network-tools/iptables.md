# [Iptables](https://www.netfilter.org/projects/iptables/index.html)

>本文描述的 iptables 仅作用于 ipv4 网络，对 ipv6 请查看 ip6tables 相关文档

iptables 提供了包过滤、NAT 以及其他的包处理能力，iptables 应用最多的两个场景是 firewall 和 NAT

iptables 及新的 nftables 都是基于 netfilter 开发的，是 netfilter 的子项目。

但是 eBPF 社区目前正在开发旨在取代 netfilter 的新项目 bpfilter，他们的目标之一是兼容 iptables/nftables 规则，让我们拭目以待吧。

>吐槽：感觉 iptables 好复杂啊

## 概念 - 四表五链


详细的说明参见 [iptables详解（1）：iptables概念](https://www.zsythink.net/archives/1199)，这篇文章写得非常棒！

默认情况下，iptables 提供了四张表和五条链，数据在这四表五链中的处理流程如下图所示：

![iptables-chains](./_imgs/iptables-chains.png)

对照上图，对于发送到某个用户层程序的数据而言，流量顺序如下：

- 首先进入 PREROUTING 链，依次经过这三个表： raw -> mangle -> nat
- 然后进入 INPUT 链，这个链上也有三个表，处理顺序是：mangle -> nat -> filter
- 过了 INPUT 链后，数据才会进入内核协议栈，最终到达用户层程序。

用户层程序发出的报文，则依次经过这几个表：OUTPUT -> POSTROUTING

从图中也很容易看出，如果数据仅由本机负责转发，那它通过的几个链依次是：PREROUTEING -> FORWARD -> POSTROUTING

五链的功能和名称完全一致，应该很容易理解。下面按优先级分别介绍下链中的四个表：

- raw: 对收到的数据包在连接跟踪前进行处理。一般用不到，可以忽略
  - 一旦用户使用了 RAW 表，RAW 表处理完后，将跳过 NAT 表和 ip_conntrack 处理，即不再做地址转换和数据包的链接跟踪处理了
- mangle: 用于修改报文、给报文打标签
- nat: 主要用于做网络地址转换，SNAT 或者 DNAT
- filter: 主要用于过滤数据包

数据在按优先级经过四个表的处理时，一旦在某个表中匹配到一条规则 A,下一条处理规则就由规则 A 的 target 参数指定，**后续的所有表**都会被忽略。target 有如下几种类型：

- ACCEPT: 直接允许数据包通过
- DROP: 直接丢弃数据包，对程序而言就是 100% 丢包
- REJECT: 丢弃数据包，但是会给程序返回  RESET。这个对程序更友好，但是存在安全隐患，通常不使用。
- MASQUERADE: （伪装）将 src ip 改写为网卡 ip，和 SNAT 的区别是它会自动读取网卡 ip。路由设备必备。
- SNAT/DNAT: 顾名思义，做网络地址转换
- REDIRECT: 在本机做端口映射
- LOG: 在/var/log/messages文件中记录日志信息，然后将数据包传递给下一条规则，也就是说除了记录以外不对数据包做任何其他操作，仍然让下一条规则去匹配。
  - 只有这个 target 特殊一些，匹配它的数据仍然可以匹配后续规则，不会直接跳过。

理解了上面这张图，以及四个表的用途，就很容易理解 iptables 的命令了。

## 常用命令




## 参考

- [iptables详解（1）：iptables概念](https://www.zsythink.net/archives/1199)

