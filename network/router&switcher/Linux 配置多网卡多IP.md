# Linux 配置多网卡多 IP

很多的服务器都提供多个网口，自然就会有多个 IP 地址，多个网口可以让服务器同时连接到多个网段中，比如同时访问内网和外网。
但是服务器的默认网关(Default Gateway)只能有一个，这会导致所有的流量都会从默认网关出去，无法利用上多网口。

## 默认网关介绍

网关，是具有路由功能的设备（路由器）的 IP 地址，负责跨网段的数据包路由，属于网络层的控制平面。它本身必须和主机在同一网段内。

服务器的默认网关，其实就是一条动态添加的默认路由，通过如下命令查看：

```shell
ryan@RYAN-MI-DESKTOP:~$ ip route | column -t
default          via  172.23.112.1  dev    eth0
172.23.112.0/20  dev  eth0          proto  kernel  scope  link  src  172.23.116.40
```

上面输出的第一行就是默认网关生成的路由，第一列是目标 IP 地址(dest ip)，`default` 也可写成 `0.0.0.0/0`，能匹配任何 IP 地址。

路由表是根据优先级进行路由的，我们将外网设为默认网关，然后再配置静态路由让内网流量走内网，这样就大功告成了。

>其实这就是路由器的工作模式，路由器就是有多个网口（甚至包括 WIFI），通过路由表、防火墙、NAT 等策略进行数据的增删查改与路由。

## 一、修改各网口的配置文件

以 CentOS7+双网口为例，进入 `/etc/sysconfig/network-scripts`，修改其中的 `ifcfg-enp2s0` 和 `ifcfg-enp5s0` 两个配置文件：

```conf
# ifcfg-enp2s0
TYPE=Ethernet
PROXY_METHOD=none
BROWSER_ONLY=no
BOOTPROTO=static  # 设为静态
DEFROUTE=yes
IPV4_FAILURE_FATAL=no
IPV6INIT=no
IPV6_AUTOCONF=yes
IPV6_DEFROUTE=yes
IPV6_FAILURE_FATAL=no
IPV6_ADDR_GEN_MODE=stable-privacy
NAME=enp2s0
UUID=b5123cac-593f-45634-c27a-6781a663e0a9
DEVICE=enp2s0
ONBOOT=yes
# 添加如下内容：
IPADDR=192.168.1.66  # 静态 IP
PREFIX=24             # 网段
# GATEWAY=192.168.1.1  # 默认网关只能有一个，改用公网网关，因此必须注释掉这一行！
DNS1=192.168.1.33  # 内网 DNS 服务器
DNS2=114.114.114.114  # 没啥用的公网服务器
```

```conf
# ifcfg-enp5s0
# 此网口连接网络供应商提供的固定 IP 宽带
TYPE=Ethernet
PROXY_METHOD=none
BROWSER_ONLY=no
BOOTPROTO=static
DEFROUTE=yes
IPV4_FAILURE_FATAL=no
IPV6INIT=no
IPV6_AUTOCONF=yes
IPV6_DEFROUTE=yes
IPV6_FAILURE_FATAL=no
IPV6_ADDR_GEN_MODE=stable-privacy
NAME=enp5s0
UUID=c43a39c1-bc1a-3b1h-7dc1-402a94531add
DEVICE=enp5s0
# 下面的 xx 请替换成网络供应商提供的内容。
IPADDR=xxx.xxx.xxx.xxx
PREFIX=xx
GATEWAY=xxx.xxx.xxx.xxx  # 以公网网关为默认网关
ONBOOT=yes
```

然后重启 netweork，应该就可以通过默认网关访问公网了：

```shell
systemctl restart network
ping zhihu.com
```

## 二、添加静态路由

上一步配置完成后，我们所有的流量都会走公网，内网仍然无法访问。
现在需要手动添加静态路由，让内网的流量走内网网口。

先查看路由，可看到有两个网段，默认网关为公网 IP：

```shell
$ ip route | column -t
default            via  xxx.xxx.xxx.xxx  dev    enp5s0  proto  static  metric  101
192.168.1.0/24     dev  enp2s0          proto  kernel  scope  link    src     192.168.1.66    metric  100
xxx.xxx.xxx.xxx/27  dev  enp5s0          proto  kernel  scope  link    src     xxx.xxx.xxx.xxx  metric  101
```

现在添加一条静态路由：

```shell
# 添加一条临时的静态路由（重启失效）
$ ip route add 192.168.0.0/16 via 192.168.1.1 dev enp2s0
```

这样所有访问 `192.168.0.0/16` 网段的流量就都会走 `192.168.1.1` 这个网关了。

测试没有问题后，可以将这条静态路由写入配置 `/etc/sysconfig/network-scripts/route-<interface-name>` 中，使永久生效：

```shell
# /etc/sysconfig/network-scripts/route-enp2s0
192.168.0.0/16 via 192.168.1.1
```

然后重启网络适配器，静态路由就永久生效了：

```shell
systemctl restart network
```

