# Kubernetes CHANGELOG

> CHANGELOG: https://github.com/kubernetes/kubernetes/tree/master/CHANGELOG

> 各版本的 API 不兼容变更：https://kubernetes.io/docs/reference/using-api/deprecation-guide

> 通常所有 beta/stable 特性都是默认启用的，而 alpha 则需要手动设定控制面参数来打开。

此外对于相应的云厂商发行版，可能还存在一些不一样的点，比如权限验证、树内插件的移除等等，请参考对应云
厂商的相关文档，如：

- [AWS EKS Versions](https://docs.aws.amazon.com/zh_cn/eks/latest/userguide/kubernetes-versions.html)

## [1.16](https://github.com/kubernetes/kubernetes/blob/master/CHANGELOG/CHANGELOG-1.16.md#whats-new-major-themes)

- server side apply 进入 beta 并默认开启
  - 这会导致 `kubectl get po` 多出一堆的 `metadata.managedFields` 数据，它是 server side apply 自动
    生成的
  - 要避免输出没啥用的 managedFields 信息， 可使用 [yq](https://github.com/mikefarah/yq)，或者使用
    `kubectl 1.21+`:
    - `kubectl get po xxx -o yaml | yq eval 'del (.metadata.managedFields)' -`
- 不兼容的 API 变更:
  - All resources under `apps/v1beta1` and `apps/v1beta2` - use `apps/v1` instead
  - daemonsets, deployments, replicasets resources under `extensions/v1beta1` - use `apps/v1`
    instead
  - networkpolicies resources under `extensions/v1beta1` - use networking.k8s.`io/v1` instead
  - podsecuritypolicies resources under `extensions/v1beta1` - use `policy/v1beta1` instead

## [1.18](https://github.com/kubernetes/kubernetes/blob/master/CHANGELOG/CHANGELOG-1.18.md#whats-new-major-themes)

- 添加 IngressClass，Ingress 资源定义更新
  - 添加字段 `spec.ingressClassName`
  - path 的定义中，添加字段 `pathType`，可选 `Exact`/`Prefix`/`ImplementationSpecific`
- [alpha] 添加 `kubectl alpha debug` 命令

## [1.19](https://github.com/kubernetes/kubernetes/blob/master/CHANGELOG/CHANGELOG-1.19.md#whats-new-major-themes)

- [alpha] `kubectl alpha debug` 现在支持多种调试方式
  - Troubleshoot workloads that crash on startup by creating a copy of the pod that uses a different
    container image or command.
  - Troubleshoot distroless containers by adding a new container with debugging tools, either in a
    new copy of the pod or using an ephemeral container.
    ([Ephemeral containers](https://github.com/kubernetes/enhancements/tree/master/keps/sig-node/277-ephemeral-containers)
    are an alpha feature that are not enabled by default.)
  - Troubleshoot on a node by creating a container running in the host namespaces and with access to
    the host’s filesystem.
- 默认启动 `EndpointSlices`
- `Ingress` GA
- `securityContext.seccompProfile` GA
- [alpha]
  [generic ephemeral inline volumes](https://github.com/kubernetes/enhancements/tree/master/keps/sig-storage/1698-generic-ephemeral-volumes)，
  支持使用 `storageClass` 创建临时存储卷（以前只能使用 `emptyDir`，它实际是使用主机的存储空间，导致
  存储卷大小受限）
- [beta] 不可变的 Secrets/Configmap
- windows 容器支持进入 beta

## [1.20](https://github.com/kubernetes/kubernetes/blob/master/CHANGELOG/CHANGELOG-1.20.md#whats-new-major-themes)

- CSI Volume Snapshot GA
- [alpha] Node `GracefulNodeShutdown`
- `kubectl debug` 进入 beta

## [1.21](https://github.com/kubernetes/kubernetes/blob/master/CHANGELOG/CHANGELOG-1.21.md#whats-new-major-themes)

- `kubectl` 现在默认不再输出烦人的 manageFields 信息
- Immutable Secrets and ConfigMaps GA
- Generic Ephemeral Volumes 进入 beta 并默认启用
- Kubelet 节点的 GracefulNodeShutdown 特性进入 beta 并默认开启
- [alpha] 新增 `TopologyAwareHints` 功能（取代了之前同为 alpha 的 `Topology-aware traffic routing`）
- The PodSecurityPolicy API is deprecated in 1.21, and will no longer be served starting in 1.25.
- CrossNamespacePodAffinity
- PodAffinityTerm 添加 `namespaceSelector` 属性
- EndpointSlices GA
- [alpha] 新增注解 `controller.kubernetes.io/pod-deletion-cost`，同一个 ReplicaSet 中，该值最低的
  Pod 将会最先被删除
- 优化 ReplicaSet 的缩容顺序：[#99212](https://github.com/kubernetes/kubernetes/pull/99212)
  - 大致可以理解为，越晚被扩容出来的节点，会最先被删除
- PodDisruptionBudget GA 并进入 API `policy/v1`
  - 新增特性：空的 Selector 将选中名字空间下的所有 Pods.
- 可使用 `kubectl.kubernetes.io/default-container` 注解来标识默认容器
- 可使用 `kubectl.kubernetes.io/default-exec-container` 指定 `kubectl exec` 默认登录的容器
- `IPv6Dualstack` 进入 Beta 并默认启用

## [1.22](https://github.com/kubernetes/kubernetes/blob/master/CHANGELOG/CHANGELOG-1.22.md#whats-new-major-themes)

- 移除 API: [](https://kubernetes.io/docs/reference/using-api/deprecation-guide/#v1-22)
  - 如下这些资源都彻底移除了对 v1beta1 的支持，需要改成 v1
    - ValidatingWebhookConfiguration,
    - MutatingWebhookConfiguration,
    - CustomResourceDefinition,
    - APIService,
    - TokenReview,
    - SubjectAccessReview,
    - CertificateSigningRequest,
    - Lease,
    - Ingress,
    - IngressClass
- 自 April 23, 2021 开始，k8s 的发布周期从 4 个版本/年改为 3 个版本/年
- Server-side Apply GA
- [alpha] `RootlessControlPlane` 运行在非 root 环境下运行 kubeadm
- etcd 升级到 3.5.0
- [alpha] K8s 节点允许开启 swap 交换空间
- [alpha] 提升内存资源的服务质量：可在内存资源争用时提高 pod 和 node 的可用性
  - k8s 一直使用 cgroups v1 (`cpu_shares`/`memory.limit_in_bytes`)来限制 cpu/memory，但是对于
    `Guaranteed` 的 Pods 而言，内存并不能完全预留，资源竞争总是有可能发生的。
  - 此特性改用 cgroups v2 来控制内存分配以及隔离

## [1.23](https://github.com/kubernetes/kubernetes/blob/master/CHANGELOG/CHANGELOG-1.23.md#whats-new-major-themes)

- [beta] `TopologyAwareHints` 功能升级到 Beta
  - 此功能能使流量尽量在同一可用区内路由，能帮助减少跨区流量。
- IPv4/IPv6 Dual-stack Networking GA
- HorizontalPodAutoscaler v2 GA
  - autoscaling/v2beta2 被标记为弃用
- Generic Ephemeral Volume GA
- 旨在替代 PSP 的
  [Pod Security Admission](https://kubernetes.io/docs/concepts/security/pod-security-admission/) 进
  入 Beta
- K8s 现在默认使用 Container Runtime Interface (CRI) v1 API
- Structured logging 进入 Beta
  - json 日志默认写到 stderr 而不是 stdout!
- 简化 Scheduler 的「多插入点」插件配置 `MultiPoint`
- `rbac.authorization.k8s.io/v1alpha1` 被移除，请改用`rbac.authorization.k8s.io/v1`
- `scheduling.k8s.io/v1alpha1` 被移除，需要改用 `scheduling.k8s.io/v1`

## [1.24](https://github.com/kubernetes/kubernetes/blob/master/CHANGELOG/CHANGELOG-1.24.md#whats-new-major-themes)

- 彻底移除 Dockershim，不再支持使用 Docker 作为容器运行时。
  - 请改用目前已经广泛使用的 containerd，或者面向未来的 cri
  - 迁移到 containerd 的主要难题
    - 使用了 docker in docker：请改用 buildah/buildkit 实现镜像构建
    - 挂载了宿主机 `docker.socket` 等：请改用相关组件提供的其他方案，比如 argo-workflows 官方文档
    - GPU 等特殊硬件的支持
    - docker 日志插件：containerd 开始日志全部由 kubelet 接管，如果做了自定义的日志插件，建议改用
      fluentbit 等流行社区组件
- `client.authentication.k8s.io/v1alpha1` 被移除，它影响 kubeconfig 的配置方式，如果使用了此版本的
  kubeconfig，需要升级到 `v1`

## [1.25](https://github.com/kubernetes/kubernetes/blob/master/CHANGELOG/CHANGELOG-1.25.md#whats-new-major-themes)

- PodSecurityPolicy 被移除，替代品 Pod Security Admission GA
- policy/v1beta1 被移除，PodDisruptionBudget 需要改用 policy/v1
- Ephemeral Containers GA
- cgroups v2 的支持 GA

## [1.26](https://github.com/kubernetes/kubernetes/blob/master/CHANGELOG/CHANGELOG-1.26.md#changelog-since-v1250)

- autoscaling/v2beta2 被移除，HorizontalPodAutoscaler 需要改用 autoscaling/v2
  - 但是 kubectl 仍然默认使用 autoscaling/v2beta2，所以需要手动指定版本号
    `kubectl get hpa.v2.autoscaling` 才能看到正确的 HPA 的信息
- flowcontrol.apiserver.k8s.io/v1beta1 被移除，需要改用 flowcontrol.apiserver.k8s.io/v1beta3

## [1.27](https://github.com/kubernetes/kubernetes/blob/master/CHANGELOG/CHANGELOG-1.27.md#changelog-since-v1260)

- 彻底移除注解 `seccomp.security.alpha.kubernetes.io/pod` 与
  `container.seccomp.security.alpha.kubernetes.io`，需要改用 `securityContext.seccompProfile`
- 废弃 `SecurityContextDeny`
- kubectl 默认使用 `autoscaling/v2`

## [1.28](https://github.com/kubernetes/kubernetes/blob/master/CHANGELOG/CHANGELOG-1.28.md#changelog-since-v1270)

- 支持从非优雅的节点关闭中恢复
- 在 Linux 上支持交换空间（Beta）
- 新特性 `SidecarContainers` 进入 Alpha
- [PodFailurePolicy](https://kubernetes.io/docs/tasks/job/pod-failure-policy/) 进入 Beta

## [1.29](https://github.com/kubernetes/kubernetes/blob/master/CHANGELOG/CHANGELOG-1.29.md#changelog-since-v1280)

- `SidecarContainers` 进入 Beta 并默认启用
- 以及其他一堆特性完全进入 GA，删除相关的 feature gate
  - CSIMigrationvSphere
  - ProbeTerminationGracePeriod
  - TopologyManager
  - CronJobTimeZone
  - DownwardAPIHugePages
  - GRPCContainerProbe
  - ReadWriteOncePod
  - ...
- kubelet 一批监控指标进入 GA


## [1.30](https://github.com/kubernetes/kubernetes/blob/master/CHANGELOG/CHANGELOG-1.30.md#changelog-since-v1290)

- AppArmor profiles can now be configured through fields on the `PodSecurityContext` and container `SecurityContext`. 
- 如下特性进入 GA
  - ValidatingAdmissionPolicy
  - AdmissionWebhookMatchConditions
- 新增 Alpha 特性
  - ServiceTrafficDistribution: 给 Service 添加 `spec.trafficDistribution` 参数用于控制流量分发配置

