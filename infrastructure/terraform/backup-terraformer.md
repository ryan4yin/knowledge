# terraformer

[terraformer](https://github.com/GoogleCloudPlatform/terraformer) 是 Google 的一个非官方项目，功能是将已存在的资源转换成 terraform 的 HCL 配置以及 state 文件。

虽然转换出的配置文件可能会有一些小瑕疵需要手动修正，但是不失为一个方便的工具，它主要有如下用途：

- 资源配置备份与版本管理
  - 使用它定期备份资源配置，可提供一定的灾难恢复能力。
- 将已存在的资源纳入 terraform 的管理

## 使用流程

首先，安装好 terraform 与 terraformer 两个工具：

```shell
wget https://github.com/GoogleCloudPlatform/terraformer/releases/download/0.8.20/terraformer-aws-linux-amd64
mv terraformer-aws-linux-amd64 ~/bin/terraformer-aws

wget https://releases.hashicorp.com/terraform/1.2.1/terraform_1.2.1_linux_amd64.zip
unzip terraform_1.2.1_linux_amd64.zip
mv terraform ~/bin/
```

然后就可以愉快地使用了，AWS provider 相关文档如下：

<https://registry.terraform.io/providers/hashicorp/aws/latest/docs>


## 使用方法

首先 cd 到对应的 terraform 配置文件夹：

```shell
cd elb
```

如果是本地首次运行，首先需要先初始化，下载 aws provider:

```shell
terraform init
```

然后修改或者添加配置，再执行如下命令检查配置正确性，同时确认变更：

```shell
terraform plan
```

确认无误后，使用如下命令应用变更：


```shell
terraform apply
```


## terraformer 资源导入

[terraformer](https://github.com/GoogleCloudPlatform/terraformer): 支持为已存在的资源创建 terraform 的 tf/json 配置以及 tfstate 状态文件。

下面介绍使用方法，首先建一个新文件夹 `route53`，在其中编写 `provider.tf` 内容如下：

```
provider "aws" {}

terraform {
	required_providers {
		aws = {
	    version = "~> 4.15.1"
		}
  }
}
```

现在在 route53 文件夹中执行如下命令下载 provider:

```shell
terraform init
```

provider 下载完成后，使用 terraform 导入所有 route53 资源（修改参数可导入其他资源）：

```shell
terraformer-aws import aws --resources=route53
```

>因为 route53 api 限制了每秒只能访问 5 次，视 DNS 记录数量，这个用时可能会很长，需要慢慢等待。
其他无严格限制的资源导入会快非常多。

>运行完成后，会打印出总的 DNS 记录数量，以及完成导入的 DNS 记录数量。

导入完成后，生成的 terraform.state 文件还有些问题——它写入的 terraform 版本过低（0.12.x），还需要执行如下命令进行更新：

```shell
terraform state replace-provider -auto-approve \
  "registry.terraform.io/-/aws" \
  "hashicorp/aws"
```

这之后，我们就可以通过这里的配置进行 route53 的配置更新了。

首先修改配置，然后执行 `terraform plan` 查看变更。
