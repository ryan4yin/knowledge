# Virtual Machine - 虚拟机

>虚拟机（Virtual Machine）指通过软件模拟的具有完整硬件系统功能的、运行在一个完全隔离环境中的完整计算机系统。

在很多场景下，我们都会需要用到虚拟机：

1. 测试、尝鲜新系统。
2. 完全隔离的沙箱环境，用于运行某些不安全的或者敏感的文件/程序。
3. 云服务商或企业会通过服务器虚拟化，提升服务器的利用率。
4. 虚拟机可以创建快照，系统环境可以随时还原到已有的快照，也能方便地拷贝给他人。（有点类似 docker 镜像，但是没有标准化的 dockerfile 定义文件）


## 桌面虚拟化软件

桌面虚拟化软件，就是提供 UI 界面的，使用很方便的虚拟化软件。通常直接安装在个人的桌面 PC 上。

1. [VMware Workstation](https://www.vmware.com/products/workstation-pro/workstation-pro-evaluation.html): 闭源收费软件，但是网上许可证一大堆。
2. [VirtualBox](https://www.virtualbox.org/): 免费开源，但是 UI 没 VMware 好看。


## 服务器虚拟化 - Hypervisor

服务器虚拟化软件，也叫 Hypervisor——虚拟机管理程序，有时也称做 Virtual Machine Monitor(VMM)，它可以在宿主机上创建并管理多个虚拟机。
目前比较流行的 Hypervisor 有：

1. [vShpere Hypervisor](https://www.vmware.com/cn/products/vsphere-hypervisor.html): 也就是 ESXi，这是一个闭源收费的服务器虚拟化系统。基于 Linux，可直接安装在物理机上。
   1. 优点是简单方便，但是收费。适合中小企业，或者个人搭着玩。
   2. 成熟稳定，用户众多。但是各大云服务提供商全都用 KVM 做了自己的虚拟化平台，因为免费且自主可控。
   3. ESXi 搭配 vCenter 可以中心化地管理 ESXi 集群，搭配 terraform/python sdk 可以实现虚拟机的自动化创建等功能。
2. [ProxmoxVE](https://pve.proxmox.com/wiki/Main_Page): 一个开源免费的服务器虚拟化系统，基于 Debian + QEMU/KVM + LXC.
   1. 体验和 ESXi 基本一致，但是开源免费。
   2. 适合个人使用。或者搭测试环境
3. KVM: 直接搞 KVM，有一定难度。适合进阶用户，或者大厂自己 DIY。
