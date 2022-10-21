# Kubernetes 集群的成本分析 - FinOps

>主要内容已迁移至：https://thiscute.world/posts/finops-for-kubernetes/

## 从集群伸缩的角度进行成本优化

商业服务：
- [spotinst.com](spotinst.com): spotinst 的 Ocean 对 K8s 的成本统计做得比较精细，但是是商业服务，而且必须用它来进行扩缩容。而且它的统计或许还不如 kubecost 精准，因为它不依赖 prometheus 的数据。

Spotinst 使用机器学习算法帮助客户在上产环境充分利用 AWS 的 Spot 容量，达成云计算成本的节约，同时还能保证服务的 SLA.

Spot 持续对不同操作系统、实例类型、可用区、区域和云提供商的不同容量池进行评分，以便实时做出最明智的决策，决定选择哪些实例进行配置，以及主动重新平衡和替换哪些实例。

- 会持续分析集群的各种计算资源使用情况，自动选择最佳的 Spot/OD/RI 实例进行扩容
- 设置 Spot 比例为 100% 后，会优先扩容 Spot 实例，在 Spot 实例资源紧张时会 fallback 到 OD 实例。
- 可基于 EKS 的多种维度进行成本分析：Namespace/Deployment/StatefulSet/PodLabel...
- **根据 Spot 中断概率以及服务的需求，动态调整实例配置，保障 SLA**
- 默认与 Kubernetes 社区的做法一致：检测到 Pending 的容器时执行节点扩容
- 在扩容节点长时间未响应时，删除 Node 并尝试重新选择子网执行扩容操作
  - 这个在新加子网配置有问题时会比较有用，可避免新扩容的 Node 全卡在问题子网，导致集群资源不足。
  - karpenter 没这功能，新扩容的 Node 如果在问题子网，就会全部卡住，无法 ready...
- 也支持为集群配置 Headroom，它会**维护一个空闲缓冲池**，确保新扩容的实例可以立即被启动，不需要等待节点扩容（节约了 2mins 时间）。
  - 默认保留 5% 的余量，也就是不论如何扩缩容，总是保留 5% 的可用空间。
- 缩容：Ocean 会**主动缩容使用量低的节点，降低集群成本**。不过会尊重 PDB 与它的一个 restric-down 标签
- 集群自动分批滚动更新的功能

与开源的 CA 相比，CA 缺少如下功能：

- **成本分析，这个需要靠 kubecost 补足**
- **优先扩容 Spot，fallback 到 OD**
- **无法根据 requests 选择合适的实例类型**
  - CA 假定每个 nodegroup 中所有的实例类型大小都一致，默认随机选择 nodegroup 进行扩缩容。
- **不支持 asg 的 warmpool 功能**，提前申请 OD 机器并关机，以实现快速扩容。
- 不支持使用机器学习算法进行扩缩容
- 不支持集群自动分批滚动更新的功能

Karpenter 相比 Spotinst 缺少了如下功能：

- 成本分析
- **不支持预留一定空闲资源**
- 不支持**主动缩容使用量低的节点**
- **不支持亲和性反亲和性**，推荐使用 topologySpreadConstraint
- 不支持使用机器学习算法进行扩缩容
- 不支持集群自动分批滚动更新的功能，但是可以写个脚本自动 delete 节点实现，很简单

总的来说目前 spotinst 功能仍然是最强的，而开源的 karpenter/cluster-autosclaer 各有优缺点。

