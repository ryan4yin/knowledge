# [Pixie](https://github.com/pixie-io/pixie)

Pixie 是基于 eBPF 开发的 Kubernetes 原生应用观测工具。

某种程度上说，它提供如下观测能力：

- 节点及 Pod 的 CPU/MEM/Network 监控：大致相当于 Kubelet 自带的 cAdvisor 指标 + Prometheus
- 服务的 HTTP 请求、报错、超时监控、数据库查询监控：这能力对标 Istio 服务网格监控、cilium-hubble 网络插件层面的监控
- 绘制应用性能火焰图

Pixie 默认只保留 24h 历史数据。

Pixie 最大的特点是**可实时交互**，就是说可以在节点上实时执行 eBPF 脚本，抓取需要的指标并展示。


另一个与之类似的工具是 [mizu](https://github.com/up9inc/mizu)，不过它是基于 netfilter/tcpdump 进行的嗅探，没用上 ebpf，也就不支持实时运行自定义的 eBPF 脚本，因此它的自定义监控能力或者说潜力要比 Pixie 差一些。
