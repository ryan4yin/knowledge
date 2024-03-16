## Steps to Install Debian 12 Bookworm on a LUKS Encrypted Disk + Secure Boot

First, download an live CD image of Debian 12 Bookworm from <https://www.debian.org/CD/live/>,
choose the `-standard` suffix which comes without a GUI, and copy it to a Ventoy USB drive.

Then, boot Ventoy from the USB drive, choose Debian 12, run the following commands in the live
environment to start a SSH server, so that we can connect to the server to do the installation,
which is more convenient than using the live environment's terminal directly.

```bash
# Become root
sudo -i
# Updating apt is important as live ISOs are behind on packages
apt update
# Install SSH
apt install -y ssh git
# Start SSH daemon
systemctl start ssh
# Set a password for the regular user (we use this to connect in the next step)
useradd -m -s /bin/bash ryan
passwd ryan
usermod -aG sudo ryan
# Find out the IP address
ip addr
```

Then use `ssh -o "StrictHostKeyChecking=no" ryan@x.x.x.x` to connect to the server, note that we use
`StrictHostKeyChecking=no` to skip the host key checking, because the live environment's SSH
server's host key will change every time you boot the live environment.

### 1. Encrypting with LUKS(everything except ESP)

> [Frequently asked questions (FAQ) - cryptsetup](https://gitlab.com/cryptsetup/cryptsetup/wikis/FrequentlyAskedQuestions)

Securing a root file system is where dm-crypt excels, feature and performance-wise. An encrypted
root file system protects everything on the system, it make the system a black box to the attacker.

1. The EFI system partition(ESP) must be left unencrypted, and is mounted at `/boot`
   1. Since the UEFI firmware can only load boot loaders from unencrypted partitions.
2. Secure Boot is enabled, everything in ESP is signed.
3. The BTRFS file system with subvolumes is used for the root partition, and the swap area is a
   swapfile on a dedicated BTRFS subvolume, thus the swap area is also encrypted.

And the boot flow is:

1. The UEFI firmware loads the boot loader from the ESP(`/boot`).
2. The boot loader loads the kernel and initrd from the ESP(`/boot`).
3. **The initrd reads the keyfile from `/dev/sda`(a USB drive)**.
   - You can also use a passphrase, and type it in remotely via SSH. This can be done by
     `dropbear-initramfs`.
4. The initrd unlocks the root partition and mounts it at `/`.
5. The initrd continues the boot process, and hands over the control to the kernel.

Partitioning the disk:

```bash
# Install Nix first.
sh <(curl -L https://nixos.org/nix/install) --daemon

git clone -b pve-cluster https://github.com/ryan4yin/nix-config.git
cd nix-config/pulumi/pve-cluster/

# Generate a keyfile from the true random number generator
KEYFILE=./pve-xxx-keyfile
DEVICE=/dev/sdb
dd bs=8192 count=4 iflag=fullblock if=/dev/random of=$KEYFILE
# Write the keyfile to a USB drive
dd bs=8192 count=4 iflag=fullblock if=$KEYFILE of=$DEVICE

# Partition the disk
nix --experimental-features "nix-command flakes" run github:nix-community/disko -- --mode disko ./disko-fs.nix
```

### 2. Install Debian 12 Bookworm on a LUKS Encrypted Disk

> https://www.debian.org/releases/bookworm/amd64/apds03.en.html

> [dm-crypt/Encrypting an entire system - Arch Wiki](https://wiki.archlinux.org/title/Dm-crypt/Encrypting_an_entire_system)

> [Encrypted /boot - GRUB2 - Arch Wiki](https://wiki.archlinux.org/title/GRUB#Encrypted_/boot)

```bash
# Install a minimal Debian system
apt install -y debootstrap
debootstrap --arch amd64 bookworm /mnt https://mirrors.bfsu.edu.cn/debian/

echo '
# /etc/fstab: static file system information.
#
# file system    mount point   type   options                  dump pass
UUID=abd445a2-f302-4adf-9542-2c6c6ce991aa   /boot         ext4   defaults                 0    2
UUID=2E67-1744   /boot/efi     vfat   defaults                 0    2
proc             /proc         proc   defaults                 0    0

/dev/mapper/crypted /          btrfs  x-initrd.mount,subvol=@root,compress-force=zstd:1 0 0
/dev/mapper/crypted /home      btrfs  x-initrd.mount,subvol=@home,compress-force=zstd:1 0 0
/dev/mapper/crypted /var/lib   btrfs  x-initrd.mount,subvol=@lib,compress-force=zstd:1 0 0
/dev/mapper/crypted /tmp       btrfs  x-initrd.mount,subvol=@tmp,compress-force=zstd:1 0 0
/dev/mapper/crypted /swap      btrfs  subvol=@swap,ro          0    0

/swap/swapfile   /swap/swapfile none  bind,rw                  0    0
' > /mnt/etc/fstab

CRYPT_UUID=$(blkid -s UUID -o value /dev/nvme0n1p3 | tr -d '\n')
KEY_UUID=$(blkid -s UUID -o value /dev/sdb | tr -d '\n')
# `man crypttab` for the documentation of /etc/crypttab
echo "
# name, underlying device, keyfile, cryptsetup options
encrypted UUID=${CRYPT_UUID} /dev/sda luks,discard,keyfile-size=32768,keyfile-offset=0
" > /mnt/etc/crypttab
```

Continue the installation in the chroot environment:

````bash
cd /mnt
mount -t proc /proc proc/
mount --rbind /sys sys/
mount --rbind /dev dev/

# chroot into the installed system
LANG=C.UTF-8 chroot /mnt /bin/bash

export TERM=xterm-color

# install all packages with “standard” priority
tasksel install standard

apt install apt-transport-https ca-certificates


echo "
# 默认注释了源码镜像以提高 apt update 速度，如有需要可自行取消注释
deb https://mirrors.bfsu.edu.cn/debian/ bookworm main contrib non-free non-free-firmware
# deb-src https://mirrors.bfsu.edu.cn/debian/ bookworm main contrib non-free non-free-firmware

deb https://mirrors.bfsu.edu.cn/debian/ bookworm-updates main contrib non-free non-free-firmware
# deb-src https://mirrors.bfsu.edu.cn/debian/ bookworm-updates main contrib non-free non-free-firmware

deb https://mirrors.bfsu.edu.cn/debian/ bookworm-backports main contrib non-free non-free-firmware
# deb-src https://mirrors.bfsu.edu.cn/debian/ bookworm-backports main contrib non-free non-free-firmware

deb https://mirrors.bfsu.edu.cn/debian-security bookworm-security main contrib non-free non-free-firmware
# deb-src https://mirrors.bfsu.edu.cn/debian-security bookworm-security main contrib non-free non-free-firmware
" > /etc/apt/sources.list

# install hardware drivers for amdgpu
apt install -y firmware-amd-graphics libgl1-mesa-dri libglx-mesa0 mesa-vulkan-drivers
# hardware drivers for wired/wireless network(realtek, intel, mediatek)
apt install -y firmware-realtek firmware-iwlwifi firmware-misc-nonfree

# configure locales
apt install -y locales
dpkg-reconfigure locales

# SSH
apt install -y ssh
systemctl enable ssh
passwd root

# install a kernel, will install initrd(initramfs) & vmlinuz(kernel) into /boot
apt search linux-image
apt install -y linux-image-6.1.0-18-amd64

# make /etc/crypttab available as /cryptroot/crypttab in initramfs
echo '
#!/bin/sh
cp /etc/crypttab "${DESTDIR}/cryptroot/crypttab"
exit 0
' > /etc/initramfs-tools/hooks/mkcryptroot
chmod +x /etc/initramfs-tools/hooks/mkcryptroot

# update boot loader and initramfs
# cryptsetup-initramfs add the support for LUKS encrypted root partition
apt install -y grub-efi cryptsetup-initramfs cryptsetup
apt install -y btrfs-progs dosfstools efibootmgr
grub-install --efi-directory /boot/efi --target x86_64-efi --no-floppy --bootloader-id='debian' /dev/nvme0n1
# grub will found the kernel and initrd in /boot, and add them to the boot menu
update-grub
# update-initramfs will generate the initrd for all installed kernels
update-initramfs -c -k all -v

```bash
# inspect the /crypttab in the initrd
mkdir /tmp/x; cd /tmp/x; unmkinitramfs -v /boot/initrd.img-$(uname -r) .
cat cryptroot/crypttab
````

```bash
# exit the chroot environment
exit

# devices
apt-get install -y makedev
cd /dev
MAKEDEV generic

apt clean
reboot
```

```bash
apt install -y cryptsetup btrfs-progs
# fix problems manually
cryptsetup open /dev/nvme0n1p3 encrypted --key-file /dev/sdb --keyfile-size 32768
mkdir -p /mnt/{boot,home,var/lib,tmp}
mount -o compress-force=zstd:1,noatime,subvol=@root /dev/mapper/crypted /mnt
mount /dev/nvme0n1p1 /mnt/boot
mount /dev/nvme0n1p2 /mnt/boot/efi
mount -o compress-force=zstd:1,noatime,subvol=@home /dev/mapper/crypted /mnt/home # mount-1
mount -o compress-force=zstd:1,noatime,subvol=@lib  /dev/mapper/crypted /mnt/var/lib # mount-1
mount -o compress-force=zstd:1,subvol=@tmp          /dev/mapper/crypted /mnt/tmp  # mount-1
mount -o subvol=@swap                               /dev/mapper/crypted /mnt/swap  # mount-1
```

```bash
# set ipaddr and gateway, and up the network
echo "
auto eno1
iface eno1 inet static
        address 192.168.5.176/24
        network 192.168.5.0
        broadcast 192.168.5.255
        gateway 192.168.5.1
        dns-nameservers 223.5.5.5
" > /etc/network/interfaces.d/eno1
systemctl restart networking.service
ip addr show

# install the eseential packages
apt install -y sudo curl rsync
```

Then use `ssh -o "StrictHostKeyChecking=no" ryan@x.x.x.x` to connect to the server.

```bash
hostnamectl set-hostname pve-s500plus.lan
echo " 192.168.5.176 pve-s500plus.lan" >> /etc/hosts

# replace the default gateway to speed up the installation
ip route del default via 192.168.5.1
ip route add default via 192.168.5.101
```
