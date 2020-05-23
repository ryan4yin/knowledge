# [Knative - Serverless 应用的构建、部署与管理平台](https://github.com/knative)

## Serverless 介绍

Serverless 指对平台的用户屏蔽掉了服务器层面的配置和管理， Serverless 平台自己把这些“脏活累活”都默默干好了。上层用户（后端开发）只需要关注自己的业务逻辑，而运维就可以下岗了。。。

Serverless 的好处是它**分离了关注点**，底层的服务器配置与管理被直接封装好了。用户需要关注的东西少了，效率也就更高了。

目前的 Serverless 产品有好几种，它们分别实现了不同级别的 Serverless 能力：

1. 阿里云 Serverless Kubernetes: 提供了一套与节点(Node)无关的 k8s 系统，运维人员不再需要考虑服务器的扩缩容问题。
    - 这是比较靠近底层的 Serverless 产品，因为 k8s 本身还比较底层，容器的调度、灰度升级回滚、扩缩容等还是需要运维通过 k8s 来处理。
1. 基于容器的 Serverless 平台（Knatvie）：用户只需要提供容器，Knative 自己帮你把容器调度、灰度升级回滚、弹性扩缩容等都干了。
    - 这个是容器级别的 Serverless，比 Serverless  K8s 更进一步地分离了关注点。
    - 比较适合基于微服务架构的应用。
2. 函数计算（Function as a Server, FaaS）：将运维能力封装到了极致。用户只要给源码，其他的杂事都由云平台处理。
    - 目前还处于比较早期的阶段，落地案例比较少。
    - 函数式计算按 API 调用次数以及资源使用量收费，而且有很高的免费额度。很值得自己尝试一下。

另外，上述所有的容器、函数，都必须是无状态的（Stateless），因为显然只有无状态的容器/函数，才可以随意的扩缩容。

目前我并没发现哪家云厂商提供了使用 Serverless 部署有状态应用/容器的功能。
相反我只看到云厂商们说：应用自己应该是无状态的，所有数据都应该用我们的对象存储(OSS)、数据库等产品来保存。

## 架构

Knative 由两大组件组成：

1. Servering
2. Eventing

Knative 本身只提供容器级别的 Serverless 能力，而从源码到容器的流程，它建议你使用 Tekton:

3. [Tekton](https://github.com/tektoncd/pipeline)




## 参考


- [《Knative 云原生应用开发指南》开启云原生时代 Serverless 之门 - 阿里云社区](https://developer.aliyun.com/article/739122)
