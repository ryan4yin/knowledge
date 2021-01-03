QEMU/KVM 虚拟化
---

QEMU/KVM 是目前最流行的服务器虚拟化技术，
它基于 Linux 内核提供的 kvm 模块，结构精简，性能损失小，而且开源免费（对比收费的 vmware），因此成了大部分企业的首选虚拟化方案。

目前各大云厂商的虚拟化方案，底层都是 KVM。

目前最流行的开源服务器虚拟化方案，是基于 KVM 的 Proxmox,而闭源的服务器虚拟化方案则是 VMware 全家桶。


## 一、安装 QUEU/KVM

QEMU/KVM 环境需要安装很多的组件，它们各司其职：

1. qemu: 模拟各类输入输出设备（网卡、磁盘、USB端口等）
    - qemu 底层使用 kvm 模拟 CPU 和 RAM，比软件模拟的方式快很多。
1. libvirt: 提供简单且统一的工具和 API，用于管理虚拟机，屏蔽了底层的复杂结构。（支持 qemu-kvm/virtualbox/vmware）
1. ovmf: 为虚拟机启用 UEFI 支持
1. virt-manager: 用于管理虚拟机的 GUI 界面（可以管理远程 kvm 主机）。
2. virt-viewer: 通过 GUI 界面直接与虚拟机交互（可以管理远程 kvm 主机）。
3. dnsmasq vde2 bridge-utils openbsd-netcat: 网络相关组件，提供了以太网虚拟化、网络桥接、NAT网络等虚拟网络功能。
    - dnsmasq 提供了 NAT 虚拟网络的 DHCP 及 DNS 解析功能。
    - vde2: 以太网虚拟化
    - bridge-utils: 顾名思义，提供网络桥接相关的工具。
    - openbsd-netcat: TCP/IP 的瑞士军刀，详见 [/network/network-tools/socat 和 netcat](/network/network-tools/socat%20和%20netcat.md)，这里不清楚是哪个网络组件会用到它。


安装命令：

```shell
# archlinux/manjaro
sudo pacman -S qemu virt-manager virt-viewer dnsmasq vde2 bridge-utils openbsd-netcat

# ubuntu,参考了官方文档，但未测试
sudo apt install qemu-kvm libvirt-daemon-system virt-manager virt-viewer virtinst bridge-utils

# centos,参考了官方文档，但未测试
sudo yum groupinstall "Virtualization Host"
sudo yum install virt-manager virt-viewer virt-install

# opensuse
# see: https://doc.opensuse.org/documentation/leap/virtualization/html/book-virt/cha-vt-installation.html
sudo yast2 virtualization
# enter to terminal ui, select kvm + kvm tools, and then install it.
```

完了还需要安装 ebtables/iptables，这两个工具也是用来做网络虚拟化的。
了解 docker 的应该知道，docker 就是使用 iptables 实现的容器虚拟网络。



### 1. libguestfs - 虚拟机磁盘映像处理工具

[libguestfs](https://libguestfs.org/) 是一个虚拟机磁盘映像处理工具，可用于直接修改/查看/虚拟机映像、转换映像格式等。


它提供的命令列表如下：

1. `virt-df centos.img`: 查看硬盘使用情况
2. `virt-ls centos.img /`: 列出目录文件
3. `virt-copy-out -d domain /etc/passwd /tmp`：在虚拟映像中执行文件复制
4. `virt-list-filesystems /file/xx.img`：查看文件系统信息
5. `virt-list-partitions /file/xx.img`：查看分区信息
6. `guestmount -a /file/xx.qcow2(raw/qcow2都支持) -m /dev/VolGroup/lv_root --rw /mnt`：直接将分区挂载到宿主机
7. `guestfish`: 交互式 shell，可运行上述所有命令。 
8. `virt-v2v`: 将其他格式的虚拟机(比如 ova) 转换成 kvm 虚拟机。
9. `virt-p2v`: 将一台物理机转换成虚拟机。


安装命令：


```shell
# archlinux/manjaro
sudo pacman -S libguestfs

# opensuse
sudo zypper install libguestfs

# ubuntu
sudo apt install libguestfs-tools

# centos
sudo yum install libguestfs-tools
```

### 2. 启动 QEMU/KVM

通过 systemd 启动 libvirtd 后台服务：

```shell
sudo systemctl enable libvirtd.service
sudo systemctl start libvirtd.service
```

### 3. 让非 root 用户能正常使用 kvm

qumu/kvm 装好后，默认情况下需要 root 权限才能正常使用它。
为了方便使用，首先编辑文件 `/etc/libvirt/libvirtd.conf`:

1. `unix_sock_group = "libvirt"`，取消这一行的注释，使 `libvirt` 用户组能使用 unix 套接字。
1. `unix_sock_rw_perms = "0770"`，取消这一行的注释，使用户能读写 unix 套接字。

然后新建 libvirt 用户组，将当前用户加入该组：

```shell
newgrp libvirt
sudo usermod -aG libvirt $USER
```

最后重启 libvirtd 服务，应该就能正常使用了：

```shell
sudo systemctl restart libvirtd.service
```

### 3. 启用嵌套虚拟化

如果你需要在虚拟机中运行虚拟机，那就需要启用内核模块 kvm_intel 实现嵌套虚拟化。

```shell
# 临时启用 kvm_intel 嵌套虚拟化
sudo modprobe -r kvm_intel
sudo modprobe kvm_intel nested=1
# 修改配置，永久启用嵌套虚拟化
echo "options kvm-intel nested=1" | sudo tee /etc/modprobe.d/kvm-intel.conf
```

验证嵌套虚拟化已经启用：

```shell
$ cat /sys/module/kvm_intel/parameters/nested 
Y
```


## 二、虚拟机磁盘映像管理

这需要用到两个工具：

1. libguestfs: 虚拟机磁盘映像管理工具，前面介绍过了
2. qemu-img: qemu 的磁盘映像管理工具，用于创建磁盘、扩缩容磁盘、生成磁盘快照、查看磁盘信息、转换磁盘格式等等。

```shell
# 创建磁盘
qemu-img create -f qcow2 -o cluster_size=128K virt_disk.qcow2 20G

# 扩容磁盘
qemu-img resize ubuntu-server-cloudimg-amd64.img 30G

# 查看磁盘信息
qemu-img info ubuntu-server-cloudimg-amd64.img

# 转换磁盘格式
qemu-img convert -f raw -O qcow2 vm01.img vm01.qcow2  # raw => qcow2
qemu-img convert -f qcow2 -O raw vm01.qcow2 vm01.img  # qcow2 => raw
```

### 1. 导入 vmware 镜像

直接从 vmware ova 文件导入 kvm，这种方式转换得到的镜像应该能直接用（网卡需要重新配置）：

```shell
virt-v2v -i ova centos7-test01.ova -o local -os /vmhost/centos7-01  -of qcow2
```

也可以先从 ova 中解压出 vmdk 磁盘映像，将 vmware 的  vmdk 文件转换成 qcow2 格式，然后再导入 kvm（网卡需要重新配置）：

```shell
# 转换映像格式
qemu-img convert -p -f vmdk -O qcow2 centos7-test01-disk1.vmdk centos7-test01.qcow2
# 查看转换后的映像信息
qemu-img info centos7-test01.qcow2
```

直接转换 vmdk 文件得到的 qcow2 镜像，启会报错，比如「磁盘无法挂载」。
根据 [Importing Virtual Machines and disk images - ProxmoxVE Docs](https://pve.proxmox.com/pve-docs/chapter-qm.html#_importing_virtual_machines_and_disk_images) 文档所言，需要在网上下载安装 MergeIDE.zip 组件，
另外启动虚拟机前，需要将硬盘类型改为 IDE，才能解决这个问题。

### 2. 导入 img 镜像

img 镜像文件，就是所谓的 raw 格式镜像，也被称为裸镜像，IO 速度比 qcow2 快，但是体积大，而且不支持快照等高级特性。
如果不追求 IO 性能的话，建议将它转换成 qcow2 再使用。

```shell
qemu-img convert -f raw -O qcow2 vm01.img vm01.qcow2
```


## 三、虚拟机管理

虚拟机管理可以使用命令行工具 `virsh`/`virt-install`，也可以使用 GUI 工具 `virt-manager`.

GUI 很傻瓜式，就不介绍了，这里主要介绍命令行工具 `virsh`/`virt-install`

先介绍下 libvirt 中的几个概念：

1. Domain: 指代运行在虚拟机器上的操作系统的实例 - 一个虚拟机，或者用于启动虚拟机的配置。
1. Guest OS: 运行在 domain 中的虚拟操作系统。

大部分情况下，你都可以把下面命令中涉及到的 `domain` 理解成虚拟机。

### 0. 设置默认 URI

`virsh`/`virt-install`/`virt-viewer` 等一系列 libvirt 命令，
默认情况下会使用 `qemu:///session` 作为 URI 去连接 QEMU/KVM，
而 `virt-manager` 这个 GUI 工具，默认会使用 `qemu:///system` 去连接 QEMU/KVM.

`qemu:///system` 是系统全局的 qemu 环境，而 `qemu:///session` 的环境是按用户隔离的。
另外 `qemu:///session` 没有默认的 `network`，创建虚拟机时会出毛病。。。

总之，你需要将默认的 URI 改为 `qemu:///system`，否则绝对会被坑: 

```shell
echo 'export LIBVIRT_DEFAULT_URI="qemu:///system"' >> ~/.bashrc
```

### 1. 创建虚拟机 - virt-intall

```shell
# 创建全新的虚拟机，自动创建一个 20G 的磁盘。同时将 opensuse 的 iso 挂进去安装系统。
virt-install --virt-type kvm \
--name opensuse15 \
--vcpus 2 --memory 2048 \
--disk size=20 --graphics vnc \
--disk /path/to/opensuse15.2.iso,device=cdrom \
--os-variant opensuse15.2

# 使用已存在的磁盘创建虚拟机
virt-install --virt-type kvm \
  --name ubuntu20.04 \
  --memory 2048 \
  --disk ubuntu-server-cloud-amd64.img,device=disk,bus=virtio \
  --disk seed.img,device=cdrom \
  --os-type linux \
  --os-variant ubuntu20.04 \
  --graphics none \
  --network network=default,model=virtio \
  --import
```

### 3. 虚拟机管理 - virsh

虚拟机创建好后，可使用 virsh 管理虚拟机：

查看虚拟机列表：

```
# 查看正在运行的虚拟机
virsh list

# 查看所有虚拟机，包括 inactive 的虚拟机
virsh list --all
```

使用 `virt-viewer` 以 vnc 协议登入虚拟机终端：

```shell
# 使用虚拟机 ID 连接
virt-viewer 8
# 使用虚拟机名称连接，并且等待虚拟机启动
virt-viewer --wait opensuse15
```

启动、关闭、暂停(休眠)、重启虚拟机：

```shell
virsh start opensuse15
virsh suuspend opensuse15
virsh resume opensuse15
virsh reboot opensuse15
# 优雅关机
virsh shutdown opensuse15
# 强制关机
virsh destroy opensuse15

# 启用自动开机
virsh autostart opensuse15
# 禁用自动开机
virsh autostart --disable opensuse15
```

虚拟机快照管理：

```shell
# 列出一个虚拟机的所有快照
virsh snapshot-list --domain opensuse15
# 给某个虚拟机生成一个新快照
virsh snapshot-create <domain>
# 使用快照将虚拟机还原
virsh snapshot-restore <domain> <snapshotname>
# 删除快照
virsh snapshot-delete <domain> <snapshotname>
```

删除虚拟机：

```shell
virsh undefine opensuse15
```

迁移虚拟机：

```shell
# 使用默认参数进行离线迁移，将已关机的服务器迁移到另一个 qemu 实例
virsh migrate 37 qemu+ssh://tux@jupiter.example.com/system
# 还支持在线实时迁移，待续
```

cpu/内存修改：

```shell
# 改成 4 核
virsh setvcpus opensuse15 4
# 改成 4G
virsh setmem opensuse15 4096
```

虚拟机监控：
```shell
# 待续
```

修改磁盘、网络及其他设备：

```shell
# 添加新设备
virsh attach-device
virsh attach-disk
virsh attach-interface
# 删除设备
virsh detach-disk
virsh detach-device
virsh detach-interface
```


虚拟机网络管理：

```shell
# 列出所有虚拟机网络
virsh net-list
# 待续
```

## 参考

- [Virtualization Guide - OpenSUSE](https://doc.opensuse.org/documentation/leap/virtualization/html/book-virt/index.html)
- [Complete Installation of KVM, QEMU and Virt Manager on Arch Linux and Manjaro](https://computingforgeeks.com/complete-installation-of-kvmqemu-and-virt-manager-on-arch-linux-and-manjaro/)
- [virtualization-libvirt - ubuntu docs](https://ubuntu.com/server/docs/virtualization-libvirt)
- [RedHat Docs - KVM](https://developers.redhat.com/products/rhel/hello-world#fndtn-kvm)

