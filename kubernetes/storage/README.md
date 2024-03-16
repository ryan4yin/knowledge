# 分布式数据存储

kubernetes 上的分布式 PV/PVC 存储方案有很多，对于各种云服务商，可以考虑直接使用其提供的 CSI
Provider。

如果你搭建自建，那目前比较被看好的开源方案有这几个：

1. rook
   1. 在 kubernetes 上部署 ceph/edgefs 等分布式文件系统，最成熟的方案是 ceph
   2. 应该是社区最流行的企业级存储解决方案，足够成熟健壮、性能也足够好。
   3. 缺点：虽然安装部署简单，但是 ceph 实际相当复杂，对 ceph 没有深入了解的话，出问题会非常麻烦。
2. OpenEBS
   1. 与 kubernetes 的集成相当简单，使用方便，这也是它流行的原因。
   2. 作为分布式存储的核心能力——高可用、数据安全，它当然也支持多副本同步复制。
3. Longhorn
   1. Rancher 推出的一个轻量级存储解决方案，也支持多副本同步复制。
4. [GlusterFS heketi](https://github.com/heketi/heketi/)
   1. 跟 rook 一样，都是老牌分布式存储方案。
   2. GlusterFS 的 k8s 支持，即 heketi，**基本没人维护了，不建议使用**。

上述 storage on kubernetes 方案的可靠性还有待考察，可以在 homelab 之类的场景玩一玩，但是在没有足够使
用经验之前，不建议上生产环境。目前云上存储首选各云厂商提供的存储方案，企业级的自建存储建议直接连接集
群外部的 Ceph/GlusterFS/OSS.

此外还有构建在 Kubernetes 上的对象存储服务提供商，目前主要是 minio.

## 参考

- [Kubernetes Storage Solutions: Top 4 Solutions & How to Choose](https://cloudian.com/guides/kubernetes-storage/kubernetes-storage-solutions-top-4-solutions-how-to-choose/)
