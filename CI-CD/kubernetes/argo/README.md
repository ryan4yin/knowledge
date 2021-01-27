# [Argo Workflow](https://github.com/argoproj/argo/)

Argo Workflow 是一个云原生工作流引擎，专注于**编排并行任务**。它的特点如下：

1. 使用 Kubernetes 自定义资源(CR)定义工作流，其中工作流中的每个步骤都是一个容器。
1. 将多步骤工作流建模为一系列任务，或者使用有向无环图（DAG）描述任务之间的依赖关系。
2. 可以在短时间内轻松运行用于机器学习或数据处理的计算密集型作业。
3. Argo Workflow 可以看作 Tekton 的加强版，因此显然也可以通过 Argo Workflow 运行 CI/CD 流水线(Pipielines)。

文章已迁移至：[云原生流水线 Argo Workflow 的安装、使用以及个人体验](https://ryan4yin.space/posts/expirence-of-argo-workflow/)

## 参考文档

- [Argo加入CNCF孵化器，一文解析Kubernetes原生工作流](https://www.infoq.cn/article/fFZPvrKtbykg53x03IaH)


视频:

- [How to Multiply the Power of Argo Projects By Using Them Together - Hong Wang](https://www.youtube.com/watch?v=fKiU7txd4RI&list=PLj6h78yzYM2Pn8RxfLh2qrXBDftr6Qjut&index=149)

