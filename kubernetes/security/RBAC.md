# Kubernetes RBAC


## 给一个 AWS user/role 添加访问 EKS 集群的权限

官方文档: https://aws.amazon.com/cn/premiumsupport/knowledge-center/amazon-eks-cluster-access/

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
