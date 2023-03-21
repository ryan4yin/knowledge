# 荔枝糖 Tang 9K

##  1. 完成一个入门级的点灯实验

首先当然是根据官方文档 [Tang Nano 9K - Sipeed Wiki](https://wiki.sipeed.com/hardware/zh/tang/Tang-Nano-9K/Nano-9K.html) 完成一个点灯实验。

我使用的是 Endeavour 系统，一个基于 Arch 的发行版，在其上安装高云 IDE 教育版的方法如下：

```shell
# 通过 yay 从 aur 仓库安装高云 IDE 教育版
yay -S gowin-eda-edu-ide
```

IDE 用于编写生成固件，而固件烧录就需要使用烧录器，高云官方提供的「高云云源编程器 programmer for linux」在我的系统上有 Bug，无法识别到 USB 连接的设备。

根据官方文档 [Linux 下烧录方法 - Sipeed Wiki](https://wiki.sipeed.com/hardware/zh/tang/Tang-Nano-Doc/get_started/flash_in_linux.html)，在 Linux 上使用 [openFPGALoader](https://github.com/trabucayre/openFPGALoader) 进行烧录才是最稳的。

安装方法如下：

```shell
sudo pacman -S openfpgaloader
```

安装完成后还需要手动配置下 udev 规则：

```shell
# 这份 udev 规则赋予了 plugdev 组访问各种端口的权限，貌似仅针对
curl -o 99-openfpgaloader.rules https://raw.githubusercontent.com/trabucayre/openFPGALoader/master/99-openfpgaloader.rules
sudo mv 99-openfpgaloader.rules /etc/udev/rules.d/
sudo udevadm control --reload-rules && sudo udevadm trigger # force udev to take new rule
# 将用户添加到 plugdev 组，Ubuntu/Debian 都自带这个组，而 Arch Linux 可以手动建一个
# 或者不加这个组，后面直接以 root 权限执行 openFPGALoader 也是可以的
sudo groupadd plugdev
sudo usermod -a -G plugdev $USER
```

安装完成后的使用方法（默认情况下只有 root 用户才能读写）：

```shell
# 首先需要创建项目并完成综合，生成出固件
# 然后在命令行 cd 到项目根目录中，如下是我的项目路径
cd /home/ryan/codes/fpga/tang-9k-led

# 接下来进行烧录，有两种方法，二选一即可
## 1. 将固件加载到 SRAM，重启后失效
openFPGALoader -b tangnano9k ./impl/pnr/tang-9k-led.fs
## 2. 将固件加载到 Flash 中，长期生效
openFPGALoader -b tangnano9k -f ./impl/pnr/tang-9k-led.fs
```

