# Kubernetes 中的负载均衡

Kubernetes 集群中有多种流量转发的方法：

1. Service - ClusterIP: 四层负载均衡。群内部使用广泛的一种流量转发方式。
   - 四层负载均衡，主要适合短连接。它均衡不了 tcp 长连接中的七层请求（比如 HTTP/1.1 gRPC 等）。
2. Service - Internal LoadBalancer: 四层/七层的负载均衡。云上环境中的内部负载均衡器，在 LoadBalancer 类型的 Service 上使用注解可配置。
   1. 这种用法貌似很少见？LoadBalancer 主要还是被用于将服务暴露给外部访问。
3. Istio 服务网格：最灵活，性能损耗也最大的一种负载均衡策略。但是它能实现最丰富的负载均衡策略，甚至按比例切分流量。
4. 底层的网络插件，有可能提供更高级的负载均衡功能


## 四层负载均衡和七层负载均衡

主要区别在于：

1. 依据第几层的信息进行转发
   1. 第四层：IP 和 端口号
   2. TLS（也被分到第七层）: TLS Client Hello 中的 Host
   3. 第七层：HTTP 中的 Host/Path 等信息
2. 四层负载均衡不查看七层信息，因此它无法负载均衡一个 TCP 长连接中的 HTTP 请求，也无法负载均衡 gRPC 请求。
   1. 这将造成一 Pod 有难，多 Pod 围观的情况。
   2. 七层负载均衡器只负责做 NAT，客户端和服务端是在 TCP 层直连的。
3. 七层负载均衡会查看七层信息，如果客户端通过一个 TCP 连接发送过来多个 HTTP/2 请求，它能够将请求均衡到多个后端去。
   1. 七层负载均衡器是分别与客户端、服务端建立 TCP 连接，然后解析客户端发来的七层请求，将请求内容均衡发送给后端。
   1. 客户端不是在 TCP 层直连服务端，它只是直连了七层负载均衡器。
4. 四层负载均衡工作在更底层，性能更好，但是能力也更弱。而且客户端直连服务端，服务端抗 DDos 能力弱。
   1. 适合做内部的负载均衡，即客户端可信的情况。
5. 七层负载均衡要处理更多的数据，性能更差。但是：
   1. 它可以在 HTTP 请求粒度上做负载均衡，更智能。
   2. 甚至可以魔改 HTTP 请求内容，或者缓存图片等静态资源（通过 content-type 判断是否静态资源），使用 gzip 等压缩技术，tls 加密等等。
   3. 抗 DDos 能力强，DDos 作为一种TCP(四层)攻击，只会影响负载均衡器自身，影响不到后端服务器。
   4. 

## Kubernetes Service - 服务发现与流量代理

Kubernetes 的内部服务发现是基于 Service + DNS 解析实现的，默认情况下解析到的是一个稳定的虚拟 IP 地址（Service），该虚拟 IP 再通过 kube_proxy 将流量均衡到后端的 Pods 上。

Pod 的 IP 可能会随着 Pod 的重建而变动，但 Service 的 IP 是稳定的。

上面讲到的这个稳定 IP 地址，就是一个 ClusterIP 类型的 Service，这个 Service 根据 kube-proxy 的代理模式的不同，有不同的表现：

1. userspace 模式（最老，性能差，已经彻底弃用了。）
1. iptables  模式（性能适中，当前默认）：通过 Iptables 实现的一个四层（TCP）NAT，kube_proxy 只负责创建 iptables 的 nat 规则，不负责流量转发。
    - 这种模式下流量的负载均衡很差劲。往往造成多个副本时“一 Pod 有难，多 Pod 围观”。
    - 仍然有部分集群在使用这个方案。
1. ipvs 模式（最新、性能与负载均衡兼得）：可通过 `--ipvs-scheduler` 指定负载均衡算法，有多种算法可选，详见 [ipvs-based-in-cluster-load-balancing](https://kubernetes.io/blog/2018/07/09/ipvs-based-in-cluster-load-balancing-deep-dive/)
    - 最推荐的方案，性能最高，而且支持更复杂的负载均衡策略。
    - ipvs 模式下，默认的负载均衡算法是：round robin（rr, 轮询调度）


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
内部负载均衡的主要用途：

   1. 使得 Kubernetes 群集所在的同一虚拟网络中运行的应用程序能够访问 Kubernetes 服务
   2. 支持四层/七层转发与负载均衡，相比普通 Service，它多了一个第七层均衡的功能。
