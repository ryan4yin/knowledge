# 荔枝糖 Tang 9K

## 高云 FPGA 开发环境介绍

1. 支持 VHDL、Verilog HDL 和 System Verilog 语言

## 1. 完成一个入门级的点灯实验

首先当然是根据官方文档
[Tang Nano 9K - Sipeed Wiki](https://wiki.sipeed.com/hardware/zh/tang/Tang-Nano-9K/Nano-9K.html) 完
成一个点灯实验。

我使用的是 Endeavour 系统，一个基于 Arch 的发行版，在其上安装高云 IDE 教育版的方法如下：

```shell
# 通过 yay 从 aur 仓库安装高云 IDE 教育版
yay -S gowin-eda-edu-ide
```

IDE 用于编写生成固件，而固件烧录就需要使用烧录器，高云官方提供的「高云云源编程器 programmer for
linux」在我的系统上有 Bug，无法识别到 USB 连接的设备。

根据官方文档
[Linux 下烧录方法 - Sipeed Wiki](https://wiki.sipeed.com/hardware/zh/tang/Tang-Nano-Doc/get_started/flash_in_linux.html)，
在 Linux 上使用 [openFPGALoader](https://github.com/trabucayre/openFPGALoader) 进行烧录才是最稳的。

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

## 在 NixOS 上进行开发

### 使用高云 IDE 进行开发

NixOS 上可用我打好的
[高云教育版 IDE](https://github.com/ryan4yin/nur-packages/tree/main/pkgs/gowin-eda-edu-ide)，烧录器
则建议使用 openfpgaloader.

跑完综合跟布局布线后，会在项目根目录下生成一个 `impl` 文件夹，里面有 `pnr` 文件夹，里面有 `xxx.fs`
文件，这个就是生成的固件。

直接使用 openfpgaloader 烧录即可：

```shell
openFPGALoader -b tangnano9k -f ./impl/pnr/*.fs
```

### 使用开源工具链进行开发

代码可以直接用 vscode / neovim 等编辑器编写，然后使用 apicula 进行综合、布局布线、生成固件。

- [YosysHQ/apicula](https://github.com/YosysHQ/apicula)

首先，我们需要两个源文件：

1. `blinky.v`：点灯实验的 verilog 源文件
2. `tang-9k-led.cst`：荔枝糖 Tang 9K 的约束文件

纯命令行操作方法如下（其中的 CST 文件不好编辑，建议先用 Gowin IDE 生成好）：

```bash
CST='tang-9k-led.cst'

# 1. 使用 yosys 进行综合
yosys -D LEDS_NR=8 -p "read_verilog blinky.v; synth_gowin -json blinky.json"

# 2. 使用 nextpnr 布局布线
nextpnr-gowin --json blinky.json --write pnrblinky.json --family GW1N-9C --device 'GW1NR-LV9QN88PC6/I5' --cst $CST

# 3. 使用 apicula 生成固件 fs 文件
gowin_pack -d GW1N-9C -o pack.fs pnrblinky.json

# 4. 使用 openFPGALoader 烧录固件
openFPGALoader -b tangnano9k -f pack.fs
```
