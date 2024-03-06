# Nix

笔记已迁移至: <博客 <https://thiscute.world/posts/nixos-and-flake-basics/>>

我的 nix 配置：[ryan4yin/nix-config](https://github.com/ryan4yin/nix-config)


## NixOS 镜像构建

相关源码：

1. 磁盘映像构建：<https://github.com/NixOS/nixpkgs/blob/nixos-23.11/nixos/lib/>
1. 安装器构建（ISO/SD 卡等）：<https://github.com/NixOS/nixpkgs/tree/nixos-23.11/nixos/modules/installer>
   - 这里面的脚本基本都是借助磁盘映像构建的脚本来构建的，会引用其中的脚本
   - CD-DVD
     - 使用了镜像构建脚本中的 `make-iso9660-image.nix` 来构建 ISO 镜像。
   - SD 卡
     - 再额外补充一些 extlinux/u-boot 相关的固件、BOOT 分区修改逻辑。
     - `sd-image.nix` 是构建 SD 卡镜像的基础脚本，它使用了 `make-ext4-fs.nix` 来构建 ext4 文件系统映像。
1. 虚拟化镜像构建（AWS/QEMU/virtualbox/oci-container/proxmox/...）：<https://github.com/NixOS/nixpkgs/tree/nixos-23.11/nixos/modules/virtualisation>
   - 同样，这里面的脚本也是借助磁盘映像构建的脚本来构建的，基本都是使用的 `make-disk-image.nix` 这个脚本。

那么这里的核心脚本其实是这几个：

1. `make-disk-image.nix`: 最通用的磁盘映像构建脚本，被大多数镜像构建脚本使用。
    1. 支持 BIOS/UEFI，但不清楚是否支持 U-BOOT extlinux 这种嵌入式环境常用的引导方式。
    1. 默认使用 ext4 文件系统，可以通过参数指定其他文件系统。
    1. 默认会启动一个 QEMU 虚拟机来完成构建。
1. `make-iso9660-image.nix`: TODO
1. `make-ext4-fs.nix`: TODO

我在测试使用 `make-disk-image.nix` 构建使用 EDK2(UEFI) 启动的 NixOS 镜像时遇到了问题：

1. 如果将交叉编译工具链（pkgsCross）作为 `make-disk-image.nix` 的参数传入，那么：
    1. 会导致 offical cache 失效，`mkae-disk-image.nix` 会尝试从源码构建它的所有依赖，尤其是 QEMU！这非常费时间，而且常常失败。
1. 如果使用本地工具链（x86_64-linux）来运行 `make-disk-image.nix`，流程很顺畅，但在 `chroot` 阶段会报错，目前怀疑是无法在 `x86_64-linux` 的系统上 `chroot` 到 `aarch64-linux` 的 rootfs.
1. 如果使用模拟工具链（即在 qemu-aarch64）来运行 `make-disk-image.nix`，那么：
    1. 会导致在运行时疯狂报错 ` Cannot allocate memory`，即使给 `make-disk-image.nix` 传递的参数设置了 8G 内存，还是同样的错误。

TODO

## devbox 调研

优点：基本等同于 Nix 的优点，外加的一条是它多了一层抽象，使得普通用户不需要理解底层 Nix 的细节。

缺点：

1. 只能使 Nix 生态中的东西可复用，因此你如果需要使用非 Nix 生态中的东西，就需要自己写 flake，这就需要你理解 Nix 的细节了。
    1. 抽象泄漏，不过这个可以由基础设施团队 cover 住，开发者就可以专注于业务了。
2. 互联网企业大都用 macOS，但是 macOS 下的 devbox，实际跟线上 Linux 环境是有较大区别的，这会导致 devbox 的开发环境与线上环境不一致。
    1. 不同的 OS、不同的 CPU 架构，对应的 Nix 打包代码、构建工具链都可能会不一样，这没法避免。
    2. 比较好的解决方案仍然是容器化，但是容器化的话，就跟 devcontainer 差不多了。虽然也比纯 devcontainer 可复现性更强，但原生的开发体验就没了。


## 软件打包

1. nativeBuildInputs: 本地环境（编译环境）的构建依赖，仅在编译期需要，软件架构也与构建平台一致
3. buildInputs: 运行环境的运行依赖，软件架构与目标运行环境一致

### Python 应用

TODO


## Linux 内核选择

1. https://wiki.archlinux.org/title/kernel
1. https://nixos.wiki/wiki/Linux_kernel
2. https://nixos.org/manual/nixpkgs/stable/#sec-linux-kernel

Nixpkgs 的内核都在这里声明： <https://github.com/NixOS/nixpkgs/blob/nixos-23.11/pkgs/top-level/linux-kernels.nix>

内核的种类有：

1. 默认内核：即标准的 Linux 官方内核，它稳定、可靠且经过广泛测试，兼容性最佳，但并不总是针对特定用例提供最佳性能。
    1. 最稳定可靠的选择
1. Hardened Linux Kernel: A security-focused Linux kernel applying a set of hardening patches to mitigate kernel and userspace exploits. It also enables more upstream kernel hardening features than linux.
    1. 最安全的选择，但牺牲了性能，某些程序甚至可能无法在此内核上正常运行。适用于安全性优先的关键应用程序，不太适合普通用户。
1. [XanMod kernel](https://xanmod.org/): 对高性能工作站、游戏主机、媒体服务器等场景做了针对性的调优，响应更灵敏、更流畅。
    1. **是 Linux 社区中久负盛名的第三方定制内核**
    1. This kernel uses the MuQSS or Task Type scheduler, BFQ I/O scheduler, UKSM realtime memory data deduplication, **TCP BBR** congestion control, x86_64 advanced instruction set support, and other default changes.
    1. 普通桌面建议使用其标准版，而对竞技游戏、音视频直播等场景则可尝试使用其实时版本。
1. [Zen Kernel](https://github.com/zen-kernel/zen-kernel/wiki/FAQ): Zen Kernel is a fork of Linux that applies out-of-tree features, early backports, and fixes, that impact desktop usage of Linux.
1. [Liquorix Kernel](https://github.com/zen-kernel/zen-kernel/wiki/FAQ): Zen Kernel 的一个 distribution，以功耗为代价换取了更极致的性能。是比较老牌针对媒体、音乐和游戏优化的内核，**和 Xanmod 对比，互有胜负**。
1. [Libre Kernel](https://www.fsfla.org/ikiwiki/selibre/linux-libre/): 去掉了 Linux 中所有非自由代码的精简内核，GNU/GUIX 目前的默认内核。
    1. 最狂热的开源爱好者可以选择它。
1. 其他 RaspberryPi 等嵌入式设备的专用 Kernel

所以总的来看，个人用户可以选择尝试：默认内核、XanMod 内核以及 Liquorix 内核这三个版本，看看哪用得更舒服。

## Linux 内核更新记录

- https://9to5linux.com/category/news/kernel

## 在 NixOS 上运行高可用 Kubernetes 集群

https://github.com/NixOS/nixpkgs/tree/nixos-23.05/nixos/modules/services/cluster/kubernetes

https://nixos.org/manual/nixos/stable/index.html#sec-kubernetes

https://nixos.wiki/wiki/Kubernetes

