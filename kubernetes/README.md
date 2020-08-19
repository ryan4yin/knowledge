# Kubernetes

## 集群安装工具/发行版

支持裸机安装多节点 K8s 集群的工具：

> `-` 表示未测试，待考察。

| 安装工具     | 安装难度 |  集群可靠程度  |  集群自定义难度 |  升级降级难度  |
| --------     | -----:   | :----:  | :----:  | :----:  |
| [rke(rancher)](https://docs.rancher.cn/rke/) |    1     |   2     |    1    | 2 |
| SealOS       |    1     |   4     |    3    | - |
| KubeSpray    |    3     |   -     |    -    | - |
| kubeadm      |    -     |   -     |    -    | - |
| KubeOperator |    -     |   -     |    -    | - |

个人观点：sealos/rke 很适合用于部署测试环境，方便快捷，其中 sealos 对离线部署的支持非常简便。

kubeadm/kubespray 也许适合自建生产级别的集群，但是我目前不怎么熟悉。

kubeoperator 没有用过，不做评论。kubesphere 全家桶可以考虑试试。

另外还有个 openshift 国内貌似用的人少，不怎么了解。

### 1. Minikube: 部署一个本地测试用的单节点集群

```shell
# 1. 下载最新版 minikube: https://github.com/kubernetes/minikube/releases
# 2. 以 docker 方式启动 minikube，注意 base-image 要换成最新的
minikube start --driver=docker \
    --cpus 4 --memory=10G \
    --image-mirror-country cn \
    --base-image registry.cn-hangzhou.aliyuncs.com/google_containers/kicbase:v0.0.10
# 3. 或者也可以使用 hyperv 启动 minikube，注意 iso 的版本号要匹配
minikube start  start --driver=hyperv \
    --cpus 4 --memory=10G \
    --image-mirror-country cn \
    --iso-url  https://kubernetes.oss-cn-hangzhou.aliyuncs.com/minikube/iso/minikube-v1.10.0.iso
```

## 节点配置

以下为我日常使用 rke 部署的集群中，摸索出来的主节点配置：

| Worker 节点数   | HA 主节点配置(3个，每个节点上跑一个 etcd+controlplane) |
| --------       | -----:        |
|   1-5         |    2c/2g/disk-16g     |  
|   5-30        |    4c/4g/disk-20g      |

另外主节点性能也受集群 Pods 个数的影响，上述配置应该可以支撑到每个 Worker 节点跑 100 个 Pod.


## 日志收集

参见 [monitoring/fluentd](/monitoring/fluentd/README.md)
