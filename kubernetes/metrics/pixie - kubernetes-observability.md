# Pixie

Pixie 是基于 eBPF 开发的 Kubernetes 原生应用观测工具。

某种程度上说，它提供如下观测能力：

- 节点及 Pod 的 CPU/MEM/Network 监控：大致相当于 Kubelet 自带的 cAdvisor 指标 + Prometheus
- 服务的 HTTP 请求、报错、超时监控、数据库查询监控：这能力对标 Istio 服务网格监控、cilium-hubble 网络插件层面的监控
- 绘制应用性能火焰图

