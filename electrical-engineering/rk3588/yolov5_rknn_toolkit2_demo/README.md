# 在 RK3588 上运行 yolov5 目标检测模型

基于 rknn_toolkit2 v1.4.0，在官方的 [examples/onnx](https://github.com/rockchip-linux/rknn-toolkit2/tree/d8074d7954cc4d50af0add9c4375acd823987898/examples/onnx) 上做了点改动，通过 opencv 从 mp4 文件中逐帧运行模型。

作为新手记录下我的首次 NPU 体验流程：

1. 首先使用我自己写的 [Dockerfile.rknn_toolkit2_1.4.0](../Dockerfile.rknn_toolkit2_1.4.0) 构建出 x64 镜像用于在本地编写代码与调试。
   1. [demos_rk3588](../README.md) 中有提过如何通过容器进行调试，并使用本机的 X11 GUI 环境。
   2. 我这么整主要是因为本地不是 Ubuntu 系统（是 Arch），而且不想污染本地环境。
2. 调试通过后，去掉代码中的模型转换代码，直接加载 rknn 模型，并将 RKNN 类换成 rknn_toolkit2_lite 中的 RKNNLite 类，再 scp 到板子中执行。
   1. 同样，这也需要你的板子有 GUI 环境，或者使用 SSH X11 Forwarding 远程显示 GUI 界面（其实也简单，就 SSH 加一个参数，`ssh -X orangepi@host` 就行）。

运行时要注意，`yolo_video_rk3588_npu.py` 代码中硬编码了视频文件地址 `BadApple.mp4`，请将其改为你自己的测试视频地址。

有大佬测试过的结论：

1. 单核模式下利用率能基本跑满，但是两核围观。
2. 需要写多进程程序才能完全利用上三核，将自带 SDK 的参数调整为三核会导致资源利用率都上不去，对性能提升不大。

## 性能测试

在执行此 AI 推理任务时，发现性能不太行，开始做个性能排查。

首先查看下 NPU 负载：

```shell
root@orangepi5:/home/orangepi/yolov5_demo# cat /sys/kernel/debug/rknpu/load
NPU load:  Core0: 16%, Core1:  6%, Core2:  6%,    
```

可以看到 NPU 的负载很低，最高的 Core0 利用率也仅 16%，说明瓶颈大概率在 CPU 上。

我们将 CPU 跟 NPU 的执行频率调到上限，再看看性能如何：

```shell
# 查看 CPU 可用频率
cat /sys/devices/system/cpu/cpufreq/policy0/scaling_available_frequencies
# => 408000 600000 816000 1008000 1200000 1416000 1608000 1800000
# 查看 NPU 可用频率
cat /sys/class/devfreq/fdab0000.npu/available_frequencies
# => 300000000 400000000 500000000 600000000 700000000 800000000 900000000 1000000000


# 设置 CPU 频率，例如设置为最高的 1.8GHz
echo userspace > /sys/devices/system/cpu/cpufreq/policy0/scaling_governor
echo 1800000 > /sys/devices/system/cpu/cpufreq/policy0/scaling_setspeed

# 设置 NPU 频率，例如设为最高的 1 GHz
echo userspace > /sys/class/devfreq/fdab0000.npu/governor
echo 1000000000 > /sys/kernel/debug/clk/clk_npu_dsu0/clk_rate
```

调整完后，发现 NPU 利用率确实提升了一些，而且 opencv 渲染的内容也快了不少：

```shell
root@orangepi5:/home/orangepi/yolov5_demo# cat /sys/kernel/debug/rknpu/load 
NPU load:  Core0: 19%, Core1:  8%, Core2:  8%,
```

但是感觉推理无关的程序逻辑还有改进空间，比如能否用上 GPU 之类的。


