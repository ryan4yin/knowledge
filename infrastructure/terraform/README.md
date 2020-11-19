# [Terraform 基础设施即代码](https://github.com/hashicorp/terraform)

预先编写好配置文件，就能使用 Terraform 进行云资源的自动化创建/销毁/查询。

使用场景：

1. 使用 terrform 实现 PVE 虚拟机的自动化创建、参数配置（网络配置、硬件配置等）、自动销毁。
2. 云上资源的生命周期管理，比如阿里云。
    1. 比如自动化测试环境的搭建过程。
    2. 对于繁杂的 RAM 账号权限体系、 VPC 专有网络等配置，可以预先在本地设计好结构，然后使用 terraform 编写代码一次性创建。

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
terraform.tfvars        ### 配置 provider 要用到的变量
variable.tf              ### 通用变量
resource.tf             ### 资源定义
data.tf                 ### data 定义
output.tf               ### 输出（常用做 debug）
```


### 4. terraform 状态管理

terraform 默认将状态保存在本地的 `.tfstate` 文件中，但也支持设定不同的远端 Backend 存储状态。

推荐使用远端存储保存状态，默认使用的本地 `.tfstate` 容易导致管理混乱，安全性也很差。


## 常见用途

## 1. [Proxmox-Provider](https://github.com/Telmate/terraform-provider-proxmox/)

本地开发环境，可使用 PVE 搭建。
PVE 虚拟机的创建/修改/销毁：[pve-vm.tf](./pve-vm.tf)

## 2. [阿里云 Provider](https://registry.terraform.io/providers/aliyun/alicloud/latest/docs)

使用 Terraform，可以自动化阿里云的：

1. RAM 账号权限体系
2. NAT/VPC 专有网络、DNS解析
3. K8s 集群、各类数据库
4. OSS/CDN 数据存储与分发
5. TLS 证书的申请/自动更新，以及上传到阿里云：[./tls-certs.tf](./tls-certs.tf)
6. ......


