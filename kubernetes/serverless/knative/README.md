# [Knative - Serverless 应用的构建、部署与管理平台](https://github.com/knative)

## 架构

Knative 由两大组件组成：

1. Servering（工作负载管理）: 负责处理容器部署、网络、扩缩容和版本追踪。
2. Eventing（事件管理）: 统一的事件管理，

Knative 本身只提供容器级别的 Serverless 能力，而从源码到容器的流程，它建议你使用 Tekton:

1. [Tekton](/CI-CD/tekton/README.md): 一个云原生的 CI/CD 流水线。


结合上述三个组件，就得到了 Knative: 应用从源码到生产环境的全生命周期管理平台。

此外，Knative 还可以与服务网格 Istio 结合，提供服务路由管理、灰度发布等功能。


## 应用场景

Knative 感觉还是太底层了，抽象程度更好，对运维而言复杂度又增加了。
而且为了实现「缩容到 0」、「按并发请求数进行扩容」等操作，Knative 增加了一个网络代理（流量又多转发一次、甚至可能还要等待应用扩容到 1）。

而「缩容至0」对微服务架构而言意义不大，首先就不确定微服务流量会不会低到几乎没有，其次扩缩容对微服务而言速度还是比较慢的（好几秒）。
就为了这么个特性而增加网络性能损耗，甚至还可能会让用户等待微服务扩容，个人感觉是得不偿失。

Knative 应该是比较适合比微服务更轻量的 FaaS 架构，结合 serverless framework 使用。
在 FaaS 架构下，业务被拆分得更细了，更轻量级的容器显然能获得更快的扩缩容速度，这时从 0 扩容到 1 的等待过程，对用户而言可能就可以接受了。
另外对数量庞大的 Fucntions 而言，将大量「非热点 Functions」缩容到 0 也许能节约大量资源。
「缩容到 0」对 FaaS 意义很大。

Serverless 在微服务领域的应用场景：BFF - Backend for Frontend

## 参考


- [《Knative 云原生应用开发指南》开启云原生时代 Serverless 之门 - 阿里云社区](https://developer.aliyun.com/article/739122)
- [实现Serverless面临的五大挑战](https://zhuanlan.zhihu.com/p/143389610)
