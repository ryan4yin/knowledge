# OIDC Provider for Kubernetes

>https://kubernetes.io/docs/reference/access-authn-authz/authentication/#configuring-the-api-server.

Kubernetes 的 RBAC 体系中包含两类用户：

1. SerivceAccount: 由 K8s 管理的，提供给 Pod 使用的用户
2. 普通用户：由与 k8s 无关的其他服务管理

K8s 自身不提供「普通用户」的实现，K8s 将这项工作交给了第三方组件，常见的实现方式有：

- 由 AWS IAM、Google Accounts 或者其他支持 OIDC 协议的 Provider 管理，并提供 OIDC Provider URL 给到 K8s API Server
- 由管理员向集群 CA 申请签发的证书与私钥，这也被认为是一个普通用户，其 RBAC 中的用户名即为证书的 `CN` 字段，
    - 各种集群安装工具最初生成的 admin kubeconfig 就是使用这种方式制作的。


## 使用 [dex](https://github.com/dexidp/dex) 为 K8s 添加「普通用户」功能

>仅适用于测试环境，未做高可用

>官方文档: [Kubernetes Authentication Through Dex](https://dexidp.io/docs/kubernetes/)

直接使用官方提供的示例 yaml 部署：https://github.com/dexidp/dex/blob/master/examples/k8s/dex.yaml


