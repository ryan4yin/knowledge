# NAS 系统 - OpenMediaVault

## 如何选择 NAS 系统？

目前开源领域主要就两个 NAS 系统：

- [TrueNAS](https://github.com/truenas)
    - 它基于 FreeBSD，使用 ZFS 文件系统，支持横向扩容，用户众多，自称全世界用户量第一。
    - 缺点是比较吃性能，要求至少 2C 8G 资源
- OpenMediaVault
  - 也是目前比较流行的 NAS 系统，基于 Debian 系统，比 TrueNAS 要轻量些。
  - 集成了 SMB/NFS/FTP 等常用的文件夹软件，并提供方便的 Web UI。支持硬盘自动挂载、RAID、硬盘休眠、简单的系统监控等等。

其实 NAS 的这些功能也可以自己在 Debian 系统安装一大堆的程序来实现，但是程序太多，配置麻烦。而且 SMB 之类的协议本来就很复杂，自己搭建还是挺折磨人的。

NAS 功能比较多，可能不适合容器化，或者容器化维护难度比较大。因此目前没看到有还在维护的容器版 OMV。
目前 NAS 系统推荐使用虚拟机方式部署。


## Windows Server

2022/11/27 更新，我在想是否直接使用 windows server 提供 SMB/ISCSI 服务，才是最正确的开箱方式？
因为发现 OMV 的 iscsi 服务性能太差了。
