# Linux 文件系统介绍

> https://en.wikipedia.org/wiki/Comparison_of_file_systems

## 一、老一代文件系统

### 1. ext4 文件系统

> First Stable Version: 21 October 2008

ext4 是近十年来 Linux 上最常用的文件系统之一，Ubuntu 与 Debian 默认使用 ext4。

ext4 从 Linux 上最早的文件系统 ext2 演化而来，其特点就是稳定、可靠。

但 ext4 与一些新兴的文件系统相比，缺失了许多新特性，比如：透明压缩、快照、去重等。

### 2. XFS 文件系统

> RHEL 7.0, released in June 2014, uses XFS as its default file system

XFS 是 RedHat/CentOS 系的发行版默认使用，因这些发行版的流行，XFS 也是最常见的文件系统之一。

XFS 与 ext4 相比，能更搞笑地支持并行 IO 操作，并且使用更少的硬盘空间。

## 二、新一代文件系统

### 1. Btrfs 文件系统

> https://btrfs.readthedocs.io/en/latest/

> Become default filesystem on Oracle Linux and SUSE since 2012.

> Btrfs 一度因为各种严重的 BUG 而臭名昭著，但随着 Btrfs 的更新迭代，稳定性不断提升，目前 Btrfs 已经
> 被越来越多的前沿发行版与用户所接受。

Btrfs 是 Linux 上最新的稳定可用的文件系统，其特点是支持 COW 写时拷贝、快照、去重、透明压缩等特性，并
且对 SSD 友好。

目前较新的 Linux 发行版，比如 Fedora 与 openSUSE 都默认使用 Btrfs。

Btrfs 相对于 ext4/xfs 的优势在于：

1. Copy-on-write COW：只有在对文件进行修改（write）操作时才会创建副本（private copy）。也就是说对文
   件的任何读操作（比如复制操作、或者并发读同一个文件），实际都不会创建副本。
   1. 如果调用者没有修改（write）该资源，就不会有副本（private copy）被创建。
   2. COW 永远不会覆盖原始数据，对文件的每次修改都会创建一个新的副本。
   3. COW 因其高性能，对广泛应用在数据库、虚拟内存管理等领域。
2. subvolume：类似于 LVM 的逻辑卷，LVM 可以在多个物理卷上创建出多个虚拟数据卷，而 Btrfs 可以在一个
   Btrfs 文件系统上创建出多个 btrfs 子卷。
3. [存储池与 RAID](https://btrfs.readthedocs.io/en/latest/Volume-management.html)：Btrfs 可以将多个
   磁盘组合成一个存储池，然后在存储池上创建文件系统。
   1. Btrfs 存储池支持 RAID0/RAID1/RAID10，另外 RIAD5/RAID6 因被报告支持不够完全不推荐使用。
4. 快照：Btrfs 的快照占用的空间很小，因为它使用 COW 技术。
5. 去重：Btrfs 支持去重，可以将重复的数据块合并成一个，从而节省空间。
6. 透明压缩：Btrfs 支持透明压缩，可以将某个文件系统设置为压缩模式，这样在写入数据时，会自动根据设定
   的参数压缩数据。
   1. 在吞吐量受限的场景下（比如云硬盘、SATA SSD、HDD 等），启用压缩能提升读写性能（即用算力换 IO 性
      能）。
   2. 对 SSD 场景，启用压缩能减少读写数据量，从而延长 SSD 的寿命。
7. SSD 友好：Btrfs 支持 [TRIM](https://btrfs.readthedocs.io/en/latest/Trim.html)，可以在删除文件时，
   通知 SSD 回收空间。
8. [数据完整性校验与自动修复](https://btrfs.readthedocs.io/en/latest/Auto-repair.html)：在读数据
   时，Btrfs 会自动校验数据的完整性，如果发现数据损坏，并且能在 RAID 存储池或其他副本中找到正确的数
   据，就会自动修复数据。
9. ...

可以看到新一代文件系统相对上一代的 ext4/xfs，有了很大的进步。

### 1. ZFS 文件系统

> OpenZFS since 2013

ZFS 最早是 Sun 公司开发的文件系统，后来被 Oracle 收购后演变出开源的 OpenZFS.

ZFS 的设计理念很先进，其主要特点有：

1. 存储池：将多个磁盘组合成一个存储池，然后在存储池上创建文件系统。
   1. ZFS 的存储池可以动态扩容，还支持添加高性能 SSD 作为缓存盘提升读写性能。
2. 冗余：可以在存储池上设置多种冗余策略，比如 RAID1/RAID5/RAID6 等。
3. COW 写时拷贝：与 Btrfs 类似。
4. 快照：其快照跟 Btrfs 类似，占用的空间很小。
5. 数据完整性校验与自动修复
6. 单个文件大小支持 16 EiB（2^64 字节）
7. 最大存储池大小支持 256 ZiB（2^78 字节）
8. 支持透明压缩
   1. 与 Btrfs 的透明压缩功能类似，在 HDD 存储池上启用压缩功能甚至能提升读写性能。对 NVMe SSD 场景，
      启用压缩也能减少读写数据量，从而延长 SSD 的寿命。

因为上面这些特性，ZFS 相当适合用于大规模存储系统，因此 ZFS 被广泛应用于 NAS 系统中。

但 ZFS 在 Linux 上不够开箱即用，并非内核模块。另一方面普通用户需要的大部分新特性 Btrfs 同样支持，而
Btrfs 要比 ZFS 简单许多，对新手更友好，因此在 Linux 社区中 Btrfs 比 ZFS 要流行很多。

FreeBSD 对 ZFS 的支持比 Linux 更好，因此一些基于 ZFS 的 NAS 系统选择 FreeBSD 作为底层操作系统。

## 三、下一代文件系统 - BcacheFS

> https://bcachefs.org/

> Will land in the Linux kernel 6.7

Bcachefs 的目标是在一个干净的 codebase 上，是 Btrfs / ZFS 的诸多新特性，同时提供更高的性能与更好的稳
定性。

Bcachefs 基本上是一个大一统的文件系统解决方案，存储池、RAID、COW、快照、去重、压缩、数据完整性校验与
自动修复、基于现代密码算法的 AEAD 认证加密（取代 LUKS）、副本等功能都有，而且性能更好。

很期待 Bcachefs 的 stable 版本发布。

## 四、该选用哪个文件系统？

个人使用：建议 Btrfs

企业使用：

1. 一般选用最稳定的 ext4/xfs
2. 对于使用低速硬盘（HDD/ SATA SSD / 云硬盘），且数据安全性要求不高（比如无状态的 K8s 集群节点？），
   可以尝试使用 Btrfs+启用 zstd 压缩提升 IO 性能，缩减存储空间占用。3. 得看数据重要性，像关键的数据
   中间件，还是建议选用最稳定可靠的 ext4/xfs。
