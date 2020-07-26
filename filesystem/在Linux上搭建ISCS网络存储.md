# 在Linux上搭建ISCS网络存储

iSCSI是一种使用TCP/IP协议，在现有IP网络上传输SCSI协议数据的工业标准。
而 SCSI 本来是一个计算机和外部设备之间的通用接口标准。

简单解释：SCSI 是计算机和硬盘之间的接口标准（就像 SATA/M.2 一样），而 iSCSI 则将这个接口标准移植到了 TCP/IP 网络之上，使计算机和存储设备可以通过 TCP/IP 网络连接。

>而 SMB/NFS 是更高层的协议，它们构建在文件系统之上。

## 用途

1. 分布式数据存储：ceph 就提供 iscsi 协议支持，可以将分布式存储挂载到主机/容器内。
2. 中心存储：各大网吧的无盘系统，应该都有利用到 iscsi。
3. 个人娱乐：可以将 steam/gog 的游戏都下载到 iscsi 磁盘中，而影音资源则通过 SMB/串流等方式提供。

## iSCSI 介绍

包含两个组件：

1. 服务端（iSCSI Target）：也就是提供实际存储资源的服务器。
   1. iSCSI LUN: 指具体的存储资源（可理解成硬盘），一个服务端可以提供多个 LUN。
   2. Linux 服务端：linux 上 iscsi 的标准实现是 [ISCSI/LIO](https://wiki.archlinux.org/index.php/ISCSI/LIO) 
2. 客户端（iSCSI initiator）：客户端将服务端的存储资源挂载到本机上。
   1. Windows10 自带 iscsi 客户端。
   2. Linux 客户端：`apt install open-iscsi`


## 在 Debian 上运行 ISCSI/LIO

待续

## 参考

- [iSCSI存储系统知识](https://www.cnblogs.com/chris-cp/p/6022383.html)
