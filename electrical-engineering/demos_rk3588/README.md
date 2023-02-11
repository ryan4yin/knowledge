# RK3588/RK3588S 开发版 demo

RK3588/RK3588S 是瑞芯微推出的一款高性能 ARM64 SoC，配置如下：

- 8C(A76*4 + A55*4)
- GPU(4Cores, Mail-G610)，支持 8K 硬件解码
- NPU(6Tops)

其中 RK3588 多一些外部模块，支持更多接口，RK3588S 则没有这些模块，但是价格更低一点。

我目前拥有 Rock 5A 4G（已购，预计 2023Q2 出货）、Orange Pi 5 8G 这两块使用 RK3588S 芯片的开发版。


## RK3588 开发版可以用来干啥

1. 通过 gpio 玩嵌入式
2. 装安卓系统，当做直播主机用，比如循环直播本地视频、直播摄像头内容等
3. 用来自动录制喜欢的 up 主的直播，开播自动录制，随时可回看
4. 当成直播服务器/视频聊天室使用，支持实时编解码成不同分辨率
5. 当虚拟服务器或 docker，虚拟多台 arm 主机，可装 Android
6. 当成 proxmox 虚拟机集群的 arm 节点


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

此外官方提供的 x64 闭源 docker 镜像太大了，未保存在仓库中，仅在 README 中附带的 百度云盘 分享中提供了该镜像文件。

## GPU 驱动

orange pi 5 用 armbian wayland 可以用 GPU 硬解 8K 视频，基本不占用 CPU：

>armbian 跟 orangepi5/rock5 官方提供的 ubuntu/debian 等系统相比会更有开源氛围，社区更活跃，ARM 相关的驱动更新更快，而且在各种 ARM 板子上体验都一致。

- [视频加速驱动](https://forum.armbian.com/topic/26450-accelerated-video-options-for-installing-and-running/#comment-159265)
- [带有 GPU 硬件加速和 HDMI 音频的 Orange Pi 5 上的 Kodi](https://forum.armbian.com/topic/25957-guide-kodi-on-orange-pi-5-with-gpu-hardware-acceleration-and-hdmi-audio/#comment-157913)

