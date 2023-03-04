# RK3588/RK3588S 开发版 demo

RK3588/RK3588S 是瑞芯微推出的一款高性能 ARM64 SoC，配置如下：

- 8C(A76*4 + A55*4)
- GPU(4Cores, Mail-G610)，支持 8K 硬件解码
- NPU(6Tops)

其中 RK3588 多一些外部模块，支持更多接口，RK3588S 则没有这些模块，但是价格更低一点。

## 开发板对比

我目前拥有 Rock 5A 4G（已购，预计 2023Q2 出货）、Orange Pi 5 8G 这两块使用 RK3588S 芯片的开发版。

根据描述 Orange Pi 的文档、生态貌似要比 Rock Pi 更好一些，我体验上 Orange Pi 的文档确实写得可以，很清晰，而且有中英双语。
而 Rock Pi 的 WIKI 虽然看起来更现代化一点，但是生态貌似被喷得比较多，而且看别人说 Rock 5 的 PD 供电坑很多。

所以目前的感觉是软件生态方面 Raspberry Pi >> Orange Pi > Rock Pi，性价比方面 Orange Pi > Rock PI >> Raspberry Pi。

而其他的 RK3588 或者其他 ARM Soc 的板子，要么就是价格贼高，要么就是性能不太行，反正目前看国产派就是 Orange Pi 跟 Rock Pi 性价比高一点，而且好折腾。

>还有啥友善之臂，听这名字就...而且一搜那官网就是几百年没更新了，论坛也没啥活人，看设计还主要是搞软路由的，我直接避坑。

其他大佬的折腾资料：

- [Rock 5B (RK3588) 开箱体验和踩坑记录（也可以是上手教程）](https://neucrack.com/p/466)
- [各大国产派对比贴 - 知乎](https://www.zhihu.com/question/493634573/answer/2186324937)

## RK3588 开发版可以用来干啥

1. 通过 gpio 玩嵌入式
2. 装安卓系统，装个 OSB 当做直播推流主机用，比如循环直播本地视频、直播摄像头内容等
3. 用来自动录制喜欢的 up 主的直播，开播自动录制，随时可回看
4. 当成直播服务器/视频聊天室使用，支持实时编解码成不同分辨率
5. 当虚拟服务器或 docker，虚拟多台 arm 主机，可装 Android
6. 当成 proxmox 虚拟机集群的 arm 节点

## 使用远程桌面

为了在 Orange Pi 5 上做些 NPU 调试，经常要查看各种 opencv 输出的图像，所以远程桌面是比较需要的功能。

查了一圈最成熟稳定的方案貌似有两个：

- SSH X11 Forwarding: 这是最简单的方案，在局域网下，而且客户端就是 Linux 时体验非常好，很适合用于偶尔跑些图形任务。
- [xrdp](https://github.com/neutrinolabs/xrdp): 它是 Windows 远程桌面协议的 Linux 实现，好处是性能不错，而且你还可以使用全平台的 [Microsoft Remote Desktop](https://learn.microsoft.com/en-us/windows-server/remote/remote-desktop-services/clients/remote-desktop-clients) 连接你的 Linux 远程桌面，能够自动做剪切板同步、音频转发、使用客户端 GPU 进行图形渲染加速等，还支持多屏操作，体验很好。
- VNC: VNC 是 Linux 下非常流行的远程桌面协议，它实现简单但不够安全，而且不支持传输声音，一般仅用于偶尔登录下服务器使用。

经我测试发现，局域网环境下，SSH X11 Forwarding 是最好用的，不需要任何额外配置，直接 `ssh -X user@host` 就能用了！而且仅在运行 GUI 应用时才会开启 GUI 窗口，与使用本机 APP 的体验别无二致。

相比之下 xrdp xrdp 我第一次跑时就黑屏了，一番查找才解决，还是有一定的工作量才能把环境配好的，而且 xrdp 需要在服务端安装完整的桌面环境，要占据服务端更多的存储，渲染时估计也会更吃资源。

### 1. SSH X11 Forwarding

SSH X11 Forwarding 能把 client 当成一台显示器来用，尤其是在客户端就是 Linux 桌面的情况下，局域网使用体验很好。不过它没做啥优化，数据都是全量发送，建议仅在局域网使用.

另外 SSH X11 Forwarding 不需要完整的桌面环境，不需要在 Linux 远程主机上装完整的 xfce/gnome 等环境，这也是一个很大的优势。

先说下前置条件：

- 如果客户端桌面也是 Linux，那不需要改任何东西，直接就能用，体验也是三个桌面中最佳的。
- 如果客户端是 MacOS，则需要提前安装好 [XQuartz](https://www.xquartz.org/)
- 如果客户端是 Windows，则需要先安装好 [xming](https://sourceforge.net/projects/xming/)，可能还需要其他配置，我没试过请自行搜索解决。

然后首先修改 Linux 服务器的 ssh 配置 `/etc/ssh/sshd_config`，启用 `X11Forwarding` 功能：

```shell
# 启用 X11Forwarding
echo 'X11Forwarding yes' | sudo tee /etc/ssh/sshd_config
sudo systemctl restart ssh
```

最简单的用法就是 ssh 直接加个 `-X` 命令：

```shell
ssh -X user@host
```

加了 `-X` 后的命令会等待一会儿才进入远程终端，然后就可以直接运行 X11 应用了。

[How to start a GUI software on a remote Linux PC via SSH](https://askubuntu.com/questions/47642/how-to-start-a-gui-software-on-a-remote-linux-pc-via-ssh) 中介绍了多种用法，

>如果你想远程使用更新的 wayland 系统，可以看看 [waypipe](https://gitlab.freedesktop.org/mstoeckl/waypipe)。

### 2. 安装使用 [xrdp](https://github.com/neutrinolabs/xrdp)

xrdp 远程连接得到的是一个完整的图形化桌面，因此需要先在 Orange Pi 5 上安装好桌面环境，服务器场景下建议使用性能最佳的 Xfce（或者直接用窗口管理器 i3wm），安装方式如下：

```shell
sudo apt update
sudo apt install xfce4 xfce4-goodies xorg dbus-x11 x11-xserver-utils
```

安装完成后最好重启下系统。

```shell
# 安装 xrdp 与它底层使用的 xorgxrdp
sudo apt install xrdp xorgxrdp

# Xrdp uses the /etc/ssl/private/ssl-cert-snakeoil.key, give it the permission to access it
sudo adduser xrdp ssl-cert

sudo systemctl enable xrdp
sudo systemctl restart xrdp
sudo systemctl status xrdp
```

另外还需要注意下 Linux 的防火墙配置，开放 3389 端口。

然后就能使用 Windows 自带的 `remote` 程序，或者跨平台且体验更佳的 [Microsoft Remote Desktop](https://learn.microsoft.com/en-us/windows-server/remote/remote-desktop-services/clients/remote-desktop-clients) 来连接主机即可。

如果连接完是黑屏，可以先等待一会儿，说不定就 OK 了...如果超过 10s 一直黑屏，可以使用如下命令改下 xrdp 的启动环境变量，再重新连接试试：

```shell
cat <<EOF | sudo tee /etc/xrdp/startwm.sh
unset DBUS_SESSION_BUS_ADDRESS
unset XDG_RUNTIME_DIR
EOF

sudo systemctl restart xrdp
```

要是解决不了，可以看看 Arch Linux WIKI 中的常见问题及解法 [Xrdp - Arch Linux WIKI](https://wiki.archlinux.org/title/xrdp)

## NPU 使用案例

>如果使用 NPU，建议板子上直接装 Orange Pi 5 的官方 Debian 镜像，这个问题应该最少。

瑞芯微官方提供了两个 NPU 相关的仓库，其中包含使用手册、examples、驱动等内容：

- [rknn-toolkit2](https://github.com/rockchip-linux/rknn-toolkit2): 这个仓库实际保存了两个 Python 包，介绍如下
  - rknn-toolkit2 x64: 仓库根目录的 docs/examples/packages 文件夹，包含的是 x64 版本的文档、示例、whl 包，只能安装在 x64 主机上，而且依赖了 onnx、tensorflow、pytorch 等 AI 框架，支持 NPU AI 推理、本地模拟器 AI 推理，以及将 onnx 模型转换为 NPU 可用的 rknn 格式
    - 主要用于在 PC 机上进行模型调试
    - **注意**: 根据官方文档，截止版本 1.4，此 SDK 仅适配 Ubuntu18.04(x64) / Ubuntu20.04(x64) 系统，以及 Python 的 3.6/3.8 两个版本
  - rknn-toolkit2-lite2 arm64: 保存在仓库的 rknn_toolkit_lite2 文件夹中，仅依赖 opencv 和 numpy，它为 NPU 提供了 Python API
    - 可用于通过 Python API 部署模型
    - **注意**: 根据官方文档，截止版本 1.4，此 SDK 仅适配 Debian 10(arm64) / Debian 11(arm64) 系统，以及 Python 的 3.7/3.9 两个版本
- [rknpu2](https://github.com/rockchip-linux/rknpu2): rknpu2 为 NPU 提供了 C API，主要用于通过 C 语言部署模型。

>注意下，调试 PC 的环境，与板子的系统环境要求并不一致，需要注意区分！

上面两个仓库虽然是用的 git 仓库，但实际底层内容都仅公开了 `.so`、`.whl`、docker 镜像等二进制安装包，并未开放源码。

此外官方提供的 x64 闭源 docker 镜像太大了，而且还仅通过龟速百度网盘分享，我根据文档自己写了个 `Dockerfile.rknn_toolkit2_1.4.0` 用着正常。

开发测试流程是这样的，首先把容器跑起来，并且把我的工作目录映射进去，同时通过 `--net=host --env="DISPLAY" --volume="$HOME/.Xauthority:/root/.Xauthority:rw"` 添加了 X11 Forwarding 功能，使容器内的 GUI 程序能直接通过宿主机的 X11 Server 显示出来：

```shell
docker run --name rknn -d \
  --net=host --env="DISPLAY" --volume="$HOME/.Xauthority:/root/.Xauthority:rw" \
  -v /home/ryan/Downloads/rk3588s/:/work \
  rknn-toolki2:1.4.0 \
  bash -c 'while true; do sleep 1000000; done'
```

然后直接 vscode 远程进入容器里搞开发~

先整了个视频目标检测的 demo 玩，代码在这里 [yolov5_rknn_toolkit2_demo](./yolov5_rknn_toolkit2_demo/)

### 1. 在 orangepi 上运行 rknn-toolkit2-lite2 中的官方 demo

安装流程跟 rknn_toolkit2 别无二致：

```shell
# 安装 python 基础包
sudo apt-get update
sudo apt-get install -y python3 python3-dev python3-pip gcc

# 安装 rknn-toolkit2-lite2 的依赖项
sudo apt-get install -y python3-opencv python3-numpy

# cd 进 rknn_toolkit_lite2 包存储位置
cd rknn_toolkit_lite2/packages
# 用北外源加速 Python 包下载
pip config set global.index-url https://mirrors.bfsu.edu.cn/pypi/web/simple
# 在用户目录下安装 rknn_toolkit_lite2, debian 11 安装 cpython3.9 的 whl
pip install --user rknn_toolkit_lite2-1.4.0-cp39-cp39-linux_aarch64.whl
```

这样就搞定了，可以开始跑 npu 任务了。

它的 API 几乎跟 rknn_toolkit2 完全一致，但是只能加载跟 SoC 型号一致的 rknn 模型，不具备模型转换功能。

如果你想部署基于 [rknpu2](https://github.com/rockchip-linux/rknpu2) 开发的程序，流程也类似，直接看它仓库里的官方文档吧。


### 2. NPU 性能调试

>rknpu2 的官方文档 [Rockchip_RKNPU_User_Guide_RKNN_API_V1.4.0_CN.pdf](https://github.com/rockchip-linux/rknpu2/blob/master/doc/Rockchip_RKNPU_User_Guide_RKNN_API_V1.4.0_CN.pdf) 末尾有一节专门讲了性能调试，如下内容主要摘抄自该文档

通常，板子上的各个单元的频率是动态调频，这种情况下测试出来的模型性能会有波动。为
了防止性能测试结果不一致，在性能评估时，建议固定板子上的相关单元的频率再做测试。相关
单元的频率查看和设置命令如下：

#### 1. CPU 调试命令

1. 查看 CPU 频率：
   ```shell
   # 方法一
   cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_cur_freq
   # 方法二
   cat /sys/kernel/debug/clk/clk_summary | grep arm
   ```
2. 固定 CPU 频率（rk3588 支持此功能）
   ```shell
   # 查看 CPU 可用频率
   cat /sys/devices/system/cpu/cpufreq/policy0/scaling_available_frequencies
   # 输出 => 408000 600000 816000 1008000 1200000 1416000 1608000 1800000

   # 设置 CPU 频率，例如设置为最高的 1.8GHz
   echo userspace > /sys/devices/system/cpu/cpufreq/policy0/scaling_governor
   echo 1800000 > /sys/devices/system/cpu/cpufreq/policy0/scaling_setspeed
   ```
#### 2. 内存（DDR）调试命令

1. 查看内存（DDR）频率
   ```shell
   cat /sys/kernel/debug/clk/clk_summary | grep ddr
   ```
2. 固定内存（DDR）频率
   >需要固件支持，orangepi5 跑下面的命令报错，应该是不支持
   ```shell
   # 查看 DDR 可用频率
   cat /sys/class/devfreq/dmc/available_frequencies
   # 设置 DDR 频率，例如，设置 1560MHz
   echo userspace > /sys/class/devfreq/dmc/governor
   echo 1560000000 > /sys/class/devfreq/dmc/userspace/set_freq
   ```

#### 3. NPU 调试命令

1. 查看 NPU 频率（rk3588 专用）

   ```shell
   cat /sys/class/devfreq/fdab0000.npu/cur_freq
   ```
2. 固定 NPU 频率（rk3588 专用）
   >注意：在 NPU 驱动 0.7.2 版本之后，需要先打开 NPU 电源，才能进行频率设置
   ```shell
   # 查看 NPU 可用频率
   cat /sys/class/devfreq/fdab0000.npu/available_frequencies
   # => 300000000 400000000 500000000 600000000 700000000 800000000 900000000 1000000000
   # 设置 NPU 频率，例如设为最高的 1 GHz
   echo userspace > /sys/class/devfreq/fdab0000.npu/governor
   echo 1000000000 > /sys/kernel/debug/clk/clk_npu_dsu0/clk_rate
   ```

#### 4. NPU 支持查询设置项

NPU 驱动版本在 0.7.2 之后的，可通过节点查询 NPU 的版本、NPU 不同核心的利用率以
及手动开关 NPU 电源

```shell
# 1. 查询 NPU 驱动版本
## 这个命令我修正了下，官方文档末尾写的是 /driver_version 导致报错
cat /sys/kernel/debug/rknpu/version

# 2. 查询 NPU 利用率
cat /sys/kernel/debug/rknpu/load

# 3. 查询 NPU 电源状态
cat /sys/kernel/debug/rknpu/power

# 4. 打开 NPU 电源
echo on > /sys/kernel/debug/rknpu/power

# 5. 关闭 NPU 电源
echo off > /sys/kernel/debug/rknpu/power
```

NPU 驱动版本在 0.8.2 之后新增频率、电压、动态开关电源功能：

```shell
# 1. 查询 NPU 工作频率
cat /sys/kernel/debug/rknpu/freq

# 2. 设置 NPU 工作频率
## 查看 RK3588 NPU 可用频率
cat /sys/class/devfreq/fdab0000.npu/available_frequencies
## 设置 RK3588 NPU 频率，例如，设置 1 GHz
echo 1000000000 > /sys/kernel/debug/rknpu/freq

# 3. 查询 NPU 工作电压
## 注意：不支持直接修改电压，只能修改工作频率，电压跟随修改
cat /sys/kernel/debug/rknpu/volt

# 4. 查询 NPU 动态开关电源，电源延迟关闭时间（单位：ms）
cat /sys/kernel/debug/rknpu/delayms

# 5. 设置 NPU 动态开关电源，电源延迟关闭时间（单位：ms）
## 设置电源延迟 2s 关闭
echo 2000 > /sys/kernel/debug/rknpu/delayms
```



## GPU 驱动

orange pi 5 用 armbian wayland 可以用 GPU 硬解 8K 视频，基本不占用 CPU：

>armbian 跟 orangepi5/rock5 官方提供的 ubuntu/debian 等系统相比会更有开源氛围，社区更活跃，ARM 相关的驱动更新更快，而且在各种 ARM 板子上体验都一致。

- [视频加速驱动](https://forum.armbian.com/topic/26450-accelerated-video-options-for-installing-and-running/#comment-159265)
- [带有 GPU 硬件加速和 HDMI 音频的 Orange Pi 5 上的 Kodi](https://forum.armbian.com/topic/25957-guide-kodi-on-orange-pi-5-with-gpu-hardware-acceleration-and-hdmi-audio/#comment-157913)

