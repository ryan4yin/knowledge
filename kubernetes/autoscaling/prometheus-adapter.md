# [Prometheus Apdaptor](https://github.com/kubernetes-sigs/prometheus-adapter) - Prometheus 的 HPA Custom Metrics API 适配器

Prometheus Apdaptor 实现了 Kubernetes 的 Custom Metrics、External Metrics 等 API，通过它，你能将 Prometheus 的指标用于 HPA 进行 Pod 扩缩容。

## 为 Deployment 设置基于 QPS 的扩缩容（使用 istio sidecar 提供的指标）

直接在 `Prometheus Apdaptor` 上定义好服务 QPS 的自定义指标，详见 [prometheus-adapter 官方文档](https://github.com/kubernetes-sigs/prometheus-adapter/blob/master/docs/config-walkthrough.md)

一个 `rules.yaml` 的示例如下：
```yaml
# 适用于 istio 代理的 HTTP, HTTP/2 和 GRPC 请求
# 统计出单个 pod 的 QPS
rules:
- seriesQuery: 'istio_requests_total{destination_workload_namespace!="",destination_workload!="", destination_app!=""}'
  resources:
    overrides:
      destination_workload_namespace: {resource: "namespace"}
      destination_workload: {resource: "pod"}
  name:
    matches: "^(.*)_total"
    as: "${1}_per_second"
  # 下面参数中的 `<<xxx>>` 会被根据前面的设置，自动推导出来
  metricsQuery: 'sum(rate(<<.Series>>{<<.LabelMatchers>>}[2m])) by (<<.GroupBy>>)'
```

上面的配置貌似需要重启 prometheus-adapter 才能生效。

然后添加 HPA 配置：

```yaml
apiVersion: autoscaling/v2beta2
kind: HorizontalPodAutoscaler
metadata:
  name: httpserver
  namespace: httpserver
spec:
  minReplicas: 1
  maxReplicas: 1000
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: httpserver
  metrics:
  - type: Pods
    pods:
      metric:
        name: istio_requests_per_second
      target:
        averageValue: 350  # QPS 的期望平均值
        type: AverageValue
```

接下来可以压测一下，验证效果。
