# Linux LVM 逻辑卷管理

>本文大部分命令都要求 root 权限。

LVM 通过在物理分区上，虚拟了一个逻辑层，来实现灵活的磁盘分配。
它灵活性的最大体现在于：**逻辑卷可以将多个分区、甚至多个物理硬盘，虚拟成一个逻辑卷来使用。**

## 一、LVM 扩容

- [Linux 挂载新硬盘/LVM 逻辑卷扩容](https://www.cnblogs.com/kirito-c/p/11938024.html)


在使用 Linux 的过程中，有时会因为某些原因，预分配的磁盘/挂载点的容量不够用，需要扩容。
这时通常有三种方法进行扩容：

1. 挂载新硬盘: 添加新硬盘，将硬盘挂到新路径下，再将数据备份到这个新路径下，实现扩容。
1. LVM 逻辑卷扩容：如果你的数据文件夹在 LVM 逻辑卷内，那么可以直接将新硬盘的容量扩给你的逻辑卷，实现原地扩容。
1. 对于非 LVM 分区，如果是虚拟机，可以直接扩容硬盘的容量，然后在系统中使用 fdisk 扩容。
    - 虚拟机最简单的扩容方法，应该是使用 cloud-init，在扩容硬盘容量后，cloud-init 会自动运行 cloud-utils-growpart 自动扩容分区。

LVM 通过在物理分区上，虚拟了一个逻辑层，来实现灵活的磁盘分配。
它灵活性的最大体现在于：**逻辑卷可以将多个分区、甚至多个物理硬盘，虚拟成一个逻辑卷来使用。**

下面介绍 LVM 扩容的具体方法。

### 1. 添加新硬盘/扩容硬盘大小

不管是要怎样扩容分区，首先都得先添加新物理硬盘，有两种方法。

#### 方法一：虚拟机直接扩容虚拟硬盘

如果是虚拟机，可以考虑直接扩容已有的虚拟硬盘容量，不需要添加新硬盘。

1. 直接在虚拟机设置里面，调整虚拟硬盘的大小。
1. 重启虚拟机，否则硬盘大小不会刷新
    - 或许有方法可以不重启虚拟机，以后研究下。

非 LVM 分区的虚拟机，也可以使用这种方法扩容硬盘大小。

#### 方法二：添加新硬盘，可以不重启

>非 LVM 分区无法使用这种方法，只有 LVM 能实现跨硬盘扩容分区。

物理机或虚拟机都可以通过如下方法添加新硬盘：

1. 为主机添加新硬盘
    - 虚拟机：直接在设置界面选择「添加新设备」-「硬盘」，必须选择 scsi 协议。
    - 物理机：直接插入新硬盘，服务器基本都支持热插拨。
1. 将新硬盘加载到虚拟机内：
    - 方法一：重启服务器
    - 方法二：手动扫描所有 scsi 总线
    ```shell
    # 1. 查看硬盘
    $ lsblk  # list block devices
    # 输出略，反正只有 sda，没有 sdb

    # 2. 扫描所有总线
    $ cd /sys/class/scsi_host/
    $ ls
    host0 host1 host2
    $ for h in *; do echo "- - -" > "${h}/scan"; done

    # 3. 再次查看硬盘
    $ lsblk
    # 已经有 sdb 了
    ```

### 2. Linux 存储扩容

>非 LVM 分区，可以直接在这一步使用 fdisk 扩容旧分区大小，总的流程更短一些。

#### 2.1. 使用 `fdisk /dev/sdb` 为新硬盘 sdb 创建分区

操作流程如下：
```shell
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
分区号 (1-4，默认 1)：1
起始 扇区 (2048-33554431，默认为 2048)：
将使用默认值 2048
Last 扇区, +扇区 or +size{K,M,G} (2048-33554431，默认为 33554431)：
将使用默认值 33554431
分区 1 已设置为 Linux 类型，大小设为 16 GiB

命令(输入 m 获取帮助)：t
已选择分区 1
Hex 代码(输入 L 列出所有代码)：L

 0  空              24  NEC DOS         81  Minix / 旧 Linu bf  Solaris        
 1  FAT12           27  隐藏的 NTFS Win 82  Linux 交换 / So c1  DRDOS/sec (FAT-
 2  XENIX root      39  Plan 9          83  Linux           c4  DRDOS/sec (FAT-
 3  XENIX usr       3c  PartitionMagic  84  OS/2 隐藏的 C:  c6  DRDOS/sec (FAT-
 4  FAT16 <32M      40  Venix 80286     85  Linux 扩展      c7  Syrinx         
 5  扩展            41  PPC PReP Boot   86  NTFS 卷集       da  非文件系统数据 
 6  FAT16           42  SFS             87  NTFS 卷集       db  CP/M / CTOS / .
 7  HPFS/NTFS/exFAT 4d  QNX4.x          88  Linux 纯文本    de  Dell 工具      
 8  AIX             4e  QNX4.x 第2部分  8e  Linux LVM       df  BootIt         
 9  AIX 可启动      4f  QNX4.x 第3部分  93  Amoeba          e1  DOS 访问       
 a  OS/2 启动管理器 50  OnTrack DM      94  Amoeba BBT      e3  DOS R/O        
 b  W95 FAT32       51  OnTrack DM6 Aux 9f  BSD/OS          e4  SpeedStor      
 c  W95 FAT32 (LBA) 52  CP/M            a0  IBM Thinkpad 休 eb  BeOS fs        
 e  W95 FAT16 (LBA) 53  OnTrack DM6 Aux a5  FreeBSD         ee  GPT            
 f  W95 扩展 (LBA)  54  OnTrackDM6      a6  OpenBSD         ef  EFI (FAT-12/16/
10  OPUS            55  EZ-Drive        a7  NeXTSTEP        f0  Linux/PA-RISC  
11  隐藏的 FAT12    56  Golden Bow      a8  Darwin UFS      f1  SpeedStor      
12  Compaq 诊断     5c  Priam Edisk     a9  NetBSD          f4  SpeedStor      
14  隐藏的 FAT16 <3 61  SpeedStor       ab  Darwin 启动     f2  DOS 次要       
16  隐藏的 FAT16    63  GNU HURD or Sys af  HFS / HFS+      fb  VMware VMFS    
17  隐藏的 HPFS/NTF 64  Novell Netware  b7  BSDI fs         fc  VMware VMKCORE 
18  AST 智能睡眠    65  Novell Netware  b8  BSDI swap       fd  Linux raid 自动
1b  隐藏的 W95 FAT3 70  DiskSecure 多启 bb  Boot Wizard 隐  fe  LANstep        
1c  隐藏的 W95 FAT3 75  PC/IX           be  Solaris 启动    ff  BBT            
1e  隐藏的 W95 FAT1 80  旧 Minix       
Hex 代码(输入 L 列出所有代码)：8e
已将分区“Linux”的类型更改为“Linux LVM”

命令(输入 m 获取帮助)：p

磁盘 /dev/sdb：17.2 GB, 17179869184 字节，33554432 个扇区
Units = 扇区 of 1 * 512 = 512 bytes
扇区大小(逻辑/物理)：512 字节 / 512 字节
I/O 大小(最小/最佳)：512 字节 / 512 字节
磁盘标签类型：dos
磁盘标识符：0xbb986126

   设备 Boot      Start         End      Blocks   Id  System
/dev/sdb1            2048    33554431    16776192   8e  Linux LVM

命令(输入 m 获取帮助)：w
The partition table has been altered!

Calling ioctl() to re-read partition table.
正在同步磁盘。
```

#### 2.2. 扩容已有的 LVM 逻辑卷/添加新 LVM 数据卷

使用 LVM 的好处就是可以方便地原地扩缩容。缺点就是有一点学习门槛，需要首先了解一下 LVM 中 **pv vg lv pe** 等概念的意义。

![](https://img2020.cnblogs.com/blog/968138/202011/968138-20201118093557465-190434158.png)


抛开具体的意义，直接说操作流程的话：

1. `pvcreate /dev/sdb1`(physical volume): 创建物理卷
1. `pvdisplay`(physical volume): 查看物理卷
1. `vgdisplay`(volume group): 使用该命令，记录下 vg 的名称
1. 扩展已有 lvm 卷：`vgextend <vg-name> /dev/sdb1`
    1. 如果是新建 lvm 卷：`vgcreate <vg-name> /dev/sdb1`，vg 名称可设为 `data_vg`.
1. `vgdisplay`: 记录下输出中 `Free PE / Size` (physical extent)对应的值，应该增大了。
1. `lvdisplay`(logical volume): 使用该命令，记录下 lv 逻辑卷的 Path
1. `lvresize --extents +<Num> --resizefs <Path>`：使用此命令拓展 lv 分区的大小
    - <Num> 为第一步记录下的Free PE 数值
    - <Path> 为第二步记录下的 Path
    - 如果是新建 lv 逻辑卷：`lvcreate -l 100%VG -n <lv-name> <vg-name>`，使用全部的 vg 空间。

#### 2.3. 设置数据卷的自动挂载

如果是新建的 lv 逻辑卷，那接下来还得将建好的 lv 逻辑卷初始化好，然后挂载到文件目录下：

```shell
# 格式化
mkfs.ext4 /dev/<vg-name>/<lv-name>
# 创建文件夹路径，挂载 lv 逻辑卷
mkdir /data
mount /dev/<vg-name>/<lv-name> /data
```

修改 `/etc/fstab` 设置开机自动挂载：

>注意：**此处需谨慎，否则将导致系统无法启动！**

```shell
df -h  # 查看 lv 逻辑卷的映射路径
# 设置开机自动挂载，每一列的含义：要挂载的分区设备号 	挂载点 	文件系统类型 	挂载选项 	是否备份 	是否检测
echo "/dev/mapper/<vg-name>-<lv-name> /data ext4 defaults 1 2" >> /etc/fstab
mount -a  # 测试设置的配置是否成功
```

设置 `/etc/fstab` 时注意， 对于物理硬盘，「分区设备号」需要填写设备的 UUID 号：

```shell
$ blkid /dev/sdb1
/dev/sdb1: UUID="0e515b28-cf80-11e9-acd6-000c29299178" TYPE="ext4" PARTUUID="c6932ee3-1ed9-4047-b5e6-ac490af39b88"

# 物理设备需要填写 UUID 号
$ echo "UUID=0e515b28-cf80-11e9-acd6-000c29299178 /data ext4 defaults 1 2" >> /etc/fstab
```

关于设备挂载，详见 [Linux挂载（mount/umount及开机自动挂载）](https://www.cnblogs.com/isme-zjh/p/11421334.html)


## 二、LVM 缩容，去除物理磁盘

注意！缩容貌似是很危险的操作，很可能导致数据丢失！
需要提前将需要移除的硬盘上的数据迁移走，目前还没搞清楚怎么迁移。。

我上次缩容根文件系统，直接导致系统核心文件损坏，整个虚拟机崩溃。。。

## 相关文档

- [逻辑卷管理器管理 - RedHat Docs](https://access.redhat.com/documentation/zh-cn/red_hat_enterprise_linux/7/html/logical_volume_manager_administration/lvm_overview)
- [鸟哥的 Linux 私房菜 - 邏輯捲軸管理員 (Logical Volume Manager)](https://linux.vbird.org/linux_basic/centos7/0420quota.php#lvm)
- [添加新硬盘，LVM在线扩容](https://www.jianshu.com/p/5fd48d6d87a9)
- [Linux添加新硬盘并挂载(mount)到目录下](https://blog.csdn.net/qq6759/article/details/85319274)