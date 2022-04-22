# 集群监控指标 - metrics

- metrics-server
- kube-state-metrics
- istio metrics
- 应用程序自身的 metrics

而指标数据库，目前云原生领域 Prometheus 的应用最为广泛。其他类似的产品也基本都支持 PromQL.

## 集群监控方案

1. kubelet(cAdvisor) + metrics-server +  kubernetes+dashboard
   1. 支持监控节点、各项 k8s 资源，但是只能看近期的指标，而且没有整个集群的利用率等信息。
2. kubelet(cAdvisor) + metrics-server + prometheus + grafana
   1. 支持监控节点、各项 k8s 资源非常详细的信息，也支持长期指标
   2. 但是如果集群节点数非常动态（比如计算专用的集群），p8s 需要很高的配置才能顶住高峰期那么大的节点数，而低峰期 p8s 却无法缩容。这是一个问题。
3. kubelet(cAdvisor) + metrics-server + istio + prometheus
   1. 添加了 istio 服务网格后，除了 istio 的负载均衡、故障注入等能力外，它还提供了服务网格上的 HTTP/gRPC 等协议的观测能力。
4. kubelet(cAdvisor) + cilium + hubble + prometheus
   1. 同样能提供集群内的网络观测能力，但是比服务网格的方案更轻量。
   2. 依赖于 cilium 网络插件，底层需要较大变动，好处是基于 ebpf 的 cilium 性能很高，值得投入。
   3. 另外它仅提供观测能力，无法提供服务网格在负载均衡、故障注入等方面的对等能力。
5. pixie
   1. 与 cilium/istio 相比，它的侵入性最小，但是能提供**最强大**的的集群内流量观测能力
   2. 支持一键查看 Pod/Node 的 CPU 火焰图、JVM 性能分析、HTTP 指标、
   3. 但是目前部署测试的感觉是，如果自建 Pixie Cloud，那组件会比较多，跑了一堆的容器，可能会提升维护难度。
