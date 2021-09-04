# 本地 Kubernetes 集群安装工具

>云上的 Kubernetes 集群，基本上各云厂商都支持一键部署。这里主要关注本地部署，或者叫做裸机(baremetal)部署

kubernetes 是一个组件化的系统，安装过程有很大的灵活性，很多组件都有多种实现，这些实现各有特点，让初学者眼花缭乱。

而且要把这些组件一个个安装配置好并且能协同工作，也是很不容易的。

因此社区出现了各种各样的安装方案，下面主要介绍几种支持 baremetal 部署的工具：


2. [kubeadm](https://kuboard.cn/install/install-k8s.html): 适合自己学习 kubernetes 架构使用
   1. 需要提前手动整理好要用到的镜像，提前传到所有节点上，或者上传放在私有镜像仓库中。
   2. 其使用方法还算简单，只是网络插件、ingress-controller 等需要自行部署
   3. 另外 kube-apiserver 的负载均衡需要自行处理
3. [k3s](https://github.com/k3s-io/k3s): 轻量级 kubernetes，资源需求小，部署也非常简单，适合开发测试用或者边缘环境
    - 支持 airgap 离线部署
4. [kubespray](https://github.com/kubernetes-sigs/kubespray): 适合自建生产级别的集群，是一个大而全的 kubernetes 安装方案，自动安装容器运行时、k8s、网络插件等组件，而且各组件都有很多方案可选，但是感觉有点复杂。
   1. 底层使用了 kubeadm 部署集群
   2. 在国内使用的话，最大的麻烦是网络问题，需要研究清楚它的 airgap 模式


## 节点配置

以下为我日常使用 rke 部署的集群中，摸索出来的主节点配置：

| Worker 节点数   | HA 主节点配置(3个，每个节点上跑一个 etcd+controlplane) |
| --------       | -----:        |
|   1-5         |    2c/3g/disk-16g     |  
|   5-30        |    4c/4g/disk-20g      |

另外主节点性能也受集群 Pods 个数的影响，上述配置应该可以支撑到每个 Worker 节点跑 100 个 Pod.

主节点至少需要 2c/3g，否则很可能出现性能问题，etcd 无法正常启动。


## 使用 kubeadm+containerd+calico 部署一个集群

>适合开发测试使用，安全性、稳定性、长期可用性等方案都可能还有问题。

>参考 [Kubernetes Docs - Installing kubeadm](https://kubernetes.io/docs/setup/production-environment/tools/kubeadm/install-kubeadm/)

### 1. 节点的环境准备

首先准备三台 Linux 虚拟机，系统这里选用 debian 11，然后调整这三台机器的设置：

- 节点配置：
  - master：不低于 2c/3g
  - worker：看需求，建议不低于 2c/4g
- 处于同一网络内并可互通（通常是同一局域网）
- 各主机的 hostname 和 mac/ip 地址以及 `/sys/class/dmi/id/product_uuid`，都必须唯一
  - 这里最容易出问题的，通常是 hostname 冲突！
- **必须**关闭 swap，kubelet 才能正常工作！

方便起见，我直接使用 [ryan4yin/pulumi-libvirt](https://github.com/ryan4yin/pulumi-libvirt#examples) 自动创建了五个虚拟机，并设置好了 ip/hostname.

#### 1.1 iptables 设置

目前 kubernetes 的容器网络，默认使用的是 bridge 模式，这种模式下，需要使 `iptables` 能够接管 bridge 上的流量。

配置如下：
```shell
cat <<EOF | sudo tee /etc/modules-load.d/k8s.conf
br_netfilter
EOF

cat <<EOF | sudo tee /etc/sysctl.d/k8s.conf
net.bridge.bridge-nf-call-ip6tables = 1
net.bridge.bridge-nf-call-iptables = 1
EOF
sudo sysctl --system
```

#### 1.2 开放节点端口

>局域网环境的话，建议直接关闭防火墙。这样所有端口都可用，方便快捷。

>通常我们的云上集群，也是关闭防火墙的，只是会通过云服务提供的「安全组」来限制客户端 ip

Control-plane 节点，也就是 master，需要开放如下端口：

| Protocol | Direction | Port Range | Purpose                 | Used By                   |
|----------|-----------|------------|-------------------------|---------------------------|
| TCP      | Inbound   | 6443\*      | Kubernetes API server   | All                       |
| TCP      | Inbound   | 2379-2380  | etcd server client API  | kube-apiserver, etcd      |
| TCP      | Inbound   | 10250      | kubelet API             | Self, Control plane       |
| TCP      | Inbound   | 10251      | kube-scheduler          | Self                      |
| TCP      | Inbound   | 10252      | kube-controller-manager | Self                      |

Worker 节点需要开发如下端口：

| Protocol | Direction | Port Range  | Purpose               | Used By                 |
|----------|-----------|-------------|-----------------------|-------------------------|
| TCP      | Inbound   | 10250       | kubelet API           | Self, Control plane     |
| TCP      | Inbound   | 30000-32767 | NodePort Services†    | All                     |


另外通常我们本地测试的时候，可能更想直接在 `80` `443` `8080` 等端口上使用 `NodePort`，
就需要修改 kube-apiserver 的 `--service-node-port-range` 参数来自定义 NodePort 的端口范围，相应的 Worker 节点也得开放这些端口。



### 2. 安装 containerd


