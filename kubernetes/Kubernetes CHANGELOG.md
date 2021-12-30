# Kubernetes CHANGELOG

>CHANGELOG: https://github.com/kubernetes/kubernetes/tree/master/CHANGELOG

>各版本的 API 不兼容变更：https://kubernetes.io/docs/reference/using-api/deprecation-guide

>通常所有 beta/stable 特性都是默认启用的，而 alpha 则需要手动设定控制面参数来打开。

## [1.16](https://github.com/kubernetes/kubernetes/blob/master/CHANGELOG/CHANGELOG-1.16.md#whats-new-major-themes)

- server side apply 进入 beta 并默认开启
  - 这会导致 `kubectl get po` 多出一堆的 `metadata.managedFields` 数据，它是 server side apply 自动生成的
  - 要避免输出没啥用的 managedFields 信息， 可使用 yq，或者使用 `kubectl 1.21+`:
    - `kubectl get po xxx -o yaml | yq eval 'del (.metadata.managedFields)' -`
- 不兼容的 API 变更:
    - All resources under `apps/v1beta1` and `apps/v1beta2` - use `apps/v1` instead
    - daemonsets, deployments, replicasets resources under `extensions/v1beta1` - use `apps/v1` instead
    - networkpolicies resources under `extensions/v1beta1` - use networking.k8s.`io/v1` instead
    - podsecuritypolicies resources under `extensions/v1beta1` - use `policy/v1beta1` instead

## [1.18](https://github.com/kubernetes/kubernetes/blob/master/CHANGELOG/CHANGELOG-1.18.md#whats-new-major-themes)

- 添加 IngressClass，Ingress 资源定义更新
  - 添加字段 `spec.ingressClassName`
  - path 的定义中，添加字段 `pathType`，可选 `Excat`/`Prefix`/`ImplementationSpecific`
- [alpha] 添加 `kubectl alpha debug` 命令


## [1.19](https://github.com/kubernetes/kubernetes/blob/master/CHANGELOG/CHANGELOG-1.19.md#whats-new-major-themes)

- [alpha] `kubectl alpha debug` 现在支持多种调试方式
  - Troubleshoot workloads that crash on startup by creating a copy of the pod that uses a different container image or command. 
  - Troubleshoot distroless containers by adding a new container with debugging tools, either in a new copy of the pod or using an ephemeral container. ([Ephemeral containers](https://github.com/kubernetes/enhancements/tree/master/keps/sig-node/277-ephemeral-containers) are an alpha feature that are not enabled by default.) 
  - Troubleshoot on a node by creating a container running in the host namespaces and with access to the host’s filesystem. 
- 默认启动 `EndpointSlices`
- `Ingress` GA
- `securityContext.seccompProfile` GA
- [alpha] [generic ephemeral inline volumes](https://github.com/kubernetes/enhancements/tree/master/keps/sig-storage/1698-generic-ephemeral-volumes)，支持使用 `storageClass` 创建临时存储卷（以前只能使用 `emptyDir`，它实际是使用主机的存储空间，导致存储卷大小受限）
- [beta] 不可变的 Secrets/Configmap
- windows 容器支持进入 beta

## [1.20](https://github.com/kubernetes/kubernetes/blob/master/CHANGELOG/CHANGELOG-1.20.md#whats-new-major-themes)

- CSI Volume Snapshot GA
- [alpha] Node `GracefulNodeShutdown`
- `kubectl debug` 进入 beta


## [1.21](https://github.com/kubernetes/kubernetes/blob/master/CHANGELOG/CHANGELOG-1.21.md#whats-new-major-themes)

- `kubectl` 现在默认不再输出烦人的 manageFileds 信息
- Immutable Secrets and ConfigMaps GA
- Generic Ephemeral Volumes 进入 beta 并默认启用
- Kubelet 节点的 GracefulNodeShutdown 特性进入 beta 并默认开启
- [alpha] 新增 `TopologyAwareHints` 功能（取代了之前同为 alpha 的 `Topology-aware traffic routing`）
- The PodSecurityPolicy API is deprecated in 1.21, and will no longer be served starting in 1.25.
- CrossNamespacePodAffinity
- PodAffinityTerm 添加 `namespaceSelector` 属性
- EndpointSlices GA
- [alpha] 新增注解 `controller.kubernetes.io/pod-deletion-cost`，同一个 ReplicaSet 中，该值最低的 Pod 将会最先被删除
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
  - k8s 一直使用 cgroups v1 (`cpu_shares`/`memory.limit_in_bytes`)来限制 cpu/memory，但是对于 `Guaranteed` 的 Pods 而言，内存并不能完全预留，资源竞争总是有可能发生的。
  - 此特性改用 cgroups v2 来控制内存分配以及隔离


## [1.23](https://github.com/kubernetes/kubernetes/blob/master/CHANGELOG/CHANGELOG-1.23.md#whats-new-major-themes)


- IPv4/IPv6 Dual-stack Networking GA
- HorizontalPodAutoscaler v2 GA
- Generic Ephemeral Volume GA
- 旨在替代 PSP 的 [Pod Security Admission](https://kubernetes.io/docs/concepts/security/pod-security-admission/) 进入 Beta
- K8s 现在默认使用 Container Runtime Interface (CRI) v1 API
- Structured logging 进入 Beta
  - json 日志默认写到 stderr 而不是 stdout!
- 简化 Scheduler 的「多插入点」插件配置 `MultiPoint`
- `rbac.authorization.k8s.io/v1alpha1` 被移除，请改用`rbac.authorization.k8s.io/v1`
- `scheduling.k8s.io/v1alpha1` 被移除，需要改用 `scheduling.k8s.io/v1`

## [1.24](https://github.com/kubernetes/kubernetes/blob/master/CHANGELOG/CHANGELOG-1.24.md#whats-new-major-themes)

- 彻底移除 Dockershim，不再支持使用 Docker 作为容器运行时。
  - 请改用目前已经广泛使用的 containerd，或者面向未来的 cri


