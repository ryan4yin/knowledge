# RISCV Boot Flows

Linux 引导相关内容：

- vmlinux
- Image
- u-boot
  - u-boot spl
    - spl：Secondary Program Loader，二级加载器
  - u-boot proper
- opensbi

## RISCV 开发版当前的引导流程

![](_img/current-riscv-boot-flow.webp)

## ARM64 开发版当前的引导流程

![](_img/current-arm64-boot-flow.webp)

## u-boot，u-boot-spl，u-boot-tpl 的关系

对于一般嵌入式而言只需要一个 u-boot 作为 bootloader 即可，但是在小内存，或者有 atf 的情况下还可以有 spl，tpl:

- spl：Secondary Program Loader，二级加载器
- tpl：Tertiary Program Loader，三级加载器

出现 spl 和 tpl 的原因最开始是因为系统 sram 太小，rom 无法在 ddr 未初始化的情况下一次性把所有代码从 flash，emmc，usb 等搬运到 sram 中执行，也或者是 flash 太小，无法完整放下整个 u-boot 来进行片上执行。所以 u-boot 又定义了 spl 和 tpl，spl 和 tpl 走 u-boot 完全相同的 boot 流程，不过在 spl 和 tpl 中大多数驱动和功能被去除了，根据需要只保留一部分 spl 和 tpl 需要的功能，通过 CONFIG_SPL_BUILD 和 CONFIG_TPL_BUILD 控制；一般只用 spl 就足够了，spl 完成 ddr 初始化，并完成一些外设驱动初始化，比如 usb，emmc，以此从其他外围设备加载 u-boot，但是如果对于小系统 spl 还是太大了，则可以继续加入 tpl，tpl 只做 ddr 等的特定初始化保证代码体积极小，以此再次从指定位置加载 spl，spl 再去加载 u-boot。

从目前来看，spl 可以取代上图中 bl2 的位置，或者 bl1，根据具体厂商实现来决定，有一些芯片厂商会将 spl 固化在 rom 中，使其具有从 emmc，usb 等设备加载 u-boot 或者其他固件的能力。

## OpenSBI

OpenSBI 是 System call type interface layer between Firmware runtime, M-Mode
to Operating system, S-Mode.

```mermaid
flowchart LR
    U["U-Boot SPL(M-Mode)"] --> O["OpenSBI(M-Mode)"] --> O2["U-Boot Proper(S-Mode)"]
    O2--> L["Linux Kernel(S-Mode)"] --> USER["User Space(U-Mode)"]
```

### FW_DYNAMIC

- Pack the firmware with runtime accessible to the next level boot stage, fw_dynamic.bin
- Can be packable in U-Boot SPL, Coreboot

首先编译出 `fw_dynamib.bin`：

```
CROSS_COMPILE=riscv64-buildroot-linux-gnu- make PLATFORM=sifive/fu540
```

然后基于该文件构建 u-boot-spl.bin:

```
CROSS_COMPILE=riscv64-buildroot-linux-gnu- make sfive_fu540_spl_defconfig

export OPENSBI=</path/to/fw_dynamic.bin>
CROSS_COMPILE=riscv64-buildroot-linux-gnu- make
```

## vmlinux vmlinuz Image zImage 等都有何关系

> https://www.baeldung.com/linux/kernel-images

按生成顺序依次介绍如下：

- vmlinux：Linux 内核编译出来的原始的内核文件，elf 格式，未做压缩处理。
  - 该映像可用于定位内核问题，但不能直接引导 Linux 系统启动。
- Image：Linux 内核编译时，使用 objcopy 处理 vmlinux 后生成的二进制内核映像。
  - 该映像未压缩，可直接引导 Linux 系统启动。
- zImage：一种 Linux 内核映像，专为 X86 架构的系统设计，它使用 LZ77 压缩算法。
- bzImage: 一种可启动的二进制压缩内核映像
  - `bz` 是 big zipped 的缩写。通常使用 gzip 压缩算法，但是也可以用别的算法。
  - 包含 boot loader header + gzip 压缩后的 vmlinux 映像
- vmlinuz: 它跟 bzImage 一样都是指压缩后的内核映像，两个名称基本可以互换。

## initrd 与 initramfs

> https://www.zhihu.com/question/22045825

### initrd

在早期的 linux 系统中，一般只有硬盘或者软盘被用来作为 linux 根文件系统的存储设备，因此也就很容易把这些设备的驱动程序集成到内核中。但是现在的嵌入式系统中可能将根文件系统保存到各种存储设备上，包括 scsi、sata，u-disk 等等。因此把这些设备的驱动代码全部编译到内核中显然就不是很方便。

为了解决这一矛盾，于是出现了 initrd，它的英文含义是 boot loader iniTIalized RAM disk，就是由 boot loader 初始化的内存盘。在 linux 内核启动前， boot loader 会将存储介质中的 initrd 文件加载到内存，内核启动时会在访问真正的文件系统前先访问该内存中的 initrd 文件系统。
在 boot loader 配置了 initrd 在这情况下，内核启动被分成了两个阶段，第一阶段内核会解压缩 initrd 文件，将解压后的 initrd 挂载为根目录；第二阶段才执行根目录中的 /linuxrc 脚本（cpio 格式的 initrd 为 /init,而 image 格式的 initrd<也称老式块设备的 initrd 或传统的文件镜像格式的 initrd>为 /initrc）。
在 `/init` 通常是一个 bash 脚本，我们可以通过它加载 realfs（真实文件系统）的驱动程序，并挂载好 /dev /proc /sys 等文件夹，接着就可以 mount 并 chroot 到真正的根目录，完成整个 rootfs 的加载。

### initramfs

在 linux2.5 中出现了 initramfs，它的作用和 initrd 类似，只是和内核编译成一个文件(该 initramfs 是经过 gzip 压缩后的 cpio 格式的数据文件)，该 cpio 格式的文件被链接进了内核中特殊的数据段.init.ramfs 上，其中全局变量**initramfs_start 和**initramfs_end 分别指向这个数据段的起始地址和结束地址。内核启动时会对.init.ramfs 段中的数据进行解压，然后使用它作为临时的根文件系统。

## References

- [An Introduction to RISC-V Boot flow: Overview, Blob vs Blobfree standards](https://crvf2019.github.io/pdf/43.pdf)
- [ARMv8 架构 u-boot 启动流程详细分析(一)](https://bbs.huaweicloud.com/blogs/363735)
- [聊聊 SOC 启动（五） uboot 启动流程一](https://zhuanlan.zhihu.com/p/520060653)
- [基于 qemu-riscv 从 0 开始构建嵌入式 linux 系统 ch5-1. 什么是多级 BootLoader 与 opensbi(上)¶](https://quard-star-tutorial.readthedocs.io/zh_CN/latest/ch5-1.html)
