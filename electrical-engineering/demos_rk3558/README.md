# RK3558/RK3558S demo

RK3558/RK3558S 是瑞芯微推出的一款高性能 ARM64 SoC，配置如下：

- 8C(A76*4 + A55*4)
- GPU(4Cores, Mail-G610)
- NPU(6Tops)

其中 RK3558 多一些外部模块，支持更多接口，RK3558S 则没有这些模块，但是价格更低一点。

我目前拥有 Rock 5A 4G（已购，预计 2023Q2 出货）、Orange Pi 5 8G 这两块使用 RK3558S 芯片的开发版。

## NPU 使用案例

瑞芯微官方提供了两个 NPU 相关的仓库，其中包含使用手册、examples、驱动等内容：

- [rknpu2](https://github.com/rockchip-linux/rknpu2): rknpu2 为 NPU 提供了高层 C API 
- [rknn-toolkit2](https://github.com/rockchip-linux/rknn-toolkit2): AI 模型都需要转换为 rknn 格式后才能运行在 rk3558s 上。rknn-toolkit2 提供了模型转换与 AI 推理功能，其中 AI 推理可以运行在 PC 的 qemu 模拟器中，也可以跑在 rk3558s 的 npu 上。同时它还提供了 python 接口实现用 rk3558s npu 进行 AI 推理。

上面两个仓库虽然是用的 git 仓库，但实际底层内容都仅公开了 `.so`、`.whl`、docker 镜像等二进制安装包，并未开放源码。

此外官方提供的闭源 docker 镜像太大了，未保存在仓库中，仅在 README 中附带的 百度云盘 分享中提供了该镜像文件。
