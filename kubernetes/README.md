# Kubernetes

支持裸机安装多节点 K8s 集群的工具：

> `-` 表示未测试，待考察。

| 安装工具     | 安装难度 |  集群可靠程度  |  集群修改难度（升级/降级）
| --------     | -----:   | :----:  | :----:  |
| [rke(rancher)](https://docs.rancher.cn/rke/) |    1     |   3     |    1    |
| kubeadm      |    -     |   -     |    -    |
| KubeOperator |    -     |   -     |    -    |
| KubeSpray    |    3     |   -     |    -    |


## 节点配置

以下为我日常使用 rke 部署的集群中，摸索出来的主节点配置：

| Worker 节点数   | HA 主节点配置(3个，每个节点上跑一个 etcd+controlplane) |
| --------       | -----:        |
|   1-5         |    2c/2g/disk-16g     |  
|   5-30        |    4c/4g/disk-20g      |

另外主节点性能也受集群 Pods 个数的影响，上述配置应该可以支撑到每个 Worker 节点跑 100 个 Pod.


## 日志收集

- [fluentd+elasticsearch](https://github.com/fluent/fluentd-kubernetes-daemonset/blob/master/fluentd-daemonset-elasticsearch.yaml)，ES 为有状态应用，另做部署。
