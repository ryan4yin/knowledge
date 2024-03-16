# MultiCloud 多云管理

> https://github.com/topics/multicloud

随着云计算的发展，为了避免被云服务商绑定（vendor lock-in）从而提高企业的议价能力，也为了提升服务的可
用性（更多 Region/Zones），企业对多云的需求越来越强烈。

此外部分金融政企等行业，企业会有私有化部署的需求，但同时可能也需要用到公有云的一些服务，这推动了私有
云、混合云的发展。为了分到这块蛋糕，各家云服务商近两年都推出了一些核心云服务的私有化部署能力。

这个文件夹的内容，主要就是讲多云管理，即在同时使用多家云服务商的情况下，如何管理云环境的各种资源及权
限、Kubernetes 集群、运行在 Kubernetes 中的微服务等等。

## 多云管理的挑战

- FinOps: 多云成本分析、管控与优化
- 多云网络与 API 网关搭建
  - 多云网络：使用第三方多云解决方案，最好是开源的
  - 基于 DNS + 开源 API Gateway + Istio 多集群服务网格实现多云流量分发
- 跨云应用的发布更新、实例调度、监控、告警、日志、链路追踪
  - 可能的方案：借助 Kubernetes 与其他云原生解决方案实现，比如多集群管理工具 karmada
- 多云的资源管理：从 SRE 角度看借助 terraform/pulumi 来管理多云资源是个不错的方案
- 多云的权限统一管理：基本都是 RBAC，也可以考虑直接使用 terraform/pulumi 来管理

## 参考

- [Kubernetes Everywhere: Lessons Learned From Going Multi-Cloud - Niko Smeds, Grafana Labs](https://www.youtube.com/watch?v=ZY5h8Atc14A)
