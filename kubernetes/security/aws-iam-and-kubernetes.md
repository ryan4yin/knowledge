## 一、给 EKS ServiceAccount 绑定一个 AWS IAM Role

> [IAM roles for service accounts- AWS Docs](https://docs.aws.amazon.com/eks/latest/userguide/iam-roles-for-service-accounts.html)

> [为集群创建 IAM OIDC Provider](https://docs.aws.amazon.com/eks/latest/userguide/enable-iam-roles-for-service-accounts.html)

这种授权方式，主要用于给 Pods 赋予访问 AWS 某些服务的权限。

授权步骤如下：

1. 每个 EKS 集群都有一个 OIDC issuer URL，首先我们需要使用它，创建一个 IAM OIDC Prodiver
   1. [Create an IAM OIDC provider for your cluster](https://docs.aws.amazon.com/eks/latest/userguide/enable-iam-roles-for-service-accounts.html)
2. 创建 IAM Role，绑定需要的 Policy 权限策略，并将 EKS 集群的 serviceAccount 加入到「信任关系」中
   1. [Creating an IAM role and policy for your service account](https://docs.aws.amazon.com/eks/latest/userguide/create-service-account-iam-policy-and-role.html)
3. 创建 EKS ServiceAccount，使用 annotation 关联到前面创建的 IAM Role，然后在 Pod 中使用此
   serviceaccount
4. [Associate an IAM role to a service account](https://docs.aws.amazon.com/eks/latest/userguide/specify-service-account-role.html)

## 二、给一个 AWS User/Role 添加访问 EKS 集群的权限

> https://aws.amazon.com/cn/premiumsupport/knowledge-center/amazon-eks-cluster-access/

这种授权方式，主要用于给某些 AWS 用户或者 Role，授予访问 EKS 集群中某些资源的权限。可以理解到这跟前
面的授权是刚好相反的，前一个是授权 EKS Pods 访问 AWS，而这里是授权 AWS 用户访问 EKS。

首先，使用 `kubectl edit configmap aws-auth -n kube-system` 修改配置，添加 `mapUsers` 配置，如下:

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: aws-auth
  namespace: kube-system
data:
  mapRoles: |
    - rolearn: arn:aws:iam::<a-userrole>
      username: system:node:{{EC2PrivateDNSName}} 
      groups: 
        - system:bootstrappers 
        - system:nodes
  # 添加如下配置，将 IAM 用户和 k8s 用户绑定起来
  mapUsers: |
    - userarn: arn:aws:iam::11122223333:user/designated_user  # IAM user
      username: designated_user    # kubernetes user
      groups: 
        - system:masters
```

完成后，再使用 kubectl 给 `designated_user` 赋予集群管理员的角色：

```shell
kubectl create clusterrolebinding xxx-cluster-admin --clusterrole=cluster-admin --user=designated_user
```

这样完成后，`designated_user` 就可以使用 aws 命令，生成 `kubeconfig` 并访问 eks 集群了：

```shell
# 生成 Kubeconfig
aws eks --region <region> update-kubeconfig --name <cluster_name>
# 访问 eks 集群
kubectl get pods
```
