# CI/CD on Kubernetes


1. Tekton:  CI/CD pipeline，是从 Knative 中分化出来的
2. Argo: 一个基于 DAG 的复杂 Workflow 工具，它对复杂的任务编排的支持比 Tekton 强很多。
   1. Argo Workflow 主要是设计用于数据处理的，因此它需要更灵活的任务编排功能。
   2. 而 Tekton 的目标只是 CI/CD，CI/CD 的流程往往非常固定，不需要很复杂的任务编排。（当然这也不绝对，因此也确实有人使用 Argo 做 CI/CD 的）
3. ArgoCD: GitOps 的 k8s 自动化部署工具
4. Knative: 全生命周期管理(从源码到上线)，Serverless 平台。

详细的文档参见 [kubernetes](/kubernetes/) 文件夹。
