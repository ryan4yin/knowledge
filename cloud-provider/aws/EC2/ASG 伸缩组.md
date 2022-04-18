# Auto Scaling Group 伸缩组

AWS 的 ASG 实例伸缩组，跟 EKS 的 Deployments 比较类似，也可以设定最小实例数，再按需扩缩容。
区别在于 ASG 管理的是节点数量。

EKS 的 Node Group 节点组，就是基于 ASG 实现的，K8s 社区的 ClusterAutoscaler 也是基于 ASG 实现的。

不过因为 ASG 的功能比较有限：不支持混合使用 OD 与 Spot 实例、配置多种实例类型的情况下，扩缩容不够智能，等等。
无法满足非常动态的场景，这导致市场上出现了一些第三方的扩缩容服务，比如 Spotinst, SpotMax.

ASG 本身不收费，只有 EC2 收费。但是如果你给 EC2 配置了如 AWS Config 之类的 EC2 配置变更记录，可能因为因为 EC2 过于动态，产生大量的 AWS Config 费用。

## 结构

ASG 由这几个部分组成：

- EC2 启动模板
  - 包含了 EC2 的所有初始配置，如 AMI 镜像（包含 ARM/X86 架构）、实例类型、EBS 卷大小及类型、SSH 密钥、Tags、VPC 及网卡、userdata 等
- ASG 伸缩组
  - 可选择一组实例类型（它将覆盖掉启动模板里的默认配置）
  - 对于 Spot 伸缩组，一般建议同时使用最新两代的实例，优先使用最新的实例，老一代的用于兜底。
  - 可定义多个启动模板，以支持不同的 CPU 架构（ARM/X86）
      - 这个也基本没用过
  - 可为每个实例类型定义一个独立的权重，在实例的 CPU/MEM/存储/网络 性能差距较大时比较有用
    - 通常没啥用
  - 设定是要用 OD 按需实例还是 Spot 竞价实例，或者按指定的比例混合使用这两种实例
  - [启用「Capacity Rebalancing」](https://docs.aws.amazon.com/autoscaling/ec2/userguide/ec2-auto-scaling-capacity-rebalancing.html)，这样当 Spot 实例有较高中断风险时，ASG 会提前扩容，然后再终止这些有风险的旧实例。
  - 指定一个实例分配策略
    - Spot 实例有这两个策略，分别侧重容量与价格：capacity-optimized 与 lowest-price
    - OD 实例也有两个策略：
      - lowest-price：按价格申请实例
      - prioritized：按给定的实例列表顺序，申请实例，越靠前的优先级越高

## 使用

>https://docs.aws.amazon.com/autoscaling/ec2/userguide/ec2-auto-scaling-mixed-instances-groups.html

TBD

## 自动伸缩策略

ASG 支持非常多的伸缩策略：

1. [按计划（预测时间）进行伸缩](https://docs.aws.amazon.com/autoscaling/ec2/userguide/schedule_time.html)
2. [动态伸缩](https://docs.aws.amazon.com/autoscaling/ec2/userguide/as-scale-based-on-demand.html) - 按 CPU 等资源使用率进行伸缩

一般来说，动态伸缩是最灵活的，我们的 EKS 集群一直都是用的动态伸缩特性，这里就主要介绍下这个。
动态伸缩有好几种类型，其中最主要的应该是「**target tracking scaling policy**」，它基于某个指标进行动态扩缩容。
有这几个预定义的 ASG 伸缩指标：

- ASGAverageCPUUtilization
- ASGAverageNetworkIn
- ASGAverageNetworkOut
- ALBRequestCountPerTarget

通常来讲 `ASGAverageCPUUtilization` 是用得最多、最通用的指标。

## Warm pools 热池

>https://docs.aws.amazon.com/autoscaling/ec2/userguide/ec2-auto-scaling-warm-pools.html

TBD

## ASG 与 K8s 集群伸缩

>https://docs.aws.amazon.com/eks/latest/userguide/autoscaling.html

AWS 集群伸缩有这几个组件：

- K8s 社区的 Cluster Autoscaler: 基于原生的 ASG 实现
- aws 官方搞的 karpanter: 抛弃了 ASG，自己搞了一套

TBD

