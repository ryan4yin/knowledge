# [containerd](https://github.com/containerd/containerd)

在 kubernetes 中使用 dockerd 做运行时，本身是不必要的。

越过 dockerd，直接使用它底层的 containerd 做运行时，削减中间环节，可以提升代码的可维护性，减少 Bug.

各家大厂早就将运行时切换到了 containerd，对安全要求更高的甚至已经切换到了 kata-containers 等安全容器方案。

为此有必要尽快熟悉 containerd，将集群尽快迁移过来。



