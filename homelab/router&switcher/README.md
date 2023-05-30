# 路由器 - 交换机

最流行的一些专门为网络设计的开源操作系统有：

- [openwrt](https://github.com/openwrt/openwrt): 全世界最著名的开源路由器操作系统，基于 Linux 内核与 musl 库，专门面向嵌入式场景
  - 有大量的路由器固件，都是基于 openwrt 开发的
- [vyos](https://github.com/vyos/vyos-build): 一个从 deiban 分支出来的操作系统，主要面向网络设备。ubnt 的 EdgeOS 与它同源。
- [BSDRP](https://github.com/ocochard/BSDRP): 也有一些路由器操作系统是基于 FreeBSD 开发的，比如这个开源的 BDSRP.

>详见 [Network operating system - wiki](https://en.wikipedia.org/wiki/Network_operating_system)

各类路由器专用的操作系统，其最大的优势是对各类路由器硬件驱动的支持！

此外，对于虚拟化的软路由而言，它并非直接运行在嵌入式硬件上，因此它完全可以使用任何普通 Linux 发行版作为该软路由的操作系统。
因为所有基于 Linux 的路由器，其网络功能都是基于 iptables/netfilter 实现的，任何 Linux 发行版都拥有完整的网络能力。

相关项目有：

- [linux-router](https://github.com/garywill/linux-router): 一行命令将 linux 服务器变成一台路由器

在虚拟化软路由场景下，路由器专用系统的最大优势「硬件兼容性与驱动支持」不复存在，选择不同的操作系统可能会出于如下理由：

- 使用 openwrt 等路由器专用系统的好处是，有大量现成的插件生态可用，也提供久经考验的 Web 面板，对会友好很多
- 使用 Ubuntu/Debian 等其他发行版的主要原因可能是，用户对这些系统要更熟悉，而且熟知 iptables/netfilter 的各项功能与命令

其实还有最简单的配置方法，几行命令就能将一台 Linux 主机改成路由器（仅 ipv4）：

```shell
# 1. 修改内核参数，打开 ip 转发功能
sysctl -w net.ipv4.ip_forward=1
# 2. 允许 ip 地址不匹配的数据包通过
sudo iptables -A FORWARD -i eth0 -j ACCEPT
# 3. 使用 iptables 命令配置 MASQUERADE 规则
sudo iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
```

只需要上面三行命令就能将一台 Linux 主机改造成路由器，不过它只是临时生效，重启后需要重新设置。

## 相关知识点

- MASQUERADE：即 IP 伪装技术，所有 NAT 网关都需要启用此功能与 nf_conntrack 连接跟踪，用于实现 NAT 的 IP 地址翻译
- 混杂模式（promiscuous mode）：是指一台机器的网卡能够接收所有经过它的数据流，而不论其目的地址是否是它。

