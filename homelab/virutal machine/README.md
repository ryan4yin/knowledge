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
3. QEMU/KVM: 用 qemu/kvm+virt-manager 做桌面虚拟化，性能是最好的，但是有一定门槛，适合专业人员。
    - 它没有做到像 vmware/virtualbox 那样简单易懂，有一定学习门槛。
    - 深入使用，需要熟悉 libvirtd 的命令行和 xml.


## 服务器虚拟化 - Hypervisor

服务器虚拟化软件，也叫 Hypervisor——虚拟机管理程序，有时也称做 Virtual Machine Monitor(VMM)，它可以在宿主机上创建并管理多个虚拟机。
目前比较流行的 Hypervisor 有：

1. [vShpere Hypervisor](https://www.vmware.com/cn/products/vsphere-hypervisor.html): 也就是 ESXi，这是一个闭源收费的服务器虚拟化系统。基于 Linux，可直接安装在物理机上。
   1. 优点是简单方便，但是收费。适合中小企业，或者个人搭着玩。
   2. 成熟稳定，用户众多。但是各大云服务提供商全都用 KVM 做了自己的虚拟化平台，因为免费且自主可控。
   3. ESXi 搭配 vCenter 可以中心化地管理 ESXi 集群，搭配 terraform/python sdk 可以实现虚拟机的自动化创建等功能。
2. [ProxmoxVE](https://pve.proxmox.com/wiki/Main_Page): 一个开源免费的服务器虚拟化系统，基于 Debian + QEMU/KVM + LXC.
   1. PVE 开源免费，而 VMware 的全套技术都是闭源收费的
   2. PVE 底层是 QEMU/KVM，存储方案也是 Ceph/iSCSI/NFS/LVM 这些都是使用很广泛的开源技术，对提升个人及公司的技术能力有很大帮助。
   3. PVE 支持 cloudinit，这是一个虚拟机的预配置工具，可以用于预配置网络、磁盘扩容、设置 hostname 等，非常方便！
   5. 文档齐全，而且很接地气，还包含许多 QEMU/KVM/CEPH/Cloudinit 等开源技术的内容。 反观 VMware 的文档，真的是写得烂得一批，不知所云，随便找篇博客都要比官方文档好理解得多。
   4. 提供一套方便的 CLI 工具，以及 RESTful API。不论是 CLI 还是 HTTP API/Python SDK 都比 vmware 先进很多。VMware 的 python sdk 真的是超级难用，印象深刻。
   6. 缺点在于，PVE 的 WebUI 功能不全，有些功能必须通过命令行才能实现。（这和路由器类似，高级功能只有 CLI 支持）

3. KVM+OpenStack: 难度较高(openstack 我还没用过)。适合进阶用户，或者大厂自己 DIY。


## 虚拟机集群管理 - OpenStack

OpenStack 与虚拟机的关系，和 Kubernetes 与容器的关系一样。

OpenStack 管理虚拟机集群，底层的虚拟化可以是 ESXi，也可以是 KVM.

Kubernetes 管理容器集群，它底层的容器化可以由 Docker 提供，也可以使用 cri-o

## 超融合基础设施(Hyper-Converged Infrasturcture)

超融合=计算虚拟化+网络虚拟化+分布式存储，它和传统的虚拟化软件最大的不同是：分布式存储。

超融合对存储的一些要求：

- 软件定义 – 解除硬件绑定，可通过升级拓展更丰富的功能，自动化能力高
- 全分布式架构 - 扩展性好，消除单点故障风险
- 高可靠性 - 智能的故障恢复功能，丰富的数据保护手段
- 高性能 – 支持多种存储介质，充分挖掘和利用新式硬件的性能
- 高度融合 – 架构简单并易于管理

超融合架构可以降低私有云的构建与维护难度，让私有云的使用维护和公有云一样简单。
超融合架构下，虚拟机的计算和存储是完全高可用的：计算资源能智能动态更换，存储也是分布式存储，底层计算和存储也可以很简单的扩缩容。

相关开源产品：

- [rancher/harvester](https://github.com/rancher/harvester): Rancher 开源的基于 kubernetes 的超融合平台。

超融合架构的核心——分布式存储，要求必须使用万兆以太网(10GbE/25GbE)+SSD存储，否则性能肯定不够。

## 参考

- [KVM 虚拟化环境搭建 - ProxmoxVE](https://zhuanlan.zhihu.com/p/49118355)
- [KVM 虚拟化环境搭建 - WebVirtMgr](https://zhuanlan.zhihu.com/p/49120559)

