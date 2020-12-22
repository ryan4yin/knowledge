## 集群安装工具/发行版

支持裸机安装多节点 K8s 集群的工具：

> `-` 表示未测试，待考察。

| 安装工具     | 安装难度 |  集群可靠程度  |  集群自定义难度 |  升级降级难度  |
| --------     | -----:   | :----:  | :----:  | :----:  |
| [sealos](https://github.com/fanux/sealos)       |    1     |   4     |    3    | - |
| [kubespray](https://github.com/kubernetes-sigs/kubespray)    |    2     |   -     |    -    | - |
| [kubeadm](https://kuboard.cn/install/install-k8s.html)      |    3     |   2     |    2    | 3 |
| [rke](https://docs.rancher.cn/rke/) |    1     |   2     |    1    | 2 |
| [minikube]](https://github.com/kubernetes/minikube) |    1     |   2     |    1    | 2 |

个人的使用体验：

1. sealos: 「开发/测试环境」首选，是列表中最轻量级最简便的方案，而且是完全离线的。
    - 缺点是只提供免费的 1.xx.0 版本的资源包，小版本的资源包收费hhh...
2. kubespray: 适合自建生产级别的集群，是一个大而全的 kubernetes 安装方案。使用难度比 kubeadm 低一些。
    - 其离线部署方案，要求使用一个内部「容器镜像仓库」如 harbor，对个人测试环境而言比 sealos 要麻烦一些。
3. kubeadm: 适合自己学习 kubernetes 架构使用。其使用方法还算简单，只是网络插件、ingress-controller 等需要自行部署。
4. rke: 部署也很简单，一个 cluster-config.yml 搞定，可以考虑使用。
    - rke 最大的特点是「完全容器化」，kubelet 都跑在容器里面。但是相对的也更容易出问题。。反正我去年使用时感觉它出问题的可能性比 sealos 高。
    - 其离线部署方案，和 kubespray 一样也需要一个内部「容器镜像仓库」。
1. minikube: 单节点 k8s 集群，不过我觉得用 sealos/rke 部署单节点集群更舒服。。

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

