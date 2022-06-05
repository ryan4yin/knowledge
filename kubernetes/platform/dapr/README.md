# Dapr

Dapr 是一种可移植的，无服务器的，事件驱动的运行时，它使开发人员可以轻松构建弹性，无状态或有状态的微服务，让它们在云或边缘上运行，同时它支持多种编程语言和开发框架。

看上面这句介绍，有 serverless 和 event-driven，因此它貌似和 knative/kubevela 都存在交集。

它给自己的定位是 Multi-Runtime - 一个比服务网格更通用、能力更强的运行时，一个运行时就能提供原本需要多个 Sidecar 实现的能力（如缓存代理，绑定代理）

## Dapr 的使用举例

Dapr 的每种能力，都是对最佳实践的一个封装，被称为 Build Blocks，目前 Dapr 提供如下 Build Blocks:

- Service invocation
  - 即服务间调用，支持 HTTP/gRPC 两种方法。本质上的功能与 Istio 服务网格是一样的，它提供服务间调用的流量治理能力。
  - 提供如下流量治理能力：服务发现、标准化服务间调用的 API、流量加密、处理请求超时与重试、实现流量可见性与链路追踪
- State management
  - Dapr 的状态管理能力，为服务提供标准的 key-value 存储/查询接口
  - [支持的存储](https://docs.dapr.io/reference/components-reference/supported-state-stores/)主要有：MongoDB/Redis/MySQL/PostgreSQL，但是封装代码的完善程度不一，部分功能不一定支持，此外许多存储的支持状态还是 Alpha.
- Publish & subscribe
  - 提供了平台无关的 API 用于消息的发布与订阅
  - 后端支持 Redis/NATs/
- Bindings
  - 绑定某个 Input/Output 事件，在事件发生时，触发某个内部 APP 或者外部资源
  - 感觉类似 serverless 服务的 API Gateway 等触发器？
- Actors
  - Actors 是一种并发模型，它使用户可以将程序拆成许多 Actors 来实现。
  - 每个 Actor 都是单线程的，仅处理输入消息，然后发送若干输出消息给其他 Actors，或者直接创建新的 Actors
  - Dapr 运行时会处理这些 Actor 的创建、运行、调度，把用户从这些并发逻辑中解放出来。
  - 适用于高并发、不关心程序当前并发状态、代码中不存在高 IO 延迟的场景
- Observability
  - Monitor applications through tracing, metrics, logs and health
- Secrets management
  - 提供统一的 API 用于 secrets 的存储、查询，简化代码编写，屏蔽后端差异
  - 支持许多后端存储：Hashicorp Vault、Kubernetes Secrets、AWS Secrets Manager、Azure Key Vault 等
- Configuration
  - 允许用户动态读写配置内容，并且立即应用到程序中
  - 目前仅支持 gRPC 协议，仅支持使用 redis 作为存储


## Multi-Runtime 与 Service-Mesh 的区别

>https://docs.dapr.io/concepts/service-mesh/

虽然同为 Sidecar 模式，但是和 Service Mesh 相比，Multi-Runtime 有自身的特点：

- 提供能力的方式和范围
  - Multi-Runtime 提供的是分布式能力（Build Blocks），是封装了微服务开发的各种最佳实践，是以开发者为中心（Developer-centric）
  - Service-Mesh 专注于服务网格内的流量治理，是基础设施为中心（Infrastructure-centric），而且不关注其他流量的治理（如 Redis/MySQL/Queue/...）
- 和 App 的交互方式
  - Multi-Runtime 和应用之间的交互是开放而有 API 标准的（屏蔽了具体后端的协议差异从而提高可移植性，如 Redis/Memcache/dynamodb/...），应用程序可通过引入 Dapr SDK 简化开发。
  - 除链路追踪外，Service-Mesh 对应用而言是完全透明的（直接使用原协议转发，最多对数据稍做修改），同样也无法解决与某些中间件沟通时的移植性问题。

![](./_imgs/multiruntime-vs-servicemesh.webp)

## 参考

- [一年增加1.2w星，Dapr能否引领云原生中间件的未来？](https://mp.weixin.qq.com/s/KSln4MPWQHICIDeHiY-nWg)


