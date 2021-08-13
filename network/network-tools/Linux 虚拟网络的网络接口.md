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
#include <linux/if.h>
#include <linux/if_tun.h>

#include <sys/ioctl.h>

#include <fcntl.h>
#include <string.h>

#include <unistd.h>
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

更复杂的 tun 程序，可以参考

- [simpletun](https://github.com/gregnietsky/simpletun)
- [marywangran/simpletun](https://github.com/marywangran/simpletun)
- [tun go 语言版](https://github.com/marywangran/gotun-tunnel/blob/main/tun/tun.go)

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

以 qemu-kvm 为例，在虚拟机的桥接模式下，qemu-kvm 会为每个虚拟机创建一个 tun/tap 虚拟网卡并连接到 br0 网桥。
虚拟机内部的网络接口 `eth0` 是 qemu-kvm 软件模拟的，实际上虚拟机内网络数据的收发都会被 qemu-kvm 转换成对 `/dev/net/tun` 的读写。

以发送数据为例，整个流程如下：

- 虚拟机发出去的数据包先到达 qemu-kvm 程序
- 数据被用户层程序 qemu-kvm 写入到 `/dev/net/tun`，到达 tap 设备
- tap 设备把数据传送到 br0 网桥
- br0 把数据交给 eth0 发送出去

整个流程跑完，数据包都不需要经过宿主机的协议栈，效率高。

```
+------------------------------------------------+-----------------------------------+-----------------------------------+
|                       Host                     |           VirtualMachine1         |           VirtualMachine2         |
|                                                |                                   |                                   |
|    +--------------------------------------+    |    +-------------------------+    |    +-------------------------+    |
|    |         Network Protocol Stack       |    |    |  Network Protocol Stack |    |    |  Network Protocol Stack |    |
|    +--------------------------------------+    |    +-------------------------+    |    +-------------------------+    |
|                       ↑                        |                ↑                  |                 ↑                 |
|.......................|........................|................|..................|.................|.................|
|                       ↓                        |                ↓                  |                 ↓                 |
|                  +--------+                    |            +-------+              |             +-------+             |
|                  | .3.101 |                    |            | .3.102|              |             | .3.103|             |
|     +------+     +--------+     +-------+      |            +-------+              |             +-------+             |
|     | eth0 |<--->|   br0  |<--->|tun/tap|      |            | eth0  |              |             | eth0  |             |
|     +------+     +--------+     +-------+      |            +-------+              |             +-------+             |
|         ↑             ↑             ↑      +--------+           ↑                  |                 ↑                 |
|         |             |             +------|qemu-kvm|-----------+                  |                 |                 |
|         |             ↓                    +--------+                              |                 |                 |
|         |         +-------+                    |                                   |                 |                 |
|         |         |tun/tap|                    |                                   |                 |                 |
|         |         +-------+                    |                                   |                 |                 |
|         |             ↑                        |            +--------+             |                 |                 |
|         |             +-------------------------------------|qemu-kvm|-------------|-----------------+                 |
|         |                                      |            +--------+             |                                   |
|         |                                      |                                   |                                   |
+---------|--------------------------------------+-----------------------------------+----------------------------------
     Physical Network  (192.168.3.0/24)
```

#### 跨 namespace 通信场景（容器网络，NAT 模式）

由于容器运行在自己单独的 network namespace 里面，所以和虚拟机一样，它们也都有自己单独的协议栈。

容器网络的结构和虚拟机差不多，但是它改用了 NAT 网络，并把 tun/tap 换成了 veth，导致 br0 过来的数据，要先经过宿主机协议栈，然后才进入 veth 接口。

多了一层 NAT，以及多走了一层宿主机协议栈，都会导致性能下降。

示意图如下：

```
+-----------------------------------------------+-----------------------------------+-----------------------------------+
|                      Host                     |           Container 1             |           Container 2             |
|                                               |                                   |                                   |
|   +---------------------------------------+   |    +-------------------------+    |    +-------------------------+    |
|   |       Network Protocol Stack          |   |    |  Network Protocol Stack |    |    |  Network Protocol Stack |    |
|   +---------------------------------------+   |    +-------------------------+    |    +-------------------------+    |
|        ↑             ↑                        |                ↑                  |                 ↑                 |
|........|.............|........................|................|..................|.................|.................|
|        ↓             ↓                        |                ↓                  |                 ↓                 |
|    +------+     +--------+                    |          +-------------+          |           +-------------+         |
|    |.3.101|     |  .9.1  |                    |          |    .9.2     |          |           |    .9.3     |         |
|    +------+     +--------+     +-------+      |          +-------------+          |           +-------------+         |
|    | eth0 |     |   br0  |<--->|  veth |      |          | eth0(veth)  |          |           | eth0(veth)  |         |
|    +------+     +--------+     +-------+      |          +-------------+          |           +-------------+         |
|        ↑             ↑             ↑          |                ↑                  |                 ↑                 |
|        |             |             +---------------------------+                  |                 |                 |
|        |             ↓                        |                                   |                 |                 |
|        |         +-------+                    |                                   |                 |                 |
|        |         |  veth |                    |                                   |                 |                 |
|        |         +-------+                    |                                   |                 |                 |
|        |             ↑                        |                                   |                 |                 |
|        |             +------------------------------------------------------------|-----------------+                 |
|        |                                      |                                   |                                   |
|        |                                      |                                   |                                   |
+--------|--------------------------------------+-----------------------------------+-----------------------------------+
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


## 其他虚拟网络接口的类型

除了上面介绍的这些，Linux 还支持 VLAN、VXLAN 等类型的虚拟网络接口，可通过 `ip link help` 查看，因为用的不多，这里就不介绍了。


## 虚拟网络接口的速率

Loopback 和本章讲到的其他虚拟网络接口一样，都是一种软件模拟的网络设备。
他们的速率是不是也像物理链路一样，存在链路层（比如以太网）的带宽限制呢？

比如目前很多老旧的网络设备，都是只支持到百兆以太网，这就决定了它的带宽上限。
即使是较新的设备，目前基本也都只支持到千兆，也就是 1GbE，那本文提到的虚拟网络接口单纯在本机内部通信，是否也存在这样的制约呢？是否也只能跑到 1GbE?

使用 ethtool 检查：

```
# docker 容器的 veth 接口速率
> ethtool vethe899841 | grep Speed
        Speed: 10000Mb/s

# 网桥看起来没有固定的速率
> ethtool docker0 | grep Speed
        Speed: Unknown!

# tun0 设备的默认速率貌似是 10MB/s ?
> ethtool tun0 | grep Speed
        Speed: 10Mb/s

# 此外 ethtool 无法检查 lo 以及 wifi 的速率
```

### 网络性能实测

接下来实际测试一下，先给出机器参数：

```
❯ cat /etc/os-release 
NAME="openSUSE Tumbleweed"
# VERSION="20210810"
...

❯ uname -a
Linux legion-book 5.13.8-1-default #1 SMP Thu Aug 5 08:56:22 UTC 2021 (967c6a8) x86_64 x86_64 x86_64 GNU/Linux


❯ lscpu
Architecture:                    x86_64
CPU(s):                          16
Model name:                      AMD Ryzen 7 5800H with Radeon Graphics
...

❯ lsmem
RANGE                                  SIZE  STATE REMOVABLE  BLOCK
0x0000000000000000-0x00000000cfffffff  3.3G online       yes   0-25
0x0000000100000000-0x000000072fffffff 24.8G online       yes 32-229

Memory block size:       128M
Total online memory:      28G
Total offline memory:      0B
```

使用 iperf3 测试：

```shell
# 服务端
iperf3 -s

-------------
# 客户端通过 loopback 接口访问 iperf3-server，大概 49Gbits/s
❯ iperf3 -c 127.0.0.1
Connecting to host 127.0.0.1, port 5201
[  5] local 127.0.0.1 port 48656 connected to 127.0.0.1 port 5201
[ ID] Interval           Transfer     Bitrate         Retr  Cwnd
[  5]   0.00-1.00   sec  4.46 GBytes  38.3 Gbits/sec    0   1.62 MBytes       
[  5]   1.00-2.00   sec  4.61 GBytes  39.6 Gbits/sec    0   1.62 MBytes       
[  5]   2.00-3.00   sec  5.69 GBytes  48.9 Gbits/sec    0   1.62 MBytes       
[  5]   3.00-4.00   sec  6.11 GBytes  52.5 Gbits/sec    0   1.62 MBytes       
[  5]   4.00-5.00   sec  6.04 GBytes  51.9 Gbits/sec    0   1.62 MBytes       
[  5]   5.00-6.00   sec  6.05 GBytes  52.0 Gbits/sec    0   1.62 MBytes       
[  5]   6.00-7.00   sec  6.01 GBytes  51.6 Gbits/sec    0   1.62 MBytes       
[  5]   7.00-8.00   sec  6.05 GBytes  52.0 Gbits/sec    0   1.62 MBytes       
[  5]   8.00-9.00   sec  6.34 GBytes  54.5 Gbits/sec    0   1.62 MBytes       
[  5]   9.00-10.00  sec  5.91 GBytes  50.8 Gbits/sec    0   1.62 MBytes       
- - - - - - - - - - - - - - - - - - - - - - - - -
[ ID] Interval           Transfer     Bitrate         Retr
[  5]   0.00-10.00  sec  57.3 GBytes  49.2 Gbits/sec    0             sender
[  5]   0.00-10.00  sec  57.3 GBytes  49.2 Gbits/sec                  receiver

# 客户端通过 wlp4s0 wifi 网卡(192.168.31.228)访问 iperf3-server，实际还是走的本机，但是速度要比 loopback 快一点，可能是默认设置的问题
❯ iperf3 -c 192.168.31.228
Connecting to host 192.168.31.228, port 5201
[  5] local 192.168.31.228 port 43430 connected to 192.168.31.228 port 5201
[ ID] Interval           Transfer     Bitrate         Retr  Cwnd
[  5]   0.00-1.00   sec  5.12 GBytes  43.9 Gbits/sec    0   1.25 MBytes       
[  5]   1.00-2.00   sec  5.29 GBytes  45.5 Gbits/sec    0   1.25 MBytes       
[  5]   2.00-3.00   sec  5.92 GBytes  50.9 Gbits/sec    0   1.25 MBytes       
[  5]   3.00-4.00   sec  6.00 GBytes  51.5 Gbits/sec    0   1.25 MBytes       
[  5]   4.00-5.00   sec  5.98 GBytes  51.4 Gbits/sec    0   1.25 MBytes       
[  5]   5.00-6.00   sec  6.05 GBytes  52.0 Gbits/sec    0   1.25 MBytes       
[  5]   6.00-7.00   sec  6.16 GBytes  52.9 Gbits/sec    0   1.25 MBytes       
[  5]   7.00-8.00   sec  6.08 GBytes  52.2 Gbits/sec    0   1.25 MBytes       
[  5]   8.00-9.00   sec  6.00 GBytes  51.6 Gbits/sec    0   1.25 MBytes       
[  5]   9.00-10.00  sec  6.01 GBytes  51.6 Gbits/sec    0   1.25 MBytes       
- - - - - - - - - - - - - - - - - - - - - - - - -
[ ID] Interval           Transfer     Bitrate         Retr
[  5]   0.00-10.00  sec  58.6 GBytes  50.3 Gbits/sec    0             sender
[  5]   0.00-10.00  sec  58.6 GBytes  50.3 Gbits/sec                  receiver

# 从容器中访问宿主机的 iperf3-server，速度几乎没区别
❯ docker run  -it --rm --name=iperf3-server networkstatic/iperf3 -c 192.168.31.228
Connecting to host 192.168.31.228, port 5201
[  5] local 172.17.0.2 port 43436 connected to 192.168.31.228 port 5201
[ ID] Interval           Transfer     Bitrate         Retr  Cwnd
[  5]   0.00-1.00   sec  4.49 GBytes  38.5 Gbits/sec    0    403 KBytes       
[  5]   1.00-2.00   sec  5.31 GBytes  45.6 Gbits/sec    0    544 KBytes       
[  5]   2.00-3.00   sec  6.14 GBytes  52.8 Gbits/sec    0    544 KBytes       
[  5]   3.00-4.00   sec  5.85 GBytes  50.3 Gbits/sec    0    544 KBytes       
[  5]   4.00-5.00   sec  6.14 GBytes  52.7 Gbits/sec    0    544 KBytes       
[  5]   5.00-6.00   sec  5.99 GBytes  51.5 Gbits/sec    0    544 KBytes       
[  5]   6.00-7.00   sec  5.86 GBytes  50.4 Gbits/sec    0    544 KBytes       
[  5]   7.00-8.00   sec  6.05 GBytes  52.0 Gbits/sec    0    544 KBytes       
[  5]   8.00-9.00   sec  5.99 GBytes  51.5 Gbits/sec    0    544 KBytes       
[  5]   9.00-10.00  sec  6.12 GBytes  52.5 Gbits/sec    0    544 KBytes       
- - - - - - - - - - - - - - - - - - - - - - - - -
[ ID] Interval           Transfer     Bitrate         Retr
[  5]   0.00-10.00  sec  58.0 GBytes  49.8 Gbits/sec    0             sender
[  5]   0.00-10.00  sec  58.0 GBytes  49.8 Gbits/sec                  receiver
```

把 iperf3-server 跑在容器里再测一遍：

```shell
# 在容器中启动 iperf3-server，并映射到宿主机端口 6201
> docker run  -it --rm --name=iperf3-server -p 6201:5201 networkstatic/iperf3 -s

-----------------------------
# 测试容器之间互访的速度，ip 为 iperf3-server 的容器 ip，速度要慢一些。
# 毕竟过了 veth -> veth -> docker0 -> veth -> veth 五层虚拟网络接口
❯ docker run  -it --rm networkstatic/iperf3 -c 172.17.0.2
Connecting to host 172.17.0.2, port 5201
[  5] local 172.17.0.3 port 40776 connected to 172.17.0.2 port 5201
[ ID] Interval           Transfer     Bitrate         Retr  Cwnd
[  5]   0.00-1.00   sec  4.74 GBytes  40.7 Gbits/sec    0    600 KBytes       
[  5]   1.00-2.00   sec  4.48 GBytes  38.5 Gbits/sec    0    600 KBytes       
[  5]   2.00-3.00   sec  5.38 GBytes  46.2 Gbits/sec    0    600 KBytes       
[  5]   3.00-4.00   sec  5.39 GBytes  46.3 Gbits/sec    0    600 KBytes       
[  5]   4.00-5.00   sec  5.42 GBytes  46.6 Gbits/sec    0    600 KBytes       
[  5]   5.00-6.00   sec  5.39 GBytes  46.3 Gbits/sec    0    600 KBytes       
[  5]   6.00-7.00   sec  5.38 GBytes  46.2 Gbits/sec    0    635 KBytes       
[  5]   7.00-8.00   sec  5.37 GBytes  46.1 Gbits/sec    0    667 KBytes       
[  5]   8.00-9.00   sec  6.01 GBytes  51.7 Gbits/sec    0    735 KBytes       
[  5]   9.00-10.00  sec  5.74 GBytes  49.3 Gbits/sec    0    735 KBytes       
- - - - - - - - - - - - - - - - - - - - - - - - -
[ ID] Interval           Transfer     Bitrate         Retr
[  5]   0.00-10.00  sec  53.3 GBytes  45.8 Gbits/sec    0             sender
[  5]   0.00-10.00  sec  53.3 GBytes  45.8 Gbits/sec                  receiver

# 本机直接访问容器 ip，走的是 docker0 网桥，居然还挺快
❯ iperf3 -c 172.17.0.2
Connecting to host 172.17.0.2, port 5201
[  5] local 172.17.0.1 port 56486 connected to 172.17.0.2 port 5201
[ ID] Interval           Transfer     Bitrate         Retr  Cwnd
[  5]   0.00-1.00   sec  5.01 GBytes  43.0 Gbits/sec    0    632 KBytes       
[  5]   1.00-2.00   sec  5.19 GBytes  44.6 Gbits/sec    0    703 KBytes       
[  5]   2.00-3.00   sec  6.46 GBytes  55.5 Gbits/sec    0    789 KBytes       
[  5]   3.00-4.00   sec  6.80 GBytes  58.4 Gbits/sec    0    789 KBytes       
[  5]   4.00-5.00   sec  6.82 GBytes  58.6 Gbits/sec    0    913 KBytes       
[  5]   5.00-6.00   sec  6.79 GBytes  58.3 Gbits/sec    0   1007 KBytes       
[  5]   6.00-7.00   sec  6.63 GBytes  56.9 Gbits/sec    0   1.04 MBytes       
[  5]   7.00-8.00   sec  6.75 GBytes  58.0 Gbits/sec    0   1.04 MBytes       
[  5]   8.00-9.00   sec  6.19 GBytes  53.2 Gbits/sec    0   1.04 MBytes       
[  5]   9.00-10.00  sec  6.55 GBytes  56.3 Gbits/sec    0   1.04 MBytes       
- - - - - - - - - - - - - - - - - - - - - - - - -
[ ID] Interval           Transfer     Bitrate         Retr
[  5]   0.00-10.00  sec  63.2 GBytes  54.3 Gbits/sec    0             sender
[  5]   0.00-10.00  sec  63.2 GBytes  54.3 Gbits/sec                  receiver

# 如果走本机 loopback 地址 + 容器端口映射，速度就慢了好多
# 或许是因为用 iptables 做端口映射导致的？
❯ iperf3 -c 127.0.0.1 -p 6201
Connecting to host 127.0.0.1, port 6201
[  5] local 127.0.0.1 port 48862 connected to 127.0.0.1 port 6201
[ ID] Interval           Transfer     Bitrate         Retr  Cwnd
[  5]   0.00-1.00   sec  2.71 GBytes  23.3 Gbits/sec    0   1.37 MBytes       
[  5]   1.00-2.00   sec  3.64 GBytes  31.3 Gbits/sec    0   1.37 MBytes       
[  5]   2.00-3.00   sec  4.08 GBytes  35.0 Gbits/sec    0   1.37 MBytes       
[  5]   3.00-4.00   sec  3.49 GBytes  30.0 Gbits/sec    0   1.37 MBytes       
[  5]   4.00-5.00   sec  5.50 GBytes  47.2 Gbits/sec    2   1.37 MBytes       
[  5]   5.00-6.00   sec  4.06 GBytes  34.9 Gbits/sec    0   1.37 MBytes       
[  5]   6.00-7.00   sec  4.12 GBytes  35.4 Gbits/sec    0   1.37 MBytes       
[  5]   7.00-8.00   sec  3.99 GBytes  34.3 Gbits/sec    0   1.37 MBytes       
[  5]   8.00-9.00   sec  3.49 GBytes  30.0 Gbits/sec    0   1.37 MBytes       
[  5]   9.00-10.00  sec  5.51 GBytes  47.3 Gbits/sec    0   1.37 MBytes       
- - - - - - - - - - - - - - - - - - - - - - - - -
[ ID] Interval           Transfer     Bitrate         Retr
[  5]   0.00-10.00  sec  40.6 GBytes  34.9 Gbits/sec    2             sender
[  5]   0.00-10.00  sec  40.6 GBytes  34.9 Gbits/sec                  receiver

# 可走 wlp4s0 + 容器端口映射，速度也不慢啊
❯ iperf3 -c 192.168.31.228 -p 6201
Connecting to host 192.168.31.228, port 6201
[  5] local 192.168.31.228 port 54582 connected to 192.168.31.228 port 6201
[ ID] Interval           Transfer     Bitrate         Retr  Cwnd
[  5]   0.00-1.00   sec  4.34 GBytes  37.3 Gbits/sec    0    795 KBytes       
[  5]   1.00-2.00   sec  4.78 GBytes  41.0 Gbits/sec    0    834 KBytes       
[  5]   2.00-3.00   sec  6.26 GBytes  53.7 Gbits/sec    0    834 KBytes       
[  5]   3.00-4.00   sec  6.30 GBytes  54.1 Gbits/sec    0    875 KBytes       
[  5]   4.00-5.00   sec  6.26 GBytes  53.8 Gbits/sec    0    875 KBytes       
[  5]   5.00-6.00   sec  5.75 GBytes  49.4 Gbits/sec    0    875 KBytes       
[  5]   6.00-7.00   sec  5.49 GBytes  47.2 Gbits/sec    0    966 KBytes       
[  5]   7.00-8.00   sec  5.72 GBytes  49.1 Gbits/sec    2    966 KBytes       
[  5]   8.00-9.00   sec  4.81 GBytes  41.3 Gbits/sec    2    966 KBytes       
[  5]   9.00-10.00  sec  5.98 GBytes  51.4 Gbits/sec    0    966 KBytes       
- - - - - - - - - - - - - - - - - - - - - - - - -
[ ID] Interval           Transfer     Bitrate         Retr
[  5]   0.00-10.00  sec  55.7 GBytes  47.8 Gbits/sec    4             sender
[  5]   0.00-10.00  sec  55.7 GBytes  47.8 Gbits/sec                  receiver
```

总的来看，loopback、bridge、veth 这几个接口基本上是没被限速的，veth 有查到上限为 10000Mb/s（10Gb/s） 感觉也是个假数字，
实际上测出来的数据基本在 35Gb/s 到 55Gb/s 之间，视情况浮动。

性能的变化和虚拟网络设备的链路和类型有关，或许和默认配置的区别也有关系。

另外 TUN 设备这里没有测，`ethtool tun0` 查到的值是比较离谱的 10Mb/s，但是感觉不太可能这么慢，有时间可以再测一波看看。

## 参考

- [Linux虚拟网络设备之tun/tap](https://segmentfault.com/a/1190000009249039)
- [Linux虚拟网络设备之veth](https://segmentfault.com/a/1190000009251098)
- [云计算底层技术-虚拟网络设备(Bridge,VLAN)](https://opengers.github.io/openstack/openstack-base-virtual-network-devices-bridge-and-vlan/)
- [云计算底层技术-虚拟网络设备(tun/tap,veth)](https://opengers.github.io/openstack/openstack-base-virtual-network-devices-tuntap-veth/)
- [Universal TUN/TAP device driver - Kernel Docs](https://www.kernel.org/doc/Documentation/networking/tuntap.txt)
- [Tun/Tap interface tutorial](https://backreference.org/2010/03/26/tuntap-interface-tutorial/)
- [Linux Loopback performance with TCP_NODELAY enabled](https://stackoverflow.com/questions/5832308/linux-loopback-performance-with-tcp-nodelay-enabled)

