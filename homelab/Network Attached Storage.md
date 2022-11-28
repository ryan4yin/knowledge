# Network Attached Storage

Network Attached Storage 即网络存储系统，缩写为 NAS。

在家家户户都接入了互联网络的今天，家庭里搭一个 NAS 系统的好处还是很明显的—— NAS 中的文件能够在家里所有联网设备之间无缝流转，影视、音乐、照片、文档，或者将手机等移动设备中的数据备份到家庭 NAS，都非常方便。

## NAS 存储共享协议选择

NAS 存储共享协议主要有这几种：

- **ISCSI**: 一个复杂的块存储共享协议，可直接提供裸磁盘给远程主机挂载。
  - 许多 ISCSI 的协议实现比较拉，导致性能问题。OpenMediaVault 的 tgt 插件就是其中典型。
- **SMB/CIFS**: 微软研发的一种文件共享协议，对延迟比较敏感，只适合在局域网内使用。
  - 好处是兼容性好，获得了各类操作系统、软件的广泛支持。
  - Windows 挂载(powershell): `New-SmbGlobalMapping -LocalPath z: -RemotePath \\my-host\myshare -Persistent $true`
    - 或者直接在「我的电脑」=>「映射网络驱动器」，输入盘号跟 WebDAV/SMB 地址点击连接即可。
  - Linux 挂载:
    - 首先安装 `cifs-utils`，一般直接 apt/yum 安装就行
    - `sudo mount -t cifs //my-host/myshare /mnt -o vers=2.0,guest,uid=0,gid=0,dir_mode=0755,file_mode=0755,mfsymlinks`
    - 也可以将账号密码单独保存到文件以提升安全性，建议网上搜索相关信息。
  - Android 挂载：建议使用 [X-plore File Manager][X-plore File Manager] 或者 [Total Commander][Total Commander]
  - MacOS 挂载: 「Finder」=>「Go」=>「Connect to Server」，输入 SMB 地址即可，格式为 `smb://host/share-dir`

- **WebDAV**: HTTP 协议的一个拓展，安全性高，在公网局域网上都可使用它部署文件访问服务。
  - 对延迟不敏感，常被用于各类公网的数据同步，比如各类写作软件都支持 WebDAV 数据同步。
  - Windows 挂载(powershell): `New-PSDrive -Name S -PSProvider FileSystem -Root '\\live.sysinternals.com\Tools'`
    - 注意 URI 需要去掉 `https:` 头部！
    - 或者直接在「我的电脑」=>「映射网络驱动器」，输入盘号跟 WebDAV/SMB 地址点击连接即可。
  - Linux 挂载:
    - 首先安装 `davfs2`，一般直接 apt/yum 安装就行
    - `sudo mount -t davfs https://xxxxxx /mnt/webdav -o username=xxx,password=your-password,gid=1000,uid=1000`
  - Android 挂载: 建议使用 [X-plore File Manager][X-plore File Manager] 或者 [Total Commander][Total Commander]
  - MacOS 挂载: 「Finder」=>「Go」=>「Connect to Server」，输入 SMB 地址即可，格式为 `https://host/share-dir`
- **SFTP**: 使用 SSH 协议进行文件传输，安全性跟兼容性都很高，也是很流行的一种公网数据分享方法。
- **NFS**: 最初由 Sun 公司开发的协议，广泛应用于类 Unix 系统，因而也在企业级远程存储场景中被广泛使用。
  - NAS 场景下一般较少使用此协议

总的来说，一般建议使用 SMB 或者 WebDAV 作为远程数据共享协议，其中 SMB 仅适用于内网，而 WebDAV 更通用些。

仅在明确需要裸磁盘的场景下，才应该使用 ISCSI 协议，而且要考虑到客户端/服务端的 ISCSI 底层实现性能如何，否则很容易遇到性能问题。


## 如何选择 NAS 系统

在折腾了 [OpenMediaVault](https://www.openmediavault.org/)、[TrueNAS](https://github.com/truenas) 以及 Windows Server 后，我发现直接 docker 跑几个小容器提供 WebDAV 网络存储是符合我个人需求的。

我实际没有 ISCSI/SMB 等协议的需求，而且 OpenMediaVault 的 ISCSI 插件性能还奇差，Windows Server 我也不太感冒，TrueNAS 底层是 freebsd 也玩不明白。
所以直接用 docker 跑几个 Web 文件服务器跟 webdav 服务器，实际就完全 cover 住我的需求了，根本没必要搞啥专用 NAS 系统。

所以我现在的方案是，使用 docker-compose 跑下面这些软件，提供所有我需要的功能：

- WebDAV 服务器
  - [sftpgo](https://github.com/drakkan/sftpgo): 一个文件共享服务器，支持 sftp、webdav、ftp/s 等协议，支持本地存储，或者使用 AWS/GCP/Azure 的对象存储。
  - [dufs](https://github.com/sigoden/dufs): 一个 rust 写的轻量级文件服务器，支持文件上传/下载/搜索/WebDAV...
    - 第一行代码提交于 2022/5/22，非常年轻所以请谨慎选用
- 数据同步与备份
  - [syncthing](https://github.com/syncthing/syncthing): 在多台机器之间进行持续性的增量同步，支持多操作系统，包括 Android/IOS，也提供 UI 界面。
    - 跟我们在 linux 上常用的 rsync 有点类似，不过 rsync 是一个强大的命令行工具
  - [rclone](https://github.com/rclone/rclone): 支持将数据 copy 到各类云存储或者 WebDAV/SMB/NFS 服务器中
    - 跟 syncthing 的区别是，它并不在后台做持续性的同步，而是通过一条条命令执行对应的同步动作。
- Web 文件服务器
  - [filebrowser](https://github.com/filebrowser/filebrowser): 文件浏览器，支持查看、上传、下载
- 其他影视、文档系统
  - [jellyfin](https://github.com/jellyfin/jellyfin): 影音系统
  - ...

## 使用 ubuntu cloud image 自建 NAS 系统踩过的坑

### 1. Ubuntu Cloud Image 无法识别到 USB 设备

现象：

- 在尝试使用 PVE 将 USB 接口直通到 Ubuntu Cloud Image 启动的虚拟机作为 NAS 系统时，发现 `lsblk` 根本无法找到我的 USB 硬盘
- 换成我笔记本接硬盘盒，能够正常识别并挂载硬盘
- 使用 `lsusb` 不会报错，但是也看不到任何内容
- 使用 `lspci` 能找到 USB 对应的 PCI 设备
- 进一步使用 `cat /proc/modules | grep usb` 与 `lsmod | grep usb` 均查不到任何 usb 相关的内核模块
  - 而在我笔记本上 `lsmod | grep usb` 能够输出 `usb_storage` `usb_core` 等多项内核模块。 
- 再用 `modprobe usb` 会提示 `modprobe: FATAL: Module usb not found in directory /lib/modules/5.15.0-1021-kvm`

问题原因很明显了，Ubuntu 根本没有为 cloud image 预置 usb 内核模块，所以才有这个问题...

进一步搜索发现这个帖子：[What's the difference between ubuntu's amd64-disk-kvm.img and the regular amd64.img cloud images?](https://askubuntu.com/questions/1315370/whats-the-difference-between-ubuntus-amd64-disk-kvm-img-and-the-regular-amd64)，解答了我的疑惑。

原因是，我使用了 ubuntu 为 cloud 环境做了精简的 kvm 内核，非常轻量，但是缺少 usb 等常用内核模块。

对于 NAS 外接存储这个场景，我应该使用不以 kvm 结尾的 ubuntu cloud image，换了个基础镜像后问题就解决了~

### 2. Linux 如何自动挂载 USB 硬盘合

网上很多文章会教你使用 `/etc/fstab` 去挂载 USB 硬盘，我得说这是一项非常危险的操作！因为 `/etc/fstab` 出任何问题都将导致系统无法启动，也就是说如果对应的 USB 设备接触不良了，或者被拔掉了，机器可能就启动不了了！（猜测哈，我有时间验证下...）

更合适的办法是使用在各类桌面 Linux 中广泛应用的 [udisks2](https://wiki.archlinux.org/title/Udisks)

以 ubuntu cloud image generic 为例，首先安装并启用 udisks2:

```shell
sudo apt install udisks2
sudo systemctl enable udisks2
sudo systemctl start udisks2

# 查看 usidks2 daemon 的状态
sudo systemctl status udisks2
# 这里我看到错误提示显示，需要安装些依赖，所以再执行如下命令
sudo apt-get install libblockdev-crypto2 libblockdev-mdraid2
sudo systemctl restart udisks2
```

接着就可以通过 `udisksctl` 来查看 udisks2 的状态了：

```shell
# udisks2 扫描到的所有磁盘
udisksctl status

# 查看所有磁盘
lsblk

# 手动挂载 /dev/sdb1 块存储设备（会要求输入用户密码）
udisksctl mount -b /dev/sdb1
```

上面的测试都没问题后，现在来实现我们的自动挂载。

经过三小时与 udisks2 以及 policykit/polkit 的搏斗与搜索后，我找到了解决方案，创建 `/etc/polkit-1/localauthority/50-local.d/10-udisks2.pkla`，内容如下：

```conf
[udisks]
Identity=unix-group:plugdev
Action=org.freedesktop.udisks.*
ResultAny=yes
[udisks2]
Identity=unix-group:plugdev
Action=org.freedesktop.udisks2.*
ResultAny=yes
```

然后就可以实现无密码挂载磁盘：

```shell
udisksctl mount --no-user-interaction -b /dev/sdb1
```

实现了免密码挂载后，还需要再进一步实现自动挂载...目前找到比较靠谱的工具是 udiskie:

```shell
# 安装 udiskie
sudo apt install udiskie

# 简单测试下 udiskie 能正常工作
udiskie
```

确认能正常挂载后，接下来为它创建一个 systemd 服务，使它能开机启动启动。添加配置文件 `/usr/lib/systemd/system/udiskie.service`，内容如下：

```conf
[Unit]
Description=Removable disk automounter using udisks

[Service]
Type=simple
# 自动挂载所有磁盘
ExecStart=/usr/bin/udiskie
# 停止前卸载所有挂载
ExecStop=/usr/bin/udiskie-umount -a
Restart=always
# 程序的 user 和 group
# 为了让我的默认用户能读能写，这些都设为 ryan
User=ryan
Group=ryan

[Install]
WantedBy=default.target
```

然后启用 udiskie 服务，就大功告成了：

```shell
sudo systemctl enable udiskie
sudo systemctl start udiskie
sudo systemctl status udiskie
```

现在可以重启下机器，看看自动挂载是否正常工作~

## 参考

- [awesome-webdav](https://github.com/fstanis/awesome-webdav)
- [Adding permissions for udiskie-mount to policykit](https://unix.stackexchange.com/questions/277606/adding-permissions-for-udiskie-mount-to-policykit)

[X-plore File Manager]: https://play.google.com/store/apps/details?id=com.lonelycatgames.Xplore
[Total Commander]: https://play.google.com/store/apps/details?id=com.ghisler.android.TotalCommander
