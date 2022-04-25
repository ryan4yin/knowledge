# [aws/karpenter](https://github.com/aws/karpenter)

karpenter 是 aws 官方推出的一个集群伸缩组件，相比 Kubernetes 社区的 Cluster Autoscaler 组件，它的优势在于：

- karpenter 对 aws 数百种实例类型、可用区、购买参数的支持要更好些
- Karpenter 直接管理每个节点实例，完全绕过了 AWS EKS NodeGroup 等编排机制，这免去了管理大量不同配置的 NodeGroups 的烦恼，而且使它的扩缩容、重试机制等更灵活快速
- 社区的 Cluster Autoscaler 自身不提供 Pod 调度能力，完全依赖于 kube-scheduler 进行 pod 调度。而 Karpenter 在节点上线后会立即主动将未调度成功的 Pod 绑定到新节点，从而使 kubelet 预先准备容器运行时、预拉取镜像，这可以缩短几秒钟的节点启动延时
- 只要你同时选择了 Spot/OD 两种实例类型，Karpenter 的扩容策略就会自动扩容最佳的实例，Spot 实例的分配优先级是比 OD 更高的，因此会被优先分配。
  - 并且在 Spot 实例申请失败的时候（资源不足），fallback 到 OD，这个 fallback 的速度非常的快，不会影响集群扩容速度。

注意 karpenter 并不会响应 spot 中断等 EC2 事件，这需要使用 [AWS Node Termination Handler](https://github.com/aws/aws-node-termination-handler) 实现。

实际观测上看，karpenter 扩容确实非常迅速，而且会提前将节点配置加入到集群中，从扩容到新节点就绪，用时大概在 75s-120s 的样子。

注意事项：

- karpenter 不支持 podAntiAffinity
- karpenter 不会主动回收非空节点！除非该节点触发了 `Node Expired` 策略！
  - 即使使用了 descheduler 来优化 pod 拓扑分布，也起不到应有的效果！
  - 相关 issue: https://github.com/kubernetes-sigs/descheduler/issues/749
  - 临时解决方法：对于大数据这类纯计算的集群，创建一个小的 Spot 节点组专门给集群组件使用，跟计算任务隔离开。
    - 修改所有这些实例的 nodeSelector，只允许在这个专用节点组上运行


## 一、安装方法

### 创建并关联 Karpenter 节点的 IAM 相关资源

AWS EC2 的 InstanceProfile 是一个 IAM Role 的容器，EC2 不能直接关联 IAM Role，必须使用 InstanceProfile 作为中介。

Karpenter 也需要一个具备必要权限的 InstanceProfile 来为 EKS 创建新节点，这样新建出的节点才能正常加入到集群中。

```shell
export KARPENTER_VERSION=v0.8.2
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


参考 [AWS IAM 权限控制](/cloud-provider/aws/IAM%20权限控制.md) 末尾的内容。可通过 AWS CLI 为已存在的 IAM Role 创建 InstanceProfile.

建议使用 GitOps 的方式创建这些资源，pulumi/terraform 都是很好的工具。

如果你是将一个已存在的集群迁移到 Karpenter，那就更建议自主管理 NodeRole 及 InstanceProfile 了。

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

### 为 KarpenterController 服务绑定 KarpenterControllerPolicy

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

详细的参数可以通过如下命令 check:

```shell
helm pull karpenter/karpenter  --untar
cat karpenter/values.yaml
```

## 二、使用方法

Karpenter 使用名为 `Provisioner` 的 CRD 来管理集群的伸缩，Kapenter 基于 `Provisioner` 的配置内容，参考 Pod 的 lables/affinity 等属性进行集群的伸缩决策。

简单的说，使用了 Karpenter 的 `Provisioner`，你再就不再需要管理多个 EKS 节点组了。


一个简单的 Provisioner 配置如下：

```yaml
# karpenter-provisioner.yaml
apiVersion: karpenter.sh/v1alpha5
kind: Provisioner
metadata:
  name: default
spec:
  # EC2 节点的可选配置
  requirements:
    - key: "node.kubernetes.io/instance-type"
      operator: In
      values: [
        "m6i.large", "m6i.xlarge", "m6i.2xlarge", "m6i.4xlarge",
        "m5.large", "m5.xlarge", "m5.2xlarge", "m5.4xlarge",
        ]
    - key: "topology.kubernetes.io/zone"
      operator: In
      values: ["us-east-1a", "us-east-1b", "us-east-1c", "us-east-1d", "us-east-1f"]
    - key: "kubernetes.io/arch"
      operator: In
      values: ["amd64"]
    - key: karpenter.sh/capacity-type
      operator: In
      values: ["spot"]  # 只允许用 spot 实例


  ttlSecondsAfterEmpty: 180  # 定义节点的最大空闲时间（单位秒），超过此时间将被自动关闭
  # ttlSecondsUntilExpired: 86400  # 定义节点的最大存活时间（单位秒），超过此时间将被强制回收。可用于确保所有节点都始终在使用最新的配置

  # Provisioned nodes will have these taints
  # Taints may prevent pods from scheduling if they are not tolerated
  # taints:
  #   - key: example.com/special-taint
  #     effect: NoSchedule

  # Labels are arbitrary key-values that are applied to all nodes
  labels:
    billing-team: my-team
    # 如下标签可用于兼容 eks nodegroup 的调度方式
    eks.amazonaws.com/nodegroup: worker

  limits:
    resources:
      cpu: 100
      memory: 400Gi

  provider:
    # EC2 需要借由 instance profile 来绑定一个 IAM Role
    # instance profile 只能通过 AWS CLI 来单独查询、修改、创建，详见此仓库的 AWS IAM 笔记
    instanceProfile: xxx
    # EC2 的启动模板，记录了磁盘大小、userdata 等信息。
    # 如果不指定 karpenter 会自动创建
    launchTemplate: xxx
    subnetSelector:  # 通过资源标签自动发现可用的 subnets
      karpenter.sh/discovery: ${CLUSTER_NAME}
    securityGroupSelector:  # 通过标签自动发现可用的 security groups
      karpenter.sh/discovery: ${CLUSTER_NAME}
    # 为 EC2 节点添加自定义的标签
    tags:
      dev.corp.net/app: Calculator
      dev.corp.net/team: MyTeam
    amiFamily: AL2  # 通过 AMI 家族名称自动发现合适的 AMI 镜像，AL2/Bottlerocket
    # 设定磁盘大小，它的优先级比 launchTemplate 低，两者不能共用
    blockDeviceMappings: 
      - deviceName: /dev/xvda
        ebs:
          volumeSize: 40Gi
          volumeType: gp3
          # iops: 3000
          # throughput: 125
          deleteOnTermination: true
  ttlSecondsAfterEmpty: 180  # 定义节点的最大空闲时间（单位秒），超过此时间将被自动关闭
  # ttlSecondsUntilExpired: 86400  # 定义节点的最大存活时间（单位秒），超过此时间将被强制回收。可用于确保所有节点都始终在使用最新的配置
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


## 自定义 Launch Template

CRD 中直接提供的参数有限，如果需要自定义 AMI、userdata 等更底层的数据，就需要用到自定义 launch templates.

但是要注意，一旦使用了自定义 Launch Template，那除了实例类型、网络配置之外的其他参数，都将使用你配置的参数，如果配置不当就会导致实例无法启动，或者无法加入集群。

Launch Template 的网络接口配置、实例类型配置都会被 karpenter 强制覆盖，所以不要配置它们，这没啥意义。

官方推荐用 CloudFormation 创建 LaunchTemplate

```yaml
# launch-template-eks-test.yaml
AWSTemplateFormatVersion: '2010-09-09'
Resources:
  KarpenterCustomLaunchTemplate:
    Type: AWS::EC2::LaunchTemplate
    Properties:
      LaunchTemplateData:
        # InstanceProfile 跟 Role 都需要提前创建好，感觉没必要单独为 Karpanter 搞一套
        IamInstanceProfile:
          Arn: arn:aws:iam::112233445566:instance-profile/TestEKSClusterNodeInstanceRole
        # AMI ID
        ImageId: ami-074cce78125f09d61
        # UserData is Base64 Encoded
        UserData: !Base64 |
          #!/bin/bash
          /etc/eks/bootstrap.sh 'MyClusterName' \
          --kubelet-extra-args '--node-labels=node.k8s.aws/capacity-type=spot' \
          --b64-cluster-ca 'LS0t....0tCg==' \
          --apiserver-endpoint 'https://xxxxxx.gr7.us-east-2.eks.amazonaws.com'
        BlockDeviceMappings:
          - Ebs:
              VolumeSize: 40
              VolumeType: gp3
            DeviceName: /dev/xvda
        # The SecurityGroup must be associated with the cluster VPC
        SecurityGroupIds:
          - sg-xadsafds
      LaunchTemplateName: KarpenterCustomLaunchTemplate
```

然后使用如下命令创建

```shell
aws cloudformation create-stack \
  --stack-name KarpenterCustomLaunchTemplateStack \
  --template-body file://$(pwd)/launch-template-eks-test.yaml
```

