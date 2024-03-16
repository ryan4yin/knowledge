# Nvidia CUDA

## K8s 中的 GPU 监控

> https://github.com/NVIDIA/dcgm-exporter

> https://catalog.ngc.nvidia.com/orgs/nvidia/teams/k8s/containers/dcgm-exporter

## 利用 CUDA 加速计算

> https://developer.nvidia.cn/gpu-accelerated-libraries

### 1. TensorRT

> https://developer.nvidia.cn/tensorrt

如何使用 TensorRT 加速 pytorch 的推理？

参考：

4. [Saving/Loading models compiled with Torch-TensorRT](https://pytorch.org/TensorRT/user_guide/saving_models.html)
5. [Torch-TensorRT - Compile Stable Diffusion and Inference](https://pytorch.org/TensorRT/tutorials/_rendered_examples/dynamo/torch_compile_stable_diffusion.html)
6. [Compile a Torch Model(.pt) into Torch-TensorRT(xxx_trt.ts) via CLI](https://pytorch.org/TensorRT/cli/torchtrtc.html)

### 2. TF32 精度

1. https://pytorch.org/docs/stable/notes/cuda.html#tensorfloat-32-tf32-on-ampere-devices
2. https://blogs.nvidia.com/blog/tensorfloat-32-precision-format/

## Nvidia GPU 架构、CUDA 版本、Nvidia 驱动版本、PyTorch 版本之间的兼容性

> https://docs.nvidia.com/deeplearning/frameworks/support-matrix/index.html

上述这几个版本 / 架构之间存在一定的兼容性关系，如果不匹配，可能会导致程序无法充分利用上 GPU，导致运
行效率低下，甚至直接无法运行。

对于容器方案，建议参考
[Nvidia Frameworks Support Matrix](https://docs.nvidia.com/deeplearning/frameworks/support-matrix/index.html)
列出的搭配方案，以 Nvidia 官方提供的 Docker 镜像为基础镜像构建符合自己需求的应用镜像。

如果容器运行在云服务上，建议同时参考云服务商官方的文档，比如：

1. GCP 的 GPU 驱动相关文档:
   https://cloud.google.com/compute/docs/gpus/install-drivers-gpu#no-secure-boot
   1. 比如说其中就建议 Nvidia L4 使用 525.60.13+ 版本的驱动，以及 CUDA Toolkit 12.1+ 的 CUDA. 对应的
      支持 CUDA 12.1 的 PyTorch 版本是 2.1.0.

## Nvidia 相关容器镜像

> https://catalog.ngc.nvidia.com/containers

1. cuda: https://catalog.ngc.nvidia.com/orgs/nvidia/containers/cuda/tags
   1. such as `nvcr.io/nvidia/cuda:12.1.0-cudnn8-devel-ubi8`
2. tensorrt: https://catalog.ngc.nvidia.com/orgs/nvidia/containers/tensorrt
3. pytorch: https://catalog.ngc.nvidia.com/orgs/nvidia/containers/pytorch
   1. such as `nvcr.io/nvidia/pytorch:23.10-py3`

## 其他通用的加速库

- xFormers
-

## 常见问题

### 1. 安装驱动报错 `An NVIDIA kernel module 'nvidia' appears to already be loaded in your kernel.`

解决方法：通过 `lsof /dev/nvidia*` 查看哪些进程占用了 `/dev/nvidia*`，然后通过 `ps -ef | grep $pid`
查看对应的进程，然后 kill 掉这些进程。将进程全部 kill 掉后，再重新安装驱动即可。
