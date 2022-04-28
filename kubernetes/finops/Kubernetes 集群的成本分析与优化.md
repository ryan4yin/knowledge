# Kubernetes 集群的成本分析 - FinOps

Kubernetes 作为一个多租户的计算平台，我们很自然地会在上面运行多种微服务、CICD、数据分析、机器学习等任务，并且让 Kubernetes 的节点组按需动态扩缩容。

这样就会产生一个需求——如何计算各项计算任务使用了多少资源？花了多少钱？
更近一步的，某个业务团队、某个业务产品花了多少钱？

如果没有资源使用统计及成本统计，整个集群的资源用量就无法拆分，就很难定位到资源占用问题、成本增长问题，换句话说集群的资源池、成本就完全不可控。


## 相关工具与文档

开源工具：
- [kubecost](https://github.com/kubecost/cost-model): kubecost 应该是目前最优秀的开源成本分析工具了，self-hosted 是免费的，也提供收费的云上版本，值得研究。
- [crane](https://github.com/gocrane/crane): 腾讯开源的一款 Kubernetes 成本优化工具，支持成本报表以及 EHPA 两个功能，才刚开源几个月，目前还比较简陋。
  - [腾讯推出国内首个云原生成本优化开源项目 Crane](https://cloud.tencent.com/developer/article/1960014)
- [kube-opex-analytics](https://github.com/rchakode/kube-opex-analytics): 这个工具只依赖 metrics-server，而且只能做 namespace 级别的成本拆分，比较简陋。

商业服务：
- [spotinst.com](spotinst.com): spotinst 的 Ocean 对 K8s 的成本统计做得比较精细，但是是商业服务，而且必须用它来进行扩缩容。而且它的统计或许还不如 kubecost 精准，因为它不依赖 prometheus 的数据。
    - 集群成本 API： [oceanK8sClusterCosts](https://docs.spot.io/api/#operation/oceanK8sClusterCosts)


文档：

- [Calculating Container Costs - FinOps Fundation](https://www.finops.org/projects/calculating-container-costs/)

### 商业服务 Spotinst.com 介绍

Spotinst 使用机器学习算法帮助客户在上产环境充分利用 AWS 的 Spot 容量，达成云计算成本的节约，同时还能保证服务的 SLA.

Spot 持续对不同操作系统、实例类型、可用区、区域和云提供商的不同容量池进行评分，以便实时做出最明智的决策，决定选择哪些实例进行配置，以及主动重新平衡和替换哪些实例。

- 会持续分析集群的各种计算资源使用情况，自动选择最佳的 Spot/OD/RI 实例进行扩容
- 设置 Spot 比例为 100% 后，会优先扩容 Spot 实例，在 Spot 实例资源紧张时会 fallback 到 OD 实例。
- 可基于 EKS 的多种维度进行成本分析：Namespace/Deployment/StatefulSet/PodLabel...
- 根据 Spot 中断概率以及服务的需求，动态调整实例配置，保障 SLA
- 默认与 Kubernetes 社区的做法一致：检测到 Pending 的容器时执行节点扩容
- 也支持为集群配置 Headroom，它会维护一个空闲缓冲池，确保新扩容的实例可以立即被启动，不需要等待节点扩容（节约了 2mins 时间）。
  - 默认保留 5% 的余量，也就是不论如何扩缩容，总是保留 5% 的可用空间。
- 缩容：Ocean 会主动缩容使用量低的节点，降低集群成本。不过会尊重 PDB 与它的一个 restric-down 标签
- 集群自动分批滚动更新的功能

与开源的 CA 相比，CA 缺少如下功能：

- 成本分析
- 优先扩容 Spot，fallback 到 OD
- 使用机器学习算法进行扩缩容
- CA 底层的 ASG 只建议使用相同大小的实例
- 不支持 headroom 功能
- 集群自动分批滚动更新的功能

Karpenter 相比 CA 多一个 fallback 的功能，另外底层不使用 ASG，会更灵活很多。


### kubecost 介绍

TBD

## 简单的思路

以 1mins 为单位，对每个 Pod，统计其在每个节点上的运行时间，CPU/MEM 消耗，如果 Pod 的资源 requests=limits，那资源消耗就是固定的，更好统计了~

然后结合每个节点的实例类型/可用区（`node.kubernetes.io/instance-type`/`topology.kubernetes.io/region`/`topology.kubernetes.io/zone`）、CPU/MEM 总量（`status.capacity`），就能估算出 Pod 使用了该节点多大比例的资源（节点存储成本很低，这里就直接按 CPU/MEM 计算了）。

持续统计，就能计算出每个 Pod 生命周期内的资源用量变化。

Pod 每次调度的成本=占用节点资源的比例 * 节点单价 * 用时，求和就能得到 Pod 某段时间的总成本了。

再根据 Pod 的 ownership/label，就可以查询出 Namespace/Deployment/DaemonSet/Label 等更上层的资源视图及成本视图。


其他成本：
- 冗余资源的成本：简单起见，这部分成本可以直接按权重拆分给所有 Pod。
- PV 的成本：是固定的，可以直接按空间*使用时长来计算。
- 网络成本：网络成本最主要是跨区/跨域的流量成本，这部分目前还没有很好的办法做拆分。下一节会做简单介绍


## 网络成本统计

>这里不考虑 CDN/Lodbalancer 成本，它们跟 Kubernetes 集群关系不大。

对提供线上服务的云上 Kubernetes 集群而言，网络成本很可能等于甚至超过计算成本。这里面最贵的，是跨区/跨域传输的流量成本。

使用单个可用区风险比较高，资源池也可能不够用，因此我们通常会使用多个可用区，这就导致跨区流量成本激增。

比较好的估算方法是，按 Pod 的 network 监控指标计算出每个服务每天平均的 TX/RX 流量速率，然后使用这个指标对整个集群的流量成本进行拆分。
这样能比较好地完成网络成本的统计。


## 更精确的估算

还有其他方法可以实现更精确的成本估算：

- 不同的业务使用不同的节点组，在节点组层面实现成本隔离
  - 不同的节点组拥有不同的 ec2 tags 与 k8s node labels
  - 这样可以确保各业务的 EKS 成本不会互相影响

