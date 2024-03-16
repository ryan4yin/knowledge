# OpenWRT 路由专用系统

## 在 PVE 配置 OpenWRT 虚拟机

首先是虚拟机安装流程：

1. 下载最新的 OpenWRT 镜像
   1. 不熟悉 OpenWRT 的话建议在恩山论坛下载高排名的小白固件，比如
      [sirpdboy/openwrt](https://github.com/sirpdboy/openwrt)
   2. 如果打算使用官方固件，为了避免踩坑，建议回退至少一个大版本。比如说现在最新版为 22.03.2，那就下
      载 [21.02.3//targets/x86/64/](https://downloads.openwrt.org/releases/21.02.3//targets/x86/64/)
      或者更早的版本
   3. 请下载其中第一个镜像文件 `generic-ext4-combined-efi.img.gz`，此镜像支持 EFI 启动，也带了一个
      BIOS 分区。
2. 在 PVE 中手动创建虚拟机，BIOS 使用 OVMF(UEFI) ，然后把默认磁盘卸载并删除
   1. OVMF 模式下会自动生成一个 uefi 硬盘，不需要去动它
   2. 为了确保性能，cpu 请选用 host 模式，配置建议给到 1C/0.5G - 2c/1G
3. 使用命令将下载的 `img` 文件导入到新建的虚拟机并挂载，然后将该磁盘增大 1G
   1. 导入命令（需要将 106 修改为虚拟机
      ID）：`qm importdisk 106 openwrt-22.03.2-x86-64-generic-ext4-combined-efi.img local-lvm`
4. 修改启动顺序为仅从新硬盘启动：scsi0
5. 启动主机
6. 一开始会启动失败进入 UEFI shell，因为 openwrt 不支持「secure boot」
   1. 解决方法：使用 `exit` 退出 UEFI shell 后会进入 UEFI 界面，将「secure boot」关掉，保存并重启，
      即可正常启动 OpenWRT

虚拟机安装完成后，通过 `ip link` 能看到相应的端口，但是会发现并未使用 DHCP 自动配置任何 IP 地址，也
就无法通过网络连接。需要先手动配置网络：

1. 修改 `/etc/config/network` 位置文件，找到 `lan` 配置，将其参数设置为与本地局域网一致，就能实现加
   入到局域网中。

示例配置：

```shell
root@OpenWrt:~# cat /etc/config/network

config interface 'loopback'
	option device 'lo'
	option proto 'static'
	option ipaddr '127.0.0.1'
	option netmask '255.0.0.0'

config globals 'globals'
	option ula_prefix 'fd0c:702e:10d6::/48'

config device
	option name 'br-lan'
	option type 'bridge'
	list ports 'eth0'

# 修改这部分配置，其中 ipaddr 为 openwrt 自身的 IP，其他参数要与整个局域网一致
config interface 'lan'
	option device 'br-lan'
	option proto 'static'
	option ipaddr '192.168.5.201'
	option netmask '255.255.255.0'
	option ip6assign '60'
   # 如下两行需要手动添加
	option gateway 192.168.5.1
	option dns 114.114.114.114 8.8.8.8

config interface 'wan'
	option device 'eth1'
	option proto 'dhcp'

config interface 'wan6'
	option device 'eth1'
	option proto 'dhcpv6'
```

修改完成后 `/etc/init.d/network restart` 重启网络服务，然后就能直接通过 `http://192.168.5.201` 访问
此 OpenWRT 虚拟机啦，命令行有提示初始密码为 `passwd`，进入 Web 页面后需要自行修改。

## 常用插件

使用 OpenWRT 作为软路由系统，好像唯二的优势就在于：

1. 它对网络的支持比较好
2. 拥有丰富的网络相关插件
3. 提供一个比较完善的 Web UI 控制台，能方便地配置各种网络与安全相关参数。
4. 如果你熟悉 openwrt 的使用，可以复用之前的经验

列举一些常用插件如下：

- `qemu-ga`: 即 qemu-guest-agent 的 openwrt 版本，建议安装，Proxmox-VE 通过它控制 openwrt 启停、获取
  openwrt 内部信息（如 ip 地址）。
- 一款漂亮的 OpenWRT Web 皮肤：[luci-theme-argon](https://github.com/jerrykuku/luci-theme-argon)
- OpenClash 网络代理工具：[OpenClash](https://github.com/vernesong/OpenClash)
- 解锁网易云灰色歌
  曲：[luci-app-unblockneteasemusic](https://github.com/cnsilvan/luci-app-unblockneteasemusic)

插件可以使用 `opkg install` 安装，也可通过 openwet web console 安装，请随意。

> 画外：额好像上述这几个插件都没什么特点，换个操作系统照样能搞...考虑拿 Ubuntu Server 取代掉它...

> 画外：自己用 Ubuntu 搞，要装个东西太多了，最后还是恩山论坛上找了个预装了各种插件的流行固件...特别
> 省心 emmm

## PVE 无线网卡直通 OpenWRT 并设置为访客 WiFi 网络

我目前家里就一台 ZTE 5400 Plus+ 作为主路由拨号上网 + 家庭 WiFi，但是 DHCP 服务是关掉了，仅在 OpenWRT
旁路由上开了 DHCP 功能。

但我发现这样配置后，ZTE 5400 Plus+ 这台主路由的访客 WiFi 功能就废掉了，连接上后根本无法使用，分配不
到 IP 地址。所以说为了使用它的访客 WiFi 功能就不能关掉它的 DHCP，但是不关掉的话局域网内就有两台 DHCP
服务器...

因为 ZTE 5400 Plus+ 的 DHCP 改不了默认网关的地址，那我为了在局域网内使用上旁路由的代理加速，就只有这
几个选择：

1. 仍然使用旁路由做 DHCP，但是主路由的访客 WiFi 功能就废了，为了朋友来玩方便，需要找个替代品。
2. 使用主路由做 DHCP，这样的话为了使用旁路由，就需要手动修改我相关主机的网络配置，手动设置默认网关
   IP。
3. 刷入自定义程度更高的第三方固件（如果有的话），直接在主路由的 DHCP 上改默认网关地址。

想了下我需要代理加速的主要是虚拟机，它们大部分都是直接通过 cloud-init 设置的静态 IP. 另外就是几台手
机、笔记本，不多，手动改下网关 IP 地址也能接受。

所以感觉方案一跟方案二，我都可以接受，目前用的是方案二。

但是！但是我三台小主机都有 WiFi6 网卡，不用上也真可惜啊，所以也顺便想摸索下能不能用它们搞个隔离的访
客 WiFi 出来，主要是为了折腾...

搜了下「OPENWRT 访客网络 网络隔离」，网上资料不少，下面介绍下处理流程吧。

第一步当然是网卡直通

TODO
