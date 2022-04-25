# AWS - [kubernetes/autoscaler](https://github.com/kubernetes/autoscaler)

cluster-autoscaler（以下简写为 CAS）是 kubernetes 官方提供的一个节点伸缩组件，支持 AWS.

CAS 相比 karpenter 的区别在于，它底层是基于 AWS ASG 伸缩组实现的，因此也能很方便地用上 ASG 的各种特性：

- Spot/OD、多种实例类型混用的 ASG

当然也有些 ASG 特性 CAS 目前还不支持：

- 热池：提前扩容一批实例并关机，在需要时可以立即启动并加入集群
  - 这个可能是一个仅针对 OD 按需实例的功能？还是也支持 Spot 呢？有空可以研究下
  - https://github.com/kubernetes/autoscaler/issues/4005

CAS 还存在一个缺陷，就是 AWS ASG 虽然提供 Spot/OD 混用的能力，但是必须手动设定它们之间的比例。如果 Spot 资源不足，ASG 仍然会无法扩容！社区的解决方法是：

- 配置两个节点组，一个只扩容 Spot 实例，另一个只扩容 OD 实例
- 配置 cluster-autoscaler，优先扩容 Spot 实例的节点组，如果扩容失败，再 fallback 到 OD 节点组。

>必须吐槽，EKS 的 NodeGroup 太难用了，创建后就无法修改实例类型，直接改底层的 ASG 它还会报错「Degraded」，看着烦心。

而 Karpenter 你直接配上 Spot/OD 两个实例类型，它就会优先扩容 Spot，在 Spot 申请失败时会自动 fallback 回 OD，配置非常简单。

总的来看，karpenter 的特性是比 CAS 更多的，使用也更简单，不需要手动建一堆 Node Group，文档也更清晰。

但是 karpenter 目前（0.8.2）比 CAS 缺少两个关键特性，这导致在生产环境中它还不太实用，详见此文件夹中的 karpenter 笔记。


## 安装 CA

### 1. 配置权限

CA 只会查询 ASG 配置，通过 ASG Tag 自动发现它需要管理的 ASG，然后动态调整 ASG 的「DesiredCapacity」，如下是它需要的所有权限，可以命名为 `xxxK8sClusterAutoScalerPolicy`：

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "autoscaling:DescribeAutoScalingGroups",
        "autoscaling:DescribeAutoScalingInstances",
        "autoscaling:DescribeLaunchConfigurations",
        "autoscaling:DescribeTags",
        "ec2:DescribeInstanceTypes",
        "ec2:DescribeLaunchTemplateVersions"
      ],
      "Resource": ["*"]
    },
    {
      "Effect": "Allow",
      "Action": [
        "autoscaling:SetDesiredCapacity",
        "autoscaling:TerminateInstanceInAutoScalingGroup",
        "ec2:DescribeInstanceTypes",
        "eks:DescribeNodegroup"
      ],
      "Resource": ["*"]
    }
  ]
}
```

如果你希望将权限限制到具体的 ASG，可以自行调整 `Resource` 参数的值。

然后将该 Policy 绑定到 CAS 的 ServiceAccount:

```shell
export CLUSTER_NAME="xxx"
export AWS_ACCOUNT_ID="112233445566"

eksctl create iamserviceaccount \
  --cluster "${CLUSTER_NAME}" --name cluster-autoscaler --namespace kube-system \
  --role-name "${CLUSTER_NAME}-cluster-autoscaler" \
  --attach-policy-arn "arn:aws:iam::${AWS_ACCOUNT_ID}:policy/xxxK8sClusterAutoScalerPolicy" \
  --role-only \
  --approve
```

## 2. 部署 Cluster AutoScaler

首先下载自动发现节点组的 CAS 配置模板：

```yaml
curl https://github.com/kubernetes/autoscaler/blob/master/cluster-autoscaler/cloudprovider/aws/examples/cluster-autoscaler-autodiscover.yaml
```

- 修改其参数中的标签 `k8s.io/cluster-autoscaler/<YOUR CLUSTER NAME>`，填充上你的集群名称，这会使 CAS 自动发现该集群下的所有节点组。
- 修改其 ServiceAccount，绑定前面创建好的 IAM Role `${CLUSTER_NAME}-cluster-autoscaler`
  - 添加此 annotations 即可: `eks.amazonaws.com/role-arn: arn:aws:iam::${AWS_ACCOUNT_ID}:role/${CLUSTER_NAME}-cluster-autoscaler`

## 配置 CA

>https://github.com/kubernetes/autoscaler/blob/master/cluster-autoscaler/FAQ.md

### 避免 Pod 被 CAS 驱逐

添加如下 annotation 即可：

```
"cluster-autoscaler.kubernetes.io/safe-to-evict": " false"
```

### 如何调整扩缩容策略

比如对于一个大数据计算的集群，可能会非常动态，我们就希望能尽可能快地缩容：节点 2mins 没有使用即缩容。

CA 默认在上次扩容 10mins 后，才会执行缩容评估，可手动添加如下命令行参数将该值调整为 2mins:

```
--scale-down-delay-after-add=120s
--scale-down-unneeded-time=120s
```

我们的集群非常动态，因此还希望能非常快速地缩容，空节点一次可以全部缩掉：

```
--max-empty-bulk-delete=500
```

尽量不要让 CAS 缩容掉我们有实例正在跑的节点（可能会造成资源浪费，调整后需要验证效果）：

```
--scale-down-non-empty-candidates-count=30
```

同时我们希望限制集群扩容的上限，避免使用的资源太多：

```
--cores-total=0:3000
--memory-total=0:12000
```

平衡相似节点组的实例数量，常用场景是平衡各可用区的实例数（手动建多个节点组，每个节点组对应不同可用区，其他配置都一致）。

```
--balance-similar-node-groups=true
```

纯计算实例，都是无状态的，临时存储都可以随意删除：

```
--skip-nodes-with-local-storage=false
```

系统的实例跑着的节点也可以缩容：

```
--skip-nodes-with-system-pods=false
```

日志输出到 info 级别：

```
--stderrthreshold=info
```


### 如何配置多个节点组、实例类型之间的优先级

>https://github.com/kubernetes/autoscaler/blob/master/cluster-autoscaler/FAQ.md#what-are-expanders

>https://github.com/kubernetes/autoscaler/blob/master/cluster-autoscaler/expander/priority/readme.md

CA 通过名为 expander 的组件决定如何扩容，为了实现调整优先级，我们需要使用 `priority` 这个 expander，通过如下参数设定 expander:

```
--expander=priority
```

也可以设定多个 expander:

```
--expander=priority,least-waste
```

上述参数表示，如果 `priority` 选中了多个节点组，就使用 `least-waste` 再筛选一次。

选用了 `priority` 这个 expander 后，可以通过调整 `cluster-autoscaler-priority-expander` 这个 configmap，配置不同节点组、实例类型之间的优先级。

让名为 `worker-spot` 的节点组，拥有比 `worker-od` 节点组更高的优先级（永远优先扩容 Spot 实例，如果容量不够，可以 fallback 回 On-Demand 实例）：

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: cluster-autoscaler-priority-expander
  namespace: kube-system
data:
  priorities: |-
    10:
      - .*worker-od.*
    20:
      - .*worker-spot.*    
```

其中的匹配语句是正则语法，至于被它匹配的节点组/实例类型信息的完整示例...我没在文档中找到...（文档写得是真随意）


### 如何缩容到 0

>https://github.com/kubernetes/autoscaler/blob/master/cluster-autoscaler/FAQ.md#how-can-i-scale-a-node-group-to-0

根据官方文档，AWS 支持缩容到 0，但是如果使用了 `nodeSelector` 的话，需要为 ASG 添加一个特殊标签。

比如假设你的 nodeSelector 为 `eks.amazonaws.com/nodegroup: xxx`，那就需要为 ASG 添加标签：

- key: `k8s.io/cluster-autoscaler/node-template/label/eks.amazonaws.com/nodegroup`
- value: `xxx`

如果不加这个标签，在节点组缩容到 0 后，再次扩容时 CAS 可能会因为无法识别到该节点组的 node labels 而扩容失败，提示你标签不匹配！


## 参考

- [Cluster Autoscaler on AWS](https://github.com/kubernetes/autoscaler/tree/master/cluster-autoscaler/cloudprovider/aws)


