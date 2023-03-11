# 野火 - 鲁班猫 0 无线版

野火新推出的鲁班猫是类似树莓派的一类开发板，其中我买的 0 无线版（LubanCat Zero W）自带 WiFi 蓝牙，但是需要插 SD 卡启动。

## 烧录系统镜像

>官方文档：[系统镜像烧录 - LubanCat-RK系列板卡快速使用手册](https://doc.embedfire.com/linux/rk356x/quick_start/zh/latest/quick_start/flash_img/flash_img.html)

首先需要下载好镜像，下载地址参见上面提供的官方文档。

>目前官方仅提供了百度云盘地址，百度云盘的电脑客户端不行，但是**手机端可以看 40 秒广告就获得 30s 的加速时间，加上家里千兆宽带的话能跑到近 85M/s**，很快就下好了。

我下载的是「通用镜像(extboot)-适用于所有板卡」，镜像名称为 `rk356x-lubancat-rk_series-debian10-lite-20230103_update.7z`，解压后得到 .img 文件。

烧录需要使用瑞芯微官方提供的 SD 卡烧录程序 `SDDiskTool`/`SD_Firmware_Tool`，前面野火的百度网盘就有这个工具，或者也可以在 Firefly 这里从 Google 云盘下载 [
ROC-RK3566-PC Tools - Firefly Downloads](https://en.t-firefly.com/doc/download/93.html)，需要代理工具，但好处是不限速。

程序下载解压后，根据官方文档描述，使用里面的 `SD_Firmware_Tool.exe` 进行烧录即可。

>很尴尬的一点是这个 SD 卡烧录程序仅有 Windows 版本，我尝试了直接使用 dd/etcher 烧录的镜像，均无法正常启动，应该是缺了 boot 之类的分区。
还好我 Homelab 有一台 Windows 虚拟机，最后把 USB 设备映射到 Windows 中才完成 SD 卡烧录...

## 登录板卡终端

### 1. 使用串口登录

连好线直接登录就行，注意根据官方文档，波特率要设为 `1500000`

```shell
screen /dev/ttyUSB0 1500000
```

板子系统默认有两个用户，可以按需选择其中一个登录，如果内网不安全建议尽快修改密码，或者添加好私钥后立即禁用 SSH 登录：

```shell
用户  --- 用户名 -- 密码
超级用户 - root -- root
普通用户 - cat  -- temppwd
```

### 2. USB 终端登录

好像没啥需要，设好 WiFi 后直接 ssh 就行。

跳过

## 连接 WiFi 网络

我买的这块 LubanCat Zero W 只有 WiFi 没有以太网口，所以登录进终端后第一件事当然是连 WiFi:

```shell
# 连接普通 WiFi（注意替换带尖括号的占位内容）
sudo nmcli device wifi connect <wifi-name> password <your-password>

# 连接隐藏 WiFi（注意替换带尖括号的占位内容）
export SSID=<hidden-wifi-name>
export PASSWORD=<your-password>
sudo nmcli c add type wifi con-name $SSID ifname wlan0 ssid $SSID
sudo nmcli con modify $SSID wifi-sec.key-mgmt wpa-psk
sudo nmcli con modify $SSID wifi-sec.psk "${PASSWORD}"
sudo nmcli con up $SSID
```

连接完成后，检查网络情况，确认连接正常，路由表配置正常：

```shell
ip a
ip route ls
```

如果还需要设置静态 IP，接下来就可以 ssh 到电脑上，通过 nmtui 的命令行 TUI 来设置了。

>我这里遇到的问题：重启后 WiFi 自动连接会报错，必须通过 `sudo nmcli con up $SSID` 手动重连才能连上，暂时不清楚原因。。。


## 40 pin 引脚定义图

>https://doc.embedfire.com/linux/rk356x/quick_start/zh/latest/quick_start/40pin/40pin.html


## GPIO 控制

>https://doc.embedfire.com/linux/rk356x/quick_start/zh/latest/quick_start/40pin/gpio/gpio.html

libgpiod 是内核的标准模块，负责向上层提供标准的 gpio api



## Linux 镜像构建

在网络良好的情况下，使用我的 GTR5 5900HX 进行全量构建大约要 30 mins。

不要用容器构建，因为容器中内核版本会有差异，而且 QEMU 可能会出问题。

最稳妥的方法仍然是开一台 Ubuntu 18.04 虚拟机干这个活。
