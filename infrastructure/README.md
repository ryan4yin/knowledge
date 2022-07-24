# Infrastructure - 基础设施的配置与管理


## 一、服务器环境配置工具

首选 ansible，别的工具没研究过，不做考虑。

## 二、IaaC - 基础设施即代码

基础设施：指云上的各类资源、Kubernetes 集群中的各类资源等。

这个领域，我目前了解到的有三个代表性的项目，它们都是通过声明式语法来配置基础设施，但是也有些区别：

1. terraform（热度最高）: 基础设施即**配置**，通过专用的 HCL 语言来声明式地配置基础设施。HCL 功能比较弱，而且还有额外的学习成本。
1. pulumi（热度其次）: 基础设施即**代码**，通过 Python/Go/TypeScript 等通用编程语言来声明基础设施，灵活性很高，个人推荐。
    - pulumi 的 provider 基本完全来自 terraform 社区，因此 API 结构也完全一致。
2. [crossplane](https://github.com/crossplane/crossplane): 通过 Kubernetes 自定义资源(CR) 来声明基础设施。
    - crossplane 提倡通过 Kubernetes API 资源模型来声明基础设施，表现形式上目前主要是 Yaml.
    - crossplane 集成了 OAM 模型，带来的一个特性是：它可以在平台无关的层面去定义基础设施，在各云平台都能通用！！！
1. [kubevirt](https://github.com/kubevirt/kubevirt): 它和 crossplane 理念一致，只是目标不同——使用 Kubernetes CR 来声明虚拟机。
    - 我们以前是使用 vsphere 的 python sdk 创建虚拟机，非常难用。现在正在向 ProxmoxVE 的 terraform provider 迁移，计划使用 pulumi/terraform 来声明虚拟机。
    - 这个项目目前保持观望。

个人比较看好 pulumi，使用通用编程语言来编写配置，灵活性非常高，这一定是未来的发展方向。
包括像 [couler](https://github.com/couler-proj/couler) 这样的项目，目标也是提供统一的 Python API 来编写 tekton(yaml)/argo(yaml)/airflow(python) 的 workflow，它的目标之一也是使用 Python 来替代 Kubernetes yaml。

另一方面，目前 pulumi/terraform 都缺少定义可移植基础设施的能力，每个云平台都需要使用对应的 provider 及其 API。
而 Crossplane+OAM，就能将云平台与具体的基础设施定义解耦，实现配置在不同平台间的复用。
因此 Crossplane 的未来也值得期待。


## 三、其他工具

成本估算：
- [infracost](https://github.com/infracost/infracost): 根据 terraform 配置变更，估算成本变化

资源导入（配置备份）：

- [terraformer](https://github.com/GoogleCloudPlatform/terraformer)

## 参考

- [OAM和Crossplane: 构建现代应用的下一个阶段](https://zhuanlan.zhihu.com/p/145443259)
