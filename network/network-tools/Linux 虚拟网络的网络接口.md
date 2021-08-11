## Linux 虚拟网络的网络接口

>本文大量文字或者代码示例均来自参考文章，通俗的说我就是复制粘贴了一遍...并且自己实际作了些实验。

Linux 具有强大的虚拟网络能力，这也是虚拟机和容器的虚拟网络基础。

这里介绍 Linux 常用的虚拟网络接口类型，网络接口类型的列表可以通过 `ip link help` 查看。

### 1. tun/tap 虚拟网络接口

tun/tap 是操作系统内核中的虚拟网络设备，他们为用户层程序提供数据的接收与传输。

普通的物理网络接口如 eth0，它的两端分别是内核协议栈和外面的物理网络。

而对于 TUN/TAP 虚拟接口如 tun0，它的一端一定是连接的用户层程序，另一端则视配置方式的不同而变化，可以直连内核协议栈，也可以是某个 bridge（后面会介绍）。
Linux 通过内核模块 TUN 提供 tun/tap 功能，该模块提供了一个设备接口 `/dev/net/tun` 供用户层程序读写，用户层程序通过 `/dev/net/tun` 读写主机内核协议栈的数据。

```
> modinfo tun
filename:       /lib/modules/5.13.6-1-default/kernel/drivers/net/tun.ko.xz
alias:          devname:net/tun
alias:          char-major-10-200
license:        GPL
author:         (C) 1999-2004 Max Krasnyansky <maxk@qualcomm.com>
description:    Universal TUN/TAP device driver
...

> ls /dev/net/tun
/dev/net/tun
```

一个 TUN 设备的示例图如下：

```
+----------------------------------------------------------------+
|                                                                |
|  +--------------------+      +--------------------+            |
|  | User Application A |      | User Application B |<-----+     |
|  +--------------------+      +--------------------+      |     |
|               | 1                    | 5                 |     |
|...............|......................|...................|.....|
|               ↓                      ↓                   |     |
|         +----------+           +----------+              |     |
|         | socket A |           | socket B |              |     |
|         +----------+           +----------+              |     |
|                 | 2               | 6                    |     |
|.................|.................|......................|.....|
|                 ↓                 ↓                      |     |
|             +------------------------+       +--------------+  |
|             | Network Protocol Stack |       | /dev/net/tun |  |
|             +------------------------+       +--------------+  |
|                | 7                 | 3                   |     |
|................|...................|.....................|.....|
|                ↓                   ↓                     |     |
|        +----------------+    +----------------+        4 |     |
|        |      eth0      |    |      tun0      |          |     |
|        +----------------+    +----------------+          |     |
|    10.32.0.11  |                   |   192.168.3.11      |     |
|                | 8                 +---------------------+     |
|                |                                               |
+----------------|-----------------------------------------------+
                 ↓
         Physical Network
```

因为 TUN/TAP 设备的一端是内核协议栈，显然流入 tun0 的数据包是先经过本地的路由规则匹配的。

路由匹配成功，数据包被发送到 tun0 后，tun0 发现另一端是通过 `/dev/net/tun` 连接到应用程序 B，就会将数据丢给应用程序 B。

应用程序对数据包进行处理后，可能会构造新的数据包，通过物理网卡发送出去。比如常见的 VPN 程序就是把原来的数据包封装/加密一遍，再发送给 VPN 服务器。

#### C 语言编程测试 TUN 设备

为了使用 tun/tap 设备，用户层程序需要通过系统调用打开 `/dev/net/tun` 获得一个读写该设备的文件描述符(FD)，并且调用 `ioctl()` 向内核注册一个 TUN 或 TAP 类型的虚拟网卡(实例化一个 tun/tap 设备)，其名称可能是 `tun0/tap0` 等。

此后，用户程序可以通过该 TUN/TAP 虚拟网卡与主机内核协议栈（或者其他网络设备）交互。当用户层程序关闭后，其注册的 TUN/TAP 虚拟网卡以及路由表相关条目(使用 tun 可能需要手动添加路由表条目)都会被内核释放。

可以把用户层程序看做是网络上另一台主机，他们通过 tun/tap 虚拟网卡相连。

一个简单的 C 程序示例如下，它每次收到数据后，都只单纯地打印一下收到的字节数：

```c
#include <net/if.h>
#include <linux/if_tun.h>

#include <sys/ioctl.h>
#include <sys/stat.h>
#include <sys/types.h>

#include <fcntl.h>
#include <string.h>

#include<stdlib.h>
#include<stdio.h>

int tun_alloc(int flags)
{

    struct ifreq ifr;
    int fd, err;
    char *clonedev = "/dev/net/tun";

    // 打开 tun 文件，获得 fd
    if ((fd = open(clonedev, O_RDWR)) < 0) {
        return fd;
    }

    memset(&ifr, 0, sizeof(ifr));
    ifr.ifr_flags = flags;

    // 向内核注册一个 TUN 网卡，并与前面拿到的 fd 关联起来
    // 程序关闭时，注册的 tun 网卡及自动生成的相关路由策略，会被自动释放
    if ((err = ioctl(fd, TUNSETIFF, (void *) &ifr)) < 0) {
        close(fd);
        return err;
    }

    printf("Open tun/tap device: %s for reading...\n", ifr.ifr_name);

    return fd;
}

int main()
{

    int tun_fd, nread;
    char buffer[1500];

    /* Flags: IFF_TUN   - TUN device (no Ethernet headers)
     *        IFF_TAP   - TAP device
     *        IFF_NO_PI - Do not provide packet information
     */
    tun_fd = tun_alloc(IFF_TUN | IFF_NO_PI);

    if (tun_fd < 0) {
        perror("Allocating interface");
        exit(1);
    }

    while (1) {
        nread = read(tun_fd, buffer, sizeof(buffer));
        if (nread < 0) {
            perror("Reading from interface");
            close(tun_fd);
            exit(1);
        }

        printf("Read %d bytes from tun/tap device\n", nread);
    }
    return 0;
}
```

接下来开启三个终端窗口来测试上述程序，分别运行上面的 tun 程序、tcpdump 和 iproute2 指令。

首先通过编译运行上述 c 程序，程序会阻塞住，等待数据到达：
```
# 编译，请忽略部分 warning
> gcc mytun.c -o mytun

# 创建并监听 tun 设备需要 root 权限
> sudo mytun 
Open tun/tap device: tun0 for reading...
```

现在使用 iproute2 查看下链路层设备：

```
# 能发现最后面有列出名为 tun0 的接口，但是状态为 down
❯ ip addr ls
......
3: wlp4s0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc noqueue state UP group default qlen 1000
    link/ether c0:3c:59:36:a4:16 brd ff:ff:ff:ff:ff:ff
    inet 192.168.31.228/24 brd 192.168.31.255 scope global dynamic noprefixroute wlp4s0
       valid_lft 41010sec preferred_lft 41010sec
    inet6 fe80::4ab0:130f:423b:5d37/64 scope link noprefixroute 
       valid_lft forever preferred_lft forever
7: tun0: <POINTOPOINT,MULTICAST,NOARP> mtu 1500 qdisc noop state DOWN group default qlen 500
    link/none 

# 为 tun0 设置 ip 地址，注意不要和其他接口在同一网段，会导致路由冲突
> sudo ip addr add 172.21.22.23/24 dev tun0
# 启动 tun0 这个接口，这一步会自动向路由表中添加将 172.21.22.23/24 路由到 tun0 的策略
> sudo ip link set tun0 up
#确认上一步添加的路由策略是否存在
❯ ip route ls
default via 192.168.31.1 dev wlp4s0 proto dhcp metric 600 
172.17.0.0/16 dev docker0 proto kernel scope link src 172.17.0.1 linkdown 
172.21.22.0/24 dev tun0 proto kernel scope link src 172.21.22.23 
192.168.31.0/24 dev wlp4s0 proto kernel scope link src 192.168.31.228 metric 600 

# 此时再查看接口，发现 tun0 状态为 unknown
> ip addr ls
......
8: tun0: <POINTOPOINT,MULTICAST,NOARP,UP,LOWER_UP> mtu 1500 qdisc pfifo_fast state UNKNOWN group default qlen 500
    link/none 
    inet 172.21.22.23/24 scope global tun0
       valid_lft forever preferred_lft forever
    inet6 fe80::3d52:49b5:1cf3:38fd/64 scope link stable-privacy 
       valid_lft forever preferred_lft forever

# 使用 tcpdump 尝试抓下 tun0 的数据，会阻塞在这里，等待数据到达
> tcpdump -i tun0
```

现在再启动第三个窗口发点数据给 tun0，持续观察前面 `tcpdump` 和 `mytun` 的日志:
```
# 直接 ping tun0 的地址，貌似有问题，数据没进 mytun 程序，而且还有响应
❯ ping -c 4 172.21.22.23
PING 172.21.22.23 (172.21.22.23) 56(84) bytes of data.
64 bytes from 172.21.22.23: icmp_seq=1 ttl=64 time=0.167 ms
64 bytes from 172.21.22.23: icmp_seq=2 ttl=64 time=0.180 ms
64 bytes from 172.21.22.23: icmp_seq=3 ttl=64 time=0.126 ms
64 bytes from 172.21.22.23: icmp_seq=4 ttl=64 time=0.141 ms

--- 172.21.22.23 ping statistics ---
4 packets transmitted, 4 received, 0% packet loss, time 3060ms
rtt min/avg/max/mdev = 0.126/0.153/0.180/0.021 ms

# 但是 ping 该网段下的其他地址，流量就会被转发给 mytun 程序，因为 mytun 啥数据也没回，自然丢包率 100%
# tcpdump 和 mytun 都会打印出相关日志
❯ ping -c 4 172.21.22.26
PING 172.21.22.26 (172.21.22.26) 56(84) bytes of data.

--- 172.21.22.26 ping statistics ---
4 packets transmitted, 0 received, 100% packet loss, time 3055ms
```

下面给出 mytun 的输出：

```
Read 84 bytes from tun/tap device
Read 84 bytes from tun/tap device
Read 84 bytes from tun/tap device
Read 84 bytes from tun/tap device
```

以及 tcpdump 的输出：

```
00:22:03.622684 IP (tos 0x0, ttl 64, id 37341, offset 0, flags [DF], proto ICMP (1), length 84)
    172.21.22.23 > 172.21.22.26: ICMP echo request, id 11, seq 1, length 64
00:22:04.633394 IP (tos 0x0, ttl 64, id 37522, offset 0, flags [DF], proto ICMP (1), length 84)
    172.21.22.23 > 172.21.22.26: ICMP echo request, id 11, seq 2, length 64
00:22:05.653356 IP (tos 0x0, ttl 64, id 37637, offset 0, flags [DF], proto ICMP (1), length 84)
    172.21.22.23 > 172.21.22.26: ICMP echo request, id 11, seq 3, length 64
00:22:06.677341 IP (tos 0x0, ttl 64, id 37667, offset 0, flags [DF], proto ICMP (1), length 84)
    172.21.22.23 > 172.21.22.26: ICMP echo request, id 11, seq 4, length 64
```

#### TUN 与 TAP 的区别

TUN 和 TAP 的区别在于工作的网络层次不同，用户程序通过 TUN 设备只能读写网络层的 IP 数据包，而 TAP 设备则支持读写链路层的数据包（通常是以太网数据包，带有 Ethernet headers）。

TUN 与 TAP 的关系，就类似于 socket 和 raw socket.

TUN/TAP 应用最多的场景是 VPN 代理，比如:

- [clash](https://github.com/Dreamacro/clash)
- [mellow](https://github.com/mellow-io/mellow)


### 2. veth

veth 接口总是成对出现，一对 veth 接口就类似一根网线，从一端进来的数据会从另一端出去。

其主要作用就是连接不同的网络接口，比如在容器网络中，用于将容器的 namespace 与 root namespace 的 br0 相连。（后面会介绍这种连接场景）

同时 veth 又是一个虚拟网络接口，因此它和 TUN/TAP 或者其他物理网络接口一样，也都能配置 mac/ip 地址（但是并不是一定得配 mac/ip 地址）。

### 3. bridge

Linux Bridge 是工作在链路层的网络交换机，由 Linux 内核模块 `brige` 提供，它负责在所有连接到它的接口之间转发链路层数据包。

添加到 Bridge 上的设备被设置为只接受二层数据帧并且转发所有收到的数据包到 Bridge 中。
在 Bridge 中会进行一个类似物理交换机的查MAC端口映射表、转发、更新MAC端口映射表这样的处理逻辑，从而数据包可以被转发到另一个接口/丢弃/广播/发往上层协议栈，由此 Bridge 实现了数据转发的功能。

如果使用 tcpdump 在 Bridge 接口上抓包，可以抓到网桥上所有接口进出的包，因为这些数据包都要通过网桥进行转发。

与物理交换机不同的是，Bridge 本身可以设置 IP 地址，可以认为当使用 `brctl addbr br0` 新建一个 br0 网桥时，系统自动创建了一个同名的隐藏 `br0` 网络接口。`br0` 一旦设置 IP 地址，就意味着这个隐藏的 br0 接口可以作为路由接口设备，参与 IP 层的路由选择(可以使用 `route -n` 查看最后一列 `Iface`)。因此只有当 `br0` 设置 `IP` 地址时，Bridge 才有可能将数据包发往上层协议栈。

但被添加到 Bridge 上的网卡是不能配置 IP 地址的，他们工作在数据链路层，对路由系统不可见。


它常被用于在虚拟机、主机上不同的 namepsaces 之间转发数据。

#### 虚拟机场景（桥接模式）

虚拟机通过tun/tap或者其它类似的虚拟网络设备，将虚拟机内的网卡同 br0 连接起来，这样就达到和真实交换机一样的效果。

虚拟机发出去的数据包先到达 br0，然后由 br0 交给 eth0 发送出去，数据包都不需要经过宿主机的协议栈，效率高。

```
+----------------------------------------------------------------+-----------------------------------------+-----------------------------------------+
|                          Host                                  |              VirtualMachine1            |              VirtualMachine2            |
|                                                                |                                         |                                         |
|       +------------------------------------------------+       |       +-------------------------+       |       +-------------------------+       |
|       |             Network Protocol Stack             |       |       |  Network Protocol Stack |       |       |  Network Protocol Stack |       |
|       +------------------------------------------------+       |       +-------------------------+       |       +-------------------------+       |
|                          ↑                                     |                   ↑                     |                    ↑                    |
|..........................|.....................................|...................|.....................|....................|....................|
|                          ↓                                     |                   ↓                     |                    ↓                    |
|                     +--------+                                 |               +-------+                 |                +-------+                |
|                     | .3.101 |                                 |               | .3.102|                 |                | .3.103|                |
|        +------+     +--------+     +-------+                   |               +-------+                 |                +-------+                |
|        | eth0 |<--->|   br0  |<--->|tun/tap|                   |               | eth0  |                 |                | eth0  |                |
|        +------+     +--------+     +-------+                   |               +-------+                 |                +-------+                |
|            ↑             ↑             ↑                       |                   ↑                     |                    ↑                    |
|            |             |             +-------------------------------------------+                     |                    |                    |
|            |             ↓                                     |                                         |                    |                    |
|            |         +-------+                                 |                                         |                    |                    |
|            |         |tun/tap|                                 |                                         |                    |                    |
|            |         +-------+                                 |                                         |                    |                    |
|            |             ↑                                     |                                         |                    |                    |
|            |             +-------------------------------------------------------------------------------|--------------------+                    |
|            |                                                   |                                         |                                         |
|            |                                                   |                                         |                                         |
|            |                                                   |                                         |                                         |
+------------|---------------------------------------------------+-----------------------------------------+-----------------------------------------+
             ↓
     Physical Network  (192.168.3.0/24)
```

#### 跨 namespace 通信场景（容器网络，NAT 模式）

由于容器运行在自己单独的 network namespace 里面，所以和虚拟机一样，它们也都有自己单独的协议栈。

容器网络的结构和虚拟机差不多，但是它改用了 NAT 网络，并把 tun/tap 换成了 veth，导致 br0 过来的数据，要先经过宿主机协议栈，然后才进入 veth 接口。

多了一层 NAT，以及多走了一层宿主机协议栈，都会导致性能下降。

示意图如下：

```
+----------------------------------------------------------------+-----------------------------------------+-----------------------------------------+
|                          Host                                  |              Container 1                |              Container 2                |
|                                                                |                                         |                                         |
|       +------------------------------------------------+       |       +-------------------------+       |       +-------------------------+       |
|       |             Network Protocol Stack             |       |       |  Network Protocol Stack |       |       |  Network Protocol Stack |       |
|       +------------------------------------------------+       |       +-------------------------+       |       +-------------------------+       |
|            ↑             ↑                                     |                   ↑                     |                    ↑                    |
|............|.............|.....................................|...................|.....................|....................|....................|
|            ↓             ↓                                     |                   ↓                     |                    ↓                    |
|        +------+     +--------+                                 |               +-------+                 |                +-------+                |
|        |.3.101|     |  .9.1  |                                 |               |  .9.2 |                 |                |  .9.3 |                |
|        +------+     +--------+     +-------+                   |               +-------+                 |                +-------+                |
|        | eth0 |     |   br0  |<--->|  veth |                   |               | eth0  |                 |                | eth0  |                |
|        +------+     +--------+     +-------+                   |               +-------+                 |                +-------+                |
|            ↑             ↑             ↑                       |                   ↑                     |                    ↑                    |
|            |             |             +-------------------------------------------+                     |                    |                    |
|            |             ↓                                     |                                         |                    |                    |
|            |         +-------+                                 |                                         |                    |                    |
|            |         |  veth |                                 |                                         |                    |                    |
|            |         +-------+                                 |                                         |                    |                    |
|            |             ↑                                     |                                         |                    |                    |
|            |             +-------------------------------------------------------------------------------|--------------------+                    |
|            |                                                   |                                         |                                         |
|            |                                                   |                                         |                                         |
|            |                                                   |                                         |                                         |
+------------|---------------------------------------------------+-----------------------------------------+-----------------------------------------+
             ↓
     Physical Network  (192.168.3.0/24)
```

每创建一个新容器，都会在容器的 namespace 里新建一个 veth 接口并命令为 eth0，同时在主 namespace 创建一个 veth，将容器的 eth0 与 br0 连接。

可以在容器中通过 iproute2 查看到， eth0 的接口类型为 `veth`：

```shell
❯ docker run -it --rm debian:buster bash
root@5facbe4ddc1e:/# ip --details addr ls
1: lo: <LOOPBACK,UP,LOWER_UP> mtu 65536 qdisc noqueue state UNKNOWN group default qlen 1000
    link/loopback 00:00:00:00:00:00 brd 00:00:00:00:00:00 promiscuity 0 minmtu 0 maxmtu 0 numtxqueues 1 numrxqueues 1 gso_max_size 65536 gso_max_segs 65535 
    inet 127.0.0.1/8 scope host lo
       valid_lft forever preferred_lft forever
20: eth0@if21: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc noqueue state UP group default 
    link/ether 02:42:ac:11:00:02 brd ff:ff:ff:ff:ff:ff link-netnsid 0 promiscuity 0 minmtu 68 maxmtu 65535 
    veth numtxqueues 1 numrxqueues 1 gso_max_size 65536 gso_max_segs 65535 
    inet 172.17.0.2/16 brd 172.17.255.255 scope global eth0
       valid_lft forever preferred_lft forever
```

同时在宿主机中能看到对应的 veth 设备是绑定到了 docker0 的：

```shell
❯ sudo brctl show
bridge name     bridge id               STP enabled     interfaces
docker0         8000.0242fce99ef5       no              vethea4171a
```

## 参考

- [Linux虚拟网络设备之tun/tap](https://segmentfault.com/a/1190000009249039)
- [Linux虚拟网络设备之veth](https://segmentfault.com/a/1190000009251098)
- [云计算底层技术-虚拟网络设备(Bridge,VLAN)](https://opengers.github.io/openstack/openstack-base-virtual-network-devices-bridge-and-vlan/)
- [云计算底层技术-虚拟网络设备(tun/tap,veth)](https://opengers.github.io/openstack/openstack-base-virtual-network-devices-tuntap-veth/)
- [Universal TUN/TAP device driver - Kernel Docs](https://www.kernel.org/doc/Documentation/networking/tuntap.txt)
- [Tun/Tap interface tutorial](https://backreference.org/2010/03/26/tuntap-interface-tutorial/)
