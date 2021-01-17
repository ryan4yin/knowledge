
[Pulumi](https://github.com/pulumi/pulumi) 是一个基础设施的自动管理工具，使用 Python/TypeScript/Go/Dotnet 编写好声明式的资源配置，就能实现一键创建/修改/销毁各类资源，这里的资源可以是：

- AWS/阿里云等云上的负载均衡、云服务器、TLS 证书、DNS、CDN、OSS、数据库...几乎所有的云上资源
- 本地自建的 vSphere/Kubernetes/ProxmoxVE/libvirt 环境中的虚拟机、容器等资源

<!--more-->

相比直接调用 AWS/阿里云/Kubernetes 的 API，使用 pulumi 的好处有：

- 声明式配置：你只需要声明你的资源属性就 OK，所有的状态管理、异常处理都由 pulumi 完成。
- 统一的配置方式：提供统一的配置方法，来声明式的配置所有 AWS/阿里云/Kubernetes 资源。
- 声明式配置的可读性更好，更便于维护

试想一下，通过传统的手段去从零搭建一个云上测试环境、或者本地开发环境，需要手工做多少繁琐的工作。

而依靠 Pulumi 这类「基础设施即代码」的工具，只需要一行命令就能搭建好一个可复现的云上测试环境或本地开发环境。

比如我们的阿里云测试环境，包括两个 kubernetes 集群、负载均衡、VPC 网络、数据库、云监控告警/日志告警、RAM账号权限体系等等，是一个比较复杂的体系。

人工去配置这么多东西，想要复现是很困难的，非常繁琐而且容易出错。

但是使用 pulumi，只需要一行命令，就能创建并配置好这五花八门一大堆的玩意儿。
销毁整个测试环境也只需要一行命令。

**实际使用体验**：我们使用 Pulumi 自动化了阿里云测试环境搭建 95%+ 的操作，这个比例随着阿里云的 pulumi provider 的完善，还可以进一步提高！


## Pulumi vs Terraform

有一个「基础设施即代码」的工具比 Pulumi 更流行，它就是 [Terraform](https://www.terraform.io/).

实际上我们一开始使用的也是 Terraform，但是后来使用 Pulumi 完全重写了一遍。

主要原因是，Pulumi 解决了 Terraform 配置的一个痛点：配置语法太过简单，导致配置繁琐。而且还要额外学习一门 DSL - HCL

Terraform 虽然应用广泛，但是它默认使用的 HCL 语言太简单，表现力不够强。
这导致在更复杂的场景下，我们无法更自动化地进行基础设施配置，而需要更复杂的步骤：

1. 借助 Python 等其他语言先生成出 HCL 配置
2. 通过 `terraform` 命令行进行 plan 与 apply
3. 通过 Python 代码解析 `terraform.tfstat`，获取 apply 结果，再进行进一步操作。

这显然是一个很麻烦的过程。**其中最主要的原因，是 terraform 只做到了「基础设施即配置」，而「配置」过于简单。**

这种情况下，就需要用到真正的「基础设施即代码」工具 - Pulumi 了。它的优势如下：

1. pulumi 是目前最流行的 真-IaaS 工具（另一个是刚出炉没多久的 terraform-cdk），对各语言的支持最为成熟。
2. 兼容 terraform 的所有 provider，只是需要自行使用 [pulumi-tf-provider-boilerplate](https://github.com/pulumi/pulumi-tf-provider-boilerplate) 重新打包，有些麻烦。
   1. pulumi 官方的 provider 几乎全都是封装的 terraform provider，包括 aws/azure/alicloud，目前只发现 kubernetes 是原生的（独苗啊）。
3. 状态管理和 secrets 管理有如下几种选择：
   1. 使用 app.pulumi.com（默认）:免费版提供 stack 历史管理，可以看到所有的历史记录。另外还提供一个资源关系的可视化面板。总之很方便，但是多人合作就需要收费。
   2. 本地文件存储：`pulumi login file:///app/data`
   3. 云端对象存储，目前貌似只支持 aws-s3/gcp/azure 三种。
   4. [gitlab 13 支持 Terraform HTTP State 协议](https://github.com/pulumi/pulumi/issues/4727)，等这个 pr 合并，pulumi 也能以 gitlab 为 backend 了。
   5. 使用 pulumi 企业版（自建服务）：比 app.pulumi.com 提供更多的特性，但是显然是收费的。。

上述工具支持通过 Python/TypeScript 等语言来描述配置。好处有：

1. 批量创建资源，动态生成资源参数。
   1. 比如批量创建一批名称类似的 ECS 服务器/VPC交换机。如果使用 terraform，你需要编写 module 来实现配置的复用，然后使用 hcl 的特殊语法来动态拼接出资源名称，因为语法限制，这种 HCL 能实现的功能也很有限。
   2. 而使用 pulumi，Python/TypeScript 这类通用的编程语言，能满足你的一切需求，而且作为一个开发人员/DevOps，你应该对它们相当熟悉。
1. 更方便测试：可以使用各编程语言中流行的测试框架来测试 pulumi 配置！
1. 使用代码编写 Kubernetes 配置，no-yaml
   1. yaml 也存在和 HCL 一样的问题，配置太死板，导致我们现在需要通过 helm/kustomize + python 来生成 yaml ...


------------------------------------

>以下内容是我对 pulumi 的一些思考，以及使用 pulumi 遇到的各种问题+解决方法，适合对 pulumi 有一定了解的同学阅读。

>如果你刚接触 Pulumi 而且有兴趣学习，请先移步 [pulumi get started](https://www.pulumi.com/docs/get-started/install/) 入个门，再接着看下面的内容。

## 使用建议

1. **建议查看对应的 terraform provider 文档：pulumi 的 provider 基本都是封装的 terraform 版本，而且文档是自动生成的，比（简）较（直）难（一）看（坨）懂（shi），examples 也少。**
2. stack: pulumi 官方提供了两种 stack 用法：[「单体」和「微-stack」](https://www.pulumi.com/docs/intro/concepts/organizing-stacks-projects/)
   1. 单体: one stack hold them all，通过 stack 参数来控制步骤。stack 用来区分环境 dev/pro 等。
   2. 微-stack: 每一个 stack 是一个步骤，所有 stack 组成一个完整的项目。
   3. 实际使用中，我发现「微-stack」模式需要使用到 pulumi 的 inter-stack dependencies，报一堆的错，而且不够灵活。因此目前更推荐「单体」模式。

我们最近使用 pulumi 完全重写了以前用 terraform 编写的云上配置，简化了很多繁琐的配置，也降低了我们 Python 运维代码和 terraform 之间的交互难度。
另外我们还充分利用上了 Python 的类型检查和语法检查，很多错误 IDE 都能直接给出提示，强化了配置的一致性和可维护性。

体验上，terraform 只是配置编写方式，以及状态管理有些不同。实际上都是通过同样的 provider 管理云上资源。
目前我们使用 pulumi/terraform，实现了云上环境（资源组、VPC专有网络、k8s集群、数据库、账号权限系统、负载均衡等等）的一键搭建与销毁。
不过由于阿里云 provider 暂时还：

1. 不支持管理 ASM 服务网格、DTS 数据传输等资源
2. OSS 等产品的部分参数也暂时不支持配置（比如 OSS 不支持配置图片样式、ElasticSearch 暂时不支持自动创建 7.x 版本）
3. 不支持创建 ElasticSearch 7.x

这些问题，导致我们仍然有部分配置需要手动处理，另外一些耗时长的资源，需要单独去创建。
因此还不能实现完全的「一键」。


## 常见问题

### 1. pulumi 的 `Output` 常见问题

1. pulumi 通过资源之间的属性引用（`Output[str]`）来确定依赖关系，如果你通过自定义的属性(`str`)解耦了资源依赖，会导致资源创建顺序错误而创建失败。
2. `Output[str]` 是一个异步属性，类似 Future，不能被用在 pulumi 参数之外的地方！
3. `Output[str]` 提供两种方法能直接对 `Output[str]` 进行一些操作：
   1. `Output.concat("http://", domain, "/", path)`: 此方法将 str 与 `Output[str]` 拼接起来，返回一个新的 `Output[str]` 对象，可用做 pulumi 属性。
   2. `domain.apply(lambda it: print(it))`: `Output[str]` 的 `apply` 方法接收一个函数。在异步获取到数据后，pulumi 会调用这个函数，把具体的数据作为参数传入。
      - 另外 `apply` 也会将传入函数的返回值包装成 `Output` 类型返回出来。
      - 可用于：在获取到数据后，将数据打印出来/发送到邮箱/调用某个 API 上传数据等等。
   3. `Output.all(output1, output2, ...).apply(lambda it: print(it))` 可用于将多个 `output` 值，拼接成一个 `Output` 类型，其内部的 raw 值为一个 tuple 对象 `(str1, str2, ...)`.
      1. 官方举例：`connection_string = Output.all(sql_server.name, database.name).apply(lambda args: f"Server=tcp:{args[0]}.database.windows.net;initial catalog={args[1]}...")`

### 2. 如果使用多个云账号/多个k8s集群？

默认情况下 pulumi 使用默认的 provider，但是 pulumi 所有的资源都有一个额外的 `opts` 参数，可用于设定其他 provider。

示例：

```python
from pulumi import get_stack, ResourceOptions, StackReference
from pulumi_alicloud import Provider, oss

# 自定义 provider，key/secret 通过参数设定，而不是从默认的环境变量读取。
# 可以自定义很多个 providers
provider = pulumi_alicloud.Provider(
   "custom-alicloud-provider",
   region="cn-hangzhou",
   access_key="xxx",
   secret_key="jjj",
)

# 通过 opts，让 pulumi 使用自定义的 provider（替换掉默认的）
bucket = oss.Bucket(..., opts=ResourceOptions(provider=provider))
```

### 3. inter-stack 属性传递

>这东西还没搞透，待研究。

多个 stack 之间要互相传递参数，需要通过 `pulumi.export` 导出属性，通过 `stack.require_xxx` 获取属性。

从另一个 stack 读取属性的示例：
```python
from pulumi import StackReference

cfg = pulumi.Config()
stack_name = pulumi.get_stack()  # stack 名称
project = pulumi.get_project()
infra = StackReference(f"ryan4yin/{project}/{stack_name}")

# 这个属性在上一个 stack 中被 export 出来
vpc_id = infra.require("resources.vpc.id")
```

### 4. `pulumi up` 被中断，或者对资源做了手动修改，会发生什么？

1. 强行中断 `pulumi up`，会导致资源进入 `pending` 状态，必须手动修复。
   1. 修复方法：`pulumi stack export`，删除 pending 资源，再 `pulumi stack import`
2. 手动删除了云上资源，或者修改了一些对资源管理无影响的参数，对 `pulumi` 没有影响，它能正确检测到这种情况。
   1. 可以通过 `pulumi refresh` 手动从云上拉取最新的资源状态。
3. 手动更改了资源之间的关系（比如绑定 EIP 之类的），很可能导致 pulumi 无法正确管理资源之间的依赖。


### 5. pulumi-kubernetes？

pulumi-kubernetes 是一条龙服务：

1. 在 yaml 配置生成这一步，它能结合/替代掉 helm/kustomize，或者你高度自定义的 Python 脚本。
2. 在 yaml 部署这一步，它能替代掉 argo-cd 这类 gitops 工具。
3. 强大的状态管理，argo-cd 也有状态管理，可以对比看看。

也可以仅通过 kubernetes_pulumi 生成 yaml，再通过 argo-cd 部署，这样 pulumi_kubernetes 就仅用来简化 yaml 的编写，仍然通过 gitops 工具/kubectl 来部署。

使用 pulumi-kubernetes 写配置，要警惕逻辑和数据的混合程度。
因为 kubernetes 的配置复杂度比较高，如果动态配置比较多，很容易就会写出难以维护的 python 代码来。

渲染 yaml 的示例：

```python
from pulumi import get_stack, ResourceOptions, StackReference
from pulumi_kubernetes import Provider
from pulumi_kubernetes.apps.v1 import Deployment, DeploymentSpecArgs
from pulumi_kubernetes.core.v1 import (
	ContainerArgs,
	ContainerPortArgs,
	EnvVarArgs,
	PodSpecArgs,
	PodTemplateSpecArgs,
	ResourceRequirementsArgs,
	Service,
	ServicePortArgs,
	ServiceSpecArgs,
)
from pulumi_kubernetes.meta.v1 import LabelSelectorArgs, ObjectMetaArgs

provider = Provider(
   "render-yaml",
   render_yaml_to_directory="rendered",
)

deployment = Deployment(
	"redis",
	spec=DeploymentSpecArgs(...),
   opts=ResourceOptions(provider=provider),
)
```

如示例所示，pulumi-kubernetes 的配置是完全结构化的，比 yaml/helm/kustomize 要灵活非常多。

总之它非常灵活，既可以和 helm/kustomize 结合使用，替代掉 argocd/kubectl。
也可以和 argocd/kubectl 使用，替代掉 helm/kustomize。

具体怎么使用好？我也还在研究。

### 6. 阿里云资源 replace 报错？

部分只能创建删除，不允许修改的资源，做变更时会报错：「Resources aleardy exists」，
这类资源，通常都有一个「force」参数，指示是否强制修改——即先删除再重建。

### 7. 有些资源属性无法使用 pulumi 配置？ 

这得看各云服务提供商的支持情况。

比如阿里云很多资源的属性，pulumi 都无法完全配置，因为 alicloud provider 的功能还不够全面。

目前我们生产环境，大概 90%+ 的东西，都可以使用 pulumi 实现自动化配置。
而其他 OSS 的高级参数、新出的 ASM 服务网格、kubernetes 的授权管理、ElasticSearch7 等资源，还是需要手动配置。

这个没办法，只能等阿里云提供支持。

### 8. CI/CD 中如何使 pulumi 将状态保存到文件？

CI/CD 中我们可能会希望 pulumi 将状态保存到本地，避免连接 pulumi 中心服务器。
这一方面能加快速度，另一方面一些临时状态我们可能根本不想存储，可以直接丢弃。

方法：

```shell
# 指定状态文件路径
pulumi login file://<file-path>
# 保存到默认位置: ~/.pulumi/credentials.json
pulumi login --local

# 保存到远程 S3 存储（minio/ceph 或者各类云对象存储服务，都兼容 aws 的 s3 协议）
pulumi login s3://<bucket-path>
```

登录完成后，再进行 `pulumi up` 操作，数据就会直接保存到你设定的路径下。

## 缺点

### 1. 报错信息不直观

pulumi 和 terraform 都有一个缺点，就是封装层次太高了。

封装的层次很高，优点是方便了我们使用，可以使用很统一很简洁的声明式语法编写配置。
而缺点，则是出了 bug，报错信息往往不够直观，导致问题不好排查。


### 2. 资源状态被破坏时，修复起来非常麻烦

在很多情况下，都可能发生资源状态被破坏的问题：

1. 在创建资源 A，因为参数是已知的，你直接使用了常量而不是 output。这会导致 pulumi 无法识别到依赖关系！从而创建失败，或者删除时资源状态被破坏！
1. 有一个 pulumi stack 一次在三台物理机上创建资源。你白天创建资源晚上删除资源，但是某一台物理机晚上会关机。这将导致 pulumi 无法查询到这台物理机上的资源状态，这个 pulumi stack 在晚上就无法使用，它会一直报错！


## 常用 Provider

- [pulumi-alicloud](https://github.com/pulumi/pulumi-alicloud): 管理阿里云资源
- [pulumi-vault](https://github.com/pulumi/pulumi-vault): 我这边用它来快速初始化 vault，创建与管理 vault 的所有配置。

## 我创建维护的 Provider

由于 Pulumi 生态还比较小，有些 provider 只有 terraform 才有。

我为了造(方)福(便)大(自)众(己)，创建并维护了两个本地虚拟机相关的 Providers:

- [ryan4yin/pulumi-proxmox](https://github.com/ryan4yin/pulumi-proxmox): 目前只用来自动创建 PVE 虚拟机
   - 可以考虑结合 kubespray/kubeadm 快速创建 k8s 集群
- [ryan4yin/pulumi-libvirt](https://github.com/ryan4yin/pulumi-libvirt): 快速创建 kvm 虚拟机
   - 可以考虑结合 kubespray/kubeadm 快速创建 k8s 集群


