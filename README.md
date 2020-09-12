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


## 关于 DevOps

DevOps，即开发+运维。DevOps经常被描述为“开发团队与运维团队之间更具协作性、更高效的关系”。

我们通常听到的「DevOps 工程师」，更多的是指一类新的运维工程师，他们行事的核心思想有：

1. Everything as Code（GitOps）: 所有代码/流程/基础设施/文档/规范都通过 Git 做版本控制。保证任何操作的可重复性。
   1. 基础设施即代码
   2. 文档即代码：任何事件的处理流程都应该有对应的文档及规范。
2. 持续集成/持续交付: 容器化、微服务化，自动化。加快产品迭代速度，也减少人为操作引入的错误。
   1. Everything on Containers.
   2. Automate what can be automated.
3. 待补充

DevOps 并没有权威的解释，我个人觉得，使用上述思想构建与维护运维系统的运维工程师，就是一名 DevOps 工程师。


## DevOps 理论指导

不论是写前后端代码，做性能测试，还是实现 DevOps 功能，都不应该仅依靠直觉去编程、调试、排查问题。
如果能熟悉一些相关理论，了解一些最佳实践，并且在做事情的时候有意识地去比较、代入，往往能事半功倍。

这个笔记仓库记录的最多的，应该算是我个人的最佳实践，但是缺乏理论相关的东西。我对理论目前也算不上熟悉。

下面列出的是我目前可能比较欠缺的理论知识，从中也能学到些归纳总结的技巧：

- [Ledge —— DevOps knowledge learning platform](https://github.com/phodal/ledge)
- [Everything as code architecture design patten and rules](https://github.com/phodal/ascode.ink)
