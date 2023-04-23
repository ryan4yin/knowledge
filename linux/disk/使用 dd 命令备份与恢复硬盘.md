# 使用 dd 命令备份与恢复硬盘

```bash
# copy all data from /dev/sda to /dev/sdb
#     input file = /dev/sda
#     output file = /dev/sdb
#     block size = 4M, increase this to speed up the process
#     conv=noerror,sync: ignore errors and sync data to disk after each block
dd if=/dev/sda of=/dev/sdb bs=4M conv=noerror,sync status=progress

# 也可以将整个硬盘备份为文件
dd if=/dev/sda of=/data/sda.img bs=4M conv=noerror,sync status=progress
# 为了方便传输，备份的同时还可以使用 gzip 压缩
dd if=/dev/sda bs=4M conv=noerror,sync status=progress | gzip > sda.img.gz

# 从文件恢复到硬盘
dd if=/data/sda.img of=/dev/sda bs=4M conv=noerror,sync status=progress
gzip -dc sda.img.gz | dd of=/dev/sda bs=4M conv=noerror,sync status=progress
```

## DD 读写速度与 bs 参数选择

上述命令中对 dd 读写速度影响最大的是 bs 参数，其含义为 block size 块大小，用于同时指定读与写的数据块大小，默认单位为字节，也可以使用 K 或 M 作为单位，如 bs=4M 表示 4MB。如果不指定 bs 参数，则默认为 512 字节，即 0.5KB。

bs 参数的选择仅影响读写速度，对命令的执行结果没有影响。

在默认参数 512bytes 情况下，dd 的读写速度是很慢的，因为它需要频繁地执行读写操作，也就需要频繁地与执行内核空间与用户空间的数据交换，这会导致大量的上下文切换，另一方面读写操作也受到机械硬盘/固态硬盘 IOPS 的限制，这些都会影响 dd 的读写速度。


## DD 复制可能遇到的问题

dd 命令只是单纯地做数据搬运，但是目标硬盘跟源硬盘的大小不一定一致，这会导致问题。

如果目标硬盘比源硬盘大那还好说，至少数据能被完整地写入到新硬盘。但是 GPT 也会因为磁盘大小与分区表记录不一致而出问题，需要使用 gdisk/fdisk 命令修复分区表（直接进 gdisk 使用 `w` 命令即可）。

>这里涉及到 GPT 分区表（GUID partition table）的存储结构，详见 [GPT 全局唯一标识分区表 - Wikipedia](https://zh.wikipedia.org/wiki/GUID%E7%A3%81%E7%A2%9F%E5%88%86%E5%89%B2%E8%A1%A8)，简单来说，GPT 会在硬盘头部保存 Primary GPT 分区表，而在硬盘尾部保存 Secondary GPT 分区表作为冗余备份，提升提供可靠性。

而如果目标硬盘比源硬盘还小，那数据末尾的部分就会被截断，这样就会导致数据丢失。GPT 的分区表刚好存储在硬盘的末尾，所以如果 dd 复制的时候没有指定 conv 参数，那么 GPT 分区表就会被截断，导致硬盘无法启动。

如上所述，将数据从大硬盘往小硬盘全盘同步是很麻烦的操作，直接 copy 肯定不行。如果你非要这么干，可以参考 [[SOLVED] How to clone a GPT drive to a smaller drive? - Arch Linux BBS](https://bbs.archlinux.org/viewtopic.php?id=154057)



