# [Argo Workflow](https://github.com/argoproj/argo/)

Argo Workflow 是一个云原生工作流引擎，专注于编排并行任务。它的特点如下：

1. 使用 Kubernetes 自定义资源(CR)定义工作流，其中工作流中的每个步骤都是一个容器。
1. 将多步骤工作流建模为一系列任务，或者使用有向无环图（DAG）描述任务之间的依赖关系。
2. 可以在短时间内轻松运行用于机器学习或数据处理的计算密集型作业。
3. Argo Workflow 可以看作 Tekton 的加强版，因此显然也可以通过 Argo Workflow 运行 CI/CD 流水线(Pipielines)。

## 简单的使用体验

简单的总结

1. WorkflowTemplate 就相当于 Jenkins 的 Jenkinsfile
1. 在 Argo UI 的 WorkflowTemplate 界面 Submit 一个 WorkflowTemplate，对应 Jenkins 在 Job 界面点击一次构建。
1. 提交 WorkflowTemplate 时，也有一个类似 Jenkins 的参数设定界面，可以修改 WorkflowTemplate 的默认参数。
2. 提交 WorkflowTemplate 会生成一个 Workflow，Workflow 就对应 Jenkins 的一次构建(Build)。



### 1. Workflow 的分类

当 Workflow 越来越多的时候，如果不做分类，一堆 WorkflowTemplate 堆在一起就会显得特别混乱。（没错，我觉得 Drone 就有这个问题...）

Argo 是完全基于 Kubernetes 的，因此目前它也只能通过 namespace/labels 进行分类。
这样的分类结构和 Jenkins 的视图-文件夹体系当然是没法比，但是应该也够用了。

### 2. Workflow 的重用 - WorkflowTemplate

将 yaml 定义中的 `Kind` 从 `Workflow` 修改为 `WorkflowTemplate`，就能得到一个 WorkflowTemplate.

WorkflowTemplate 可以被其他 Workflow 引用并触发，也可以正常传参。

### 3. 其他特性

1. 凭据管理：利用了 Kubernetes 原生的 Secrets 存储 Git/Docker 等工具的密钥/token
1. 定时执行的 Workflow
2. 提供 RESTful API
3. step 之间可以传递 parameters，并且提供 artifact/outputs/exitcode 等返回值
4. Workflow of Workflows: 一个父工作流，可以触发并管理多个子工作流，也可以操作子工作流的 results。（我们很需要这个特性）


### 4. Web UI

Argo Workflow 的 Web UI 感觉还很原始。确实该支持的功能都有，但是它貌似不是面向「用户」的，功能比较底层。

它不像 Jenkins 一样，有很友好的使用界面。

另外它所有的 Workflow 都是相互独立的，没办法直观地找到一个 WorkflowTemplate 的所有构建记录，只能通过 label/namespace 进行分类，通过任务名称进行搜索。
而 Jenkins 可以很方便地看到同一个 Job 的所有构建历史。


## 扩展项目

- [couler](https://github.com/couler-proj/couler): 为  Argo/Tekton/Airflow 提供统一的构建与管理接口
- [argo-python-dsl](https://github.com/argoproj-labs/argo-python-dsl): 使用 Python DSL 编写 Argo Workflow
- [argo-client-python](https://github.com/argoproj-labs/argo-client-python): Argo Workflow 的 Python 客户端

看着感觉挺不错，可以考虑直接用 couler，用 Python 写 WorkflowTemplate，这样就一步到位，所有 CI/CD 代码全部是 Python 了，
再也不用维护 Jenkinsfile 了哈哈哈哈~


## 画外

Argo 相比其他 CI 工具，最大的特点，是它假设「任务」之间是有依赖关系的，因此它提供了多种协调编排「任务」的方法。

但是貌似 Argo CD 并没有继承这个理念，Argo CD 部署时，并不能在 kubernetes 资源之间，通过 DAG 等方法定义依赖关系。

微服务的按序更新，我们目前是自己用 Python 代码实现的，目前没有在社区找到类似的解决方案。

## 参考

- [Argo加入CNCF孵化器，一文解析Kubernetes原生工作流](https://www.infoq.cn/article/fFZPvrKtbykg53x03IaH)

