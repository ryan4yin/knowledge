# VPN 协议研究

## 哪些 VPN 协议比较流行

- [VPN 协议初步调研](https://docs.google.com/spreadsheets/d/1ab-23YWerXQKrsFx5mIHv93gzekfaqHH9YAp3SXttOM/edit#gid=0)

市面上用得比较多的主要是：

- OpenVPN(TCP/UDP): 支持最广泛的协议
- IPsec/IKEv2: 排第二
- WireGuard: 排第三

而 GRE、PPTP 跟 L2TP/IPSec 基本没见到有用的，大概因为某些原因被淘汰了吧。

>这里仅考虑最通用的 VPN 协议，不考虑带流量伪装功能（加密混淆）的 VPN 协议。

## 一、IPsec/IKEv2 协议

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
  - 其中 AH 协议会校验数据包的源 IP 地址，这导致它几乎无法穿越任何 NAT 网关。要穿越 NAT 只能用 ESP

IPsec 这种架构带来的问题是：

1. 参数众多且复杂，存在大量的可选参数（使用 tunnel 模式还是 transport 模式？使用 AH 还是 ESP，或者都用？），而且其中很多选项都是不安全的。这就导致 IPsec 的配置变得非常麻烦，而且很容易导致安全隐患。
2. 正因为配置众多，每个供应商都选择了各自不同的参数，这导致客户端不能通用，只有供应商自家的 VPN 客户端才能连接上它家的 IPsec 通道。
3. 运行在内核空间，带来安全隐患。

### IPsec使用的端口

IPsec中IKE协议采用UDP 500端口发起和响应协商，因此为了使IKE协商报文顺利通过网关设备，通常要在网关设备上配置安全策略放开UDP 500端口。另外，在IPsec NAT穿越场景下，还需要放开UDP 4500端口。

而AH和ESP属于网络层协议，不涉及端口。为了使IPsec隧道能正常建立，通常还要在网关设备上配置安全策略放开AH（IP协议号是51）和ESP（IP协议号是50）服务。

- [什么是IPsec？ - 华为](https://info.support.huawei.com/info-finder/encyclopedia/zh/IPsec.html)
- [什么是 IPsec？| IPsec VPN 如何运作 - Cloudflare](https://www.cloudflare.com/zh-cn/learning/network-layer/what-is-ipsec/)
- [wiki/IPsec](https://en.wikipedia.org/wiki/IPsec)


## 二、OpenVPN 协议

一种开源的 SSL VPN 协议，发布于 2001 年，也是应用最广泛的 VPN 协议，其官方有开源的的 [OpenVPN Community Edition](https://community.openvpn.net/openvpn)，因此协议也完全开源。

协议的官方文档：[OpenVPN's network protocol](https://build.openvpn.net/doxygen/network_protocol.html)


### [OpenVPN and the SSL VPN Revolution] 阅读笔记

>这份文档可以在 OpenVPN 官方文档首页找到下载链接

IPsec 包含了太多可选参数，导致非专业人员很难正确地配置它。而且 IPsec 还运行在内核空间，这导致配置不当的情况下可能会发生灾难性事故——内核崩溃或者被恶意提权。

而 OpenVPN 是比 IPsec 更便宜、更简单、更安全的一种隧道协议，它使用 TLS 协议与密码学库取代了 IPsec 复杂的配置，还提供了更强大的功能。此外 OpenVPN 运行在用户空间，因此它更安全、更稳定（注：这也导致了巨大的性能开销——数据需要在内核空间与用户空间之间交互）。

OpenVPN 官方宣称 SSL VPN 的特点是：

1. 基于被充分测试过的、成熟可靠的 SSL/TLS 协议，而且此协议实现起来比 IPsec 容易许多
2. 使用 TUN/TAP 虚拟网卡技术，运行在用户空间而不是内核空间，对 OS 安全没有影响
3. 而且跟 OS 自带的 IPsec VPN 功能没有冲突，很容易安装
4. 从 OpenVPN 2.0 开始，只需要单个 UDP 端口、一份配置文件、一个 TUN/TAP 虚拟网口，即可正常工作。

协议的握手与数据传输过程与 mTLS + PFS 别无二致。


## 三、WireGuard 协议

最潮的新宠协议 [wireguard protocol](https://www.wireguard.com/protocol/)，很牛逼。

其他参考资料：

- [WireGuard到底好在哪？](https://zhuanlan.zhihu.com/p/404402933): 比较深入浅出的随想，值得一读。
- [WireGuard 基础教程：wg-quick 路由策略解读 - 米开朗基扬](https://icloudnative.io/posts/linux-routing-of-wireguard/)

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


TODO


### WireGuard 协议实测

首先通过如下 docker-compose 配置启动一个 WireGuard 服务端：

```yaml
---
version: "2.1"
services:
  wireguard:
    image: lscr.io/linuxserver/wireguard:latest
    container_name: wireguard
    ports:
      - 51820:51820/udp
      # 8182 是下面 wg-json-api 服务的端口，因为加到了同一个网络中，所以在这边添加端口映射
      - 8182:8182
    sysctls:
      - net.ipv4.conf.all.src_valid_mark=1
    cap_add:
      - NET_ADMIN
      - SYS_MODULE
    environment:
      - PUID=1000
      - PGID=1000
      - TZ=Etc/UTC
      - SERVERURL=192.168.5.198
      - SERVERPORT=51820 #optional
      - PEERS=1 #optional
      - PEERDNS=auto #optional
      - INTERNAL_SUBNET=10.13.13.0 #optional
      - ALLOWEDIPS=0.0.0.0/0 #optional
      - PERSISTENTKEEPALIVE_PEERS= #optional
      - LOG_CONFS=true #optional
    volumes:
      - /etc/wireguard:/config
      - /lib/modules:/lib/modules #optional
    restart: unless-stopped
  wg-api:
    image: james/wg-api:latest
    container_name: wg-api
    restart: unless-stopped
    # 加入到 wireguard 服务的名字空间中
    network_mode: service:wireguard
    depends_on:
      - wireguard
    cap_add:
      - NET_ADMIN
    # 必须在同一名字空间内，才能直接访问到 wg0 设备
    command: wg-api --device wg0 --listen 0.0.0.0:8182
```

#### 1. 客户端网络分析

现在从宿主机 `/etc/wireguard/peer1` 文件夹中找到 `peer1.conf`，它是客户端配置文件。

在另一台机器上使用如下命令启动一台 WireGuard 客户端：

```bash
sudo apt install wireguard resolvconf

# 从服务端拷贝配置文件到客户端的 /etc/wireguard/peer1.conf

# 启动 WireGuard
sudo wg-quick up peer1
```

我启动时的日志如下，打印出了 wg-quick 执行的所有指令（我添加了详细的注释）：

```bash
$ sudo wg-quick up peer1
[#] ip link add peer1 type wireguard             # 创建一个名为 peer1 的 WireGuard 设备
[#] wg setconf peer1 /dev/fd/63                  # 设置 peer1 设备的配置
[#] ip -4 address add 10.13.13.2 dev peer1       # 设置 peer1 设备的 IP 地址
[#] ip link set mtu 1420 up dev peer1            # 设置 peer1 设备的 MTU
[#] resolvconf -a tun.peer1 -m 0 -x              # 设置 peer1 设备的 DNS，确保 DNS 能够正常工作
[#] wg set peer1 fwmark 51820                    # 将 peer1 设备的防火墙标记设为 51820，用于标记 WireGuard 出网流量
                                                 # 该标记是一个 32bits 整数，后面 nft 表会用它追踪连接
[#] ip -4 route add 0.0.0.0/0 dev peer1 table 51820     # 创建单独的路由表 51820，默认将所有流量转发到 peer1 接口
[#] ip -4 rule add not fwmark 51820 table 51820         # 所有不带 51820 标记的流量（普通流量），都转发到前面新建的路由表 51820
                                                        # 也就是所有普通流量都转发到 peer1 接口
[#] ip -4 rule add table main suppress_prefixlength 0   # 流量全都走 main 路由表（即默认路由表），但是排除掉前缀长度（掩码） <= 0 的流量
                                                        # 掩码 <= 0 的只有 0.0.0.0/0，即默认路由。所以意思是所有非默认路由的流量都走 main 路由表（其实就是 wireguard 自己的出网流量）
[#] sysctl -q net.ipv4.conf.all.src_valid_mark=1        # 启用源地址有效性检查，用于防止伪造源地址
[#] nft -f /dev/fd/63                                   # 配置 nftables 规则，用于确保 WireGuard 流量能正确路由，并防止恶意数据包进入网络
```

跑完后我们现在确认下状态，应该是能正常走 WireGuard 访问相关网络了。

那么现在再检查下系统的网络状态，首先检查下默认路由表（main），应该是没任何变化：

```shell
# 如下命令等同于 ip route ls table main
ryan@ubuntu-2004-builder:~$ ip route ls
default via 192.168.5.201 dev eth0 proto static 
192.168.5.0/24 dev eth0 proto kernel scope link src 192.168.5.197 
```

但是我们的 WireGuard 隧道已经生效了，这就说明并不是所有流量都走默认路由表的，而是走了 WireGuard 的路由表。
前面的日志显示 WireGuard 的路由表名为 51820，我们来检查下这个表：

```shell
ryan@ubuntu-2004-builder:~$ ip route ls table 51820
default dev peer1 scope link
```

就能看到这个表确实是走到 WireGuard 的 peer1 接口了。

系统的流量是如何被转发到这个路由表的呢？实际这是由 Linux 路由策略数据库负责的，Linux 从 2.2 开始支持多路由表，并通过路由策略数据库来为每个数据包选择正确的路由表。我们来看下系统当前的路由策略：

```shell
ryan@ubuntu-2004-builder:~$ ip rule show
0:      from all lookup local                         # 0 是最高优先级，`all` 表示所有流量，`lookup local` 表示查找 local 路由表。
                                                      # local 是一个特殊路由表，包含对本地和广播地址的优先级控制路由。
32764:  from all lookup main suppress_prefixlength 0  # 32764 目前是第二优先级，将所有流量路由到　main 路由表，但是排除掉默认路由（前缀/掩码 <= 0）
                                                      # 这条规则前面实际解释过了，它是 wg-quick 在启动隧道时添加的规则。
32765:  not from all fwmark 0xca6c lookup 51820       # 所有不带 0xca6c 标记（51820 的 16 进制格式）的流量（普通流量），都走 51820 路由表
                                                      # 也就是都转发到 WireGuard peer1 接口。
                                                      # 这条规则是前面的 `ip -4 rule add not fwmark 51820 table 51820` 命令添加的。
                                                      # 而它所匹配的防火墙标记则是由前面的 `wg set peer1 fwmark 51820` 命令设置的。
32766:  from all lookup main                          # 所有流量都走 main 路由表，当前是不生效状态，因为前面的规则优先级更高。
                                                      # main 是系统的默认路由表，通常我们使用 ip route 命令都是在这个表上操作。
32767:  from all lookup default                       # 所有流量都走 default 路由表，当前同样是不生效状态。
                                                      # default 是一个系统生成的兜底路由表，默认不包含任何路由规则，可用于自定义路由策略，也可删除。
```

那么现在路由规则就理清楚了，那么 wg-quick 日志的最后一行 `nft -f /dev/fd/63` 到底做了什么呢？
它实际是设置了一些 nftables 规则，我们查看下它的规则内容：

```shell
ryan@ubuntu-2004-builder:~$ sudo nft list ruleset
table ip wg-quick-peer1 {
        chain preraw {
                type filter hook prerouting priority raw; policy accept;
                iifname != "peer1" ip daddr 10.13.13.2 fib saddr type != local drop
        }

        chain premangle {
                type filter hook prerouting priority mangle; policy accept;
                meta l4proto udp meta mark set ct mark
        }

        chain postmangle {
                type filter hook postrouting priority mangle; policy accept;
                meta l4proto udp meta mark 0x0000ca6c ct mark set meta mark
        }
}
```

可以看到 wg-quick 添加了一个 `wg-quick-peer1` 表，通过该表在 netfilter 上设置了如下规则：

>注意：nftables 的这个 chain 名称是完全自定义的，没啥特殊意义

1. `preraw` 链：此链用于防止恶意数据包进入网络。
   1. type 开头的一行是规则的类型，这里是 `filter`，仅匹配了 `raw` 链的 `prerouting` 表。
   2. 它丢弃掉所有来源接口不是 peer1、目的地址是 10.13.13.2、且源地址不是本地地址的数据包。
   3. 总结下就是只允许本地地址或者 peer1 直接访问 10.13.13.2 这个地址。
2. `premangle` 链：此链用于确保所有 UDP 数据包都能被正确从 WireGuard 接口入站。
   1. 它将所有 UDP 数据包的标记设置为连接跟踪标记（没搞懂这个标记是如何生效的....）。
3. `postmangle` 链：此链用于确保所有 UDP 数据包都能被正确从 WireGuard 接口出站。
   1. 它将所有 UDP 数据包的标记设置为 0xca6c（51820 的 16 进制格式）（同样没理解这个标记是如何生效的...）。

这些规则都是 wg-quick 在启动隧道时自动添加的，我们可以通过 `wg-quick down peer1` 命令来删除它们，这样网络就恢复了。

最后看下 WireGuard 的状态，它是前面 `wg setconf peer1 /dev/fd/63` 设置的：

```shell
ryan@ubuntu-2004-builder:~$ sudo wg show 
interface: peer1
  public key: HR8Kp3xWIt2rNdS3aaCk+Ss7yQqC9cn6h3WS6UK3WE0=
  private key: (hidden)
  listening port: 51820
  fwmark: 0xca6c

peer: t95vF4b11RLCId3ArVVIJoC5Ih9CNbI0VTNuDuEzZyw=
  preshared key: (hidden)
  endpoint: 192.168.5.198:51820
  allowed ips: 0.0.0.0/0
  latest handshake: 18 minutes, 59 seconds ago
  transfer: 124 B received, 324 B sent
```


#### 2. 服务端网络分析

首先查看下 wireguard 服务端容器的日志：

```bash
# ...
.:53                                    # 这几行日志是启动 CoreDNS，为虚拟网络提供默认的 DNS 服务
CoreDNS-1.10.1                          # 实际上 CoreDNS 不是必须的，客户端可以改用其他 DNS 服务器
linux/amd64, go1.20, 055b2c3
[#] ip link add wg0 type wireguard         # 创建一个 wireguard 设备
[#] wg setconf wg0 /dev/fd/63              # 设置 wireguard 设备的配置
[#] ip -4 address add 10.13.13.1 dev wg0   # 为 wireguard 设备添加一个 ip 地址
[#] ip link set mtu 1420 up dev wg0        # 设置 wireguard 设备的 mtu
[#] ip -4 route add 10.13.13.2/32 dev wg0  # 为 wireguard peer1 添加路由
[#] iptables -A FORWARD -i wg0 -j ACCEPT; iptables -A FORWARD -o wg0 -j ACCEPT; iptables -t nat -A POSTROUTING -o eth+ -j MASQUERADE
                                          # 为 wireguard 设备添加 iptables 规则
[ls.io-init] done.
```

能看到服务端的配置跟客户端有些不同，它没有添加额外的路由表跟路由表选择策略，是直接在默认路由表中添加了路由规则。

此外为了让 wireguard 设备可以访问外网，它添加了一些 iptables 规则，简单解释下：

- `iptables -A FORWARD -i wg0 -j ACCEPT; iptables -A FORWARD -o wg0 -j ACCEPT;`：允许进出 wg0 设备的数据包通过 netfilter 的 FORWARD 链（默认规则是 DROP，即默认是不允许通过的）
- `iptables -t nat -A POSTROUTING -o eth+ -j MASQUERADE`：在 eth+ 网卡上添加 MASQUERADE 规则，即将数据包的源地址伪装成 eth+ 网卡的地址，目的是为了允许 wireguard 的数据包通过 NAT 访问外部网络。
  - 而回来的流量会被 NAT 的 conntrack 链接追踪规则自动允许通过，不过 conntrack 表有自动清理机制，这就是为什么 wireguard 服务端需要添加 `PersistentKeepalive = 25` 的配置项，通过心跳包来保持 NAT 表的连接追踪。

#### 3. 动态修改 WireGuard 配置

首先登录到 wireguard 服务端容器中，确认当前状态：

```bash
root@5dcfebb0755d:/# wg
interface: wg0
  public key: t95vF4b11RLCId3ArVVIJoC5Ih9CNbI0VTNuDuEzZyw=
  private key: (hidden)
  listening port: 51820

peer: HR8Kp3xWIt2rNdS3aaCk+Ss7yQqC9cn6h3WS6UK3WE0=
  preshared key: (hidden)
  allowed ips: 10.13.13.2/32
```

现在调用下 wiregard-api 容器的接口，添加一个新的 peer：

```bash
# https://github.com/jamescun/wg-api
curl http://localhost:8182 -H "Content-Type: application/json" -d '{"jsonrpc": "2.0", "method": "AddPeer", "params": {"public_key": "xoY2MZZ1UmbEakFBPyqryHwTaMi6ae4myP+vuILmJUY=","allowed_ips": [ "10.1.1.0/24" ]}}'
```

再 check 下状态：

```shell
root@5dcfebb0755d:/# wg
interface: wg0
  public key: t95vF4b11RLCId3ArVVIJoC5Ih9CNbI0VTNuDuEzZyw=
  private key: (hidden)
  listening port: 51820

peer: HR8Kp3xWIt2rNdS3aaCk+Ss7yQqC9cn6h3WS6UK3WE0=
  preshared key: (hidden)
  allowed ips: 10.13.13.2/32

peer: xoY2MZZ1UmbEakFBPyqryHwTaMi6ae4myP+vuILmJUY=
  allowed ips: 10.1.1.0/24
```

可以看到 wireguard 服务端已经动态添加了一个新的 peer，现在再调个 API 动态删除该 peer:

```shell
curl 192.168.5.198:8182 -H "Content-Type: application/json" -d '{"jsonrpc": "2.0", "method": "RemovePeer", "params": {"public_key": "xoY2MZZ1UmbEakFBPyqryHwTaMi6ae4myP+vuILmJUY=","allowed_ips": [ "10.1.1.0/24" ]}}'
{"jsonrpc":"2.0","result":{"ok":true},"id":null}
```

配置就还原了：

```shell
root@5dcfebb0755d:/# wg
interface: wg0
  public key: t95vF4b11RLCId3ArVVIJoC5Ih9CNbI0VTNuDuEzZyw=
  private key: (hidden)
  listening port: 51820

peer: HR8Kp3xWIt2rNdS3aaCk+Ss7yQqC9cn6h3WS6UK3WE0=
  preshared key: (hidden)
  allowed ips: 10.13.13.2/32
```

这样就能实现动态增删改查 wireguard peer 了。


## 四、部署 VPN Server

Github 的 [vpn](https://github.com/topics/vpn) Topic 下有众多 VPN 项目，WireGuard/IPsec/OpenVPN 相关的解决方案如下：

- [trailofbits/algo](https://github.com/trailofbits/algo): 在云上部署安全的 WireGuard/IPsec VPN
- [hwdsl2/setup-ipsec-vpn](https://github.com/hwdsl2/setup-ipsec-vpn): 一套 shell 脚本，可快速部署 IPsec VPN
  - 此作者的 wireguard/openvpn 安装脚本同样很受欢迎
- [SoftEtherVPN](https://github.com/SoftEtherVPN/SoftEtherVPN): 一个多协议 VPN 解决方案，支持几乎所有流行的 VPN 协议（不支持 IKEv2，仅 master 版本支持 WireGuard）


由于 WireGuard 的流行，这里再列一下 [awesome-wireguard](https://github.com/cedrickchee/awesome-wireguard) Topic 下的相关项目：

- Mesh 网络
  - [headscale](https://github.com/juanfont/headscale): tailscale 控制服务器的开源实现，tailscale 是一套傻瓜式的 WireGuard VPN 私有网络解决方案。
  - [netbird](https://github.com/netbirdio/netbird): 又一个基于 WireGuard 的 VPN 平台
  - [firezone](https://github.com/firezone/firezone): 同上，不过是使用 Elixir 写的，而且完全容器化，支持通过 OIDC 登录。
- 官方与社区的 wireguard 用户空间实现，主要用在非 Linux 平台的 WireGuard 客户端中。
  - [boringtun](https://github.com/cloudflare/boringtun): CloudFalre 用 Rust 实现的用户空间 wireguard
  - [wireguard-go](https://github.com/WireGuard/wireguard-go): WireGuard 官方的用户空间实现，使用 Go
  - [wireguard-lwip](https://github.com/smartalock/wireguard-lwip): 为嵌入式设备实现的 WireGuard 协议
  - [WireGuard-ESP32-Arduino](https://github.com/ciniml/WireGuard-ESP32-Arduino): 在 ESP32 上跑 WireGuard 协议
- WireGuard 的 Web UI / Web API 封装
  - [wgctrl-go](https://github.com/WireGuard/wgctrl-go): 一个用于控制 WireGuard 虚拟接口的 Go 语言库。
  - [jamescun/wg-api](https://github.com/jamescun/wg-api)
  - [suquant/wgrest](https://github.com/suquant/wgrest)
  - [wireguard-manager-and-api](https://github.com/Mawthuq-Software/wireguard-manager-and-api)


