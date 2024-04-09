# AWS 的 Linux 发行版

1. AL2: 内核 4.14 与 5.10
1. AL2023: 基于 Fedora，内核升到 6.1
1. BottleRocket: 内核 5.15 或 6.1
   - 主要特点是 OS 完全容器化、不可变文件系统（类似 NixOS）。系统镜像小、启动快、使用 Rust 所以更安全。
   - GPU 相关的机型 EC2 用这个启动，或许能快个几秒，但对容器镜像的拉取加速或应该没有明显提升。

## Amazon Linux 2 到 2023 的内核变化

> https://docs.aws.amazon.com/zh_cn/linux/al2023/ug/compare-with-al2.html

1. 内核：5.10 -> 6.1
1. 新增 squashfs 支持，并支持启用 squashfs 的 zstd 压缩
1. 网络改用 systemd-networkd 管理
1. 默认使用 UEFI 启动
1. SSH： ssh-rsa 签名处于禁用状态，默认强制使用 ssh-ed25519
1. OpenSSL 升级到 3，弃用了旧的 OpenSSL 1.1.1 系列

## Kernel 5.10 -> 6.1 的变化

1. 新的调度算法
1. 优化 EXT4 的性能，同时带来了 Btrfs 等新的文件系统

