
# Kubernetes Service - 服务发现与流量代理

Kubernetes 的内部服务发现是基于 Service + DNS 解析实现的，默认情况下解析到的是一个稳定的虚拟 IP 地址（Service），该虚拟 IP 再通过 kube_proxy 将流量均衡到后端的 Pods 上。

Pod 的 IP 可能会随着 Pod 的重建而变动，但 Service 的 IP 是稳定的。

上面讲到的这个稳定 IP 地址，就是一个 ClusterIP 类型的 Service，这个 Service 根据 kube-proxy 的代理模式的不同，有不同的表现：

1. userspace 模式（最老，性能差，已经彻底弃用了。）
1. iptables  模式（性能适中，当前默认）：通过 Iptables 实现的一个四层（TCP）NAT，kube_proxy 只负责创建 iptables 的 nat 规则，不负责流量转发。
    - 这种模式下流量的负载均衡很差劲。往往造成多个副本时“一 Pod 有难，多 Pod 围观”。
    - 仍然有部分集群在使用这个方案。
1. ipvs 模式（最新、性能与负载均衡兼得）：可通过 `--ipvs-scheduler` 指定负载均衡算法，有多种算法可选，详见 [ipvs-based-in-cluster-load-balancing](https://kubernetes.io/blog/2018/07/09/ipvs-based-in-cluster-load-balancing-deep-dive/)
    - 最推荐的方案，性能最高，而且支持更复杂的负载均衡策略。


## LoadBalancer Service

Kubernetes Service 有多种类型可选:

1. ClusterIP: 集群内的 Service，上面介绍的三种代理模式就是指这种类型的 Service。 
   1. 可以通过指定 Cluster IP（spec.clusterIP）的值为 "None" 来创建 Headless Service。
   2. Headless 的 Service 只提供 DNS SRV 解析，不创建 VIP 及流量代理。
2. NodePort: 通过每个 Node 上的 IP 和静态端口（NodePort）暴露服务。 同时它也有 ClusterIP
3. LoadBalancer: 使用云提供商的负载局衡器，将服务暴露到外部网络，每个 LoadBalancer 都会分配到一个外部 IP 地址。
   1. LoadBalancer 有外部 IP 地址，后端通过 NodePort 将均衡转发到集群内部。
   2. kubernetes 官方没有给出 LoadBalancer 的实现方式。每个云服务商都提供了自己私有的实现。
   3. 开源的 LoadBalancer 实现：[kubernetes 如何将服务暴露到外部](./kubernetes%20如何将服务暴露到外部.md)
4. ExternalName: 通过返回 CNAME 和它的值，可以将服务映射到 externalName 字段的内容（例如， foo.bar.example.com）。 
   1. 这类 Service 只是单纯地添加了一条内部 DNS CNAME 解析。

上面提到的 LoadBalancer 主要是做外部负载均衡，但是各大云厂商都提供一类注解，可以单纯创建一个内部负载均衡。
内部负载均衡的主要用途是：使得 Kubernetes 群集所在的同一虚拟网络中运行的应用程序能够访问 Kubernetes 服务,同时也支持配置更高级的负载均衡策略。
