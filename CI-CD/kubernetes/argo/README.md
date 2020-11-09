# [Argo Workflow](https://github.com/argoproj/argo/)

Argo Workflow 是一个云原生工作流引擎，专注于编排并行任务。它的特点如下：

1. 使用 Kubernetes 自定义资源(CR)定义工作流，其中工作流中的每个步骤都是一个容器。
1. 将多步骤工作流建模为一系列任务，或者使用有向无环图（DAG）描述任务之间的依赖关系。
2. 可以在短时间内轻松运行用于机器学习或数据处理的计算密集型作业。
3. Argo Workflow 可以看作 Tekton 的加强版，因此显然也可以通过 Argo Workflow 运行 CI/CD 流水线(Pipielines)。

## 简单的使用体验

### 1. Workflow 的分类

当 Workflow 越来越多的时候，如果不做分类，一堆工作流堆在一起就会显得特别混乱。（没错，我觉得 Drone 就有这个问题...）

Argo 是完全基于 Kubernetes 的，因此目前它也只能通过 namespace 进行分类。
单层的分类结构和 Jenkins 的视图-文件夹体系当然是没法比，但是应该也够用了。

### 2. Workflow 的重用 - WorkflowTemplate


### 3. 其他特性

1. 定时执行的 Workflow
2. 提供 RESTful API
3. step 之间可以传递 parameters，并且提供 artifact/outputs/exitcode 等返回值
4. 手动执行，手动指定 parameters（待验证）
5. Workflow of Workflows: 一个父工作流，可以触发并管理多个子工作流，也可以操作子工作流的 results。（我们很需要这个特性）


## 扩展项目

- [couler](https://github.com/couler-proj/couler): 为  Argo/Tekton/Airflow 提供统一的构建与管理接口
- [argo-python-dsl](https://github.com/argoproj-labs/argo-python-dsl): 使用 Python DSL 编写 Argo Workflow
- [argo-client-python](https://github.com/argoproj-labs/argo-client-python): Argo Workflow 的 Python 客户端



## 参考

- [Argo加入CNCF孵化器，一文解析Kubernetes原生工作流](https://www.infoq.cn/article/fFZPvrKtbykg53x03IaH)

