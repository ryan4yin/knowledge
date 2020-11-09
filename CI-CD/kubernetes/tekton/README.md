# Tekton Pipeline

Tekton Pipeline 是一个云原生流水线项目，通过 Kubernetes CRDs 来定义和运行流水线。

它和 Argo Workflow 其实很类似，只是目的不同，导致它的功能不如 Argo Workflow 强大。

Jenkins-X 默认使用 Tekton Pieline 作为流水线引擎。

## 简单说明

Tekton 主要提供 5 个 Kubernetes 自定义资源实现流水线的定义与运行：

1. 定义流水线：
   1. Task: 定义单个任务
   2. Pipeline: 将多个任务组合成流水线。
   3. Pipeline Resource: 流水线中的 Task 通过这种资源对象传递参数/Artifacts.
2. 运行流水线
   1. TaskRun: 直接运行单个任务，可指定参数
   2. PipelineRun: 运行一个流水线，可传参

而流水线用到的配置和敏感信息，可以直接存在 kubernetes configmap/secrets 中。
