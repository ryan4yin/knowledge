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

从图中也很容易看出，如果数据 dst ip 不是本机任一接口的 ip，那它通过的几个链依次是：PREROUTEING -> FORWARD -> POSTROUTING

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
- 其他类型，可以用到的时候再查

理解了上面这张图，以及四个表的用途，就很容易理解 iptables 的命令了。

## 常用命令

>**注意**: 下面提供的 iptables 命令做的修改是未持久化的，重启就会丢失！在下一节会简单介绍持久化配置的方法。

命令格式：
```shell
iptables [-t table] {-A|-C|-D} chain [-m matchname [per-match-options]] -j targetname [per-target-options]
```

其中 table 默认为 `filter` 表，但是感觉系统管理员实际使用最多的是 INPUT 表，用于设置防火墙。

以下简单介绍在 INPUT 表上添加、修改规则，来设置防火墙：

```shell
# --add 允许 80 端口通过
iptables -A INPUT -p tcp --dport 80 -j ACCEPT

# --list-rules 查看所有规则
iptables -S

# --list-rules 查看 INPUT 表中的所有规则
iptables -S INPUT
# 查看 iptables 中的所有规则（比 -L 更详细）

# ---delete 通过编号删除规则
iptables -D 1
# 或者通过完整的规则参数来删除规则
iptables -D INPUT -p tcp --dport 80 -j ACCEPT

# --replace 通过编号来替换规则内容
iptables -R INPUT 1 -s 192.168.0.1 -j DROP

# --insert 在指定的位置插入规则，可类比链表的插入
iptables -I INPUT 1 -p tcp --dport 80 -j ACCEPT

# 在匹配条件前面使用感叹号表示取反
# 如下规则表示接受所有来自 docker0，但是目标接口不是 docker0 的流量
iptables -A FORWARD -i docker0 ! -o docker0 -j ACCEPT

# --policy 设置某个链的默认规则
# 很多系统管理员会习惯将连接公网的服务器，默认规则设为 DROP，提升安全性，避免错误地开放了端口。
# 但是也要注意，默认规则设为 DROP 前，一定要先把允许 ssh 端口的规则加上，否则就尴尬了。
iptables -P INPUT DROP

# --flush 清空 INPUT 表上的所有规则
iptables -F INPUT
```


## 如何持久化 iptables 配置

首先需要注意的是，centos7/opensuse 15 都已经切换到了 firewalld 作为防火墙配置软件，
而 ubuntu18.04 lts 也换成了 ufw 来配置防火墙。

包括 docker 应该也是在启动的时候动态添加 iptables 配置。

对于上述新系统，还是建议直接使用 firewalld/ufw 配置防火墙吧，或者网上搜下关闭 ufw/firewalld、启用 iptables 持久化的解决方案。

本文主要目的在于理解 docker 容器网络的原理，以及为后面理解 kubernetes 网络插件 calico/flannel 打好基础，因此就不多介绍持久化了。

## Docker 如何使用 iptables + 虚拟网络接口实现容器网络

### 通过 docker run 运行容器

首先，使用 `docker run` 运行一个容器，检查下网络状况：

```shell
# 运行一个 debian 容器和一个 nginx
❯ docker run -dit --name debian --rm debian:buster sleep 1000000
❯ docker run -dit --name nginx --rm nginx:1.19-alpine 

#　查看网络接口
❯ ip addr ls
...
5: docker0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc noqueue state UP group default 
    link/ether 02:42:42:c7:12:ba brd ff:ff:ff:ff:ff:ff
    inet 172.17.0.1/16 brd 172.17.255.255 scope global docker0
       valid_lft forever preferred_lft forever
    inet6 fe80::42:42ff:fec7:12ba/64 scope link 
       valid_lft forever preferred_lft forever
56: veth4d4c1c2@if55: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc noqueue master docker0 state UP group default 
    link/ether 3e:3d:5c:6f:c3:d9 brd ff:ff:ff:ff:ff:ff link-netnsid 0
    inet6 fe80::3c3d:5cff:fe6f:c3d9/64 scope link 
       valid_lft forever preferred_lft forever
58: vethc0863a0@if57: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc noqueue master docker0 state UP group default 
    link/ether 3a:58:1b:8f:45:70 brd ff:ff:ff:ff:ff:ff link-netnsid 1
    inet6 fe80::3858:1bff:fe8f:4570/64 scope link 
       valid_lft forever preferred_lft forever

# 查看路由规则
❯ ip route ls
default via 192.168.31.1 dev wlp4s0 proto dhcp metric 600
#下列路由规则将 `172.17.0.0/16` 网段的所有流量转发到 docker0
172.17.0.0/16 dev docker0 proto kernel scope link src 172.17.0.1 linkdown 
192.168.31.0/24 dev wlp4s0 proto kernel scope link src 192.168.31.228 metric 600 

# 查看　iptables 规则
# NAT 表
❯ sudo iptables -t nat -S
-P PREROUTING ACCEPT
-P INPUT ACCEPT
-P OUTPUT ACCEPT
-P POSTROUTING ACCEPT
-N DOCKER
# 所有目的地址在本机的，都先交给 DOCKER 链处理一波
-A PREROUTING -m addrtype --dst-type LOCAL -j DOCKER
-A OUTPUT ! -d 127.0.0.0/8 -m addrtype --dst-type LOCAL -j DOCKER
# （容器访问外部网络）所有出口不为 docker0 的流量，都做下 SNAT，把 src ip 换成出口接口的 ip 地址
-A POSTROUTING -s 172.17.0.0/16 ! -o docker0 -j MASQUERADE
-A DOCKER -i docker0 -j RETURN

# filter 表
❯ sudo iptables -t filter -S
-P INPUT ACCEPT
-P FORWARD DROP
-P OUTPUT ACCEPT
-N DOCKER
-N DOCKER-ISOLATION-STAGE-1
-N DOCKER-ISOLATION-STAGE-2
-N DOCKER-USER
# 所有流量都必须先经过如下两个表处理，没问题才能继续往下走
-A FORWARD -j DOCKER-ISOLATION-STAGE-1
-A FORWARD -j DOCKER-USER
# （容器访问外部网络）出去的流量走了 MASQUERADE，回来的流量会被 conntrack 做 DNAT
# 这里直接 ACCEPT 被 conntrack 识别到的流量
-A FORWARD -o docker0 -m conntrack --ctstate RELATED,ESTABLISHED -j ACCEPT
# 将所有访问 docker0 的流量都转给自定义链 DOCKER 处理
-A FORWARD -o docker0 -j DOCKER
# 允许所有来自 docker0 的流量通过，不论下一跳是否是 docker0
-A FORWARD -i docker0 ! -o docker0 -j ACCEPT
-A FORWARD -i docker0 -o docker0 -j ACCEPT
# 下面三个表目前啥规则也没有，就是简单的 RETURN，交给后面的表继续处理
-A DOCKER-ISOLATION-STAGE-1 -j RETURN
-A DOCKER-ISOLATION-STAGE-2 -j RETURN
-A DOCKER-USER -j RETURN
```


接下来使用如下 docker-compose 配置启动一个 caddy　容器，添加自定义 network 和端口映射，待会就能验证 docker 是如何实现这两种网络的了。

`docker-compose.yml` 内容：

```yaml
version: "3.3"
services:
  caddy:
    image: "caddy:2.2.1-alpine"
    container_name: "caddy"
    restart: always
    command: caddy file-server --browse --root /data/static
    ports:
      - "8081:80"
    volumes:
      - "/home/ryan/Downloads:/data/static"
    networks:
    - caddy-1

networks:
  caddy-1:
```


## nftables

前面介绍了 iptables 以及其在 docker 和防火墙上的应用。但是实际上目前各大 Linux 发行版都已经不建议使用 iptables 了，甚至把 iptables 重命名为了 `iptables-leagacy`.

目前 opensuse/debian/opensuse 都已经预装了并且推荐使用 nftables，**而且 firewalld 已经默认使用 nftables 作为它的后端了**。

我在 opensuse tumbleweed 上实测，firewalld 添加的是 nftables 配置，而 docker 仍然在用旧的 iptables，也就是说我现在的机器上有两套 netfilter 工具并存：

```
# 查看 iptables 数据
> iptables -S
-P INPUT ACCEPT
-P FORWARD DROP
-P OUTPUT ACCEPT
-N DOCKER
-N DOCKER-ISOLATION-STAGE-1
-N DOCKER-ISOLATION-STAGE-2
-N DOCKER-USER
-A FORWARD -j DOCKER-ISOLATION-STAGE-1
-A FORWARD -o br-e3fbbb7a1b3a -m conntrack --ctstate RELATED,ESTABLISHED -j ACCEPT
-A FORWARD -o br-e3fbbb7a1b3a -j DOCKER
...

# 确认下是否使用了 nftables 的兼容层，结果提示请我使用 iptables-legacy
> iptables-nft -S
# Warning: iptables-legacy tables present, use iptables-legacy to see them
-P INPUT ACCEPT
-P FORWARD ACCEPT
-P OUTPUT ACCEPT

# 查看 nftables 规则，能看到三张 firewalld 生成的 table
> nft list ruleset
table inet firewalld {
    ...
}
table ip firewalld {
    ...
}
table ip6 firewalld {
    ...
}
```

但是现在 kubernetes/docker 都还是用的 iptables，nftables 我学了用处不大，以后有空再补充。


## 参考

- [iptables详解（1）：iptables概念](https://www.zsythink.net/archives/1199)
- [How to confirm that SNAT and MASQUERADE are using conntrack table to replace the destination IP address of the reply packet](http://fosshelp.blogspot.com/2014/07/how-to-confirm-that-snat-and-masquerade.html)
