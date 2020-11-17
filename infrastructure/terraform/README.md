# [Terraform 基础设施即代码](https://github.com/hashicorp/terraform)

预先编写好配置文件，就能使用 Terraform 进行云资源的自动化创建/销毁/查询。

使用场景：

1. 使用 terrform 实现 PVE 虚拟机的自动化创建、参数配置（网络配置、硬件配置等）、自动销毁。
2. 云上资源的生命周期管理，比如阿里云。
    1. 比如自动化测试环境的搭建过程。
    2. 对于繁杂的 RAM 账号权限体系、 VPC 专有网络等配置，可以预先在本地设计好结构，然后使用 terraform 编写代码一次性创建。

## Secrets 的安全传递

比较推荐通过环境变量来传递敏感信息。

大部分的 Provider，都支持直接使用环境变量传递 ACCESS_KEY/PASSWORD 等敏感信息。

terrafrom 也提供专用的环境变量 `TF_VAR_name` 来设置 terrafrom 变量(variable).

terraform 也可以通过 `.tfvars` 文件传变量。

## [Proxmox-Provider](https://github.com/Telmate/terraform-provider-proxmox/)

待续

## [阿里云 Provider](https://registry.terraform.io/providers/aliyun/alicloud/latest/docs)

使用 Terraform，可以自动化阿里云的：

1. RAM 账号权限体系
2. NAT/VPC 专有网络、DNS解析
3. K8s 集群、各类数据库
4. OSS/CDN 数据存储与分发
5. TLS 证书的过期检查、滚动更新:[Terraform - 阿里云 TLS 证书管理](https://registry.terraform.io/providers/aliyun/alicloud/latest/docs/data-sources/cas_certificates)
6. ......


