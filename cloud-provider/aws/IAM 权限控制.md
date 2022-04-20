
# IAM 账号与权限管理

1. Policy 编写测试工具：有一个权限测试模拟器

Policy <- Role <- Person/Resources

Role 具有信任策略，表示谁可以使用这个 Role

Asume Role - STS 临时凭证

## OIDC 身份验证

OIDC 身份验证：客户端会先查看 jwt body 内容，从中获取到 provider URL，通过它来认证身份获取到 APIKey SecretKey，然后再用 AK SK 来调用 aws api


- boto3 就封装了这些行为，它们对用户都是透明的
- 适用场景：AWS EKS 的 IAM ServiceAccount

## InstanceProfile - 实例配置文件

AWS EC2 的 InstanceProfile 是一个 IAM Role 的容器，EC2 不能直接关联 IAM Role，必须使用 InstanceProfile 作为中介。

当用户直接在 AWS 控制台上为一个 EC2 绑定某个 IAM Role 时，实际上 AWS 会**自动为该 IAM Role 创建一个同名的 InstanceProfile**，然后将这个 IntanceProfile 关联到 EC2 上。

AWS EKS 的 NodeGroup 也是使用 InstanceProfile 来创建 EC2 实例的，它首先创建一个 InstanceProfile 并绑定上 EKS 集群的基础 Role，然后使用这个 InstanceProfile 来创建 EC2 实例，这样所有的 EC2 实例默认都具有连接上 EKS 集群的必要权限，才可以正常加入到集群中。
用户也可以自定义 EKS 集群的默认 InstanceProfile，使集群的 Pod 默认就具有某些 AWS 权限。

控制台只在为 EC2 绑定 IAM Role 时才自动创建对应的 InstanceProfile，而且 AWS 并未提供 InstanceProfile 的管理页面，为了实现更细致的操作，比如手动创建 InstanceProfile、查看当前有哪些 InstanceProfile、为 InstanceProfile 打标签等等，都需要通过 AWS CLI 或者 API 实现。

如下列出一些 InstanceProfile 的实用 AWS CLI 命令：

```shell
# 列出账号下的所有 InstanceProfile
aws iam list-instance-profiles

# 列出关联了某个 Role 的所有 InstanceProfile
aws iam list-instance-profiles-for-role --role-name TestEKSClusterNodeInstanceRole

# 获取某个 InstanceProfile 的详细信息
aws iam get-instance-profile --instance-profile-name TestEKSClusterNodeInstanceRole

# 1. 创建一个 InstanceProfile
aws iam create-instance-profile --instance-profile-name TestEKSClusterNodeInstanceRole
# 2. 为 InstanceProfile 添加 Role
aws iam add-role-to-instance-profile --instance-profile-name TestEKSClusterNodeInstanceRole --role-name TestEKSClusterNodeInstanceRole
```

能看到 InstanceProfile ARN 的格式为 `arn:aws:iam::112233445566:instance-profile/xxx`
