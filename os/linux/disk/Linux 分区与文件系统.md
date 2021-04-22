## 一、Linux 分区

要对 Linux 系统进行分区，首先有两种分区方式可选：

- MBR，或者称做 DOS 分区表，最高只支持到 2TB 存储。
  - 分区工具: fdisk
- GPT，新型的分区表，支持超大存储空间。
  - 分区工具: gdisk/parted

对于服务器而言，尤其是云服务器/虚拟机，我们很少会使用到超过 2TB 的单机存储，所以目前貌似 fdisk 仍然是系统管理员使用最多的分区工具，虚拟机最常用的分区表也仍然是 DOS 类型的分区表，而且使用的最广泛的引导方式也仍然是 bios，只有少数 KVM GPU 直通玩家才会搞 UEFI。

由于本人工作主要涉及的是云服务器，这里着重介绍的大概是 fdisk，而且也不会过多讨论如何对同一磁盘进行分区——虚拟机的磁盘本身就是虚拟的，这么做没啥意义。

GPT 分区表，以及对同一磁盘进行分区，目前来看更适合物理机和机械硬盘，不论是个人电脑还是物理服务器，插几块 1TB-12TB 的磁盘都是很常见的。


### 创建新分区

在新硬盘上创建新分区只需要使用一个命令: `fdisk`，具体流程如下：

```
# 简要介绍：依次输入n、回车、p、然后一直回车、最后输入 w 就完成了
[root@tsbweb1 data]# fdisk /dev/sdb
欢迎使用 fdisk (util-linux 2.23.2)。

更改将停留在内存中，直到您决定将更改写入磁盘。
使用写入命令前请三思。


命令(输入 m 获取帮助)：p

磁盘 /dev/sdb：17.2 GB, 17179869184 字节，33554432 个扇区
Units = 扇区 of 1 * 512 = 512 bytes
扇区大小(逻辑/物理)：512 字节 / 512 字节
I/O 大小(最小/最佳)：512 字节 / 512 字节
磁盘标签类型：dos
磁盘标识符：0xbb986126

   设备 Boot      Start         End      Blocks   Id  System

命令(输入 m 获取帮助)：n
Partition type:
   p   primary (0 primary, 0 extended, 4 free)
   e   extended
Select (default p): p
分区号 (1-4，默认 1)：
起始 扇区 (2048-33554431，默认为 2048)：
将使用默认值 2048
Last 扇区, +扇区 or +size{K,M,G} (2048-33554431，默认为 33554431)：
将使用默认值 33554431
分区 1 已设置为 Linux 类型，大小设为 16 GiB

命令(输入 m 获取帮助)：w
The partition table has been altered!

Calling ioctl() to re-read partition table.
正在同步磁盘。
```

完成后再使用 `lsblk` 查看：

```
# 变成 20G 了别在意...因为运行的机器不一样...
[ec2-user@xxx ~]$ lsblk
NAME          MAJ:MIN RM SIZE RO TYPE MOUNTPOINT
sdb       259:0    0  20G  0 disk
└─sdb1   259:4    0  20G  0 part
nvme0n1       259:1    0   8G  0 disk
├─nvme0n1p1   259:2    0   8G  0 part /
└─nvme0n1p128 259:3    0   1M  0 part
```

这就已经创建了一个新分区 `/dev/sdb1`，接下来还需要将它格式化为 ext4 等格式，再挂载到系统中使用。

### 磁盘分区扩容

如果你的磁盘没有做分区，就是整个磁盘作为一个分区挂载的话，磁盘和分区的大小就永远一致。
虚拟机磁盘扩容就不需要再手动扩容分区。

而如果你的磁盘分了多个区，比如常见的系统盘都至少会有两个分区：

```shell
[ec2-user@ip-xxx ~]# lsblk
NAME          MAJ:MIN RM SIZE RO TYPE MOUNTPOINT
nvme0n1       259:0    0  60G  0 disk
├─nvme0n1p1   259:1    0  30G  0 part /
└─nvme0n1p128 259:2    0   1M  0 part

[ec2-user@ip-xxx ~]# fdisk -l
GPT PMBR 大小不符(62914559 != 125829119)，将用 w(写) 予以更正。
Disk /dev/nvme0n1：60 GiB，64424509440 字节，125829120 个扇区
单元：扇区 / 1 * 512 = 512 字节
扇区大小(逻辑/物理)：512 字节 / 512 字节
I/O 大小(最小/最佳)：512 字节 / 512 字节
磁盘标签类型：gpt
磁盘标识符：6A955D68-963D-43A8-A1E9-BB21DD465514

设备              起点     末尾     扇区 大小 类型
/dev/nvme0n1p1    4096 62914526 62910431  30G Linux 文件系统
/dev/nvme0n1p128  2048     4095     2048   1M BIOS 启动
```

这里就可以看到，磁盘一共有 60G，但是根分区 `/dev/nvme0n1p1` 只有 30G.

这时可以使用如下命令扩容根分区:

```shell
# 命令格式：growpart [disk] [分区 ID]
[ec2-user@ip-xxx ~]# growpart /dev/nvme0n1 1
CHANGED: partition=1 start=4096 old: size=62910431 end=62914527 new: size=125824991 end=125829087

# 注: 如果 Amazon Linux 2 跑这命令报奇怪的错误，很大可能是编码问题！
# 先修改系统编码 LANG，再跑 growpart 估计就正常了
[ec2-user@ip-xxx ~]# LANG=en_US.UTF-8
# 问题原因：growpart 存在编码问题，而 ssh 在建立连接时，默认会使用本地的 LANG 属性！
```

现在再看，根分区就和磁盘差不多大了:

```shell
[ec2-user@ip-xxx ~]# lsblk
NAME          MAJ:MIN RM SIZE RO TYPE MOUNTPOINT
nvme0n1       259:0    0  60G  0 disk
├─nvme0n1p1   259:1    0  60G  0 part /
└─nvme0n1p128 259:2    0   1M  0 part
```

注意: 单纯扩容分区大小，并不能用上新的容量。还需要扩容文件系统的大小才行，这会在下一章介绍

## 二、Linux 文件系统

Linux 文件系统目前最常见的是 ext4 和 xfs，此外还有对超大阵列支持很好的 zfs 以及最新型的 btrfs.

debian 系目前默认使用 ext4，而 centos/opensuse 则默认使用 xfs，此外 fedora/opensuse 等系统都已经开始在桌面版上默认使用 btrfs.

还有另一类特殊的文件系统：使用内存模拟文件系统的 tmpfs，以及依附于其他文件系统的 overlayfs，docker 容器就有使用 overlayfs.

>据说 btrfs bug 一堆？

这里从实用的角度出发，主要介绍 ext4 和 xfs.

### 文件系统扩容

首先通过 `df -hT` 确定分区的文件系统类型和文件系统大小

```shell
# TODO 这里的输出第二列应该是 FS 类型，会打印出 xfs/tmpfs 等，示例需要更新
[ec2-user@ip-xxx ~]$ df -Th
Filesystem      Size  Used Avail Use% Mounted on
devtmpfs        1.9G     0  1.9G   0% /dev
tmpfs           1.9G     0  1.9G   0% /dev/shm
tmpfs           1.9G  440K  1.9G   1% /run
tmpfs           1.9G     0  1.9G   0% /sys/fs/cgroup
/dev/nvme0n1p1   30G  2.6G   27G   9% /
tmpfs           389M     0  389M   0% /run/user/0
tmpfs           389M     0  389M   0% /run/user/1000
```

然后通过 `lsblk` 确定分区大小

```shell
[ec2-user@ip-xxx ~]$ lsblk
NAME          MAJ:MIN RM SIZE RO TYPE MOUNTPOINT
nvme0n1       259:0    0  60G  0 disk
├─nvme0n1p1   259:1    0  60G  0 part /
└─nvme0n1p128 259:2    0   1M  0 part
```

可以看到 `/dev/nvme0n1p1` 的分区大小为 60G，而它的文件系统大小只有 30G。
因此可以将文件系统扩容到 60G.

>如果分区不够大，那你得考虑先做分区扩容，分区扩容参见上一章。

ext4 文件系统的扩容命令：

```shell
sudo resize2fs /dev/xvda1
```

xfs 文件系统的扩容命令：

```shell
# sudo yum install xfsprogs
sudo xfs_growfs -d /
```

### 挂载分区

临时挂载，可以直接使用 mount/umount 命令：

```shell
mkdir /data
# 将 /dev/sdb1 挂载为 /data 目录
mount /dev/sdb1 /data

# 卸载 /data 目录
umount /data
```

要开机启动就挂载，则需要修改 /etc/fstab 文件，注意此文件比较核心，如果它写错了将导致无法挂载根分区，系统无法启动！

对于 LVM 逻辑卷，可以直接使用如下方式挂载：
```shell
# 1. 查看 lv 逻辑卷的映射路径，记录下来
df -h

# 2. 设置开机自动挂载，每一列的含义：要挂载的分区设备号 	挂载点 	文件系统类型 	挂载选项 	是否备份 	是否检测
echo "/dev/mapper/<vg-name>-<lv-name> /data ext4 defaults 1 2" >> /etc/fstab

# 3. 测试设置的配置，没有任何输出就说明挂载成功，没有错误
mount -a
```

对于**物理硬盘，「分区设备号」需要填写设备的 UUID 号**，配置方法如下：

```shell
# 查询出设备的 uuid
$ blkid /dev/sdb1
/dev/sdb1: UUID="0e515b28-cf80-11e9-acd6-000c29299178" TYPE="ext4" PARTUUID="c6932ee3-1ed9-4047-b5e6-ac490af39b88"

# 使用上一步查询出的 uuid 进行挂载
$ echo "UUID=0e515b28-cf80-11e9-acd6-000c29299178 /data ext4 defaults 1 2" >> /etc/fstab

# 3. 测试设置的配置，没有任何输出就说明挂载成功，没有错误
mount -a
```


## 相关文档

- [第七章、Linux 磁碟與檔案系統管理 - 鸟哥的 Linux 私房菜](https://linux.vbird.org/linux_basic/centos7/0230filesystem.php)
- [Extend a Linux file system after resizing a volume - AWS EC2](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/recognize-expanded-volume-linux.html?icmpid=docs_ec2_console)