# [Knative - Serverless 应用的构建、部署与管理平台](https://github.com/knative)

## 架构

Knative 由两大组件组成：

1. Servering（工作负载管理）: 负责处理容器部署、网络、扩缩容和版本追踪。
2. Eventing（事件管理）: 统一的事件管理，

Knative 本身只提供容器级别的 Serverless 能力，而从源码到容器的流程，它建议你使用 Tekton:

1. [Tekton](/CI-CD/tekton/README.md): 一个云原生的 CI/CD 流水线。


结合上述三个组件，就得到了 Knative: 应用从源码到生产环境的全生命周期管理平台。

此外，Knative 还可以与服务网格 Istio 结合，提供服务路由管理、灰度发布等功能。


## 参考


- [《Knative 云原生应用开发指南》开启云原生时代 Serverless 之门 - 阿里云社区](https://developer.aliyun.com/article/739122)
- [实现Serverless面临的五大挑战](https://zhuanlan.zhihu.com/p/143389610)
