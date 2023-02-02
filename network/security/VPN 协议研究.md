# VPN 协议研究

## 哪些 VPN 协议比较流行

- [VPN 协议初步调研](https://docs.google.com/spreadsheets/d/1ab-23YWerXQKrsFx5mIHv93gzekfaqHH9YAp3SXttOM/edit#gid=0)

市面上用得比较多的主要是：

- OpenVPN(TCP/UDP): 支持最广泛的协议
- IKEv2: 好像排第二
- IPsec: 排第三
- WireGuard: 排第四

而 PPTP 跟 L2TP/IPSec 基本没见到有用的，大概因为某些原因被淘汰了吧。

## OpenVPN 协议

支持最广泛的协议，其官方有开源的的 [OpenVPN Community Edition](https://community.openvpn.net/openvpn)，因此协议也完全开源。

协议的官方文档：[OpenVPN's network protocol](https://build.openvpn.net/doxygen/network_protocol.html)

TODO

## IKEv2 协议

排第二，有些厂家推荐优先选择它，有问题再回退到 OpenVPN

IKEv2 是 IEEE 工程组定义的标准协议，RFC 为 [rfc5996](https://www.rfc-editor.org/rfc/rfc5996)

TODO

## IPsec 协议

支持的也不少

- [什么是IPsec？ - 华为](https://info.support.huawei.com/info-finder/encyclopedia/zh/IPsec.html)
- [什么是 IPsec？| IPsec VPN 如何运作 - Cloudflare](https://www.cloudflare.com/zh-cn/learning/network-layer/what-is-ipsec/)
- [wiki/IPsec](https://en.wikipedia.org/wiki/IPsec)

TODO

## WireGuard 协议

最潮的新宠协议

- [wireguard protocol](https://www.wireguard.com/protocol/)

TODO



