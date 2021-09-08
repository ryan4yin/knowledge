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


## 一、使用 kubeadm+containerd+calico 部署一个集群

>适合开发测试使用，安全性、稳定性、长期可用性等方案都可能还有问题。

>目前仅单 master，高可用方案待更新...

参考：
- [Kubernetes Docs - Installing kubeadm](https://kubernetes.io/docs/setup/production-environment/tools/kubeadm/install-kubeadm/)
- [使用kubeadm安装kubernetes_v1.18.x - Kuboard Docs](https://kuboard.cn/install/install-k8s.html)


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
sudo modprobe br_netfilter
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

首先是环境配置：

```shell
cat <<EOF | sudo tee /etc/modules-load.d/containerd.conf
overlay
br_netfilter
nf_conntrack
EOF

sudo modprobe overlay
sudo modprobe br_netfilter
sudo modprobe nf_conntrack

# Setup required sysctl params, these persist across reboots.
cat <<EOF | sudo tee /etc/sysctl.d/99-kubernetes-cri.conf
net.bridge.bridge-nf-call-iptables  = 1
net.ipv4.ip_forward                 = 1
net.bridge.bridge-nf-call-ip6tables = 1
EOF

# Apply sysctl params without reboot
sudo sysctl --system
```

安装 containerd+nerdctl:

```shell
wget https://github.com/containerd/nerdctl/releases/download/v0.11.1/nerdctl-full-0.11.1-linux-amd64.tar.gz
tar -axvf nerdctl-full-0.11.1-linux-amd64.tar.gz
# 这里简单起见，rootless 相关的东西也一起装进去了，测试嘛就无所谓了...
mv bin/* /usr/local/bin/
mv lib/systemd/system/containerd.service /usr/lib/systemd/system/

systemctl enable containerd
systemctl start containerd
```


### 3. 安装 kubelet/kubeadm/kubectl

```shell
# 一些全局都需要用的变量
CNI_VERSION="v0.8.2"
CRICTL_VERSION="v1.17.0"
# kubernetes 的版本号
# RELEASE="$(curl -sSL https://dl.k8s.io/release/stable.txt)"
RELEASE="1.22.1"
# kubelet 配置文件的版本号
RELEASE_VERSION="v0.4.0"
# 架构
ARCH="amd64"
#　安装目录
DOWNLOAD_DIR=/usr/local/bin


# CNI 插件
sudo mkdir -p /opt/cni/bin
curl -L "https://github.com/containernetworking/plugins/releases/download/${CNI_VERSION}/cni-plugins-linux-${ARCH}-${CNI_VERSION}.tgz" | sudo tar -C /opt/cni/bin -xz

# crictl 相关工具
curl -L "https://github.com/kubernetes-sigs/cri-tools/releases/download/${CRICTL_VERSION}/crictl-${CRICTL_VERSION}-linux-${ARCH}.tar.gz" | sudo tar -C $DOWNLOAD_DIR -xz

# kubelet/kubeadm/kubectl
cd $DOWNLOAD_DIR
sudo curl -L --remote-name-all https://storage.googleapis.com/kubernetes-release/release/${RELEASE}/bin/linux/${ARCH}/{kubeadm,kubelet,kubectl}
sudo chmod +x {kubeadm,kubelet,kubectl}

# kubelet/kubeadm 配置
curl -sSL "https://raw.githubusercontent.com/kubernetes/release/${RELEASE_VERSION}/cmd/kubepkg/templates/latest/deb/kubelet/lib/systemd/system/kubelet.service" | sed "s:/usr/bin:${DOWNLOAD_DIR}:g" | sudo tee /etc/systemd/system/kubelet.service
sudo mkdir -p /etc/systemd/system/kubelet.service.d
curl -sSL "https://raw.githubusercontent.com/kubernetes/release/${RELEASE_VERSION}/cmd/kubepkg/templates/latest/deb/kubeadm/10-kubeadm.conf" | sed "s:/usr/bin:${DOWNLOAD_DIR}:g" | sudo tee /etc/systemd/system/kubelet.service.d/10-kubeadm.conf

systemctl enable --now kubelet
# 验证 kubelet 启动起来了，但是目前还没有初始化配置，过一阵就会重启一次
systemctl status kubelet
```


### 4. 初始化 kubeadm

其实需要运行的就是这条命令：

```shell
# 极简配置：
cat <<EOF | sudo tee kubeadm-config.yaml
kind: ClusterConfiguration
apiVersion: kubeadm.k8s.io/v1beta3
kubernetesVersion: v1.22.1
---
kind: KubeletConfiguration
apiVersion: kubelet.config.k8s.io/v1beta1
cgroupDriver: systemdnet.bridge.bridge-nf-call-iptables = 1
EOF
# 查看 kubeadm 默认的完整配置
kubeadm config print init-defaults > init.default.yaml

# 执行集群的初始化，这会直接将当前节点创建为 master
# 成功运行的前提：前面该装的东西都装好了，而且 kubelet 已经在后台运行了
kubeadm init --pod-network-cidr=10.244.0.0/16 --config kubeadm-config.yaml
```

kubeadm 应该会报错，提示你有些依赖不存在，下面先安装好依赖项。
```shell
sudo zypper in -y socat ebtables conntrack-tools
```

再重新运行前面的 kubeadm 命令，应该就能正常执行了，它做的操作有：
- 拉取控制面的容器镜像
- 生成 ca 根证书
- 使用根证书为 etcd/apiserver 等一票工具生成 tls 证书
- 为控制面的各个组件生成 kubeconfig 配置
- 生成 static pod 配置，kubelet 会根据这些配置自动拉起 kube-proxy

#### 4.1. 自定义镜像地址

如果你没有科学环境，kubeadm 默认的镜像仓库在国内是拉不了的。
如果对可靠性要求高，最好是自建私有镜像仓库，把镜像推送到私有仓库。

可以通过如下命令列出所有需要用到的镜像地址：

```shell
$ kubeadm config images list --kubernetes-version v1.22.1
k8s.gcr.io/kube-apiserver:v1.22.1
k8s.gcr.io/kube-controller-manager:v1.22.1
k8s.gcr.io/kube-scheduler:v1.22.1
k8s.gcr.io/kube-proxy:v1.22.1
k8s.gcr.io/pause:3.5
k8s.gcr.io/etcd:3.5.0-0
k8s.gcr.io/coredns/coredns:v1.8.4
```

使用 `skopeo` 等工具或脚本将上述镜像拷贝到你的私有仓库，或者图方便（测试环境）也可以考虑网上找找别人同步好的镜像地址。将镜像地址添加到 `kubeadm-config.yaml` 中再部署：

```yaml
cat <<EOF | sudo tee kubeadm-config.yaml
kind: ClusterConfiguration
apiVersion: kubeadm.k8s.io/v1beta3
kubernetesVersion: v1.22.1
imageRepository: <your-image-repository>
controlPlaneEndpoint: "apiserver.svc.local:6443"
networking:
  serviceSubnet: "10.96.0.0/16"
  podSubnet: "10.244.0.0/16"
  dnsDomain: "cluster.local"
dns:
  type: CoreDNS
  imageRepository: <your-image-repository>/coredns
---
apiVersion: kubelet.config.k8s.io/v1beta1
kind: KubeletConfiguration
cgroupDriver: systemd
EOF
```


### 5. 添加其他节点

走完上一步后，一个只有 master 的集群就创建好了，按照 kubeadm 的提示，将 kubeconfig 放到默认位置：

```shell
mkdir -p $HOME/.kube
sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
sudo chown $(id -u):$(id -g) $HOME/.kube/config
```

现在可以使用 kubectl 查看集群状况了：

```shell
kubectl get node --show-labels
```

同时 kubeadm 还会打印出一行添加 `worker node` 节点的命令，格式类似：

```shell
kubeadm join apiserver.svc.local:6443 --token <some-token> \
        --discovery-token-ca-cert-hash sha256:<hash-xxx> 
```

现在在其他节点运行此命令，即可将 worker 节点加入到集群中。


### 6. 安装 calico 网络插件

待续
