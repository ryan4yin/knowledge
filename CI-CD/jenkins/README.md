# [Jenkins](https://www.jenkins.io/zh/doc/)

Jenkins 是当下最流行的 CI/CD 工具之一，优势在于：

1. 众多插件供选用，因此功能繁多。（虽然是良莠不齐，甚至好多都已经停更好多年了。）
1. 提供功能完善的 Web UI，有视图-文件夹的概念，可以很方便地将 Jobs 进行分类。用户使用方便。
1. 任务之间可以互相调用，可以使用一些 Batch Job 去并行/串行地调用其他 Jobs。很适合分层结构项目的 CI/CD。
1. 可以定时构建。
1. 一个仓库可以存在很多个 Pipelines，在构建任务中指定 Jenkinsfile 的位置。
   - 而 gitlab/drone 的 pipeline 文件名称是固定的，而且貌似一个仓库只能有一个。

但是也存在很多问题：

1. 单点故障问题，Master 只能一个。
2. 没有使用到专用的数据库(mysql/postgre)、缓存(redis)、搜索(elasticsearch) 组件，因此在数据量多时，有明显的性能瓶颈。
3. Slaves 无法动态扩缩容，不能随意地创建销毁。这导致效率不好提升，垃圾数据也容易积累。
   1. 如果使用 k8s 版本的 jenkins，貌似很多别的插件都无法使用。。
4. Bug 比较多，功能也有缺失: 
   1. 节点异常断线，可能会导致任务僵死无法终止。
   2. 没有办法直接从 Jenkinsfile 中读取配置，必须构建一次 Job 才能更新。
   3. Pipeline 第一次构建时，因为不会提前读取 Jenkinsfile，就导致所有的参数全部是 NULL...
5. UI 相当丑。
6. 使用 Groovy DSL 写配置，语法提示太弱，容易写出错误的代码。
    - pipeline 的运行时报错一大堆，经常缺少关键信息，需要自己肉眼 Debug、靠想象力找 Bug...
    - 没办法写测试，不适合编写复杂的构建逻辑。复杂的任务需要用 Python 编写。
7. 对 Configuration as Code 的支持目前还不够完善。
8. 插件老旧，而且很多插件根本没人维护。


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

其实我觉得很奇怪，市面上居然找不到很好的能按照项目的依赖顺序进行分层构建的工具（Jenkins 也不能原生支持，我们目前是自己使用 Python 代码来调度 Jenkins 任务。
难道是所有使用类似结构的企业都非常庞大，因此各层都由不同的团队维护，因此不需要这样一种全局的构建功能？他们的企业内部依赖版本号都是手动更新的，能改得过来？

目前来说我觉得像 Argo Workflow 这类基于有向无环图 DAG 的工作流工具，就很适合用来干这个事，可以直接替代掉我们的 Python 调度程序和 Jenkins。
但问题是目前 Argo Workflow 没有像 Jenkins 这么简单直观的 UI 可供开发人员使用。
开发人员只是想跑个 Workflow 分层更新一下内部依赖的版本号，如果用 Jenkins 他在几个输入框里填一下参数就行。
但是用 Workflow 他得在整个 Workflow 定义中找到参数的位置，然后手动修改一下，再 submit...

目前想到的方案，是底层使用 argo 来运行实际的任务，但是仍然通过 Jenkins 提供一个给用户使用的 UI 界面来构建任务。