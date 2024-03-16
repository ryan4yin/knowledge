# GitOps CD

## Flux vs Argo CD

1. Argo CD
   1. 可视化做得比较好，有个漂亮且信息丰富的 Web UI.
   1. 可通过 Web UI 对新配置进行 Diff 确认变更内容，出问题在 Web UI 上能快速回滚。
   1. Web UI 支持多租户多集群多名字空间，可接入 LDAP。
   1. 支持设置维护窗口、自动同步模式下支持自愈（覆盖集群中的手动修改）。
   1. 可在 Web UI 上手动选择只同步部分配置，并让其他配置保持 out of sync 状态。
   1. 支持设置 Hooks，在同步的不同阶段部署不同的 K8s Job / Argo Workflow 等资源。可通过它实现发送 IM
      消息、邮件、数据库迁移等功能。
1. Flux
   1. 功能相对 Argo CD 要少很多，更适合高级用户或者说极客。
   1. 没有 Web UI，只能通过 Git 仓库配置或 CLI 来操作，而且 CLI 的操作因为不可审计，Flux 对往 CLI 中
      添加功能非常克制。
   1. 是基于 kustomize 拓展的，也就是说它原生支持 overlays，一套基础配置（kustomize 跟 helm chart 都
      行）打上不同的 overlays 就能应用到各种不同的 dev/staging/prod 环境，能极大地降低配置文件的重复
      度。
      1. Argo CD 相对没这么灵活，它的 kustomize overlays 必须统一放在仓库某个目录下。它的 Helm
         values 也必须跟 chart 一起存在 Git 仓库中。存储外部 Helm Chart 的全部内容到 Git 仓库中能确
         保数据不会丢，但它实际污染了 GitOps 仓库，放了一堆并不由我们自己维护的东西在仓库里，在做
         git diff 跟 review 的时候，这真的很烦。
      1. 对于 Helm Chart，Argo CD 中的一个解法是创建一个空 chart 并在它的依赖中声明你真正想部署的
         chart，然后在其 values.yaml 中定义对应的自定义值。但这确实不太优雅，搞出很多重复的东西。
      1. Flux 还能直接在 Helm Chart 上加一个 postRenderer 对它做二次 patch，非常强大。
   1. Flux 对数据一致性的追求更极致，对于集群配置被手动修改的情况都是直接覆盖，也不提供维护窗口（关
      闭同步功能）之类的功能。
   1. Flux 支持定义依赖关系，不过 Kustomization 只能依赖另一个 Kustomization，HelmRelease 只能依赖另
      一个 HelmRelease，不能跨类型依赖。ArgoCD 缺失此特性。

总的来说，Flux 更强大，但 Argo CD 更易用、可视化做得更好。

相关资料：

- [Comparison: Flux vs Argo CD](https://earthly.dev/blog/flux-vs-argo-cd/)
- [FluxCD vs ArgoCD](https://yashwanth-l.medium.com/fluxcd-vs-argocd-373cd26ed6c7)

## 推荐使用场景

1. K8s 集群的核心组件与配置（网络、监控、告警、数据库等）
   1. 这个是最适合使用 GitOps 的，因为这些配置通常由集群管理员编写维护，它们具有很专业的 K8s 与
      GitOps 知识，使用此类工具不会带来额外负担，而另一方面，集群状态与 Git 仓库中的配置完全一致带来
      的好处是相当明显的。
1. 集群中运行的业务服务及其配置：
   1. 对于做内部平台的企业，通常业务开发者并不会直接操作集群，而是通过内部平台的 UI 来操作，因此业务
      服务相关的配置不太适合接入 GitOps，也就不适合使用 ArgoCD 或 Flux。
      1. 或许平台上的服务版本管理，底层可以使用 GitOps 工具实现，但这些对开发人员而言是透明的。
      1. 如果内部定义一堆 CRD 给业务侧用于 GitOps，简是简化了，但是这种无法复用的知识，开发人员一般
         是不情愿学习的，这相对 Web UI 而言并无明显优势。
   1. 对于 DevOps 文化比较浓厚的企业，业务开发者对 K8s 也有一定了解，那么业务服务的配置就也比较适合
      接入 GitOps。

比较理想的情况是：

1. 只有 SRE 有权限直接操作集群，而且他们也只是在紧急情况下才会这么做。
1. SRE 日常使用 GitOps 工具管理集群核心组件与配置，配置 Merge 阶段会有 CI 流程进行验证。
1. 业务开发者使用内部平台管理业务服务与配置。

## 相关问题

### 使用 GitOps 管理业务服务存在的问题：服务更新顺序

一个复杂的微服务系统，各微服务之间的依赖关系是很复杂的，这往往要求我们按照依赖链路进行更新。

首先后端的更新策略是：

1. 微服务 API 的每次更新都应该保持向下兼容，保证旧客户端仍然能正常调用此微服务。
1. 客户端升级时可以直接使用新的 API

这导致，微服务更新时，我们**必须在服务端 A 升级完成后，才能升级客户端 B**。因为客户端不向下兼容，直
接升级会报错！

后端人员会一次性把最新的微服务全部提交给运维组，运维发布系统必须要自己去根据预先定义好的升级顺序，进
行按序升级。

目前看 Flux 已经有了 denpendsOn 的功能，或许能解决这个问题。
