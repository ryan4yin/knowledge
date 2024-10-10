# Kubernetes Service - 服务发现与流量代理

Kubernetes 的内部服务发现是基于 Service + DNS 解析实现的，默认情况下解析到的是一个稳定的虚拟 IP 地址
（Service），该虚拟 IP 再通过 kube_proxy 将流量均衡到后端的 Pods 上。

Pod 的 IP 可能会随着 Pod 的重建而变动，但 Service 的 IP 是稳定的。

上面讲到的这个稳定 IP 地址，就是一个 ClusterIP 类型的 Service，这个 Service 根据 kube-proxy 的代理模
式的不同，有不同的表现：

1. userspace 模式（最老，性能差，已经彻底弃用了。）
1. iptables 模式（性能适中，当前默认）：通过 Iptables 实现的一个四层（TCP）NAT，kube_proxy 只负责创
   建 iptables 的 nat 规则，不负责流量转发。
   - 这种模式下流量的负载均衡很差劲。往往造成多个副本时“一 Pod 有难，多 Pod 围观”。
   - 仍然有部分集群在使用这个方案。
1. ipvs 模式（最新、性能与负载均衡兼得）：可通过 `--ipvs-scheduler` 指定负载均衡算法，有多种算法可
   选，详见
   [ipvs-based-in-cluster-load-balancing](https://kubernetes.io/blog/2018/07/09/ipvs-based-in-cluster-load-balancing-deep-dive/)
   - 最推荐的方案，性能最高，而且支持更复杂的负载均衡策略。
   - ipvs 模式下，默认的负载均衡算法是：round robin（rr, 轮询调度）
   - ipvs 模式底层用的是 IPVS NAT 模式进行 service 端口映射
     - 这种模式下，被访问的服务看到的 srcAddr 仍然是客户端 ip，而不是 service 的 vip. 详见
       [ipvs 的几种模式](https://www.cnblogs.com/skyflask/p/7500899.html)

## Service 的分类

Kubernetes Service 有多种类型可选:

1. ClusterIP: 集群内的 Service，上面介绍的三种代理模式就是指这种类型的 Service。
   1. 可以通过指定 Cluster IP（spec.clusterIP）的值为 "None" 来创建 Headless Service。
   2. Headless 的 Service 只提供 DNS SRV 解析，不创建 VIP 及流量代理。
2. NodePort: 通过每个 Node 上的 IP 和静态端口（NodePort）将服务暴露到集群外部网络。 同时它也有
   ClusterIP
   1. 它分配的端口号范围受限于 kube-apiserver 的启动参数 `--service-node-port-range`，详见
      [kubernetes 如何将服务暴露到外部](./将服务暴露到外部.md)
3. LoadBalancer: 使用云提供商的负载局衡器，将服务暴露到外部网络，每个 LoadBalancer 都会分配到一个外
   部 IP 地址。
   1. LoadBalancer 有外部 IP 地址，后端通过 NodePort 将均衡转发到集群内部。
   2. kubernetes 官方没有给出 LoadBalancer 的实现方式。每个云服务商都提供了自己私有的实现。
   3. 开源的 LoadBalancer 实现：[kubernetes 如何将服务暴露到外部](./将服务暴露到外部.md)
4. ExternalName: 通过返回 CNAME 和它的值，可以将服务映射到 externalName 字段的内容（例如，
   foo.bar.example.com）。
   1. 这类 Service 只是单纯地添加了一条内部 DNS CNAME 解析。没有
   2. 因为 ExternalName 使用的是 DNS CNAME 记录，它要求值必须是合法的 DNS 名称，**不支持 ip 地址**！
   3. 如果需要针对外部 ip 做负载均衡，请参见下一小节

上面提到的 LoadBalancer 主要是做外部负载均衡，但是各大云厂商都提供一类注解，可以单纯创建一个内部负载
均衡。内部负载均衡的主要用途：

1.  使得 Kubernetes 群集所在的同一虚拟网络中运行的应用程序能够访问 Kubernetes 服务
2.  支持四层/七层转发与负载均衡，相比普通 Service，它多了一个第七层均衡的功能。

## 手动维护 Service 的 endpoints

> 官方文档:
> [Services without selectors](https://kubernetes.io/docs/concepts/services-networking/service/#services-without-selectors)

前问提到过 ExternalName 类型的 Service 可以在集群中为外部域名创建一个 CNAME 记录，但是不支持 ip 地
址。

那如果你就是需要用 K8s Service 来对部分已知的外部 ip 地址做负载均衡呢？

创建一个不带 label selector 的 service，以及一个同名的 endpoints，手动维护 endpoints 中的 ip 列表就
行。

```yaml
apiVersion: v1
kind: Service
metadata:
  name: my-service
spec:
  ports:
    - protocol: TCP
      port: 80
      targetPort: 9376
---
apiVersion: v1
kind: Endpoints
metadata:
  name: my-service
subsets:
  - addresses:
      - ip: 192.0.2.42
    ports:
      - port: 9376
```

这样，在集群内访问 `my-service:9376`，会被 Service 转发到 `182.0.2.42:9376`

## 透传客户端 IP 地址

对于 Ingress 这类 L7 Proxy 我们通常不担心客户端 IP 丢失的问题，`X-Forwarded-For` 这个 Header 会帮我
们记录客户端的 IP 地址。

但 Service 是 L4 Proxy，在使用云厂商的 LoadBalancer 服务时，有这几种方法可以透传客户端的 IP 地址：

1. 设置 `spec.externalTrafficPolicy: Local`，这样流量不会跨 Node 传输，能保证 Pod 看到的是真实的客户
   端 IP 地址。
   - 缺点是可能导致负载不均衡，在每个 Node 上都有一个 Pod 时比较适用。
1. LoadBalancer 与后端 Pod 都启用 PROXY protocol 协议，通过该协议将客户端 IP 透传到 Pod.
