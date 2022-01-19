# Prometheus 配置


## 一、「重打标签」配置 - relabel_config/metric_relabel_config

>[relabel_config - prometheus docs](https://prometheus.io/docs/prometheus/latest/configuration/configuration/#relabel_config)

「重打标签」是 Prometheus 处理指标标签的主要手段。在 serviceMonitor/podMonitor 及 prometheus.yml 中都可以看到它的存在。
虽然名为「重打标签」，但实际上对「target」及「标签(label)」的增删改，都是可以通过它来进行的。

relabel_config: 在指标被采集前进行处理，假入某个标签被 drop，那么它根本不会被采集。
metric_relabel_config: 在指标被采集完成，还没有入库前，对指标进行处理。

根据「及早处理」的原则，应该尽量使用 relabel_config，不得已时才使用 metric_relabel_config。


### 1.1 Kubernetes 自动发现 targets

在 kubernetes 配置中，可以通过 relabel_config 来配置只从所有 pod 的 9091 端口抓取指标：

```yaml
    - job_name: 'prod-apisix'
      metrics_path: /apisix/prometheus/metrics
      kubernetes_sd_configs:
      - role: pod
        namespaces:
          names:
          - prod
        selectors:
          - role: pod
            label: "app.kubernetes.io/name=apisix"
      relabel_configs:
      - action: keep
        # 只从 9091 端口抓取 apisix 指标，忽略 pod 的其他端口
        source_labels: [__meta_kubernetes_pod_container_port_number]
        regex: "9091"
      - action: labelmap
        regex: __meta_kubernetes_service_label_(.+)
      - source_labels: [__meta_kubernetes_namespace]
        action: replace
        target_label: kubernetes_namespace
      - source_labels: [__meta_kubernetes_service_name]
        action: replace
        target_label: kubernetes_name
```

