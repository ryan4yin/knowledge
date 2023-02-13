# PCI 直通

>草稿内容，目前还没测试成功

QEMU/KVM 的 PCI(e) 直通功能可以让虚拟机**独占**指定的 PCI(e) 设备，越过宿主机控制器直接与该 PCI(e) 设备通信。

相比使用 QEMU/KVM 提供的 virtio 半虚拟化硬件，PCI(e) 直通有如下优势：

- 大大提升虚拟机与 PCI(e) 设备的 IO 性能（更低的延迟，更高的速度，更低的资源占用）。
- 可以利用上 QEMU/KVM 本身不支持的硬件特性，比如 PCI 直通最常见的使用场景——显卡直通。

那么最常见的 PCI(e) 直通需求有：

- **显卡直通**，实现在内部 windows 主机中用宿主机显卡看影视、玩游戏、剪视频
- **硬盘或 USB 直通**，以提升硬盘或 USB 的 IO 性能。

首先列举下相关的文档：

- [PCI(e) Passthrough - Proxmox WIKI](https://pve.proxmox.com/wiki/PCI(e)_Passthrough).
- [GPU OVMF PCI Passthrough (recommended) - Proxmox WIKI](https://pve.proxmox.com/wiki/Pci_passthrough#GPU_OVMF_PCI_Passthrough_.28recommended.29)
- [QEMU/Guest graphics acceleration - Arch WIKI](https://wiki.archlinux.org/title/QEMU/Guest_graphics_acceleration)

GPU 直通我暂时用不到就不讨论，这里先记录下我的场景——将 USB 硬盘盒直通到虚拟机中，作为 NAS 硬盘使用。

起因是我在直接使用 PVE 将 USB 设备添加到 Windows/Linux 虚拟机中时，磁盘的读写性能很差，读写最高只能稳定在 40M/s，HDD 正常情况怎么说也得超过 100M/s 吧。又查到 [USB Passthrough really slow? - r/Proxmox](https://www.reddit.com/r/Proxmox/comments/xks9dq/usb_passthrough_really_slow/) 中都说使用 PCIe 直通功能才能获得较好的 USB IO 性能，于是我开始尝试 PCIe 直通。

我是 AMD CPU，根据前面给出的官方文档，首先修改 `/etc/default/grub` 中的 `GRUB_CMDLINE_LINUX_DEFAULT` 一行，改为：

```shell
GRUB_CMDLINE_LINUX_DEFAULT="quiet amd_iommu=on iommu=pt"
```

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

如果输出中包含 `AMD-Vi: Interrupt remapping enabled` `AMD-Vi: AMD IOMMUv2 loaded and initialized` 之类的内容，就说明 PCI 直通需要的功能已经启用成功了。

对于较旧的 CPU 还需要做一些 `IOMMU Isolation` 等功能的验证，不过我都是 AMD 5 代 CPU，貌似都没啥问题，就直接跳过了。

接下来直接使用 PCIe 直通方式，将主机的 USB 控制器直通到虚拟机中以提升性能。（注意宿主机的 USB 接口不能有任何其他用途，它们将全部被直通到虚拟机！）

首先使用如下命令查询 USB 控制器的 PCI ID，每一行末尾方括号中的内容即 PCI 设备 ID:

```shell
root@pve-um560:~# lspci -nn | grep USB
04:00.3 USB controller [0c03]: Advanced Micro Devices, Inc. [AMD] Renoir USB 3.1 [1022:1639] (rev ff)
04:00.4 USB controller [0c03]: Advanced Micro Devices, Inc. [AMD] Renoir USB 3.1 [1022:1639] (rev ff)
```

为了仅在虚拟机中使用 USB 控制器，需要先在宿主机中声明此 PCI 设备仅供 vfio-pci 使用，命令如下：

```shell
# 注意 ids= 后面是所有 pci 设备的 id，使用逗号分隔
echo 'options vfio-pci ids=1022:1639' > /etc/modprobe.d/vfio.conf
```

然后再添加 `/etc/modprobe.d/blacklist.conf` 禁用所有 USB 相关的驱动，方法如下。

```shell
# 1. 首先查询出所有 usb 相关的内核模块，我们要禁用的是其中的 usb_storage 模块
cat /proc/modules | grep usb

# 2. 查看该模块的信息
modinfo usb_storage

# 3. 使用 fake 程序 /bin/true 替换 usb-storage，同时再将 usb-storage 加入黑名单，双重保障...
cat <<EOF | tee /etc/modprobe.d/disable-usb-storage.conf
install usb-storage /bin/true
blacklist usb-storage
EOF
```

改好后需要再次使用如下命令更新 Linux 的 initramfs 文件，然后重启系统：

```shell
update-initramfs -u -k all
```

重启完成后进 Web UI 中节点的「Disks」页面，这里重启前应该会显示所有 USB 硬盘及其状态，而现在因为驱动被禁用了，就不会显示了。

然后再通过命令行验证下，所有需要 PCIe 直通的控制器，都显示为 `Kernel driver in use: vfio-pci` 就说明 OK 了：

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

接着在 Windows 虚拟机的 Hardware => Add => PCI Device 中，把 USB 3.1 的两个设备都加进去，再启动主机。

然后就失败了.....怎么搞都搞不好，`dmesg` 报错，PVE 控制台下方的 logs 也报错，问题没解决，直通失败...

PVE 控制台启动虚拟机时报错：
```
kvm: ../hw/pci/pci.c:1487: pci_irq_handler: Assertion `0 <= irq_num && irq_num < PCI_NUM_PINS' failed.
```

dmesg 报错：

```
[65452.491635] ACPI Error: Aborting method \M276 due to previous error (AE_AML_LOOP_TIMEOUT) (20210730/psparse-529)
[65452.491644] ACPI Error: Aborting method \_SB.PCI0.GP17.AZAL._PS0 due to previous error (AE_AML_LOOP_TIMEOUT) (20210730/psparse-529)
[65452.491652] acpi device:16: Failed to change power state to D0
[65452.491662] vfio-pci 0000:04:00.6: can't change power state from D3hot to D0 (config space inaccessible)
[65452.492347] vfio-pci 0000:04:00.7: can't change power state from D3hot to D0 (config space inaccessible)
[65453.530129] vfio-pci 0000:04:00.3: invalid power transition (from D3cold to D3hot)
[65453.530139] vfio-pci 0000:04:00.0: invalid power transition (from D3cold to D3hot)
```

查了一圈也没找到解决方案，待研究...

TODO

## 拓展 - 命令行如何查询 GPU 使用情况

如果使用 VirGL 这种半虚拟化的 GPU 使用方式，可以在 pve 的 shell 中通过命令行查看 GPU 的使用情况，这个工具可以做到这一点：

- [nvtop](https://github.com/Syllo/nvtop): GPUs process monitoring for AMD, Intel and NVIDIA 
