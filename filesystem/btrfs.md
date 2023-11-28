# Btrfs 文件系统

BTRFS 的主要特性：

1. subvolume: 类似于 LVM 的逻辑卷，可以在一个文件系统内创建多个子文件系统。
2. snapshot: 快照，可以在不影响原文件系统的情况下，创建一个文件系统的副本，而且其基于 COW（Write On Copy）技术，因此占用的空间很小。

相关文档

- [Btrfs - Arch Wiki](https://wiki.archlinuxcn.org/zh-hans/Btrfs)

## Deduplication 去重功能

Btrfs 本身支持去重

第三方工具：

- [duperemove](https://github.com/markfasheh/duperemove)
