# 一、节点数量 vs 节点规格

总体资源相同的集群，可以选择使用少量大规格的节点，也可以用大量小规格的节点。具体的优劣势分析如下。

## 1. 扩缩节点数量

同样的资源总量下，节点数量多的好处：

1. 节点宕机对集群的影响小。
2. Pod 更分散，互相争抢资源的可能性更小。

劣势：

1. 节点之间的通信，通常会比节点内 Pod 之间的通信慢。
2. 增加节点数量，会增大 kubernetes 控制平面的负担。
   1. etcd 的负载会升高，controller manager 的节点扫描会更慢。
   2. 主节点需要使用更高性能的机器。
3. 集群本身需要消耗更多的资源：每个节点的操作系统、kubelet/cAdvisor 等基础组件都会消耗一定资源。
4. 很容易造成无法利用的资源碎片，浪费了资源。
   1. 假设你的 Pod 要求 2G 内存，而一台 4G 内存的节点跑不了两个 2G 的 Pod（系统会有一定资源占用），
      这就造成了 1G 多的内存无法利用，被浪费了。

## 2. 扩缩节点规格

节点数量少、规格大的优势：

1. 更低的运维成本。（云服务商的托管集群除外）
1. 性价比更高：少量高规格物理服务器可能比大量小规格物理服务器更便宜。（不适用于云服务器）
1. 允许更灵活的资源设置：
   1. 可以为 Pod 设置更高的资源请求，而小规格服务器可能无法满足过高的资源请求。
   2. 可以通过超卖资源，更充分地利用上大节点上的资源。而小节点就比较难。
1. 服务器内部的 Pod 网络通信，可能比跨服务器「更快更强」。（猜测）

劣势：

1. 服务器宕机可能会引起集群资源的大幅波动，进而影响服务质量甚至可用性（雪崩）。
1. 节点上的 kubelet/容器运行时等组件的负载会上升，这可能会降低集群的响应速度，甚至使集群不可靠。
   1. kubernetes 官方建
      议[每个节点最多运行 110 个 Pod](https://kubernetes.io/docs/setup/best-practices/cluster-large/)。
1. 如果你超卖了集群资源，可能会遇到一堆 Pod 互相争抢资源的情况，整个大节点上的所有 Pod 都会受影响。

## 混合使用大小规格节点

复杂环境下，可以取长补短，混合使用大小规格的节点来构建集群。

## 二、Pod 数量 vs Pod 规格

Pod 和节点都可以调整规格，也可以自动扩缩容。那 Pod 数量和 Pod 规格，该如何折衷呢？

## 1. 互联网微服务应用的集群规格指南

Web 微服务的 CPU(core)/RAM(GB) 资源比值通常设为 1:2 或者 1:1。

1:2 的微服务通常是大量使用内存做缓存，缓存用得少的微服务，通常就设为 1:1.

常见的 Pod 资源限制：4c/8G，4c/4G。
