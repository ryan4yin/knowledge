# [aws/karpenter](https://github.com/aws/karpenter)

karpenter 是 aws 官方推出的一个集群伸缩组件，相比 Kubernetes 社区的 Cluster Autoscaler 组件，它的优势在于：

- karpenter 对 aws 数百种实例类型、可用区、购买参数的支持要更好些
- Karpenter 直接管理每个节点实例，完全绕过了 AWS EKS NodeGroup 等编排机制，这免去了管理大量不同配置的 NodeGroups 的烦恼，而且使它的扩缩容、重试机制等更灵活快速
- 社区的 Cluster Autoscaler 自身不提供 Pod 调度能力，完全依赖于 kube-scheduler 进行 pod 调度。而 Karpenter 在节点上线后会立即主动将未调度成功的 Pod 绑定到新节点，从而使 kubelet 预先准备容器运行时、预拉取镜像，这可以缩短几秒钟的节点启动延时

注意 karpenter 并不会响应 spot 中断等 EC2 事件，这需要使用 [AWS Node Termination Handler](https://github.com/aws/aws-node-termination-handler) 实现。

## 一、安装方法

### 创建或关联实例配置文件 InstanceProfile 及 IAM Role

AWS EC2 的 InstanceProfile 是一个 IAM Role 的容器，EC2 不能直接关联 IAM Role，必须使用 InstanceProfile 作为中介。

Karpenter 也需要一个具备必要权限的 InstanceProfile 来为 EKS 创建新节点，这样新建出的节点才能正常加入到集群中。


```shell
export KARPENTER_VERSION=v0.6.5
export CLUSTER_NAME="eks-xxx-cluster-v1"

export AWS_ACCOUNT_ID="$(aws sts get-caller-identity --query Account --output text)"
export CLUSTER_ENDPOINT="$(aws eks describe-cluster --name ${CLUSTER_NAME} --query "cluster.endpoint" --output text)"

TEMPOUT=$(mktemp)

curl -fsSL https://karpenter.sh/"${KARPENTER_VERSION}"/getting-started/getting-started-with-eksctl/cloudformation.yaml  > $TEMPOUT \
&& aws cloudformation deploy \
  --stack-name "Karpenter-${CLUSTER_NAME}" \
  --template-file "${TEMPOUT}" \
  --capabilities CAPABILITY_NAMED_IAM \
  --parameter-overrides "ClusterName=${CLUSTER_NAME}"
```

上面的命令会使用 AWS CloudFormation 自动创建如下资源：

- KarpenterNodeRole
- KarpenterNodeInstanceProfile
- KarpenterControllerPolicy

### 允许 Karpenter 创建的节点连接到 EKS 集群

使用如下命令修改 EKS 集群配置，允许使用 `KarpenterNodeRole-xxx` 这个 IAM Role 的 EC2 实例连接到 EKS 集群。

```shell
eksctl create iamidentitymapping \
  --username system:node:{{EC2PrivateDNSName}} \
  --cluster "${CLUSTER_NAME}" \
  --arn "arn:aws:iam::${AWS_ACCOUNT_ID}:role/KarpenterNodeRole-${CLUSTER_NAME}" \
  --group system:bootstrappers \
  --group system:nodes
```

这其实就是自动修改 `kube-system` 名字空间的 `configmap/aws-auth`，添加如下配置：

```yaml
apiVersion: v1
data:
  mapRoles: |
    # 集群默认使用的 Node Role
    - groups:
      - system:bootstrappers
      - system:nodes
      rolearn: arn:aws:iam::xxxxxxx:role/xxxxxxx
      username: system:node:{{EC2PrivateDNSName}}
    # eksctl 命令新插入的配置：
    - groups:
      - system:bootstrappers
      - system:nodes
      rolearn: arn:aws:iam:::role/KarpenterNodeRole-eks-xxx-cluster-v1
      username: system:node:{{EC2PrivateDNSName}}
```

### 为 KarpenterController 创建 IAM Role

KarpenterController 需要必要的权限来创建、删除、修改 EC2 实例，为此需要为它创建相应的 Policy 与 IAM Role，之后再通过 Kubernetes ServiceAccount 关联上这个 IAM Role.

需要的 Policy `KarpenterControllerPolicy` 应该已经在第一步的脚本中自动创建好了，这里直接关联即可：

```shell
eksctl create iamserviceaccount \
  --cluster "${CLUSTER_NAME}" --name karpenter --namespace karpenter \
  --role-name "${CLUSTER_NAME}-karpenter" \
  --attach-policy-arn "arn:aws:iam::${AWS_ACCOUNT_ID}:policy/KarpenterControllerPolicy-${CLUSTER_NAME}" \
  --role-only \
  --approve

export KARPENTER_IAM_ROLE_ARN="arn:aws:iam::${AWS_ACCOUNT_ID}:role/${CLUSTER_NAME}-karpenter"
```

上面命令将自动创建 IAM Role `${CLUSTER_NAME}-karpenter`，并自动为此 Role 配置信任关系，允许 `${CLUSTER_NAME}` 集群的 `karpenter/karpenter` 这个 ServiceAccount 绑定此 IAM Role.


### 创建 EC2 Spot 服务关联 Role

如果你的 AWS 账号还从来没使用过 EC2 Spot 服务，需要先跑下下面这个命令：

```shell
aws iam create-service-linked-role --aws-service-name spot.amazonaws.com || true
```

如果这个 Role 已经创建好了，上述命令将会产生如下报错，直接进入下一步即可：

```
An error occurred (InvalidInput) when calling the CreateServiceLinkedRole operation: Service role name AWSServiceRoleForEC2Spot has been taken in this account, please try a different suffix.
```


### 使用 Helm 安装 karpenter


```shell
helm repo add karpenter https://charts.karpenter.sh/
helm repo update
```


然后使用如下命令安装（更好的选择是使用一个自定义的 values.yaml）：

```shell
kubectl create ns karpenter
helm upgrade --install --namespace karpenter --create-namespace \
  karpenter karpenter/karpenter \
  --version ${KARPENTER_VERSION} \
  --set serviceAccount.annotations."eks\.amazonaws\.com/role-arn"=${KARPENTER_IAM_ROLE_ARN} \
  --set clusterName=${CLUSTER_NAME} \
  --set clusterEndpoint=${CLUSTER_ENDPOINT} \
  --set aws.defaultInstanceProfile=KarpenterNodeInstanceProfile-${CLUSTER_NAME} \
  --wait # for the defaulting webhook to install before creating a Provisioner
```



## 二、使用方法

Karpenter 使用名为 `Provisioner` 的 CRD 来管理集群的伸缩，Kapenter 基于 `Provisioner` 的配置内容，参考 Pod 的 lables/affinity 等属性进行集群的伸缩决策。

简单的说，使用了 Karpenter 的 `Provisioner`，你再就不再需要管理多个 EKS 节点组了。


一个简单的 Provisioner 配置如下：

```shell
cat <<EOF | tee > karpenter-provisioner.yaml
apiVersion: karpenter.sh/v1alpha5
kind: Provisioner
metadata:
  name: default
spec:
  requirements:
    - key: karpenter.sh/capacity-type
      operator: In
      values: ["spot"]
  limits:
    resources:
      cpu: 1000
  provider:
    subnetSelector:  # 通过标签自动发现可用的 subnets
      karpenter.sh/discovery: ${CLUSTER_NAME}
    securityGroupSelector:  # 通过标签自动发现可用的 security groups
      karpenter.sh/discovery: ${CLUSTER_NAME}
  ttlSecondsAfterEmpty: 30  # 定义节点的最大空闲时间，超过此时间将被自动关闭
EOF
```

## 节点回收 - Deprovisioning

首先，karpenter 会基于 `ttlSecondsAfterEmpty` 参数的配置，自动回收长时间空闲的空节点。

其次，karpenter 会自动地优雅关停（`cordon` => `drain` => `shutdown`）被 `kubectl delete no xxx` 命令删除的节点（前提是此节点受 `karpenter` 管理）。这是通过在所有节点上添加 `finalizer` 实现的，这个 `finalizer` 会一直阻塞，直到 kanpenter 完成所有前置操作。

如下配置可以组织 Karpenter 回收某个节点：

- PodDisruptionBudget: 如果回收某个节点会破坏某个 PDB 配置，Karpenter 将会停止该操作，过一段时间再重试（Backoff Retry Eviction）
  - PDB 可有效保护服务的稳定性，确保始终有足够多的 Pods 处于 Ready 状态
- Karpenter 永远不会强制删除 Pods，如果某个 Pod 无法被删除，对应的节点就永远不会被回收
- Karpenter 不会驱逐拥有 `karpenter.sh/do-not-evict` 注解的 Pods，有这类 Pods 运行的节点不会被回收
  - 有些 Pods 可能是不允许中断的，比如 spark driver, 它的中断会导致整个 spark 任务失败。为这类 pod 添加上述注解可以有效地保护它们。



