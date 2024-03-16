# 野火 - 鲁班猫 0 无线版

野火新推出的鲁班猫是类似树莓派的一类开发板，其中我买的 0 无线版（LubanCat Zero W）自带 WiFi 蓝牙，但
是需要插 SD 卡启动。

1. [基础使用 + 内核编程](https://doc.embedfire.com/linux/imx6/linux_base/zh/latest/index.html)：感觉
   跟《Linux/Unix 编程手册》内容是重复的，可以简单过一过
2. 裸机开发与 Linux 驱动开发
   1. [基于 IMX6ULL](https://doc.embedfire.com/products/link/zh/latest/linux/ebf_i.mx6ull_doc.html)
   2. [基于鲁班猫 RK356X 系列板卡](https://doc.embedfire.com/linux/rk356x/driver/zh/latest/index.html)
3. [Linux 镜像构建与部署](https://doc.embedfire.com/linux/rk356x/build_and_deploy/zh/latest/index.html)

## 烧录系统镜像

> 官方文
> 档：[系统镜像烧录 - LubanCat-RK系列板卡快速使用手册](https://doc.embedfire.com/linux/rk356x/quick_start/zh/latest/quick_start/flash_img/flash_img.html)

首先需要下载好镜像，下载地址参见上面提供的官方文档。

> 目前官方仅提供了百度云盘地址，百度云盘的电脑客户端不行，但是**手机端可以看 40 秒广告就获得 30s 的
> 加速时间，加上家里千兆宽带的话能跑到近 85M/s**，很快就下好了。

我下载的是「通用镜像(extboot)-适用于所有板卡」，镜像名称为
`rk356x-lubancat-rk_series-debian10-lite-20230103_update.7z`，解压后得到 .img 文件。

烧录需要使用瑞芯微官方提供的 SD 卡烧录程序 `SDDiskTool`/`SD_Firmware_Tool`，前面野火的百度网盘就有这
个工具，或者也可以在 Firefly 这里从 Google 云盘下载
[ROC-RK3566-PC Tools - Firefly Downloads](https://en.t-firefly.com/doc/download/93.html)，需要代理工
具，但好处是不限速。

程序下载解压后，根据官方文档描述，使用里面的 `SD_Firmware_Tool.exe` 进行烧录即可。

> 很尴尬的一点是这个 SD 卡烧录程序仅有 Windows 版本，我尝试了直接使用 dd/etcher 烧录的镜像，均无法正
> 常启动，应该是缺了 boot 之类的分区。还好我 Homelab 有一台 Windows 虚拟机，最后把 USB 设备映射到
> Windows 中才完成 SD 卡烧录...

## 登录板卡终端

### 1. 使用串口登录

连好线直接登录就行，注意根据官方文档，波特率要设为 `1500000`

```shell
screen /dev/ttyUSB0 1500000
```

板子系统默认有两个用户，可以按需选择其中一个登录，如果内网不安全建议尽快修改密码，或者添加好私钥后立
即禁用 SSH 登录：

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

> 我这里遇到的问题：重启后 WiFi 自动连接会报错，必须通过 `sudo nmcli con up $SSID` 手动重连才能连
> 上，暂时不清楚原因。。。

## 40 pin 引脚定义图

> https://doc.embedfire.com/linux/rk356x/quick_start/zh/latest/quick_start/40pin/40pin.html

## GPIO 控制

> https://doc.embedfire.com/linux/rk356x/quick_start/zh/latest/quick_start/40pin/gpio/gpio.html

libgpiod 是内核的标准模块，负责向上层提供标准的 gpio api

## Linux 镜像构建

在网络良好的情况下，使用我的 GTR5 5900HX 进行全量构建大约要 30 mins。

不要用容器构建，因为容器中内核版本会有差异，而且 QEMU 可能会出问题。

最稳妥的方法仍然是开一台 Ubuntu 18.04 虚拟机干这个活。

## 驱动开发学习目标

最近直接开始学习各种驱动知识，久了就有点迷失方向，不知道学了有啥用，也没动力学。

为了提高学习的动力，我决定把学习的目标定得更具体一些，这样就可以有一个明确的终点，而不是一直在迷茫中
浪费时间。

1. 编写一个简单的驱动，实现 GPIO 控制 LED 灯的亮灭。
2. 只是点个 LED 灯未免太简单了，再加上一个按键，按下按键时 LED 灯亮，松开按键时 LED 灯灭。
3. 多来几个 LED 灯，实现跑马灯效果。
4. 再上点难度，加上一个 7 段数码管，自增计数，每按一次按键，数码管上的数字加一。
5. 到上面这个程度，只是把之前用 MCU 实现的功能用 Linux 驱动实现了一遍。现在再上点难度，实现一个 SPI
   显示屏驱动，显示一些信息，比如说播放 Bad Apple。
6. 同样的，写个驱动使用 SPI 协议读 SD 卡、各种传感器、各种外设，实现一些有意思的功能。
7. 鲁班猫只支持使用其官方的摄像头，这里我们自己实现一个 OV2640 摄像头的驱动。

到这里为止应该就算 Linux 驱动开发入门了，而且有了这么多驱动，我也能直接使用自己的驱动做很多有意思的
事了，进阶目标：

- 两轮自平衡小车
- IP-KVM 远程控制主机
- 其他组合各种传感器的有趣玩具
