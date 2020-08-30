# DevOps Notes & Scripts

我日常总结出来的一些 DevOps 笔记与脚本。

个人笔记，并不是教程，也不保证正确！

主要包含：

1. 用于容器化部署常见应用的 docker-compose 配置（单机）。
2. Kubernetes 生态：部署、配置、组件及使用笔记。
4. Telemetry：监控、日志、链路追踪
1. 容器：Docker、容器镜像仓库、Podman、CRIO 等。
3. CI/CD：Jenkins/GitLabCI 等
1. 操作系统：Linux 系统、KVM 虚拟化等。
6. 编程语言学习笔记：Python/Golang/Java
7. Homelab: 家庭服务器相关，以及一些个人爱好。
5. DevOps 实用脚本

## docker-compose

参考资料：

- [awesome-compose](https://github.com/docker/awesome-compose)


## 国内主流镜像站

由于众所周知的原因，很多时候我们需要为各种系统、应用、包管理器设置镜像源以加速下载。

主要有如下几个镜像站：

1. [阿里云开源镜像站](https://developer.aliyun.com/mirror/): 个人感觉是国内下载速度最快的一个镜像源。
    - 提供了 ubuntu/debian/centos/alpine，以及 pypi/goproxy 等主流 OS/PL 的镜像源。比较全。
2. [清华开源镜像源](https://mirrors.tuna.tsinghua.edu.cn/): 非常全，更新也很及时。
    - 但是速度比不上阿里云，而且有时会停机维护。。
1. [北京外国语大学镜像站](https://mirrors.bfsu.edu.cn): 清华镜像的姊妹站，因为目前用的人少，感觉速度比清华源快很多。
3. [中科大开源镜像源](http://mirrors.ustc.edu.cn/): 这个也很全，更新也很快。但是不够稳定。
    - 比清华源要快一点，但是停机维护的频率更高。而且前端时间因为经费问题还将 pypi 源下线了。
4. [腾讯镜像源](https://mirrors.cloud.tencent.com/): 才推出没多久的镜像源，还没用过。

首推阿里云镜像源，稳定可靠速度快。
