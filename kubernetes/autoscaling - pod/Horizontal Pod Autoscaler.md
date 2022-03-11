# Horizontal Pod Autoscaler - Pod 自动扩缩容

Kubernetes 的 HPA 可以通过 CPU/RAM 进行 Pod 伸缩，另外也支持自定义指标（如每秒请求数等）。

大部分内容已迁移至博客：[二、服务的伸缩配置 - HPA](https://thiscute.world/posts/kubernetes-best-practices/#k8s-hpa)

## 指标服务器

- [metrics-server](../metrics/metrics-server.md)

## 如何设置使用 HPA 进行基于 QPS 的扩缩容

HPA 默认只支持基于 CPU 的扩缩容，这满足了大部分服务的需要，也足够简单可靠。
但是基于 QPS 扩缩容，也是一个比较常见的需求。

要支持基于 QPS 的扩缩容策略，需要如下几组件：
- 指标数据库 Prometheus
- QPS 指标：要有个 Metrics API 能够提供服务的 QPS 信息给 Prometheus 抓取
  - 可以由服务自身暴露 `metrics` 接口提供 QPS 指标，也可以通过注入 Istio Sidecar 实现
- Prometheus 的 Custom Metrics API 适配器
- 在 HPA 中通过添加好的 QPS Custom Metrics 进行扩缩容

其中的「Prometheus 的 Custom Metrics API 适配器」目前有两个选项：

- [KEDA](./KEDA.md) KEDA 通过它的 CRD 定义伸缩对象，然后自动生成并管理对应的 HPA + Metrics Server
  - 使用起来感觉很直观、方便，设计得很好。
  - 支持非常多的外部数据源，其中就包括 Prometheus
- [Prometheus Apdaptor](./prometheus-adapter.md): kubernetes 社区的方案，但是感觉没 KEDA 好用
  - 感觉没 KEDA 好用
  - 只支持 Prometheus

具体的 QPS 扩缩容设置方法，都在上面两个方案的链接里，请点进去看...

## 参考

- [Pod 水平自动伸缩 - Kubernetes Docs](https://kubernetes.io/zh/docs/tasks/run-application/horizontal-pod-autoscale/)
- [Horizontal Pod Autoscaler演练 - Kubernetes Docs](https://kubernetes.io/zh/docs/tasks/run-application/horizontal-pod-autoscale-walkthrough/)

