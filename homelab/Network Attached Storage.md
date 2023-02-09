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
  - Windows 挂载(powershell): `net use Y: http://sftpgo.writefor.fun:10080/ /user:<user> /persistent:YES <passsword>`
    - 注意 windows 默认仅允许基于 https 的 WebDAV 挂载，如果需要挂载 http，需要将注册表中的 `BasicAuthLevel` 修改为 `2`，另外默认的最大文件数仅为 50MB，要调大也得改注册表，详见 [WebDAV Redirector Registry Settings](https://learn.microsoft.com/en-us/iis/publish/using-webdav/using-the-webdav-redirector#webdav-redirector-registry-settings)
    - 或者直接在「我的电脑」=>「映射网络驱动器」，输入盘号跟 WebDAV/SMB 地址点击连接即可
    - 还有个 `New-PSDrive` 也能用于干这个活，但是不好用
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

先说下我的需求：

- 将所有游戏都下载到 NAS 中，Windows PC 主机直接通过挂载远程硬盘玩游戏。
- 通过 SMB/WebDAV 协议，远程挂载 NAS 硬盘，访问其中影音文件，或者共享一些数据。
- 通过 [filebrowser](https://github.com/filebrowser/filebrowser) 提供 Web 文件浏览器，支持查看、上传、下载

在折腾了 [OpenMediaVault](https://www.openmediavault.org/)、[TrueNAS](https://github.com/truenas) 以及 Windows Server 后，我确定了我应该使用 Windows Server 作为我的 NAS 系统，通过 SMB 协议提供服务。

原因列举如下：

- OpenMediaVault
  - SMB/WebDAV 协议插件性能还行，但是不支持快速文件创建，steam 下载游戏时，一个分配磁盘动作就得等到天荒地老了（它会忠实地将分配的磁盘空间全量传输一遍）...
  - ISCSI 插件性能奇差（有高手表示这是协议 fallback 导致的性能损失）
  - 总结：不论是用 SMB/WebDAV 还是 ISCSI 协议，性能都不尽如人意
- Windows Server 2022 DataCenter
  - SMB 协议：具有 SMB3.0、RDMA([SMB Direct](https://learn.microsoft.com/en-us/windows-server/storage/file-server/smb-direct)) 等黑科技，可以快速创建文件，性能非常好。
  - ISCSI 协议性能也很不错
  - 总结：在客户端就是 Windows 的情况下，Windows Server 的黑科技能提供很大加成，非常香。

所以折腾了一圈后，确定了 NAS 系统就用 Windows Server 提供 SMB 协议作为游戏与其他文件存储。

另外再启动一台 linux 主机，通过 SMB 将远程硬盘挂载到该主机上，再通过 docker-compose 运行如下容器：

- 数据备份与同步
  - [syncthing](https://github.com/syncthing/syncthing): 在多台机器之间进行持续性的增量同步，支持多操作系统，包括 Android/IOS，也提供 UI 界面。
    - 跟我们在 linux 上常用的 rsync 有点类似，不过 rsync 是一个强大的命令行工具
  - [rclone](https://github.com/rclone/rclone): 支持将数据 copy 到各类云存储或者 WebDAV/SMB/NFS 服务器中
    - 跟 syncthing 的区别是，它并不在后台做持续性的同步，而是通过一条条命令执行对应的同步动作。
- 数据浏览
  - [filebrowser](https://github.com/filebrowser/filebrowser): 文件浏览器，支持查看、上传、下载
- 影音系统
  - [jellyfin](https://github.com/jellyfin/jellyfin): 影音系统

## 如何使用 Windows Server 2022 DataCenter 作为 SMB 服务器

前面已经简述了我为什么打算用 Windows Server 作为 NAS 系统，那么这里就简述下如何用 Windows Server 作为 SMB 服务器，然后测下 steam 游戏下载与运行效果如何（内网网速 2.5G）。

首先是系统安装，这个没啥好说的，网上找找 Windows Server 2022 的 iso 镜像，安装好后使用 GVLK 批量授权密钥授权，再随便找个 KMS 在线激活服务，敲几行命令就激活了。

系统安装、激活并调整好后，再通过「添加角色或功能」，把「远程桌面」功能跟「SMB 文件共享」、「ISCSI 相关」功能添加上，再重启系统。

重启好后，再进「系统设置」勾选「允许远程桌面」，这样就可以通过微软官方的 [remote-desktop-clients](https://learn.microsoft.com/en-us/windows-server/remote/remote-desktop-services/clients/remote-desktop-clients) 来连接到这台主机的远程桌面了（使用默认的 Administrator 账号即可）。这个 client 是全平台支持的，目前所有桌面系统中远程桌面体验最好的就是 Windows 了。

>MacOS 客户端直接在 AppStore 中锁了区，国区无法下载，但是可以在文档中找到 MacOS remote desktop beta 测试版的安装镜像。

SMB 共享文件夹的创建也非常简单，在服务器管理页面的「文件与存储服务」-「共享」中直接点击创建，然后选择「SMB 共享 - 快速」，然后后面应该都不需要描述了，很简单直观的流程就能完成创建。

>ISCSI 存储的创建会稍微复杂一点，暂时用不到就不描述了。

SMB 共享创建好后，直接在客户端 Windows PC 上创建网络驱动器映射把它挂载到本地，就可以把游戏下载到这个网络存储里了~速度应该贼快。

## Linux 如何自动挂载 USB 硬盘盒

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

## 遇到过的 Bugs


### 1. SMB 传输文件突然终止时，有可能导致文件不可删除

今天在通过 smb 协议传文件到群晖服务器时，未知原因导致文件上传失败。
然后发现群晖服务器上已经出现这个文件了，现在文件无法删除，无法下载，也无法重新上传。。

- 原因分析：未找到原因
- 解决方法：重启 NAS 后恢复正常



## 参考

- [awesome-webdav](https://github.com/fstanis/awesome-webdav)
- [Adding permissions for udiskie-mount to policykit](https://unix.stackexchange.com/questions/277606/adding-permissions-for-udiskie-mount-to-policykit)

[X-plore File Manager]: https://play.google.com/store/apps/details?id=com.lonelycatgames.Xplore
[Total Commander]: https://play.google.com/store/apps/details?id=com.ghisler.android.TotalCommander
