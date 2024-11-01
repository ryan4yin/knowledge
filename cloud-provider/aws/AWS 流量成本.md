# AWS 流量成本

## 跨区流量成本 - InterZone

> 官方文档：https://aws.amazon.com/ec2/pricing/on-demand/#Data_Transfer_within_the_same_AWS_Region

对于同一个 Region 内的应用架构而言，最大的一项成本开支很可能是跨区流量成本
（`usage_type=DataTransfer-Regional-Bytes`），主要有如下几个部分：

- 服务之间互相调用造成的跨区流量成本
- 服务访问 RDS/OpenSearch 等中间件造成的跨区流量成本
- RDS 等中间件集群之间数据同步造成的跨区流量成本

**而且跨区流量成本，是固定的会在 each direction 收 $0.01/GB 的费用**，也就是说对每台 EC2，只要与其沟
通的 AWS 服务不免流量费，那跨区进入 EC2 的流量（`Zone-In`），以及从 EC2 跨区出去的流量
（`Zone-Out`），都是要收费的。

跨区流量费的优化，对所有国外云服务商而言基本是通用的，可以参考
[跨区流量处理方案](/cloud-provider/跨区流量处理方案.md)。

## 跨域流量成本 - Inter Region

对于做了多 Region 部署以实现接近用户、容灾等能力的 AWS 使用者而言，Inter Region 的成本是不可忽视的。

对于跨 Region 流量（`usage_type=DataTransfer-Out-Bytes`），AWS 的收费如下：

- 所有从 Internet/其他 Region 传输进入 EC2 的流量：免费
- 从 EC2 传出到另一 Region 的流量：价格参见官方文
  档：[data transferred "in" to and "out" of Amazon EC2](https://aws.amazon.com/ec2/pricing/on-demand/#Data_Transfer)
  - 如果两边的 VPC 需要通过 NAT Gateway 通信，就还会涉及到 NAT Gateway 的费用
    （`usage_type=NatGateway-Bytes`）
- 从 EC2 传输到 Internet 的流量：阶梯式收费
  - 注意这里还会涉及到 NAT Gateway 的流量成本
  - 这告诫我们 - 只在必要的时候，才给 EC2/RDS/ELB... 分配公网 IP/启用公网访问，避免带来额外的
    Internet 流量成本.

## 公网流量成本

对于 VPC 网络，公网流量成本主要有两种：

1. 入口网关的公网流量费用 + 网关计算费用
   1. 其中网关计算费用可以是 NLB/ALB 的数据处理费用，也可以是自建的 EC2 实例的计算存储费用
2. NAT 网关的公网流量费用 + NAT 网关计算费用
   1. 如果使用了 AWS 托管版 NAT 网关，那这收的就是数据处理费用
   2. 如果是自建了 NAT 网关，那这收的就是底层 EC2 实例的计算存储费用

其中 ALB、托管版 NAT 网关的数据处理费用，在流量大的情况下都是比较贵的，可以通过使用对应的自建方案降
低成本。

ALB 可以用 NLB + 自建 L7 网关替代，而 NAT 网关则可以用
[alternat](https://github.com/1debit/alternat) 这类开源方案替代。

不过其中要注意的是，在流量大的情况下 NAT 实例或 L7 网关实例，都可能会遇到 nf_conntrack 表用尽导致
504 等超时错误的问题，需要调整 nf_conntrack 的内核参数扩容该表容量。

以及 EC2 的 ENA driver 本身存在固定的 conntrack 上限，即使调整内核 nf_conntrack 参数也无法突破这个上
限，可以通过 AWS 监控指标（如 `conntrack_allowance_available` `conntrack_allowance_exceeded`）来监控 ENA driver 的 conntrack 使用情
况：[Metrics for the ENA driver - ENA Network Performance](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/monitoring-network-performance-ena.html#network-performance-metrics)

## FAQ

### 我能否通过加一层 ELB 来避免被收取 Cross Zone 的流量成本？

参见 [ELB 负载均衡](./ELB%20负载均衡.md)，ALB 不收跨区流量费，NLB 会收跨区流量费。

那对 HTTP 流量传输而言，ec2 => alb => ec2 这样的跨区传输方式，会不会比 ec2 => ec2 更便宜呢？

待研究（感觉是不会...）

## 相关文档

- [Overview of Data Transfer Costs for Common Architectures](https://aws.amazon.com/blogs/architecture/overview-of-data-transfer-costs-for-common-architectures/)
- [AWS Data Transfer Costs — a practical guide](https://github.com/open-guides/og-aws#aws-data-transfer-costs)
