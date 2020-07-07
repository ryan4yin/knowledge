# [Jenkins](https://www.jenkins.io/zh/doc/)

Jenkins 是当下最流行的 CI/CD 工具之一，优势在于：

1. 众多插件供选用，因此功能繁多。（虽然是良莠不齐，甚至好多都已经停更好多年了。）
1. 有视图-文件夹的概念，可以很方便地将 Jobs 进行分类。
1. 任务之间可以互相调用，可以使用一些 Batch Job 去并行/串行地调用其他 Jobs。很适合分层结构项目的 CI/CD。
1. 可以定时构建。

但是也存在很多问题：

1. 单点故障问题，Master 只能一个。
1. Slaves 无法动态扩缩容，不能随意地创建销毁。这导致效率不好提升，垃圾数据也容易积累。
1. Bug 比较多，功能也有缺失。
   1. Bugs: 任务无法终止等
   2. 特性缺失：没有办法直接从 Jenkinsfile 中读取配置，必须构建一次 Job 才能更新。
2. UI 相当丑。
3. 使用 Groovy DSL 写配置，语法提示太弱，容易写出错误的代码。
    - pipeline 的运行时错误无法提示准确的位置，需要自己肉眼 Debug...
    - 没办法写测试，不适合编写复杂的构建逻辑。复杂的任务需要用 Python 编写。


总的来说，它很适合层次结构比较复杂的项目。比如说处理很多 Git 仓库的相互依赖、分层构建。
还有一些批量工作、定时任务，比如需要批量构建、批量修改、批量更新、批量部署、定时清理等等。

对于这种批量任务，当前路径的 `jenkinsfile-templates` 中有两个模板可供参考。

另外在分层结构中，同一层次的任务流程往往一模一样，因此我一般建议将所有 Jenkinsfile 和构建脚本（如 Python）都放在同一个 Git 仓库中，每一类任务一个 Jenkinsfile。
Jenkinsfile 和 Git 仓库之间，通过 `JOB_NAME` 关联起来，这个关联关系也可以存放在这个 Git 仓库中
这样维护起来方便，不需要每次都批量修改所有 Git 仓库中的 Jenkinsfile。缺点是耦合度增加了。

另外一种方法是将 Jenkinsfile 中通用的定义存放在一个专用仓库中，源码仓库的 Jenkinsfile 只是单纯地去调用这些通用的步骤。
但是这种方法需要编写 groovy 脚本，还得符合 jenkins 规定的项目结构。跑任务时还是需要再拉取一遍用到的 Python 运维代码，感觉没啥优势。

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

一个分层结构的项目，底层依赖库的构建测试可以用 Jenkins 实现，目前来看也只能用 Jenkins，没找到别的替代品。
而最终的 docker 镜像构建与部署这两步，可以交给 GitOps 的 CI/CD 工具来做。
