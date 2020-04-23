# 通用监控方案：Prometheus + Grafana + Altermanager


## Docker 方式部署

这种方式可以部署单机版的一整套监控方案：

- [github - dockprom](https://github.com/stefanprodan/dockprom)

## Kubernetes 监控

- [coreos/kube-prometheus](https://github.com/coreos/kube-prometheus): Use Prometheus to monitor Kubernetes and applications running on Kubernetes
  - 它部署的 prometheus 可以和 istio 集成，替换掉 istioctl 自带的 prometheus+grafana，参见 [istioctl + prometheus-operator](/kubernetes/service_mesh/README.md)

## 高可用 Prometheus

由于 Prometheus 本身不支持高可用（就像 MySQL 一样，本身只是一个单机数据库），因此也有专门提供集群版 Prometheus 的工具：

- [cortex](https://github.com/cortexproject/cortex): A horizontally scalable, highly available, multi-tenant, long term Prometheus.
