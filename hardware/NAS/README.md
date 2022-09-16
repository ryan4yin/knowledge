# NAS 系统

## 如何选择 NAS 系统？

物理机安装首选 OMV，因为它起码是个正经的 Linux 系统，各种拓展功能都可以直接跑 docker 实现。

OpenMediaVault 是目前比较流行的 NAS 系统，基于 Debian 系统，集成了 SMB/NFS/FTP 等常用的文件夹软件，并提供方便的 Web UI。
支持硬盘自动挂载、RAID、硬盘休眠、简单的系统监控等等。

其实这些功能也可以自己在 Debian 系统安装一大堆的程序来实现，但是程序太多，配置麻烦。
而且 SMB 之类的协议本来就很复杂，自己搭建绝对是非常折磨人的。

虚拟机安装，可以选择 FreeNAS，基于 FreeBSD，但是用户众多。
虽然用不了 Docker，但是 Docker 可以跑在别的虚拟机里面啊。

NAS 功能比较多，可能不适合容器化，或者容器化维护难度比较大。因此目前没看到有还在维护的容器版 OMV。

目前 NAS 系统推荐使用虚拟机方式部署。


## 参考文档

- [OpenMediaVault-Plugin-Developers/installScript](https://github.com/OpenMediaVault-Plugin-Developers/installScript)
- [树莓派 配置 OMV 5 搭建 NAS（一） 安装 OMV 5](https://www.cnblogs.com/Yogile/p/12577321.html)
- [OpenMediaVault (OMV) 切换国内源](https://zhuanlan.zhihu.com/p/138552148)
