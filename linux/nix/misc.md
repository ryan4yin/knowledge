
LicheePi 4A 官方主要支持 RevyOS，根据火哥文章介绍，它也是目前唯一且确实能够启用板载 GPU 的系统，
该操作系统项目基于 Debian 开发，默认提供了两个 rootfs 镜像，一个是基本功能的镜像，没有桌面环境；
另一个默认提供了 xfce4 桌面环境的系统镜像，为用户提供 RISC-V 下 XFCE4 的桌面操作体验。

RevyOS 的内核、u-boot 和 opensbi 代码仓库：

- https://github.com/revyos/thead-kernel.git
- https://github.com/revyos/thead-u-boot.git
- https://github.com/revyos/thead-opensbi.git

RevyOS 的预构建镜像下载地址

- https://mirror.iscas.ac.cn/revyos/extra/images/lpi4a/

LicheePi 4A 的官方教程：

- https://wiki.sipeed.com/hardware/zh/lichee/th1520/lpi4a/7_develop_revyos.html

根据如上 LicheePi 4A 相关文档，应该有三个分区镜像：

- u-boot-with-spl-lpi4a.bin: 刷入到 spl 分区的 u-boot 引导程序，与 NixOS 无关
- boot.ext4: boot 分区，包含 dtb、kernel image、opensbi 等文件，需要与 NixOS 一起构建
- rootfs.ext4: rootfs 分区，包含 NixOS 的根文件系统，只有这个分区与 NixOS 有关

u-boot-with-spl-lpi4a.bin 可直接从这里下载由中科院软件研究所提供的二进制文件：

- https://mirror.iscas.ac.cn/revyos/extra/images/lpi4a/

那么，只要我们能构建出 NixOS 可用的 boot.ext4 跟 rootfs.ext4 分区，就可以在 LicheePi 4A 上运行 NixOS 了。

## 构建 boot 与 rootfs

Build sdImage(wich may take a long time, about 2 hours on my machine):

```shell
nix build .#nixosConfigurations.lp4a.config.system.build.sdImage --keep-failed
```

Extrace rootfs from sdImage:

方法一：

```shell
# mount the image
sudo losetup -P --show -f $(ls nixos-*-riscv64-linux.img)

# extract the rootfs partition
sudo dd if=/dev/loop0p2 of=rootfs.ext4 bs=1M status=progress

# umount the image
sudo losetup -d /dev/loop0
```

方法二：

```shell
IMG_FILE=$(result/sd-image/nixos-sd-image-*.img)

# check the partition of sdImage
› fdisk -lu ${IMG_FILE}
Disk result/sd-image/nixos-sd-image-23.05.20230624.3ef8b37-riscv64-linux.img: 1.81 GiB, 1940246528 bytes, 3789544 sectors
Units: sectors of 1 * 512 = 512 bytes
Sector size (logical/physical): 512 bytes / 512 bytes
I/O size (minimum/optimal): 512 bytes / 512 bytes
Disklabel type: dos
Disk identifier: 0x2178694e

Device                                                                   Boot Start     End Sectors  Size Id Type
result/sd-image/nixos-sd-image-23.05.20230624.3ef8b37-riscv64-linux.img1      16384   77823   61440   30M  b W95 FAT32
result/sd-image/nixos-sd-image-23.05.20230624.3ef8b37-riscv64-linux.img2 *    77824 3789543 3711720  1.8G 83 Linux

# extract the rootfs partition
# the rootfs' partition start from 77824 sector, and each sector is 512 bytes
# the command's format is
#    dd if=[image] of=[partition] bs=512 skip=Start count=Sectors
dd if=${IMG_FILE} of=rootfs.ext4 bs=512 skip=77824 count=3711720
```

得到的内容应该都是一样的。

## 镜像烧录到 eMMC

> 官方文档：https://wiki.sipeed.com/hardware/zh/lichee/th1520/lpi4a/4_burn_image.html

> 内核开发板不支持从 SD 卡启动，只能从 eMMC 启动！

构建好 boot 跟 rootfs 后我们就拥有了完整的三部分镜像，根据官方文档，内测版 LP4A 硬件的刷入流程如下：

1. 按住板上的 BOOT 按键不放，然后插入 USB-C 线缆上电（线缆另一头接 PC ），即可进入 USB 烧录模式（fastboot）。
   1. 在 Linux 下，使用 `lsusb` 查看设备，会显示以下设备： `ID 2345:7654 T-HEAD USB download gadget`
2. 接下来使用如下指令分别烧录镜像：
3. fastboot 程序直接从 [Android Platform Tools](https://developer.android.com/tools/releases/platform-tools) 下载，或者从包管理器安装都行。

````shell

```shell
# flash u-boot into spl partition
sudo fastboot flash ram u-boot-with-spl.bin
sudo fastboot reboot
# flash uboot partition
sudo fastboot flash uboot u-boot-with-spl.bin

# flash nixos's boot partition
sudo fastboot flash boot boot.ext4
# flash nixos's rootfs partition
sudo fastboot flash root rootfs.ext4
````

系统启动后，第一件事应该是扩容 rootfs 分区，因为默认情况下系统没有任何空闲空间（这一步可以让 NixOS 在启动时自动做，改个参数即可）：

```shell
sudo parted -s /dev/mmcblk0 "resizepart 3 -0"
sudo resize2fs /dev/mmcblk0p3
```


## 记录下一些分析流程

rootfs 已经成功构建完成，内容如下：

```shell
╭───┬───────────────────────┬──────┬──────────┬──────────────╮
│ # │         name          │ type │   size   │   modified   │
├───┼───────────────────────┼──────┼──────────┼──────────────┤
│ 0 │ boot                  │ dir  │   4.1 KB │ 53 years ago │
│ 1 │ lost+found            │ dir  │  16.4 KB │ 53 years ago │
│ 2 │ nix                   │ dir  │   4.1 KB │ 53 years ago │
│ 3 │ nix-path-registration │ file │ 242.7 KB │ 53 years ago │
╰───┴───────────────────────┴──────┴──────────┴──────────────╯
```

可以看到 NixOS 对系统真的是清理得很彻底，整个根目录下一共就两个文件夹 `/boot` 跟 `/nix/store`.

仔细看下 `/boot` 的内容，因为现在要对它进行修改：

```shell
› tree
.
├── extlinux
│   └── extlinux.conf
└── nixos
    ├── rzc42b6qjxy10wb1wkfmrxjcxsw52015-linux-riscv64-unknown-linux-gnu-5.10.113-thead-1520-dtbs
    │   ├── sifive
    │   │   └── hifive-unleashed-a00.dtb
    │   └── thead
    │       ├── fire-emu-crash.dtb
    │       ├── fire-emu.dtb
    │       ├── fire-emu-gpu-dpu-dsi0.dtb
    │       ├── fire-emu-soc-base.dtb
    │       ├── fire-emu-soc-c910x4.dtb
    │       ├── fire-emu-vi-dsp-vo.dtb
    │       ├── fire-emu-vi-vp-vo.dtb
    │       ├── ice.dtb
    │       ├── light-ant-discrete-crash.dtb
    │       ├── light-ant-discrete.dtb
    │       ├── light-ant-ref-crash.dtb
    │       ├── light-ant-ref.dtb
    │       ├── light-a-product.dtb
    │       ├── light-a-ref-dsi0.dtb
    │       ├── light-a-ref-dsi0-hdmi.dtb
    │       ├── light-a-ref.dtb
    │       ├── light-a-val-android.dtb
    │       ├── light-a-val-audio.dtb
    │       ├── light-a-val-audio-hdmi.dtb
    │       ├── light-a-val-crash.dtb
    │       ├── light-a-val-ddr1G.dtb
    │       ├── light-a-val-ddr2G.dtb
    │       ├── light-a-val-dpi0-dpi1.dtb
    │       ├── light-a-val-dpi0.dtb
    │       ├── light-a-val-dsi0-dsi1.dtb
    │       ├── light-a-val-dsi0.dtb
    │       ├── light-a-val-dsi0-hdmi.dtb
    │       ├── light-a-val-dsi1.dtb
    │       ├── light-a-val.dtb
    │       ├── light-a-val-full.dtb
    │       ├── light-a-val-gpio-keys.dtb
    │       ├── light-a-val-hdmi.dtb
    │       ├── light-a-val-iso7816.dtb
    │       ├── light-a-val-khv.dtb
    │       ├── light-a-val-miniapp-hdmi.dtb
    │       ├── light-a-val-nand.dtb
    │       ├── light-a-val-npu-fce.dtb
    │       ├── light-a-val-sec.dtb
    │       ├── light-a-val-sv.dtb
    │       ├── light-a-val-wcn.dtb
    │       ├── light-beagle.dtb
    │       ├── light-b-power.dtb
    │       ├── light-b-product-crash.dtb
    │       ├── light-b-product-ddr1G.dtb
    │       ├── light-b-product.dtb
    │       ├── light-b-product-miniapp-hdmi.dtb
    │       ├── light-b-ref.dtb
    │       ├── light-fm-emu-audio.dtb
    │       ├── light-fm-emu-dsi0-hdmi.dtb
    │       ├── light-fm-emu-dsp.dtb
    │       ├── light-fm-emu.dtb
    │       ├── light-fm-emu-gpu.dtb
    │       ├── light-fm-emu-hdmi.dtb
    │       ├── light-fm-emu-npu-fce.dtb
    │       ├── light-lpi4a-ddr2G.dtb
    │       ├── light-lpi4a.dtb
    │       └── light_mpw.dtb
    ├── rzc42b6qjxy10wb1wkfmrxjcxsw52015-linux-riscv64-unknown-linux-gnu-5.10.113-thead-1520-Image
    └── vh8624bjxdpxh7ds3nqvqbx992yx63hp-initrd-linux-riscv64-unknown-linux-gnu-5.10.113-thead-1520-initrd

5 directories, 61 files

› cat extlinux.conf
# Generated file, all changes will be lost on nixos-rebuild!

# Change this to e.g. nixos-42 to temporarily boot to an older configuration.
DEFAULT nixos-default

MENU TITLE ------------------------------------------------------------
TIMEOUT 50

LABEL nixos-default
  MENU LABEL NixOS - Default
  LINUX ../nixos/rzc42b6qjxy10wb1wkfmrxjcxsw52015-linux-riscv64-unknown-linux-gnu-5.10.113-thead-1520-Image
  INITRD ../nixos/vh8624bjxdpxh7ds3nqvqbx992yx63hp-initrd-linux-riscv64-unknown-linux-gnu-5.10.113-thead-1520-initrd
  APPEND init=/nix/store/a5gnycsy3cq4ix2k8624649zj8xqzkxc-nixos-system-nixos-23.05.20230624.3ef8b37/init console=ttyS0,115200 root=/dev/mmcblk0p3 rootfstype=ext4 rootwait rw earlycon clk_ignore_unused eth=$ethaddr rootrwoptions=rw,noatime rootrwreset=yes loglevel=4
  FDT ../nixos/rzc42b6qjxy10wb1wkfmrxjcxsw52015-linux-riscv64-unknown-linux-gnu-5.10.113-thead-1520-dtbs/thead/light-lpi4a.dtb


# 看下 init 脚本到底干了些啥，明面上它貌似创建了 /etc /etc/nixos /tmp /run /proc /dev /sys 等文件夹
› cat /nix/store/a5gnycsy3cq4ix2k8624649zj8xqzkxc-nixos-system-nixos-23.05.20230624.3ef8b37/init
#! /nix/store/ny69lqq5dgw5xz6h5ply8cwzifcvplxx-bash-5.2-p15-riscv64-unknown-linux-gnu/bin/bash

systemConfig=/nix/store/a5gnycsy3cq4ix2k8624649zj8xqzkxc-nixos-system-nixos-23.05.20230624.3ef8b37

export HOME=/root PATH="/nix/store/4l7v9y3r2mp2sdhjxjl35yvjsxmrdl4h-coreutils-riscv64-unknown-linux-gnu-9.1/bin:/nix/store/c1xb4z38bvl29vbvc2la2957gv9sdy61-util-linux-riscv64-unknown-linux-gnu-2.38.1-bin/bin"


if [ "${IN_NIXOS_SYSTEMD_STAGE1:-}" != true ]; then
    # Process the kernel command line.
    for o in $(</proc/cmdline); do
        case $o in
            boot.debugtrace)
                # Show each command.
                set -x
                ;;
        esac
    done


    # Print a greeting.
    echo
    echo -e "\e[1;32m<<< NixOS Stage 2 >>>\e[0m"
    echo


    # Normally, stage 1 mounts the root filesystem read/writable.
    # However, in some environments, stage 2 is executed directly, and the
    # root is read-only.  So make it writable here.
    if [ -z "$container" ]; then
        mount -n -o remount,rw none /
    fi
fi


# Likewise, stage 1 mounts /proc, /dev and /sys, so if we don't have a
# stage 1, we need to do that here.
if [ ! -e /proc/1 ]; then
    specialMount() {
        local device="$1"
        local mountPoint="$2"
        local options="$3"
        local fsType="$4"

        # We must not overwrite this mount because it's bind-mounted
        # from stage 1's /run
        if [ "${IN_NIXOS_SYSTEMD_STAGE1:-}" = true ] && [ "${mountPoint}" = /run ]; then
            return
        fi

        install -m 0755 -d "$mountPoint"
        mount -n -t "$fsType" -o "$options" "$device" "$mountPoint"
    }
    source /nix/store/z1b5brgask2dvsq2gjkk8vc9rv5r2c0y-mounts.sh
fi


if [ "${IN_NIXOS_SYSTEMD_STAGE1:-}" = true ]; then
    echo "booting system configuration ${systemConfig}"
else
    echo "booting system configuration $systemConfig" > /dev/kmsg
fi


# Make /nix/store a read-only bind mount to enforce immutability of
# the Nix store.  Note that we can't use "chown root:nixbld" here
# because users/groups might not exist yet.
# Silence chown/chmod to fail gracefully on a readonly filesystem
# like squashfs.
chown -f 0:30000 /nix/store
chmod -f 1775 /nix/store
if [ -n "1" ]; then
    if ! [[ "$(findmnt --noheadings --output OPTIONS /nix/store)" =~ ro(,|$) ]]; then
        if [ -z "$container" ]; then
            mount --bind /nix/store /nix/store
        else
            mount --rbind /nix/store /nix/store
        fi
        mount -o remount,ro,bind /nix/store
    fi
fi


if [ "${IN_NIXOS_SYSTEMD_STAGE1:-}" != true ]; then
    # Use /etc/resolv.conf supplied by systemd-nspawn, if applicable.
    if [ -n "" ] && [ -e /etc/resolv.conf ]; then
        resolvconf -m 1000 -a host </etc/resolv.conf
    fi


    # Log the script output to /dev/kmsg or /run/log/stage-2-init.log.
    # Only at this point are all the necessary prerequisites ready for these commands.
    exec {logOutFd}>&1 {logErrFd}>&2
    if test -w /dev/kmsg; then
        exec > >(tee -i /proc/self/fd/"$logOutFd" | while read -r line; do
            if test -n "$line"; then
                echo "<7>stage-2-init: $line" > /dev/kmsg
            fi
        done) 2>&1
        exec > >(tee -i /run/log/stage-2-init.log) 2>&1
    fi
fi


# Required by the activation script
install -m 0755 -d /etc /etc/nixos
install -m 01777 -d /tmp


# Run the script that performs all configuration activation that does
# not have to be done at boot time.
echo "running activation script..."
$systemConfig/activate


# Record the boot configuration.
ln -sfn "$systemConfig" /run/booted-system


# Run any user-specified commands.
/nix/store/ny69lqq5dgw5xz6h5ply8cwzifcvplxx-bash-5.2-p15-riscv64-unknown-linux-gnu/bin/bash /nix/store/b63lb8ssxjzdwdvrn39k73vavlk8kinj-local-cmds


# Ensure systemd doesn't try to populate /etc, by forcing its first-boot
# heuristic off. It doesn't matter what's in /etc/machine-id for this purpose,
# and systemd will immediately fill in the file when it starts, so just
# creating it is enough. This `: >>` pattern avoids forking and avoids changing
# the mtime if the file already exists.
: >> /etc/machine-id


# No need to restore the stdout/stderr streams we never redirected and
# especially no need to start systemd
if [ "${IN_NIXOS_SYSTEMD_STAGE1:-}" != true ]; then
    # Reset the logging file descriptors.
    exec 1>&$logOutFd 2>&$logErrFd
    exec {logOutFd}>&- {logErrFd}>&-


    # Start systemd in a clean environment.
    echo "starting systemd..."
    exec /run/current-system/systemd/lib/systemd/systemd "$@"
fi



# 再看看其中的 $systemConfig/activate 都干了些啥
# 能看到它就是继续生成与链接各种 Linux 运行必备的 FHS 文件树，以及各种必备的文件
# 比如 /bin/sh /home /root /etc /var 等等
› cat /nix/store/a5gnycsy3cq4ix2k8624649zj8xqzkxc-nixos-system-nixos-23.05.20230624.3ef8b37/activate
#!/nix/store/ny69lqq5dgw5xz6h5ply8cwzifcvplxx-bash-5.2-p15-riscv64-unknown-linux-gnu/bin/bash

systemConfig='/nix/store/a5gnycsy3cq4ix2k8624649zj8xqzkxc-nixos-system-nixos-23.05.20230624.3ef8b37'

export PATH=/empty
for i in /nix/store/4l7v9y3r2mp2sdhjxjl35yvjsxmrdl4h-coreutils-riscv64-unknown-linux-gnu-9.1 /nix/store/00k2kgxrxx8nrs9sqrajl43aabg58655-gnugrep-riscv64-unknown-linux-gnu-3.7 /nix/store/pjsjh36lkn6jqina5l30609d8ldyqw7g-findutils-riscv64-unknown-linux-gnu-4.9.0 /nix/store/n0wk98079d81zaa37ll4nnkh0gnnjp45-getent-glibc-riscv64-unknown-linux-gnu-2.37-8 /nix/store/j3vh88d4kkpgnjdpxhqibpjqa4x59pzy-glibc-riscv64-unknown-linux-gnu-2.37-8-bin /nix/store/wj90d7n8xfk163vwyg74fvnxh88fsp6h-shadow-riscv64-unknown-linux-gnu-4.13 /nix/store/csi20f6aksz8fdcjb7sz9a860vjd4v9g-net-tools-riscv64-unknown-linux-gnu-2.10 /nix/store/c1xb4z38bvl29vbvc2la2957gv9sdy61-util-linux-riscv64-unknown-linux-gnu-2.38.1-bin; do
    PATH=$PATH:$i/bin:$i/sbin
done

_status=0
trap "_status=1 _localstatus=\$?" ERR

# Ensure a consistent umask.
umask 0022

#### Activation script snippet specialfs:
_localstatus=0
specialMount() {
  local device="$1"
  local mountPoint="$2"
  local options="$3"
  local fsType="$4"

  if mountpoint -q "$mountPoint"; then
    local options="remount,$options"
  else
    mkdir -m 0755 -p "$mountPoint"
  fi
  mount -t "$fsType" -o "$options" "$device" "$mountPoint"
}
source /nix/store/z1b5brgask2dvsq2gjkk8vc9rv5r2c0y-mounts.sh


if (( _localstatus > 0 )); then
  printf "Activation script snippet '%s' failed (%s)\n" "specialfs" "$_localstatus"
fi

#### Activation script snippet binfmt:
_localstatus=0
mkdir -p -m 0755 /run/binfmt



if (( _localstatus > 0 )); then
  printf "Activation script snippet '%s' failed (%s)\n" "binfmt" "$_localstatus"
fi

#### Activation script snippet stdio:
_localstatus=0


if (( _localstatus > 0 )); then
  printf "Activation script snippet '%s' failed (%s)\n" "stdio" "$_localstatus"
fi

#### Activation script snippet binsh:
_localstatus=0
# Create the required /bin/sh symlink; otherwise lots of things
# (notably the system() function) won't work.
mkdir -m 0755 -p /bin
ln -sfn "/nix/store/qs8dvkg2719slcc6rvv89whphg697cwm-bash-interactive-5.2-p15-riscv64-unknown-linux-gnu/bin/sh" /bin/.sh.tmp
mv /bin/.sh.tmp /bin/sh # atomically replace /bin/sh


if (( _localstatus > 0 )); then
  printf "Activation script snippet '%s' failed (%s)\n" "binsh" "$_localstatus"
fi

#### Activation script snippet check-manual-docbook:
_localstatus=0
if [[ $(cat /nix/store/v3hlwi9fqqhgwsggd5p478rgmsqxfph5-options-used-docbook) = 1 ]]; then
  echo -e "\e[31;1mwarning\e[0m: This configuration contains option documentation in docbook." \
          "Support for docbook is deprecated and will be removed after NixOS 23.05." \
          "See nix-store --read-log /nix/store/0z3bpdvagjpmpl7m2i4ajzjyg6cipc8a-options.json.drv"
fi


if (( _localstatus > 0 )); then
  printf "Activation script snippet '%s' failed (%s)\n" "check-manual-docbook" "$_localstatus"
fi

#### Activation script snippet domain:
_localstatus=0


if (( _localstatus > 0 )); then
  printf "Activation script snippet '%s' failed (%s)\n" "domain" "$_localstatus"
fi

#### Activation script snippet users:
_localstatus=0
install -m 0700 -d /root
install -m 0755 -d /home

/nix/store/r5wdgk9pwj7bvff208vsd9a821b9dw0c-perl-riscv64-unknown-linux-gnu-5.36.0-env/bin/perl \
-w /nix/store/jb6kmxd6ixbcb8s338ah2pdz26n0bbz4-update-users-groups.pl /nix/store/yjjxriwk6s7k14hrkd4mkmixmj1vskv5-users-groups.json


if (( _localstatus > 0 )); then
  printf "Activation script snippet '%s' failed (%s)\n" "users" "$_localstatus"
fi

#### Activation script snippet groups:
_localstatus=0


if (( _localstatus > 0 )); then
  printf "Activation script snippet '%s' failed (%s)\n" "groups" "$_localstatus"
fi

#### Activation script snippet etc:
_localstatus=0
# Set up the statically computed bits of /etc.
echo "setting up /etc..."
/nix/store/h1hh2x1zj7h7ih36jy6482x01976cyhd-perl-riscv64-unknown-linux-gnu-5.36.0-env/bin/perl /nix/store/rg5rf512szdxmnj9qal3wfdnpfsx38qi-setup-etc.pl /nix/store/b154qqwp6pybryjrdn9yfcvckipn5ybj-etc/etc


if (( _localstatus > 0 )); then
  printf "Activation script snippet '%s' failed (%s)\n" "etc" "$_localstatus"
fi

#### Activation script snippet hashes:
_localstatus=0
users=()
while IFS=: read -r user hash tail; do
  if [[ "$hash" = "$"* && ! "$hash" =~ ^\$(y|gy|7|2b|2y|2a|6)\$ ]]; then
    users+=("$user")
  fi
done </etc/shadow

if (( "${#users[@]}" )); then
  echo "
WARNING: The following user accounts rely on password hashing algorithms
that have been removed. They need to be renewed as soon as possible, as
they do prevent their users from logging in."
  printf ' - %s\n' "${users[@]}"
fi


if (( _localstatus > 0 )); then
  printf "Activation script snippet '%s' failed (%s)\n" "hashes" "$_localstatus"
fi

#### Activation script snippet hostname:
_localstatus=0
hostname "nixos"


if (( _localstatus > 0 )); then
  printf "Activation script snippet '%s' failed (%s)\n" "hostname" "$_localstatus"
fi

#### Activation script snippet modprobe:
_localstatus=0
# Allow the kernel to find our wrapped modprobe (which searches
# in the right location in the Nix store for kernel modules).
# We need this when the kernel (or some module) auto-loads a
# module.
echo /nix/store/zafa80062xl2sybshivrz81qa38nas5y-kmod-riscv64-unknown-linux-gnu-30/bin/modprobe > /proc/sys/kernel/modprobe


if (( _localstatus > 0 )); then
  printf "Activation script snippet '%s' failed (%s)\n" "modprobe" "$_localstatus"
fi

#### Activation script snippet nix:
_localstatus=0
install -m 0755 -d /nix/var/nix/{gcroots,profiles}/per-user

# Subscribe the root user to the NixOS channel by default.
if [ ! -e "/root/.nix-channels" ]; then
    echo "https://nixos.org/channels/nixos-23.05 nixos" > "/root/.nix-channels"
fi


if (( _localstatus > 0 )); then
  printf "Activation script snippet '%s' failed (%s)\n" "nix" "$_localstatus"
fi

#### Activation script snippet systemd-timesyncd-init-clock:
_localstatus=0
if ! [ -f /var/lib/systemd/timesync/clock ]; then
  test -d /var/lib/systemd/timesync || mkdir -p /var/lib/systemd/timesync
  touch /var/lib/systemd/timesync/clock
fi


if (( _localstatus > 0 )); then
  printf "Activation script snippet '%s' failed (%s)\n" "systemd-timesyncd-init-clock" "$_localstatus"
fi

#### Activation script snippet udevd:
_localstatus=0
# The deprecated hotplug uevent helper is not used anymore
if [ -e /proc/sys/kernel/hotplug ]; then
  echo "" > /proc/sys/kernel/hotplug
fi

# Allow the kernel to find our firmware.
if [ -e /sys/module/firmware_class/parameters/path ]; then
  echo -n "/nix/store/h4hgs3gig9l1x1d15v3cnlq11hg4p1r0-firmware/lib/firmware" > /sys/module/firmware_class/parameters/path
fi


if (( _localstatus > 0 )); then
  printf "Activation script snippet '%s' failed (%s)\n" "udevd" "$_localstatus"
fi

#### Activation script snippet usrbinenv:
_localstatus=0
mkdir -m 0755 -p /usr/bin
ln -sfn /nix/store/4l7v9y3r2mp2sdhjxjl35yvjsxmrdl4h-coreutils-riscv64-unknown-linux-gnu-9.1/bin/env /usr/bin/.env.tmp
mv /usr/bin/.env.tmp /usr/bin/env # atomically replace /usr/bin/env


if (( _localstatus > 0 )); then
  printf "Activation script snippet '%s' failed (%s)\n" "usrbinenv" "$_localstatus"
fi

#### Activation script snippet var:
_localstatus=0
# Various log/runtime directories.

mkdir -m 1777 -p /var/tmp

# Empty, immutable home directory of many system accounts.
mkdir -p /var/empty
# Make sure it's really empty
/nix/store/2fw7rr6yaaspkwwix771lcdwj02a3qxx-e2fsprogs-riscv64-unknown-linux-gnu-1.46.6-bin/bin/chattr -f -i /var/empty || true
find /var/empty -mindepth 1 -delete
chmod 0555 /var/empty
chown root:root /var/empty
/nix/store/2fw7rr6yaaspkwwix771lcdwj02a3qxx-e2fsprogs-riscv64-unknown-linux-gnu-1.46.6-bin/bin/chattr -f +i /var/empty || true


if (( _localstatus > 0 )); then
  printf "Activation script snippet '%s' failed (%s)\n" "var" "$_localstatus"
fi

#### Activation script snippet wrappers:
_localstatus=0
chmod 755 "/run/wrappers"

# We want to place the tmpdirs for the wrappers to the parent dir.
wrapperDir=$(mktemp --directory --tmpdir="/run/wrappers" wrappers.XXXXXXXXXX)
chmod a+rx "$wrapperDir"

cp /nix/store/ms8338dmzf45grswqknyghvzfszv6cby-security-wrapper-riscv64-unknown-linux-gnu/bin/security-wrapper "$wrapperDir/chsh"
echo -n "/nix/store/wj90d7n8xfk163vwyg74fvnxh88fsp6h-shadow-riscv64-unknown-linux-gnu-4.13/bin/chsh" > "$wrapperDir/chsh.real"

# Prevent races
chmod 0000 "$wrapperDir/chsh"
chown root:root "$wrapperDir/chsh"

chmod "u+s,g-s,u+rx,g+x,o+x" "$wrapperDir/chsh"

cp /nix/store/ms8338dmzf45grswqknyghvzfszv6cby-security-wrapper-riscv64-unknown-linux-gnu/bin/security-wrapper "$wrapperDir/dbus-daemon-launch-helper"
echo -n "/nix/store/3x1cpq5axfwygjssjg42clfvi085xjgp-dbus-riscv64-unknown-linux-gnu-1.14.6/libexec/dbus-daemon-launch-helper" > "$wrapperDir/dbus-daemon-launch-helper.real"

# Prevent races
chmod 0000 "$wrapperDir/dbus-daemon-launch-helper"
chown root:messagebus "$wrapperDir/dbus-daemon-launch-helper"

chmod "u+s,g-s,u+rx,g+rx,o-rx" "$wrapperDir/dbus-daemon-launch-helper"

cp /nix/store/ms8338dmzf45grswqknyghvzfszv6cby-security-wrapper-riscv64-unknown-linux-gnu/bin/security-wrapper "$wrapperDir/fusermount"
echo -n "/nix/store/770sky5x7dbcmzc2xahvws7pw250bj2s-fuse-riscv64-unknown-linux-gnu-2.9.9/bin/fusermount" > "$wrapperDir/fusermount.real"

# Prevent races
chmod 0000 "$wrapperDir/fusermount"
chown root:root "$wrapperDir/fusermount"

chmod "u+s,g-s,u+rx,g+x,o+x" "$wrapperDir/fusermount"

cp /nix/store/ms8338dmzf45grswqknyghvzfszv6cby-security-wrapper-riscv64-unknown-linux-gnu/bin/security-wrapper "$wrapperDir/fusermount3"
echo -n "/nix/store/gkxzqirzcf548w4421jlwhn1imp4979d-fuse-riscv64-unknown-linux-gnu-3.11.0/bin/fusermount3" > "$wrapperDir/fusermount3.real"

# Prevent races
chmod 0000 "$wrapperDir/fusermount3"
chown root:root "$wrapperDir/fusermount3"

chmod "u+s,g-s,u+rx,g+x,o+x" "$wrapperDir/fusermount3"

cp /nix/store/ms8338dmzf45grswqknyghvzfszv6cby-security-wrapper-riscv64-unknown-linux-gnu/bin/security-wrapper "$wrapperDir/mount"
echo -n "/nix/store/c1xb4z38bvl29vbvc2la2957gv9sdy61-util-linux-riscv64-unknown-linux-gnu-2.38.1-bin/bin/mount" > "$wrapperDir/mount.real"

# Prevent races
chmod 0000 "$wrapperDir/mount"
chown root:root "$wrapperDir/mount"

chmod "u+s,g-s,u+rx,g+x,o+x" "$wrapperDir/mount"

cp /nix/store/ms8338dmzf45grswqknyghvzfszv6cby-security-wrapper-riscv64-unknown-linux-gnu/bin/security-wrapper "$wrapperDir/newgidmap"
echo -n "/nix/store/wj90d7n8xfk163vwyg74fvnxh88fsp6h-shadow-riscv64-unknown-linux-gnu-4.13/bin/newgidmap" > "$wrapperDir/newgidmap.real"

# Prevent races
chmod 0000 "$wrapperDir/newgidmap"
chown root:root "$wrapperDir/newgidmap"

chmod "u+s,g-s,u+rx,g+x,o+x" "$wrapperDir/newgidmap"

cp /nix/store/ms8338dmzf45grswqknyghvzfszv6cby-security-wrapper-riscv64-unknown-linux-gnu/bin/security-wrapper "$wrapperDir/newgrp"
echo -n "/nix/store/wj90d7n8xfk163vwyg74fvnxh88fsp6h-shadow-riscv64-unknown-linux-gnu-4.13/bin/newgrp" > "$wrapperDir/newgrp.real"

# Prevent races
chmod 0000 "$wrapperDir/newgrp"
chown root:root "$wrapperDir/newgrp"

chmod "u+s,g-s,u+rx,g+x,o+x" "$wrapperDir/newgrp"

cp /nix/store/ms8338dmzf45grswqknyghvzfszv6cby-security-wrapper-riscv64-unknown-linux-gnu/bin/security-wrapper "$wrapperDir/newuidmap"
echo -n "/nix/store/wj90d7n8xfk163vwyg74fvnxh88fsp6h-shadow-riscv64-unknown-linux-gnu-4.13/bin/newuidmap" > "$wrapperDir/newuidmap.real"

# Prevent races
chmod 0000 "$wrapperDir/newuidmap"
chown root:root "$wrapperDir/newuidmap"

chmod "u+s,g-s,u+rx,g+x,o+x" "$wrapperDir/newuidmap"

cp /nix/store/ms8338dmzf45grswqknyghvzfszv6cby-security-wrapper-riscv64-unknown-linux-gnu/bin/security-wrapper "$wrapperDir/passwd"
echo -n "/nix/store/wj90d7n8xfk163vwyg74fvnxh88fsp6h-shadow-riscv64-unknown-linux-gnu-4.13/bin/passwd" > "$wrapperDir/passwd.real"

# Prevent races
chmod 0000 "$wrapperDir/passwd"
chown root:root "$wrapperDir/passwd"

chmod "u+s,g-s,u+rx,g+x,o+x" "$wrapperDir/passwd"

cp /nix/store/ms8338dmzf45grswqknyghvzfszv6cby-security-wrapper-riscv64-unknown-linux-gnu/bin/security-wrapper "$wrapperDir/ping"
echo -n "/nix/store/vwzakxlkma6lg0yd5ilx0cbj69whpm38-iputils-riscv64-unknown-linux-gnu-20221126/bin/ping" > "$wrapperDir/ping.real"

# Prevent races
chmod 0000 "$wrapperDir/ping"
chown root:root "$wrapperDir/ping"

# Set desired capabilities on the file plus cap_setpcap so
# the wrapper program can elevate the capabilities set on
# its file into the Ambient set.
/nix/store/cpnqm7m872fsqky7bjbqwy8llbbf33l9-libcap-riscv64-unknown-linux-gnu-2.68/bin/setcap "cap_setpcap,cap_net_raw+p" "$wrapperDir/ping"

# Set the executable bit
chmod u+rx,g+x,o+x "$wrapperDir/ping"

cp /nix/store/ms8338dmzf45grswqknyghvzfszv6cby-security-wrapper-riscv64-unknown-linux-gnu/bin/security-wrapper "$wrapperDir/sg"
echo -n "/nix/store/wj90d7n8xfk163vwyg74fvnxh88fsp6h-shadow-riscv64-unknown-linux-gnu-4.13/bin/sg" > "$wrapperDir/sg.real"

# Prevent races
chmod 0000 "$wrapperDir/sg"
chown root:root "$wrapperDir/sg"

chmod "u+s,g-s,u+rx,g+x,o+x" "$wrapperDir/sg"

cp /nix/store/ms8338dmzf45grswqknyghvzfszv6cby-security-wrapper-riscv64-unknown-linux-gnu/bin/security-wrapper "$wrapperDir/su"
echo -n "/nix/store/jy1c86m85801g025pd6gs9ljhj301bsi-shadow-riscv64-unknown-linux-gnu-4.13-su/bin/su" > "$wrapperDir/su.real"

# Prevent races
chmod 0000 "$wrapperDir/su"
chown root:root "$wrapperDir/su"

chmod "u+s,g-s,u+rx,g+x,o+x" "$wrapperDir/su"

cp /nix/store/ms8338dmzf45grswqknyghvzfszv6cby-security-wrapper-riscv64-unknown-linux-gnu/bin/security-wrapper "$wrapperDir/sudo"
echo -n "/nix/store/54s80ssm7q2y1aqaavnrkvw7b4hkdm1g-sudo-riscv64-unknown-linux-gnu-1.9.13p3/bin/sudo" > "$wrapperDir/sudo.real"

# Prevent races
chmod 0000 "$wrapperDir/sudo"
chown root:root "$wrapperDir/sudo"

chmod "u+s,g-s,u+rx,g+x,o+x" "$wrapperDir/sudo"

cp /nix/store/ms8338dmzf45grswqknyghvzfszv6cby-security-wrapper-riscv64-unknown-linux-gnu/bin/security-wrapper "$wrapperDir/sudoedit"
echo -n "/nix/store/54s80ssm7q2y1aqaavnrkvw7b4hkdm1g-sudo-riscv64-unknown-linux-gnu-1.9.13p3/bin/sudoedit" > "$wrapperDir/sudoedit.real"

# Prevent races
chmod 0000 "$wrapperDir/sudoedit"
chown root:root "$wrapperDir/sudoedit"

chmod "u+s,g-s,u+rx,g+x,o+x" "$wrapperDir/sudoedit"

cp /nix/store/ms8338dmzf45grswqknyghvzfszv6cby-security-wrapper-riscv64-unknown-linux-gnu/bin/security-wrapper "$wrapperDir/umount"
echo -n "/nix/store/c1xb4z38bvl29vbvc2la2957gv9sdy61-util-linux-riscv64-unknown-linux-gnu-2.38.1-bin/bin/umount" > "$wrapperDir/umount.real"

# Prevent races
chmod 0000 "$wrapperDir/umount"
chown root:root "$wrapperDir/umount"

chmod "u+s,g-s,u+rx,g+x,o+x" "$wrapperDir/umount"

cp /nix/store/ms8338dmzf45grswqknyghvzfszv6cby-security-wrapper-riscv64-unknown-linux-gnu/bin/security-wrapper "$wrapperDir/unix_chkpwd"
echo -n "/nix/store/cffy2kkpwgams7b94ixrslvf9nny88pv-linux-pam-riscv64-unknown-linux-gnu-1.5.2/bin/unix_chkpwd" > "$wrapperDir/unix_chkpwd.real"

# Prevent races
chmod 0000 "$wrapperDir/unix_chkpwd"
chown root:root "$wrapperDir/unix_chkpwd"

chmod "u+s,g-s,u+rx,g+x,o+x" "$wrapperDir/unix_chkpwd"


if [ -L /run/wrappers/bin ]; then
  # Atomically replace the symlink
  # See https://axialcorps.com/2013/07/03/atomically-replacing-files-and-directories/
  old=$(readlink -f /run/wrappers/bin)
  if [ -e "/run/wrappers/bin-tmp" ]; then
    rm --force --recursive "/run/wrappers/bin-tmp"
  fi
  ln --symbolic --force --no-dereference "$wrapperDir" "/run/wrappers/bin-tmp"
  mv --no-target-directory "/run/wrappers/bin-tmp" "/run/wrappers/bin"
  rm --force --recursive "$old"


# Make this configuration the current configuration.
# The readlink is there to ensure that when $systemConfig = /system
# (which is a symlink to the store), /run/current-system is still
# used as a garbage collection root.
ln -sfn "$(readlink -f "$systemConfig")" /run/current-system

# Prevent the current configuration from being garbage-collected.
mkdir -p /nix/var/nix/gcroots
ln -sfn /run/current-system /nix/var/nix/gcroots/current-system

exit $_status
```

