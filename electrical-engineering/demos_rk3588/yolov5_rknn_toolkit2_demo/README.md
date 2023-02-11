# 在 RK3588 上运行 yolov5 目标检测模型

基于 rknn_toolkit2 v1.4.0，在官方的 [examples/onnx](https://github.com/rockchip-linux/rknn-toolkit2/tree/d8074d7954cc4d50af0add9c4375acd823987898/examples/onnx) 上做了点改动，通过 opencv 从 mp4 文件中逐帧运行模型。

作为新手记录下我的首次 NPU 体验流程：

1. 首先使用我自己写的 [Dockerfile.rknn_toolkit2_1.4.0](../Dockerfile.rknn_toolkit2_1.4.0) 构建出 x64 镜像用于在本地编写代码与调试。
   1. [demos_rk3588](../README.md) 中有提过如何通过容器进行调试，并使用本机的 X11 GUI 环境。
   2. 我这么整主要是因为本地不是 Ubuntu 系统（是 Arch），而且不想污染本地环境。
2. 调试通过后，去掉代码中的模型转换代码，直接加载 rknn 模型，并将 RKNN 类换成 rknn_toolkit2_lite 中的 RKNNLite 类，再 scp 到板子中执行。
   1. 同样，这也需要你的板子有 GUI 环境，或者使用 SSH X11 Forwarding 远程显示 GUI 界面（其实也简单，就 SSH 加一个参数，`ssh -X orangepi@host` 就行）。

运行时要注意，`yolo_video_rk3588_npu.py` 代码中硬编码了视频文件地址 `BadApple.mp4`，请将其改为你自己的测试视频地址。


## 板端性能调试

>rknpu2 的官方文档 [Rockchip_RKNPU_User_Guide_RKNN_API_V1.4.0_CN.pdf](https://github.com/rockchip-linux/rknpu2/blob/master/doc/Rockchip_RKNPU_User_Guide_RKNN_API_V1.4.0_CN.pdf) 末尾有一节专门讲了性能调试，如下内容主要摘抄自该文档

通常，板子上的各个单元的频率是动态调频，这种情况下测试出来的模型性能会有波动。为
了防止性能测试结果不一致，在性能评估时，建议固定板子上的相关单元的频率再做测试。相关
单元的频率查看和设置命令如下：

### 1. CPU 调试命令

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
   # 输出 => 408000 600000 816000 1008000 1200000 1416000 1608000 1704000

   # 设置 CPU 频率，例如，设置 1.7GHz
   echo userspace > /sys/devices/system/cpu/cpufreq/policy0/scaling_governor
   echo 1704000 > /sys/devices/system/cpu/cpufreq/policy0/scaling_setspeed
   ```
### 2. 内存（DDR）调试命令

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

### 3. NPU 调试命令

1. 查看 NPU 频率（rk3588 专用）

   ```shell
   cat /sys/class/devfreq/fdab0000.npu/cur_freq
   ```
2. 固定 NPU 频率（rk3588 专用）
   >注意：在 NPU 驱动 0.7.2 版本之后，需要先打开 NPU 电源，才能进行频率设置
   ```shell
   # 查看 NPU 可用频率
   cat /sys/class/devfreq/fdab0000.npu/available_frequencies
   # 设置 NPU 频率，例如，设置 1 GHz
   echo userspace > /sys/class/devfreq/fdab0000.npu/governor
   echo 1000000000 > /sys/kernel/debug/clk/clk_npu_dsu0/clk_rate
   ```

### 4. NPU 支持查询设置项

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
