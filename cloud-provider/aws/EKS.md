# EKS

## MISC

获取 Kubeconfig:

```
aws eks update-kubeconfig --region us-east-1 --name $CLUSTER_NAME
```

切换 PROFILE:

```
export AWS_PROFILE=profile-name
aws xxx xxx
```

## IAM 与 ServiceAccount 的角色绑定

- [Creating an IAM role and policy for your service account](https://docs.aws.amazon.com/eks/latest/userguide/create-service-account-iam-policy-and-role.html)
- [Associate an IAM role to a service account](https://docs.aws.amazon.com/eks/latest/userguide/specify-service-account-role.html)

具体而言，就是：

- EKS 要先加好 OIDC Provider

- 创建 IAM Role，并且为 EKS 配置信任关系 relationship

```yaml
{
  "Version": "2012-10-17",
  "Statement":
    [
      {
        "Effect": "Allow",
        "Principal":
          {
            "Federated": "arn:aws:iam::130132914922:oidc-provider/oidc.eks.us-east-1.amazonaws.com/id/<eks-oidc-id>",
          },
        "Action": "sts:AssumeRoleWithWebIdentity",
        "Condition": { "StringEquals": {
                # 尤其注意，这里的 key 要改成 `:sub` 结尾
                "oidc.eks.us-east-1.amazonaws.com/id/<eks-oidc-id>:sub": "system:serviceaccount:<namespace>:<serviceAccountName>",
              } },
      },
    ],
}
```

- 最后 ServiceAccount 添加注解，再提供给 Pod 使用：

```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  annotations:
    eks.amazonaws.com/role-arn: arn:aws:iam::<ACCOUNT_ID>:role/<IAM_ROLE_NAME>
```

## [amazon-vpc-cni-k8s](https://github.com/aws/amazon-vpc-cni-k8s) 网络插件

即 EKS 集群的 ip 分配插件，它能直接为 pod 分配 vpc 网络的 ip 地址，打通 pod 网络和 vpc 网络

### 网段太小，可用 ip 不足的问题

在最初设计考虑不周的情况下，集群后期可能会遇到 ip 不足的问题，导致必须重建 vpc 及集群。

但是也可以通过调整 `amazon-vpc-cni-k8s` 的 ip 预热策略来缓解此问题。

`amazon-vpc-cni-k8s` 默认情况下会为每个节点预留大量 ip，提升 ip 分配速度。

在「ip 数量受限的情况下」，可以去掉 `aws-node` 这个 `daemonset` 的 `WARM_ENI_TARGET` 环境变量，再添
加 `WARM_IP_TARGET` 及 `MINIMUM_IP_TARGET` 缓解此问题。

建议设置 `WARM_IP_TARGET=2`，使每个节点始终提前预热两个 IP，再设置 `MINIMUM_IP_TARGET` 为 「2 + 绝大
部分节点的最大 Pod 数量」。比如我们用来专门跑大数据的 EKS 集群，95%+ 的节点都只会有 3 个 pod，就可以
设置 `MINIMUM_IP_TARGET=5`

如果以上参数设得太小，可能会遇到如下问题：

- 创建新 ENI 并将其附加到节点最多可能需要 10 秒。造成 pod 创建缓慢
- ipamd 需要调用 EC2 API 将 ip 附加到实例上，调用频繁的情况下可能会遇到到 API 速率限制，导致无法将新
  的 ENI 或 IP 附加到集群中的任何实例。

详见
[WARM_ENI_TARGET, WARM_IP_TARGET and MINIMUM_IP_TARGET](https://github.com/aws/amazon-vpc-cni-k8s/blob/master/docs/eni-and-ip-target.md)
