# Serverless 介绍

>[开源 Serverless 平台 - CNCF landscape](https://landscape.cncf.io/category=installable-platform&format=card-mode&grouping=category)

Serverless 指对平台的用户屏蔽掉了服务器层面的配置和管理， Serverless 平台自己把这些“脏活累活”都默默干好了，上层用户（后端开发）只需要关注自己的业务逻辑，而运维就可以下岗了...

Serverless 的好处是它**分离了关注点**，底层的服务器配置与管理被直接封装好了。用户需要关注的东西少了，效率也就更高了。

目前的 Serverless 产品有好几种，它们分别实现了不同级别的 Serverless 能力：

1. 阿里云 Serverless Kubernetes: 提供了一套与节点(Node)无关的 k8s 系统，运维人员不再需要考虑服务器的扩缩容问题。
    - 这是比较靠近底层的 Serverless 产品，因为 k8s 本身还比较底层，容器的调度、灰度升级回滚、扩缩容等还是需要运维通过 k8s 来处理。
2. Container as a Service - [Knative](https://github.com/knative/serving)：用户只需要提供代码、Dockerfile 及流水线配置，Knative 自己帮你把容器构建、调度、灰度升级回滚、弹性扩缩容等都干了。
    - 这个是容器级别的 Serverless，比 Serverless K8s 更进一步地分离了关注点。
    - 它的主要目标是成为一个通用的 Serverless 底层平台, 因此它暴露出了很多底层细节。
    - 通过 [serverless-knative](https://github.com/serverless/serverless-knative) 可支持 serverless-framework.
1. Container as a Service - Kubevela: 从 serverless 角度看，它和 Knative 很类似。用户也只需要提供代码、Dockerfile，kubevela 通过 trait 插件帮你自动处理容器构建、调度、灰度升级回滚、弹性扩缩容...
3. 函数计算（FaaS, Function as a Service）：将运维能力封装到了极致。用户只要给源码，其他的杂事都由云平台处理。
    - [serverless-framework](https://github.com/serverless/serverless) 是目前最流行的 faas sdk，基本上所有 serverless 平台都有对应的插件。
    - 开源的完全基于 kubernetes 的 faas 平台，比较有名的有：
      - [fission - 2016-08](https://github.com/fission/fission): 大量的 Fucntions 都是使用一样的运行环境，完全没必要为每个 Function 创建一个 Pod。fission 的最大优势在于它解耦了 Pod 和 Function：通过「environment pool-manager」来管理 Pods，Functions 被动态地上传到 Pod 中执行。这提升了 Function 启动速度以及集群资源利用率。
        - fission 貌似不支持 serverless-framework，得用它专有的 SDK 写 Function.
      - [kubeless - 2016-11](https://github.com/kubeless/kubeless): 据说是最易用的开源 kubeless 平台，但是它为每个 Function 创建一个 Pod，资源利用率不够高，而且启动速度也没 fission 快。
        - 通过　[serverless-kubeless](https://github.com/serverless/serverless-kubeless) 支持　serverless-framework.
      - Knative - 2018-01: 前面已经介绍过了，Knative 更新，也更通用。既能支持 CaaS，也能支持 FaaS，而且有众多大厂的支持。

另外，上述所有的容器、函数，都必须是无状态的（Stateless），因为显然只有无状态的容器/函数，才可以随意的扩缩容。

开源领域，目前最被看好的 Serverless 平台，是 Google/RedHat(IBM) 开源的 Knative. 

## Serverless 的应用场景

首先 Serverless Kubernetes / Container as a Service 这种，一个基于 k8s，一个是基于容器，应用场景显然就是简化容器/k8s的使用。

最新奇的是 Faas，目前它的最佳应用场景有：

1. 做微服务与前端之间的胶水层：BFF - Backend for Frontend
   - 比如 API 聚合，数据裁剪、格式化、聚合等。
2. 事件请求场景：定时任务、低频请求等
3. 流量突发场景（直播、双十一等活动）：微服务的扩容速度慢，不足以应对过高的突发流量。这就需要 FaaS 基于请求的，毫秒级的扩容。

总的来说，FaaS 适合做一些轻量的业务逻辑，或者胶水层。

比如物联网数据处理、定时任务、音视频转码等，都是一次性的，轻量的任务。

### BFF 的好处

通过 FaaS 实现的 BFF，可以提供给前端更大的自主权，包括 API 的定制能力。
一些 API 的定制不再需要和后端沟通，可以减少沟通成本，前端效率也就能更高。

同时有了 BFF 这个胶水层，后端原本的一些巨型应用，就可以拆分得更细。
原本的巨型应用因为影响范围太大，每一次更新都得慎之又慎，迭代速度慢，测试、运维成本高。
做进一步拆分后，再通过 BFF 黏合起来，每一个部分各自更新迭代，影响面小了，迭代、测试、运维成本也就低了，效率也就更高了。

不过 BFF 由前端开发，对前端的能力要求也会更高了。而且成百上千的 Functions 要怎么去设计、测试、最后再上线到 Serverless 平台，
怎么做版本控制？一个函数一个 Git 仓库？这些都还需要探索。

## 相关文档

- [Serverless应用场景](https://help.aliyun.com/document_detail/65565.html)
- [你学BFF和Serverless了吗](https://juejin.cn/post/6844904185427673095)
- [Why Have Alibaba Started to Embrace OAM When Serverless Is So Popular?](https://www.alibabacloud.com/blog/why-have-alibaba-started-to-embrace-oam-when-serverless-is-so-popular_596593)
- [serverless到底是个什么鬼 - 滴滴云](https://zhuanlan.zhihu.com/p/140419955)