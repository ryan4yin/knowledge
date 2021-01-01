# 本地 Kubernetes 集群安装工具

>云上的 Kubernetes 集群，基本上各云厂商都支持一键部署。这里主要关注本地部署，或者叫做裸机(baremetal)部署

kubernetes 是一个组件化的系统，安装过程有很大的灵活性，很多组件都有多种实现，这些实现各有特点，让初学者眼花缭乱。

而且要把这些组件一个个安装配置好并且能协同工作，也是很不容易的。

因此社区出现了各种各样的安装方案。安装方案如此之多，以致于我不晓得该用哪个好。。于是我特地调查了一番，将几个流行的安装方案罗列如下：

> `-` 表示未测试，待考察。

| 安装工具     | 安装难度 |  集群可靠程度  |  集群自定义难度 |  升级降级难度  |
| --------     | -----:   | :----:  | :----:  | :----:  |
| [sealos](https://github.com/fanux/sealos)       |    1     |   4     |    3    | - |
| [kubespray](https://github.com/kubernetes-sigs/kubespray)    |    2     |   -     |    -    | - |
| [kubeadm](https://kuboard.cn/install/install-k8s.html)      |    3     |   2     |    2    | 3 |
| [rke](https://docs.rancher.cn/rke/) |    1     |   2     |    1    | 2 |
| [minikube]](https://github.com/kubernetes/minikube) |    1     |   2     |    1    | 2 |
| [k3s](https://github.com/k3s-io/k3s) |    1     |   -     |    -    | - |


个人的使用体验：

1. sealos: 「开发/测试环境」首选，是列表中最轻量级最简便的方案，而且是完全离线的。
    - 缺点是只提供免费的 1.xx.0 版本的资源包，小版本的资源包收费，价格 50 元...
    - 它支持的自定义参数比较少，很多参数都只能在部署完成后，再手动去修改 apiserver/kube-proxy 等组件的配置文件。
2. kubespray: 适合自建生产级别的集群，是一个大而全的 kubernetes 安装方案。使用难度比 kubeadm 低一些。
   1. 最大的麻烦是网络问题。。
3. kubeadm: 适合自己学习 kubernetes 架构使用。其使用方法还算简单，只是网络插件、ingress-controller 等需要自行部署，另外 kube-apiserver 的负载均衡需要自行处理。
4. rke: 部署也很简单，配置文件只有一个 cluster-config.yml，可以考虑使用。
    - rke 最大的特点是「完全使用容器运行 k8s 自身」，kubelet 都跑在容器里面。相对二进制安装而言更容易出问题...反正我去年使用时感觉它出问题的可能性比 sealos 高。
    - `rke up` 经常会健康检查失败，需要跑两三次才能成功。因此就感觉它对自动化加 k8s 节点很不友好...
5. minikube: 单节点 k8s 集群，不过我觉得用 sealos/rke 部署单节点集群更舒服。。
6. k3s: 轻量级 kubernetes，部署也非常简单。

除了 minikube 外，其他方案都支持部署多节点集群。

另外 metric-server/ingress-controller/dashboard 这些组件，上述工具可能不会帮你部署，需要自行安装。

容器运行时方面，目前推荐使用经过生产环境验证的、成熟稳定的 containerd，未来应该会渐渐切换到 crio.

## 离线部署

我的使用体验中：

- sealos 是最好用的离线部署工具，完整的离线资源包，一行命令部署，而且集群可靠性也不错。
- rke: rke 只需要额外提供一个内网镜像仓库，官方也提供了镜像列表用于将镜像备份到内网。
- kubespray: 离线安装需要一个 web 服务器托管 kubectl/crictl 等 artifacts，以及一个内网镜像仓库托管所有镜像。
    - 还需要配置 yum/apt 镜像源。
- k3s: 官方提供 airgap 资源包，也非常方便。但是它砍掉了一些功能，有些场景下不适合使用。

## 节点配置

以下为我日常使用 rke 部署的集群中，摸索出来的主节点配置：

| Worker 节点数   | HA 主节点配置(3个，每个节点上跑一个 etcd+controlplane) |
| --------       | -----:        |
|   1-5         |    2c/3g/disk-16g     |  
|   5-30        |    4c/4g/disk-20g      |

另外主节点性能也受集群 Pods 个数的影响，上述配置应该可以支撑到每个 Worker 节点跑 100 个 Pod.

主节点至少需要 2c/3g，否则很可能出现性能问题，etcd 无法正常启动。


## 1. Minikube: 部署一个本地测试用的单节点集群

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

## 2. 使用 kubespray 部署一个生产级别的 kubernetes 集群

使用 kubespray 部署集群，最大的难关是网络问题（这也是我喜欢用 sealos 的原因，它完全离线安装，基本遇不到网络问题）：

1. yum/apt 因为网络问题速度特别慢，导致 ansible 安装 socat/ebtalbes 等工具时卡住
    - 解决方法：centos 打开 fast_mirrors，apt 手动配置镜像源
1. crictl/kubectl/kubelet/kubeadm 等 artifacts 下载速度慢： 使用代理手工下载，然后在 `./inventory/sample/group_vars/k8s-cluster/offline.yml` 中配置好这些工具的本地下载地址。
1. 镜像拉取慢：
   1. 推荐：在 `./inventory/sample/group_vars/k8s-cluster/offline.yml` 中设置国内镜像源（或者私有镜像源）。
   2. 或者开启 `download_run_once: true` 和 `download_localhost: true`，然后在本机设置国内镜像源或代理。

