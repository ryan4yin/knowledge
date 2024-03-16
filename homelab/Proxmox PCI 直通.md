# PCI 直通

> 还未测试通过，仅供参考

## 1. 什么是 PCI 直通

QEMU/KVM 的 PCI(e) 直通功能可以让虚拟机**独占**指定的 PCI(e) 设备，越过宿主机控制器直接与该 PCI(e)
设备通信。

相比使用 QEMU/KVM 提供的 virtio 半虚拟化硬件，PCI(e) 直通有如下优势：

- 大大提升虚拟机与 PCI(e) 设备的 IO 性能（更低的延迟，更高的速度，更低的资源占用）。
- 可以利用上 QEMU/KVM 本身不支持的硬件特性，比如 PCI 直通最常见的使用场景——显卡直通。

那么最常见的 PCI(e) 直通需求有：

- **显卡直通**，实现在内部 windows 主机中用宿主机显卡看影视、玩游戏、剪视频
- **SATA/NVMe 硬盘或 USB 直通**，QEMU 的 USB 直通功能性能贼差，改成 PCIe 直通整个控制器，可以大大提
  升 USB 的 IO 性能。

举个例子，我在直接使用 PVE 将 USB 设备添加到 Windows/Linux 虚拟机中时，磁盘的读写性能很差，读写最高
只能稳定在 40M/s，HDD 正常情况怎么说也得超过 100M/s 吧。又查到
[USB Passthrough really slow? - r/Proxmox](https://www.reddit.com/r/Proxmox/comments/xks9dq/usb_passthrough_really_slow/)
中都说使用 PCIe 直通功能才能获得较好的 USB IO 性能，于是我开始尝试 PCIe 直通。

相关的文档：

- [PCI passthrough via OVMF - Archlinux Wiki](https://wiki.archlinuxcn.org/wiki/PCI_passthrough_via_OVMF):
  这个文档写得很详尽
- PVE 官方的一些文档
  - [PCI(e) Passthrough - Proxmox WIKI](<https://pve.proxmox.com/wiki/PCI(e)_Passthrough>).
  - [GPU OVMF PCI Passthrough (recommended) - Proxmox WIKI](https://pve.proxmox.com/wiki/Pci_passthrough#GPU_OVMF_PCI_Passthrough_.28recommended.29)

PCIe 直通是比较复杂的功能，兼容性不是很好，为了利用上最新的内核以避免旧内核的硬件兼容性问题，建议首
先将内核升级到最新版本。根据 [Proxmox VE Kernel](https://pve.proxmox.com/wiki/Proxmox_VE_Kernel) 中
的说明，PVE 7.4 当前最新的内核版本为 6.2，可使用如下命令升级内核：

```shell
apt update
apt install -y pve-kernel-6.2
```

装完重启系统，内核就升级好了。

### 2. AMD 的 USB 控制器直通

那么为了解决上面提到的 USB IO 性能问题，我首先尝试直通 USB 控制器给我的 NAS 虚拟机。

#### 2.1 启用 IOMMU 与 AMD-Vi 功能

我是 AMD CPU，虚拟机跑的是 Proxmox 系统，根据前面给出的参考文档，首先修改 `/etc/default/grub` 中的
`GRUB_CMDLINE_LINUX_DEFAULT` 一行，改为：

```shell
GRUB_CMDLINE_LINUX_DEFAULT="quiet amd_iommu=on iommu=pt pcie_acs_override=downstream"
```

简单说明下加的三个参数：

- `amd_iommu=on`：启用 IOMMU 功能
- `iommu=pt`：启用 IOMMU 的 pass-through 模式
- `pcie_acs_override=downstream`：启用 PCIe ACS override 功能，用于解决 PCIe 设备 IOMMU 组划分不合理
  的问题。IOMMU 分组不合理会导致一些 PCIe 设备无法直通，比如 USB 控制器。下一节有说明。
  - 此参数在 PVE 7.0+ 以上可以直接启用，不需要替换内核。

改好后使用如下命令应用修改后的 grub 配置:

```shell
update-grub
```

第二步是在 `/etc/modules` 末尾添加如下内容，启用 PCI(e) 直通需要用到的内核模块：

```
vfio
vfio_iommu_type1
vfio_pci
vfio_virqfd
```

改好后需要使用如下命令更新 Linux 的 initramfs 文件：

```shell
update-initramfs -u -k all
```

完成修改后重启系统，再通过如下命令验证修改：

```shell
dmesg | grep -e DMAR -e IOMMU -e AMD-Vi
```

如果输出中包含 `AMD-Vi: Interrupt remapping enabled` `AMD-Vi: AMD IOMMUv2 loaded and initialized` 之
类的内容，就说明 PCI 直通需要的功能已经启用成功了。

对于较旧的 CPU 还需要做一些 `IOMMU Isolation` 等功能的验证，不过我都是 AMD 5 代 CPU，貌似都没啥问
题，就直接跳过了。

#### 2.2 确认 IOMMU 组划分

PCIe 的最小直通单位是 IOMMU 组，但是 PCIe 硬件与 CPU、主板的连接方式会影响到 PCIe 设备的 IOMMU 组划
分，所以首先需要确认下你的 PCIe 设备的 IOMMU 组划分情况：

```shell
#!/bin/bash
shopt -s nullglob
for g in $(find /sys/kernel/iommu_groups/* -maxdepth 0 -type d | sort -V); do
    echo "IOMMU Group ${g##*/}:"
    for d in $g/devices/*; do
        echo -e "\t$(lspci -nns ${d##*/})"
    done;
done;
```

我们在前面 grub 的启动参数中添加了 `pcie_acs_override=downstream`，这个参数的作用是强制将 PCIe 设备
与 CPU、主板的连接方式改为 downstream，这样可以避免 PCIe 设备被划分到不同的 IOMMU 组中，从而导致无法
直通的问题。

以我的铭凡 UM560 为例，其输出如下：

```
......
IOMMU Group 10:
        01:00.0 Ethernet controller [0200]: Intel Corporation Ethernet Controller I225-V [8086:15f3] (rev 03)
IOMMU Group 11:
        02:00.0 Network controller [0280]: MEDIATEK Corp. Device [14c3:0608]
IOMMU Group 12:
        03:00.0 Non-Volatile memory controller [0108]: MAXIO Technology (Hangzhou) Ltd. NVMe SSD Controller MAP1202 [1e4b:1202] (rev 01)
IOMMU Group 13:
        04:00.0 VGA compatible controller [0300]: Advanced Micro Devices, Inc. [AMD/ATI] Device [1002:15e7] (rev c2)
        04:00.1 Audio device [0403]: Advanced Micro Devices, Inc. [AMD/ATI] Device [1002:1637]
        04:00.2 Encryption controller [1080]: Advanced Micro Devices, Inc. [AMD] Family 17h (Models 10h-1fh) Platform Security Processor [1022:15df]
        04:00.3 USB controller [0c03]: Advanced Micro Devices, Inc. [AMD] Renoir USB 3.1 [1022:1639]
        04:00.4 USB controller [0c03]: Advanced Micro Devices, Inc. [AMD] Renoir USB 3.1 [1022:1639]
        04:00.5 Multimedia controller [0480]: Advanced Micro Devices, Inc. [AMD] Raven/Raven2/FireFlight/Renoir Audio Processor [1022:15e2] (rev 01)
        04:00.6 Audio device [0403]: Advanced Micro Devices, Inc. [AMD] Family 17h (Models 10h-1fh) HD Audio Controller [1022:15e3]
        04:00.7 Signal processing controller [1180]: Advanced Micro Devices, Inc. [AMD] Raven/Raven2/Renoir Sensor Fusion Hub [1022:15e4]
IOMMU Group 14:
        05:00.0 SATA controller [0106]: Advanced Micro Devices, Inc. [AMD] FCH SATA Controller [AHCI mode] [1022:7901] (rev 81)
        05:00.1 SATA controller [0106]: Advanced Micro Devices, Inc. [AMD] FCH SATA Controller [AHCI mode] [1022:7901] (rev 81)
```

能看到我的 AMD 核显、声卡、 USB 控制器、加密控制器等都在 IOMMU Group 13 中，这意味着它们必须被一起直
通，否则无法正常工作。

简单分析下，将上述设备都直通到虚拟机后，宿主机将无法使用 USB 接口、声卡、核显等设备，不过剩下的设备
组够让宿主机正常工作了，所以可以进行直通。

**但是这里有个隐患是，直通后宿主机就没有任何 USB 接口跟显卡了，如果出了问题，鼠标键盘都无法使用，显
示器输出也不会 work，如果机器出了问题，就必须插个 Live CD 启动盘救砖**。

#### 2.3 隔离 IOMMU 组中的所有设备

> 注意，这会导致宿主机无法使用这些设备！所以请确保未直通的设备组能够满足宿主机正常工作的需求。

为了将设备分配给虚拟机，此设备和同在一个 IOMMU 组的所有设备必须将驱动程序更换为 vfio-pci ，以防止宿
主机尝试与其交互。

在宿主机启动过程中绑定了占位驱动程序 vfio-pci 后，相关设备处于非活动状态，直到虚拟机认领 (claim) 设
备或是切换到其他驱动程序。

IOMMU 组是直通的最小单位，被直通 IOMMU 组中的任何其它设备都应该绑定到 vfio-pci 驱动！

> 要注意，Host bridge 与 Host bridge 必须使用 pcieport 驱动，不能绑定 vfio-pci 驱动，因为它们需要连
> 接到宿主机以保持正常运行。在 grub 中启用了 `pcie_acs_override=downstream` 参数后，这两个设备会被分
> 配到不同的 IOMMU 组中，所以不需要担心。但是如果你没有启用 acs 功能，那就会有些麻烦。

可能有些驱动会在 vfio-pci 之前加载，导致 vfio-pci 无法绑定到设备上，测试发现 USB 设备就绑定失败了，
实际会绑定 xhci_pci 驱动。为了解决这个问题，可以使用如下脚本动态绑定 vfio-pci 驱动：

```shell
cat <<EOF | tee /usr/local/bin/vfio-pci-override.sh
#!/bin/sh

DEVS="0000:04:00.0 0000:04:00.1 0000:04:00.2 0000:04:00.3 0000:04:00.4 0000:04:00.5 0000:04:00.6 0000:04:00.7"

if [ ! -z "$(ls -A /sys/class/iommu)" ]; then
    for DEV in $DEVS; do
        for IOMMUDEV in $(ls /sys/bus/pci/devices/$DEV/iommu_group/devices) ; do
            echo "vfio-pci" > /sys/bus/pci/devices/$IOMMUDEV/driver_override
        done
    done
fi

modprobe -i vfio-pci
EOF
```

然后使用如下指令将 IOMMU Group 13 中的所有设备都绑定到 vfio-pci 驱动程序，

```shell
# 注意 ids= 后面是 IOMMU group 中所有 pci 设备的 id，使用逗号分隔
cat <<EOF | tee /etc/modprobe.d/vfio.conf
install vfio-pci /usr/local/bin/vfio-pci-override.sh
options vfio-pci ids=1002:15e7,1002:1637,1022:15df,1022:1639,1022:15e2,1022:15e3,1022:15e4
EOF
```

改好后需要再次使用如下命令更新 Linux 的 initramfs 文件，然后重启系统：

```shell
update-initramfs -u -k all
```

重启完成后进 Web UI 中节点的「Disks」页面，这里重启前应该会显示所有 USB 硬盘及其状态，而现在因为驱动
被禁用了，就不会显示了。

然后再通过命令行验证下，所有需要 PCIe 直通的控制器，都显示为 `Kernel driver in use: vfio-pci` 就说明
OK 了：

```shell
root@pve-um560:~# lspci -nnk
......
04:00.0 VGA compatible controller [0300]: Advanced Micro Devices, Inc. [AMD/ATI] Device [1002:15e7] (rev ff)
	Kernel driver in use: vfio-pci
	Kernel modules: amdgpu
......
04:00.3 USB controller [0c03]: Advanced Micro Devices, Inc. [AMD] Renoir USB 3.1 [1022:1639] (rev ff)
	Kernel driver in use: vfio-pci
	Kernel modules: xhci_pci
04:00.4 USB controller [0c03]: Advanced Micro Devices, Inc. [AMD] Renoir USB 3.1 [1022:1639] (rev ff)
	Kernel driver in use: vfio-pci
	Kernel modules: xhci_pci
......
```

#### 2.4 配置虚拟机

现在创建一台虚拟机，参数配置时有如下要求：

1. 必须使用 OVMF BIOS
2. CPU 类型必须选择 `host`
3. 硬盘用 virtio-scsi 性能更好
4. 其他的使用默认参数即可

创建完成后，进入虚拟机的「硬件」页面，将 IOMMU Group 5 中希望直通的 PCIe 设备添加到虚拟机中，然后启
动虚拟机。
