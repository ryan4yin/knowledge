# VPN 协议研究

## 哪些 VPN 协议比较流行

- [VPN 协议初步调研](https://docs.google.com/spreadsheets/d/1ab-23YWerXQKrsFx5mIHv93gzekfaqHH9YAp3SXttOM/edit#gid=0)

市面上用得比较多的主要是：

- OpenVPN(TCP/UDP): 支持最广泛的协议
- IPsec/IKEv2: 排第二
- WireGuard: 排第三

而 GRE、PPTP 跟 L2TP/IPSec 基本没见到有用的，大概因为某些原因被淘汰了吧。


## IPsec/IKEv2 协议

排第二，有些厂家推荐优先选择它，有问题再回退到 OpenVPN.

IPsec 是 1995 年 IETF 标准化的一个点对点的隧道协议，通过 IPsec VPN 可以在主机和主机之间、主机和网络安全网关之间或网络安全网关（如路由器、防火墙）之间建立安全的隧道连接。其协议主要工作在IP层，在IP层对数据包进行加密和验证。

IPsec 工作在 L3 网络层，比 OpenVPN 低好几个层级（SSL 比 L4 传输层还要高一个级别，可以认为是一个 L7 协议），因此效率会高很多，而且它还运行在内核空间，这又进一步提升了性能。

更准确地说，IPsec 是用于创建点对点安全隧道的一系列必要协议的集合，其主要工作流程如下：

- 识别「感兴趣流」：首先，通过 IPsec 策略匹配到本地需要通过 IPsec 隧道传输的数据包
- 建立隧道：执行 IKEv2 握手协议，与 TLS 协议类似，它也是使用非对称密钥进行相互认证与密钥交换，然后再切换到对称密钥加密通信
  - IKE 是基于 UDP 的密钥交换协议，目前主要应用的是 IKEv2
  - 其 v2 版本修复了多处密码学方面的安全漏洞，提高了安全性能，同时简化了协商过程，提升了协商效率，协议定义参见 [rfc5996](https://www.rfc-editor.org/rfc/rfc5996)。
- 进行数据传输
  - 其中会使用 AH 提供数据源认证与完整性校验（HMAC），或者使用 ESP 协议进行数据的加密认证。

IPsec 这种架构带来的问题是：

1. 参数众多，协议复杂，配置非常麻烦。
2. 正因为配置众多，每个供应商都选择了各自不同的参数，这导致客户端不能通用，只有供应商自家的 VPN 客户端才能连接上它家的 IPsec 通道。
3. 运行在内核空间，带来安全隐患。

### IPsec使用的端口

IPsec中IKE协议采用UDP 500端口发起和响应协商，因此为了使IKE协商报文顺利通过网关设备，通常要在网关设备上配置安全策略放开UDP 500端口。另外，在IPsec NAT穿越场景下，还需要放开UDP 4500端口。

而AH和ESP属于网络层协议，不涉及端口。为了使IPsec隧道能正常建立，通常还要在网关设备上配置安全策略放开AH（IP协议号是51）和ESP（IP协议号是50）服务。

- [什么是IPsec？ - 华为](https://info.support.huawei.com/info-finder/encyclopedia/zh/IPsec.html)
- [什么是 IPsec？| IPsec VPN 如何运作 - Cloudflare](https://www.cloudflare.com/zh-cn/learning/network-layer/what-is-ipsec/)
- [wiki/IPsec](https://en.wikipedia.org/wiki/IPsec)


## OpenVPN 协议

一种开源的 SSL VPN 协议，发布于 2001 年，也是应用最广泛的 VPN 协议，其官方有开源的的 [OpenVPN Community Edition](https://community.openvpn.net/openvpn)，因此协议也完全开源。

协议的官方文档：[OpenVPN's network protocol](https://build.openvpn.net/doxygen/network_protocol.html)

OpenVPN 官方宣称 SSL VPN 的特点是：

1. 基于成熟可靠的 SSL/TLS 协议，而且运行在用户空间而不是内核空间
2. 


### [OpenVPN and the SSL VPN Revolution] 阅读笔记

>这份文档可以在 OpenVPN 官方文档首页找到下载链接

IPsec 包含了太多可选参数，导致非专业人员很难正确地配置它。而且 IPsec 还运行在内核空间，这导致配置不当的情况下可能会发生灾难性事故——内核崩溃或者被恶意提权。

而 OpenVPN 是比 IPsec 更便宜、更简单、更安全的一种隧道协议，它使用 TLS 协议与密码学库取代了 IPsec 复杂的配置，还提供了更强大的功能。此外 OpenVPN 运行在用户空间，因此它更安全、更稳定（注：这也导致了巨大的性能开销——数据需要在内核空间与用户空间之间交互）。



## WireGuard 协议

最潮的新宠协议 [wireguard protocol](https://www.wireguard.com/protocol/)，很牛逼。

### WireGuard 白皮书阅读记要

#### 对比 IPsec/IKEv2

Linux 中标准的加密通道解决方案是 IPsec，用户需要往内核结构体中写入选择的 cipersuit 跟 key，以及其他 tranformer（比如压缩算法），这个数据结构通常由运行在用户空间的后台服务负责更新维护，而这些数据又实际来源于密钥交换协议的协商结果。通常使用 IKEv2 进行协议协商，因此需要填写到内核结构中的参数也都来源于其协商结果。

IKEv2 很复杂，可选参数很多，可拓展性很强，这导致了它不小的代码量与复杂度。

IPsec 包有两套完全分离的东西：IPsec 包的安全标签，跟防火墙语义。（？？？）

将密钥交换层（IKEv2）与底层的传输加密层分离，从网络分层的哲学上讲是很正确的，从学术的角度上讲是很完美的，但是这种设计实际上增加了复杂性，使协议很难被正确地实现与部署。

而 WireGuard 抛弃了这些分层逻辑，它只是简单地提供一个虚拟接口（如 wg0），管理员可以直接使用 iproute2 工具包来管理它——这就很简单直观了。

只要给 WireGuard 接口配置好接口私钥，以及所有的 peers 的公钥、IP 段，加密通道就能正常工作了。 
密钥交换、连接、重连、发现等等功能都在后台非常可靠地运行，管理员不需要关注其中的细节。从另一个角度来讲，对用户跟管理员而言，WireGuard 是 stateless 的——只要配置配好就能正常使用，不需要手动连接或者重连。

Linux 的普通防火墙策略也能直接被应用在 WireGuard 接口或流量上，没有任何新东西。

一句话总结，IPsec 在学术上很完美但是缺乏实用性，而 WireGuard 完全是从工程的角度出发设计的，虽然破坏了分层哲学，但是它大大提升了协议的易用性，降低了配置复杂度。

#### 对比 OpenVPN

OpenVPN 是基于用户空间 TUN/TAP 与 TLS 协议的加密通道方案。
由于它运行在用户空间，它的性能非常差——因为数据需要在内核空间与用户空间之间反复拷贝，同时它还需要一个常驻的后台服务。

对管理员而言 OpenVPN 跟 stateless 这个词的差距有点大。

另一方面，虽然 TUN/TAP 跟 WireGuard 的 wg0 一样具有类似的优点，但是 OpenVPN 支持了过多的 TLS 特性，这使它变得非常复杂，将相当多的代码暴露在潜在的 TLS 协议漏洞中。
在用户空间实现 OpenVPN 协议是一个正确的选择，因为内核空间 ASN.1 跟 X509 证书 parser 一直以来都问题颇多，如果将 TLS 协议栈也搬到内核空间只会把问题搞得更复杂。
TLS 自身还有一个巨大的状态机，而且它也导致 IP 地址与公钥之间的关联变得模糊。

#### 密钥分发

在 OpenSSH 协议中，协议完全不考虑密钥的分发——这完全由用户自己解决。
WireGuard 在密钥分发方面也借鉴了这一点，不提供任何密钥分发功能。说得直白一点，WireGuard 认为密钥分发不应在 WireGuard 协议中去做，用户应该通过其他密钥分发方案来做这件事。
另一个优势是，WireGuard 的公钥只有 32bytes, 可以被直接编码成 44 字符的 Base64 字符串，有很多方法可以去分发这么几行数据，比如 LDAP、GPG 签名邮件、扫二维码、HTTP API 等等。

#### 加密方案

WireGuard 非常有偏见地选择了一组现代化的加密算法，并且未提供任何 cipher 抽象与协议切换功能。
这意味着如果 WireGuard 被发现漏洞，那所有的 peers 都必须更新升级！

主要原因是 SSL/TLS 持续出现的漏洞洪流证明了 cipher 灵活性会极大增加复杂度。

算法选择如下：

- 1-RTT 密钥交换: Trevor Perrin’s Noise
- ECDH: Curve25519
- HKDF: ECDH 结果拓展
- RFC7539: ChaCha20 加密
- Poly1305: 实现认证加密
- BLAKE2s: 哈希算法

同时 WireGuard 内建了对 DoS 攻击的防范机制，使用了一种加密 cookie 机制用于 IP 地址属性确认。

同样有偏见的是，WireGuard 只支持 Layer-3 通道，因为在 Layer-3 做 packets 的认证、归因是最简洁干净的。

WireGuard 同时支持 IPv4 与 IPv6，4in6 与 6in4 两种封装方式都支持得很好。


#### Endpoints 与 Roaming(漫游)

WireGuard 的路由表设计中，每个（peer）都可以预先配置好一个可选的外部 IP 地址与 UDP 端口（Internet Endpoint），这个地址对应的主机可以给其他所有 peer 提供服务发现的功能。

提供服务发现的 peer 需要拥有固定的公网 IP 地址，该地址被在其他 peer 上设置为固定的 Internet Endpoint.
在其他 peers 需要访问另一个 peer 时，就会向这个已知 peer 的  Internet Endpoint 查询对面 peer 的 Internet Point 地址信息并使用其更新本地路由表，然后再发送消息过去。如果查询不到，就会请求失败，数据包被丢弃并返回 EHOSTUNREACH 错误。

>这种路由表的动态更新机制，也使得多个终端使用同一个 key 加入网络时，会互相「挤下线」，导致网络无法正常使用。

其他 peer 都配置好这台固定的 Internet Endpoint 后，peer 们就都可以在各 IP 地址之间漫游，再通过这台中间 peer 去发现其他 peer 的公网 Internet Point 地址。

>根据双方的 NAT 类型，这里应该涉及到一些 NAT 穿越与心跳保持相关的东西，不然多个 peer 之间难以直连。

#### 接收、发送数据流

每个 peer 的 `allowed_ips`，或者说在路由表中的 ip 地址，既可以是 ip 也可以是网段，这使所有 peer 都可能负责一个 ip 段的转发，也就是充当局域网的路由器——VPN 子路由。

同时每一个 peer 也能为其他 peer 提供数据中继服务——如果两个 peer 无法直连的话，可以通过修改路由表，就简单地通过某个中继 peer 使他们之间能正常通信。（猜的啊，还不确认）

#### 协议与密码学


