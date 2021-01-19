# [containerd](https://github.com/containerd/containerd)

在 kubernetes 中使用 dockerd 做运行时，本身是不必要的。

越过 dockerd，直接使用它底层的 containerd 做运行时，削减中间环节，可以提升代码的可维护性，减少 Bug.

各家大厂早就将运行时切换到了 containerd，对安全要求更高的甚至已经切换到了 kata-containers 等安全容器方案。

为此有必要尽快熟悉 containerd，将集群尽快迁移过来。


## 安装与配置



## 常用命令

命令行工具，建议直接使用 `crictl`，其命令行参数和 `docker-cli` 基本一致，但是:

1. 只提供和容器/镜像相关的命令，并添加了 pod 相关命令
2. 不支持 build 镜像，作为单纯的 k8s 运行时调试工具，不需要提供这个功能

crictl 支持连接任何兼容 cri 的运行时，它默认情况下按顺序尝试连接如下几个 endpoint(on linux):

- `unix:///var/run/dockershim.sock`
- `unix:///run/containerd/containerd.sock`
- `unix:///run/crio/crio.sock`

endpoint 也可以通过命令行参数/环境变量/配置文件手动设置，详见 [docs/crictl](https://github.com/kubernetes-sigs/cri-tools/blob/master/docs/crictl.md)
