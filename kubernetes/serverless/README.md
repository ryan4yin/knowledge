# Serverless 介绍

Serverless 指对平台的用户屏蔽掉了服务器层面的配置和管理， Serverless 平台自己把这些“脏活累活”都默默干好了，上层用户（后端开发）只需要关注自己的业务逻辑，而运维就可以下岗了...

Serverless 的好处是它**分离了关注点**，底层的服务器配置与管理被直接封装好了。用户需要关注的东西少了，效率也就更高了。

目前的 Serverless 产品有好几种，它们分别实现了不同级别的 Serverless 能力：

1. 阿里云 Serverless Kubernetes: 提供了一套与节点(Node)无关的 k8s 系统，运维人员不再需要考虑服务器的扩缩容问题。
    - 这是比较靠近底层的 Serverless 产品，因为 k8s 本身还比较底层，容器的调度、灰度升级回滚、扩缩容等还是需要运维通过 k8s 来处理。
1. 基于容器的 Serverless 平台（Knatvie）：用户只需要提供代码、Dockerfile 及流水线配置，Knative 自己帮你把容器构建、调度、灰度升级回滚、弹性扩缩容等都干了。
    - 这个是容器级别的 Serverless，比 Serverless  K8s 更进一步地分离了关注点。
    - 比较适合基于微服务架构的应用。
    - Knative 是目前最活跃的 Serverless 项目之一，有众多大厂参与。但是它仍然具有一定的运维复杂度，可能更适合被用作 Serverless 的底层实现。
2. 函数计算（Function as a Service, FaaS）：将运维能力封装到了极致。用户只要给源码，其他的杂事都由云平台处理。
    - [serverless-framework](https://github.com/serverless/serverless) 是目前最流行的 faas sdk，基本上所有 serverless 平台都有对应的插件。
    - 开源的完全基于 kubernetes 的 faas 平台，比较有名的有：
      - [fission](https://github.com/fission/fission): 大量的 Fucntions 都是使用一样的运行环境，完全没必要为每个 Function 创建一个 Pod。fission 的最大优势在于它解耦了 Pod 和 Function：通过「environment pool-manager」来管理 Pods，Functions 被动态地上传到 Pod 中执行。这提升了 Function 启动速度以及集群资源利用率。
      - [kubeless](https://github.com/kubeless/kubeless): 据说是最易用的开源 kubeless 平台，每个 Function 对应一个 Pod。但是它为每个 Function 创建一个 Pod，资源利用率不够高，而且启动速度也没 fission 快。

另外，上述所有的容器、函数，都必须是无状态的（Stateless），因为显然只有无状态的容器/函数，才可以随意的扩缩容。

目前我并没发现哪家云厂商提供了使用 Serverless 部署有状态应用/容器的功能。
相反我只看到云厂商们说：应用自己应该是无状态的，所有数据都应该用我们的对象存储(OSS)、数据库等产品来保存。
