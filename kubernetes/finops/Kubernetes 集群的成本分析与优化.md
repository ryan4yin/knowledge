# Kubernetes 集群的成本分析 - FinOps

Kubernetes 作为一个多租户的计算平台，我们很自然地会在上面运行多种微服务、CICD、数据分析、机器学习等任务，并且让 Kubernetes 的节点组按需动态扩缩容。

这样就会产生一个需求——如何计算各项计算任务使用了多少资源？花了多少钱？
更近一步的，某个业务团队、某个业务产品花了多少钱？

如果没有资源使用统计及成本统计，整个集群的资源用量就无法拆分，就很难定位到资源占用问题、成本增长问题，换句话说集群的资源池、成本就完全不可控。


## 相关工具与文档

开源工具：
- [kubecost](https://github.com/kubecost/cost-model): 做得比较粗糙，而且没统计数据卷的成本
- [crane](https://github.com/gocrane/crane): 腾讯开源的一款 Kubernetes 成本优化工具，待研究
  - [腾讯推出国内首个云原生成本优化开源项目 Crane](https://cloud.tencent.com/developer/article/1960014)

商业服务：
- [spotisnt.com](spotisnt.com): Ocean 对 K8s 的成本统计做得比较精细，但是是商业服务，而且必须用它来进行扩缩容
    - 集群成本 API： [oceanK8sClusterCosts](https://docs.spot.io/api/#operation/oceanK8sClusterCosts)


文档：

- [Calculating Container Costs - FinOps Fundation](https://www.finops.org/projects/calculating-container-costs/)

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

