# DevOps Notes & Scripts

我日常总结出来的一些 DevOps 笔记与脚本。

主要包含：

1. 用于容器化部署常见应用的 docker-compose 脚本。
1. Linux 系统配置：ulimit/sysctl
1. Docker 相关：镜像仓库（Harbor）管理等
1. Jenkins 相关：部署、Pipeline 流水线模板
1. Python 实用脚本库

## docker-compose

参考资料：

- [awesome-compose](https://github.com/docker/awesome-compose)


## 国内主流镜像站

由于众所周知的原因，很多时候我们需要为各种系统、应用、包管理器设置镜像源以加速下载。

主要有如下几个镜像站：

1. [阿里云开源镜像站](https://developer.aliyun.com/mirror/): 个人感觉是国内下载速度最快的一个镜像源。
    - 提供了 ubuntu/debian/centos/alpine，以及 pypi/goproxy 等主流 OS/PL 的镜像源。比较全。
1. [清华开源镜像源](https://mirrors.tuna.tsinghua.edu.cn/): 非常全，更新也很及时。但是网速比不上阿里云
    - 而且有时会停机维护。。
1. [中科大开源镜像源](http://mirrors.ustc.edu.cn/): 这个也很全，更新也很快。但是不够稳定。
    - 比清华源要快一点，但是停机维护的频率更高。而且前端时间因为经费问题还将 pypi 源下线了。
1. [腾讯镜像源](https://mirrors.cloud.tencent.com/): 才推出没多久的镜像源，还没用过。

首推阿里云镜像源。
