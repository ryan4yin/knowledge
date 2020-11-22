# [Terraform 基础设施即代码](https://github.com/hashicorp/terraform)

预先编写好配置文件，就能使用 Terraform 进行云资源的自动化创建/销毁/查询。

使用场景：

1. 使用 terrform 实现 PVE 虚拟机的自动化创建、参数配置（网络配置、硬件配置等）、自动销毁。
4. 云上资源的生命周期管理，比如阿里云。
    1. 比如自动化测试环境的搭建过程。
    2. 对于繁杂的 RAM 账号权限体系、 VPC 专有网络等配置，可以预先在本地设计好结构，然后使用 terraform 编写代码一次性创建。
5. 自动通过 ACME 自动管理 Let's Encrypt 证书，或者自动生成自签名证书（给私有 HTTP API 加密用）。
6. 自动配置 grafana 监控面板。

目前来说，terraform 拥有众多 provider，各种各样需要自动化配置的场景下，它都可能帮得上忙。
terraform 的 provider 小到单纯的 tls 证书生成与轮转， 大到各大云服务商的全套产品 API(如阿里云腾讯云)，非常全面。

## 其他竞品 - 配置代码化

terraform 虽然应用广泛，但是它默认使用的 HCL 语言太简单，表现力不够强。
这导致在更复杂的场景下，我们无法更自动化地进行基础设施配置，而需要更复杂的步骤：

1. 借助 Python 等其他语言先生成出 HCL 配置
2. 通过 `terraform` 命令行进行 plan 与 apply
3. 通过 Python 代码解析 `terraform.tfstat`，获取 apply 结果，再进行进一步操作。

这显然是一个很麻烦的过程。**其中最主要的原因，是 terraform 只做到了「基础设施即配置」，而「配置」过于简单。**

这种情况下，就需要用到真正的「基础设施即代码」的工具了：

1. [pulumi](https://github.com/pulumi/pulumi): 目前最流行的 IaaS 工具，对各语言的支持最为成熟。
   1. 兼容 terraform 的所有 provider，只是需要自行使用 [pulumi-tf-provider-boilerplate](https://github.com/pulumi/pulumi-tf-provider-boilerplate) 重新打包，有些麻烦。
   2. 状态管理和 secrets 管理比 terraform 完善很多，状态和 secrets 可以存储在 postgresql/consul 等多种后端中。
2. [terraform-cdk](https://github.com/hashicorp/terraform-cdk): 和 pulumi 类似，基于 aws 的 CDK 组件。

上述工具支持通过 Python/TypeScript 等语言来描述配置。好处有：

1. 使用代码编写 Kubernetes 配置，no-yaml
   1. yaml 也存在和 HCL 一样的问题，配置太死板，导致我们现在需要通过 Python 来动态生成 yaml...
2. 待续

不过上述工具目前流行程度都比 terraform 少很多，有时间可以试试。

## 最佳实践

### 1. Terraform 命令使用流程

1. `terraform init -plugin-dir `
2. `terraform plan`: 生成执行计划
3. `terraform apply --auto-approve`: 应用计划
4. `terraform destroy`: 释放所有资源。（快速的创建与删除，非常适合进行测试）

此外，安装了 graphviz 后，还可以直接通过命令生成资源关系图：`terraform graph | dot -Tsvg > graph.svg`


## 2. Secrets 的安全传递

比较推荐通过环境变量来传递敏感信息。

大部分的 Provider，都支持直接使用环境变量传递 ACCESS_KEY/PASSWORD 等敏感信息。

terrafrom 也提供专用的环境变量 `TF_VAR_name` 来设置 terrafrom 变量(variable).

terraform 也可以通过 `.tfvars` 文件传变量。

### 3.  terraform 项目结构

terraform 运行时也读取当前文件夹下所有的 `.tf` 和 `.tfvars` 文件，因此可以将内容拆分为如下结构：

```shell
provider.tf             ### provider 配置
variable.tf              ### 通用变量
terraform.tfvars / terraform.tfvars.json   ### 为所有 variables 设定具体的值 
resource.tf             ### 资源定义
data.tf                 ### data 定义
output.tf               ### 输出（常用做 debug）
```

### 4. terraform 状态管理

terraform 默认将状态保存在本地的 `.tfstate` 文件中，但也支持设定不同的远端 Backend 存储状态。

推荐使用远端存储保存状态，默认使用的本地 `.tfstate` 容易导致管理混乱，安全性也很差。


## 常见用途

## 1. Proxmox-Provider

本地开发环境，可使用 PVE 搭建。

目前社区主要有两个 provider:

1. [Telmate/terraform-provider-proxmox](https://github.com/Telmate/terraform-provider-proxmox/): 用户最多，但是只支持管理虚拟机资源。
1. [danitso/terraform-provider-proxmox](https://github.com/danitso/terraform-provider-proxmox): stars 少，但是可以管理 PVE 的大部分资源，包括节点、用户、资源池、TLS证书等等。

PVE 虚拟机的创建/修改/销毁：[pve-vm.tf](./pve-vm.tf)

## 2. [阿里云 Provider](https://registry.terraform.io/providers/aliyun/alicloud/latest/docs)

使用 Terraform，可以自动化阿里云的：

1. RAM 账号权限体系
2. NAT/VPC 专有网络、DNS解析
3. K8s 集群、各类数据库
4. OSS/CDN 数据存储与分发
5. TLS 证书的申请/自动更新，以及上传到阿里云：[./tls-certs.tf](./tls-certs.tf)
6. ......


