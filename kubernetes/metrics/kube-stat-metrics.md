# [kube-state-metrics](https://github.com/kubernetes/kube-state-metrics)

与 metrics-server 不同，kube-state-metrics 是通过查询 apiserver，暴露一些集群层面的资源指标，比如：

- HPA 指标
- Deployment/Daemonset/StatefulSet/ReplicaSet 等指标
- Pod/PodDistruptionBuget 指标
- 等等

它会暴露出 metrics 接口，提供给 prometheus 抓取。
