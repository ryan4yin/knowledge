# Btrfs 文件系统

BTRFS 的主要特性：

1. subvolume: 类似于 LVM 的逻辑卷，可以在一个文件系统内创建多个子文件系统。
2. snapshot: 快照，可以在不影响原文件系统的情况下，创建一个文件系统的副本，而且其基于 COW（Write On
   Copy）技术，因此占用的空间很小。

相关文档

- [Btrfs - Arch Wiki](https://wiki.archlinuxcn.org/zh-hans/Btrfs)

With Btrfs, it's also easy to install and manage multiple Linux distributions on the same disk, just
use different subvolumes for each distribution.

## Take a snapshot of a subvolume

```bash
# create a readonly snapshot of the subvolume
btrfs subvolume snapshot -r /home /snapshots/@home-2021-01-01

# restore the snapshot
## 1. delete the current subvolume
btrfs subvolume delete /home
## 2. create a new subvolume with the same name as the deleted one, using the snapshot as the source
btrfs subvolume snapshot /snapshots/@home-2021-01-01 /home

# transfer the snapshot and restore it on another machine
btrfs send /snapshots/@home-2021-01-01 | zstd | ssh root@192.168.178.110 'zstd -d | btrfs receive /home'
```

## Deduplication 去重功能

Btrfs 本身支持去重

第三方工具：

- [duperemove](https://github.com/markfasheh/duperemove)

## Usage

```bash
# format the root partition with btrfs and label it
mkfs.btrfs -L encrypted-nixos /dev/mapper/crypted-nixos

# mount the root partition and create subvolumes
mount /dev/mapper/crypted-nixos /mnt
btrfs subvolume create /mnt/@root
btrfs subvolume create /mnt/@home
btrfs subvolume create /mnt/@nix
btrfs subvolume create /mnt/@swap
umount /mnt

# Remount the root partition with the subvolumes you just created
#
# Enable zstd compression to:
#   1. Reduce the read/write operations, which helps to:
#     1. Extend the life of the SSD.
#     2. improve the performance of disks with low IOPS / RW throughput, such as HDD and SATA SSD.
#   2. Save the disk space.
mount -o compress-force=zstd:1,subvol=@root /dev/mapper/crypted-nixos /mnt
mkdir /mnt/{home,nix,swap,boot}
mount -o compress-force=zstd:1,subvol=@home /dev/mapper/crypted-nixos /mnt/home
mount -o compress-force=zstd:1,noatime,subvol=@nix /dev/mapper/crypted-nixos /mnt/nix


mount -o subvol=@swap /dev/mapper/crypted-nixos /mnt/swap
# disable CoW / compression on the swap subvolume,
# because the linux kernel requires that swapfile must not be compressed or have copy-on-write(CoW) enabled.
chattr -R +C -m /mnt/swap
# put the swapfile on the swap subvolume
cd /mnt/swap
truncate -s 0 swapfile
fallocate -l 96G wapfile
chmod 600 wapfile
mkswap swapfile
# check whether the swap subvolume has CoW disabled
# the output of `lsattr` for the swap subvolume should be:
#    ---------------C------ /swap/swapfile
# if not, delete the swapfile, and rerun the commands above.

# This is an alternative way to create the swapfile on the swap subvolume:
btrfs filesystem mkswapfile --size 96g --uuid clear /swap/swapfile

lsattr /mnt/swap
# mount the swapfile as swap area
swapon swapfile
```

## FAQ

### How to create a subvolume on top level when another subvolume is mounted on top level?

```bash
# get the uuid of the root partition
lsblk -af

# mount the root partition with the uuid
mount /dev/disk/by-uuid/<UUID> /mnt

# create a subvolume on top level
btrfs subvolume create /mnt/@snapshots
```

## Auto backup

1. [btrbk](https://github.com/NixOS/nixpkgs/blob/nixos-unstable/nixos/modules/services/backup/btrbk.nix):
   take snapshots and backup them to other instances via SSH.
2. [snapper](https://github.com/NixOS/nixpkgs/blob/nixos-23.05/nixos/modules/services/misc/snapper.nix):
   similar to btrbk, but it do not support backup remotely.
