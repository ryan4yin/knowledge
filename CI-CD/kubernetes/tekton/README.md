# Tekton Pipeline

Tekton Pipeline 是一个云原生流水线项目，通过 Kubernetes CRDs 来定义和运行流水线。

它和 Argo Workflows 其实很类似，只是目的不同，导致它的功能不如 Argo Workflows 强大。

Tekton 和 Drone 更类似，它是一个基于源代码的 CI/CD 工具。
而 Argo 是一个通用的**并行任务编排**工具，只是它的功能恰好也很契合 CI/CD 场景。

>区别于 Argo 这种基于 Kubernetes 的 Workflow 工具， Tekton 在工作流控制上的支持是比较弱的。一些复杂的场景比如循环，递归等都是不支持的。更不用说 Argo 在高并发和大集群调度下的性能优化。这和 Tekton 的定位有关， Tekton 定位于实现 CICD 的框架，对于 CICD 不需要过于复杂的流程控制。大部分的研发流程可以被若干个最佳实践来覆盖。而这些最佳实践应该也必须可以在不同的组织间共享，为此 Tekton 设计了 PipelineResource 的概念。 PipelineResource 是 Task 间交互的接口，也是跨平台跨组织共享重用的组件，在 PipelineResource 上还可以有很多想象空间。

国内京东、字节跳动等大厂都有将 Tekton 应用在自己的流水线中。

## 简单说明

Tekton 主要提供 5 个 Kubernetes 自定义资源实现流水线的定义与运行：

1. 定义流水线：
   1. Task: 定义单个任务
   2. Pipeline: 将多个任务组合成流水线，一个 Pipeline 就是一张 DAG 有向无环图，每个 Task 就是其中一个节点。
      1. Task 默认并发执行，可以通过 RunAfter 和 From 关键字控制执行顺序（DAG）。
   3. Pipeline Resource: 流水线中的 Task 通过这种资源对象传递参数/Artifacts.
2. 运行流水线
   1. TaskRun: 直接运行单个任务，可指定参数
   2. PipelineRun: 运行一个流水线，可传参

而流水线用到的配置和敏感信息，可以直接存在 kubernetes configmap/secrets 中。


## 相关文档

- [云原生在京东丨基于 Tekton 打造下一代云原生 CI 平台](https://developer.jdcloud.com/article/1195?filterType=1)
- [开源 CI/CD 构建框架 TekTon 的深入剖析 - 阿里巴巴中间件](https://mp.weixin.qq.com/s/p2mBQJFk9cCxlcIcI9w1cg)
