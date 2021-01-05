Bugs
---



## can’t lock file ‘/var/lock/qemu-server/lock-xxx.conf’ – got timeout

PVE 虚拟机卡在 BIOS 系统引导这一步，无法启动，也无法关机/强制关机/重置！

解决方法：手动删除掉 lockfile: `/var/lock/qemu-server/lock-xxx.conf`

因为虚拟机还卡在 BIOS 引导这一步，删除掉 lockfile 再关闭虚拟机并不会导致数据丢失。


## 克隆创建的虚拟机，卡在 `Booting from Hard Disk...` 状态

被用做模板的虚拟机可以正常启动，但是克隆的虚拟机就卡住了。

可能的原因：

1. 磁盘有问题，出这个问题的 cloud image 是 `ubuntu-20.10-server-cloudimg-amd64.img`，我更换成 `ubuntu-20.10-server-cloudimg-amd64-disk-kvm.img` 就没问题了。
   1. 磁盘镜像均下载自 https://cloud-images.ubuntu.com/releases/groovy/release-20201210/
2. BIOS 不匹配：将 BIOS 从 SeaBIOS 切换到 UEFI

