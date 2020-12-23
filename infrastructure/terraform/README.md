# [Terraform](https://github.com/hashicorp/terraform) - 基础设施配置化

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

## 基础设施代码化

terraform 最近推出了 [terraform-cdk](https://github.com/hashicorp/terraform-cdk)，它基于 aws 的 CDK 组件，提供了类似 pulumi 的功能：用 Python/TypeScript 等高级语言管理基础设施。

不过这个项目还处在非常早期的阶段，而且个人观感上也更喜欢 pulumi 的写法。。

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

比如

1. 使用阿里云 OSS 做状态存储: [alicoud oss backend - terraform docs](https://www.terraform.io/docs/backends/types/oss.html)
1. [gitlab 13 支持 Terraform HTTP State 协议](https://github.com/pulumi/pulumi/issues/4727)，可以直接将它用做 terraform 的 Backend.


## 常见用途

## 1. Proxmox-Provider

目前社区主要有两个 provider:

1. [Telmate/terraform-provider-proxmox](https://github.com/Telmate/terraform-provider-proxmox/): 用户最多，但是只支持管理虚拟机资源。
1. [danitso/terraform-provider-proxmox](https://github.com/danitso/terraform-provider-proxmox): stars 少，但是可以管理 PVE 的大部分资源，包括节点、用户、资源池、TLS证书等等。
    - 代码更顺眼，但是作者忙，没时间合并 pr，导致 Bug 更多一些。
    - 不能设置虚拟机开机自启(onboot)，而且目前不支持 disk resize


PVE 虚拟机的创建/修改/销毁：[pve-vm.tf](./pve-vm.tf)

## 2. [阿里云 Provider](https://registry.terraform.io/providers/aliyun/alicloud/latest/docs)

使用 Terraform，可以自动化阿里云的：

1. RAM 账号权限体系
2. NAT/VPC 专有网络、DNS解析
3. K8s 集群、各类数据库
4. OSS/CDN 数据存储与分发
5. TLS 证书的申请/自动更新，以及上传到阿里云：[./tls-certs.tf](./tls-certs.tf)
6. ......


