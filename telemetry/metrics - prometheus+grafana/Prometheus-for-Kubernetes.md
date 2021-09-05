# Prometheus for Kubernetes

>注：感觉 promeheus-operator/kube-prometheus 比较坑，它整的自定义 CRD 如 ServiceMonitor/PodMonitor 不太好用，建议直接原生安装。

建议使用社区维护的 helm chart: [prometheus-community/prometheus](https://github.com/prometheus-community/helm-charts/blob/main/charts/prometheus/README.md#scraping-pod-metrics-via-annotations)


## 指标抓取

社区版的 helm chart 会可以通过注解自动发现 targets，并抓取指标，详见其 README。


