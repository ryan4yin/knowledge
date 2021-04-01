## 一、Linux 分区

>全文默认使用 GPT 分区，不讨论已经淘汰的 MBR 相关内容

磁盘分区及查看工具：

lsblk
fdisk

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


### 文件系统扩容

首先通过 `df -hT` 确定分区的文件系统类型和文件系统大小，目前使用最广泛的是 ext4 和 xfs

```shell
[ec2-user@ip-xxx ~]$ df -h
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


## 相关文档

- [第七章、Linux 磁碟與檔案系統管理](http://linux.vbird.org/linux_basic/0230filesystem.php#disk)
- [Extend a Linux file system after resizing a volume - AWS EC2](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/recognize-expanded-volume-linux.html?icmpid=docs_ec2_console)