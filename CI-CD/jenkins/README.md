# [Jenkins](https://www.jenkins.io/zh/doc/)

Jenkins 是当下最流行的 CI/CD 工具之一，优势在于：

1. 众多插件供选用，因此功能繁多。（虽然是良莠不齐，甚至好多都已经停更好多年了。）
1. 有视图-文件夹的概念，可以很方便地将 Jobs 进行分类。
1. 任务之间可以互相调用。很适合分层结构项目的 CI/CD。
1. 可以定时构建。

但是也存在很多问题：

1. 单点故障问题，Master 只能一个。
1. Slaves 无法动态扩缩容，不能随意地创建销毁。这导致效率不好提升，垃圾数据也容易积累。
1. Bug 也是比较多，令人难受。
1. UI 也是相当丑。
1. 使用 Groovy DSL 写配置，语法提示太弱，容易写出错误的代码。
    - pipeline 的运行时错误无法提示准确的位置，需要自己肉眼 Debug...


总的来说，它很适合层次结构比较复杂的项目。比如说处理很多 Git 仓库的相互依赖、分层构建。
还有一些批量工作，比如需要批量构建、批量修改、批量更新、批量部署等等。

对于这种批量任务，当前路径的 `jenkinsfile-templates` 中有两个模板可供参考。

另外在分层结构中，同一层次的任务流程往往一模一样，因此我一般建议将所有 Jenkinsfile 和构建脚本（如 Python）都放在同一个 Git 仓库中，每一类任务一个 Jenkinsfile。
Jenkinsfile 和 Git 仓库之间，通过 `JOB_NAME` 关联起来，这个关联关系也可以存放在这个 Git 仓库中
这样维护起来方便，不需要每次都批量修改所有 Git 仓库中的 Jenkinsfile。缺点是耦合度增加了。

## 使用建议

轻量级任务可以考虑直接通过 Jenkins Pipeline 和 Jenkins 插件完成。
如果复杂度上升，肯定就要在 pipeline 中嵌入 groovy/python 脚本才能实现功能，
但是 Jenkinsfile 不方便测试，语法提示也很垃圾，报错信息混乱一片，也没有很方便的代码复用能力。因此只建议用于轻量级任务。

更复杂的任务，建议使用 Python 脚本来完成。Python 脚本要规划好目录结构，我使用的结构参见 [Jenkinsfile 与 CI/CD 代码管理](./jenkinsfile-templates/README.md)。

## Python SDK

>总的来说，jenkins 的两个 python sdk 都不是很好用。。。

推荐使用 [python-jenkins](https://pypi.org/project/python-jenkins/).

另外还有一个 [jenkinsapi](https://github.com/pycontribs/jenkinsapi)，这个东西每次登录时都会拉取所有的 Jobs 状态，导致登录特别慢！慎用！

## GitOps

最近 GitOps 好像借着云原生的热潮，越来越流行。目前 Github 上新兴的 CI/CD 工具如 Jenkins-X/Argo/Knative/flux 等，几乎全都是以 GitOps 为核心的。

但是感觉上 GitOps 以 Git 仓库为核心，忽略了 Git 仓库之间的依赖，因此它和分层结构的项目不怎么合得来。
GitOps 很适合扁平化的项目，每个 Git 仓库就是一个应用，相互独立，也就不需要去考虑它们之间的依赖关系、构建/部署顺序。

