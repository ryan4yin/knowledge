# 本地 Kubernetes 集群安装工具

>云上的 Kubernetes 集群，基本上各云厂商都支持一键部署。这里主要关注本地部署，或者叫做裸机(baremetal)部署

kubernetes 是一个组件化的系统，安装过程有很大的灵活性，很多组件都有多种实现，这些实现各有特点，让初学者眼花缭乱。

而且要把这些组件一个个安装配置好并且能协同工作，也是很不容易的。

因此社区出现了各种各样的安装方案，下面主要介绍几种支持 baremetal 部署的工具：


1. [kubeadm](https://kuboard.cn/install/install-k8s.html): 社区的集群安装工具，目前已经很成熟了。
   1. 使用难度：简单
2. [k3s](https://github.com/k3s-io/k3s): 轻量级 kubernetes，资源需求小，部署非常简单，适合开发测试用或者边缘环境
   1. 支持 airgap 离线部署
   2. 使用难度：超级简单
3. [alibaba/sealer](https://github.com/alibaba/sealer): 支持将整个 kubernetes 打包成一个镜像进行交付，而且部署也非常简单。
   1. 使用难度：超级简单 
   2. 这个项目目前还在发展中，不过貌似已经有很多 toB 的公司在使用它进行 k8s 应用的交付了。
4. [kubespray](https://github.com/kubernetes-sigs/kubespray): 适合自建生产级别的集群，是一个大而全的 kubernetes 安装方案，自动安装容器运行时、k8s、网络插件等组件，而且各组件都有很多方案可选，但是感觉有点复杂。
   1. 使用难度：中等
   2. 支持 airgap 离线部署，但是之前我试用过是有坑...
   3. 底层使用了 kubeadm 部署集群

## 一、使用 kubeadm+containerd 部署一个集群

>适合开发测试使用，安全性、稳定性、长期可用性等方案都可能还有问题。

>本文未考虑国内网络环境，建议在路由器上整个科学代理，或者自行调整文中的部分命令。

>kubernetes 官方介绍了两种高可用集群的拓扑结构：「Stacked etcd topology」和「External etcd topology」，简单起见，本文使用第一种「堆叠 Etcd 拓扑」结构，创建一个三 master 的高可用集群。

参考：
- [Kubernetes Docs - Installing kubeadm](https://kubernetes.io/docs/setup/production-environment/tools/kubeadm/install-kubeadm/)
- [Kubernetes Docs - Creating Highly Available clusters with kubeadm](https://kubernetes.io/docs/setup/production-environment/tools/kubeadm/high-availability/)


### 1. 节点的环境准备

首先准备三台 Linux 虚拟机，系统这里选用 debian 11，然后调整这三台机器的设置：

- 节点配置：
  - master：不低于 2c/3g，硬盘 20G
    - 主节点性能也受集群 Pods 个数的影响，上述配置应该可以支撑到每个 Worker 节点跑 100 个 Pod.
  - worker：看需求，建议不低于 2c/4g，硬盘不小于 20G，资源充分的话建议 40G.
- 处于同一网络内并可互通（通常是同一局域网）
- 各主机的 hostname 和 mac/ip 地址以及 `/sys/class/dmi/id/product_uuid`，都必须唯一
  - 这里最容易出问题的，通常是 hostname 冲突！
- **必须**关闭 swap，kubelet 才能正常工作！

方便起见，我直接使用 [ryan4yin/pulumi-libvirt](https://github.com/ryan4yin/pulumi-libvirt#examples) 自动创建了五个虚拟机，并设置好了 ip/hostname.

本文使用了 opensuse leap 15.3 的 cloud image 进行安装测试。

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


### 4. 为 master 的 kube-apiserver 创建负载均衡实现高可用

根据 kubeadm 官方文档 [Kubeadm Docs - High Availability Considerations](https://github.com/kubernetes/kubeadm/blob/master/docs/ha-considerations.md#kube-vip) 介绍，要实现 kube-apiserver 的高可用，目前最知名的负载均衡方式是 keepalived+haproxy，另外也可以考虑使用 kube-vip 等更简单的工具。

简单起见，我们直接用 kube-vip 吧，参考了 kube-vip 的官方文档：[Kube-vip as a Static Pod with Kubelet](https://kube-vip.io/install_static/).

>P.S. 我也见过有的安装工具会直接抛弃 keepalived，直接在每个节点上跑一个 nginx 做负载均衡，配置里写死了所有 master 的地址...

首先使用如下命令生成 kube-vip 的配置文件，以 ARP 为例（生产环境建议换成 BGP）：

```shell
cat <<EOF | sudo tee add-kube-vip.sh
# 你的虚拟机网卡，opensuse/centos 等都是 eth0，但是 ubuntu 可能是 ens3
export INTERFACE=eth0

# 用于实现高可用的 vip，需要和前面的网络接口在同一网段内，否则就无法路由了。
export VIP=192.168.122.200

# 生成 static-pod 的配置文件
mkdir -p /etc/kubernetes/manifests
nerdctl run --rm --network=host --entrypoint=/kube-vip ghcr.io/kube-vip/kube-vip:v0.3.8 \
  manifest pod \
  --interface $INTERFACE \
  --vip $VIP \
  --controlplane \
  --services \
  --arp \
  --leaderElection | tee  /etc/kubernetes/manifests/kube-vip.yaml
EOF

bash add-kube-vip.sh
```

三个 master 节点都需要跑下上面的命令（worker 不需要），创建好 kube-vip 的 static-pod 配置文件。
在完成 kubeadm 初始化后，kubelet 会自动把它们拉起为 static pod.

### 5. 使用 kubeadm 创建集群

其实需要运行的就是这条命令：

```shell
# 极简配置：
cat <<EOF | sudo tee kubeadm-config.yaml
apiVersion: kubeadm.k8s.io/v1beta3
kind: InitConfiguration
nodeRegistration:
  criSocket: "/var/run/containerd/containerd.sock"
  imagePullPolicy: IfNotPresent
---
kind: ClusterConfiguration
apiVersion: kubeadm.k8s.io/v1beta3
kubernetesVersion: v1.22.1
clusterName: kubernetes
certificatesDir: /etc/kubernetes/pki
imageRepository: k8s.gcr.io
controlPlaneEndpoint: "192.168.122.200:6443"  # 填 apiserver 的 vip 地址，或者整个域名也行，但是就得加 /etc/hosts 或者内网 DNS 解析
networking:
  serviceSubnet: "10.96.0.0/16"
  podSubnet: "10.244.0.0/16"
etcd:
  local:
    dataDir: /var/lib/etcd
---
apiVersion: kubelet.config.k8s.io/v1beta1
kind: KubeletConfiguration
cgroupDriver: systemd
# 让 kubelet 从 certificates.k8s.io 申请由集群 CA Root 签名的 tls 证书，而非直接使用自签名证书
# 如果不启用这个， 安装 metrics-server 时就会遇到证书报错，后面会详细介绍。
serverTLSBootstrap: true
EOF

# 查看 kubeadm 默认的完整配置，供参考
kubeadm config print init-defaults > init.default.yaml

# 执行集群的初始化，这会直接将当前节点创建为 master
# 成功运行的前提：前面该装的东西都装好了，而且 kubelet 已经在后台运行了
# `--upload-certs` 会将生成的集群证书上传到 kubeadm 服务器，在两小时内加入集群的 master 节点会自动拉证书，主要是方便集群创建。
kubeadm init --config kubeadm-config.yaml --upload-certs
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
- 生成 static pod 配置，kubelet 会根据这些配置自动拉起 kube-proxy 以及其他所有的 k8s master 组件

运行完会给出三部分命令：

- 将 `kubeconfig` 放到 `$HOME/.kube/config` 下，`kubectl` 需要使用该配置文件连接 kube-apiserver
- control-plane 节点加入集群的命令:
  - 这里由于我们提前添加了 kube-vip 的 static-pod 配置，这里的 preflight-check 会报错，需要添加此参数忽略该报错 - `--ignore-preflight-errors=DirAvailable--etc-kubernetes-manifests`
  ```shell
  kubeadm join 192.168.122.200:6443 --token <token> \
    --discovery-token-ca-cert-hash sha256:<hash> \
    --control-plane --certificate-key <key> \
    --ignore-preflight-errors=DirAvailable--etc-kubernetes-manifests
  ```
- worker 节点加入集群的命令:
  ```shell
  kubeadm join 192.168.122.200:6443 --token <token> \
        --discovery-token-ca-cert-hash sha256:<hash> 
  ```

跑完第一部分 `kubeconfig` 的处理命令后，就可以使用 kubectl 查看集群状况了：

```shell
k8s-master-0:~/kubeadm # kubectl get no
NAME           STATUS     ROLES                  AGE   VERSION
k8s-master-0   NotReady   control-plane,master   79s   v1.22.1
k8s-master-0:~/kubeadm # kubectl get po --all-namespaces
NAMESPACE     NAME                                   READY   STATUS    RESTARTS   AGE
kube-system   coredns-78fcd69978-6tlnw               0/1     Pending   0          83s
kube-system   coredns-78fcd69978-hxtvs               0/1     Pending   0          83s
kube-system   etcd-k8s-master-0                      1/1     Running   6          90s
kube-system   kube-apiserver-k8s-master-0            1/1     Running   4          90s
kube-system   kube-controller-manager-k8s-master-0   1/1     Running   4          90s
kube-system   kube-proxy-6w2bx                       1/1     Running   0          83s
kube-system   kube-scheduler-k8s-master-0            1/1     Running   7          97s
```

现在在其他节点运行前面打印出的加入集群的命令，就可以搭建好一个高可用的集群了。

所有节点都加入集群后，通过 kubectl 查看，应该是三个控制面 master，两个 worker：

```shell
k8s-master-0:~/kubeadm # kubectl get node
NAME           STATUS     ROLES                  AGE     VERSION
k8s-master-0   NotReady   control-plane,master   26m     v1.22.1
k8s-master-1   NotReady   control-plane,master   7m2s    v1.22.1
k8s-master-2   NotReady   control-plane,master   2m10s   v1.22.1
k8s-worker-0   NotReady   <none>                 97s     v1.22.1
k8s-worker-1   NotReady   <none>                 86s     v1.22.1
```

现在它们都还处于 NotReady 状态，需要等到我们把网络插件安装好，才会 Ready.

现在再看下集群的证书签发状态：

```shell
❯ kubectl get csr --sort-by='{.spec.username}'
NAME        AGE     SIGNERNAME                                    REQUESTOR                  REQUESTEDDURATION   CONDITION
csr-95hll   6m58s   kubernetes.io/kube-apiserver-client-kubelet   system:bootstrap:q8ivnz    <none>              Approved,Issued
csr-tklnr   7m5s    kubernetes.io/kube-apiserver-client-kubelet   system:bootstrap:q8ivnz    <none>              Approved,Issued
csr-w92jv   9m15s   kubernetes.io/kube-apiserver-client-kubelet   system:bootstrap:q8ivnz    <none>              Approved,Issued
csr-rv7sj   8m11s   kubernetes.io/kube-apiserver-client-kubelet   system:bootstrap:q8ivnz    <none>              Approved,Issued
csr-nxkgx   10m     kubernetes.io/kube-apiserver-client-kubelet   system:node:k8s-master-0   <none>              Approved,Issued
csr-cd22c   10m     kubernetes.io/kubelet-serving                 system:node:k8s-master-0   <none>              Pending
csr-wjrnr   9m53s   kubernetes.io/kubelet-serving                 system:node:k8s-master-0   <none>              Pending
csr-sjq42   9m8s    kubernetes.io/kubelet-serving                 system:node:k8s-master-1   <none>              Pending
csr-xtv8f   8m56s   kubernetes.io/kubelet-serving                 system:node:k8s-master-1   <none>              Pending
csr-f2dsf   8m3s    kubernetes.io/kubelet-serving                 system:node:k8s-master-2   <none>              Pending
csr-xl8dg   6m58s   kubernetes.io/kubelet-serving                 system:node:k8s-worker-0   <none>              Pending
csr-p9g24   6m52s   kubernetes.io/kubelet-serving                 system:node:k8s-worker-1   <none>              Pending
```

能看到有好几个 `kubernetes.io/kubelet-serving` 的证书还处于 pending 状态，
这是因为我们在 kubeadm 配置文件中，设置了 `serverTLSBootstrap: true`，让 Kubelet 从集群中申请 CA 签名证书，而不是自签名导致的。

设置这个参数的主要目的，是为了让 metrics-server 等组件能使用 https 协议与 kubelet 通信，避免为 metrics-server 添加参数 `--kubelet-insecure-tls`.

目前 kubeadm 不支持自动批准 kubelet 申请的证书，需要我们手动批准一下：

```shell
# 批准 Kubelet 申请的所有证书
kubectl certificate approve csr-cd22c csr-wjrnr csr-sjq42 csr-xtv8f csr-f2dsf csr-xl8dg csr-p9g24
```

在未批准这些证书之前，所有需要调用 kubelet api 的功能都将无法使用，比如：

- 查看 pod 日志
- 获取节点 metrics
- 等等

#### 5.1 常见问题

##### 5.1.1 使用国内镜像源

如果你没有科学环境，kubeadm 默认的镜像仓库在国内是拉不了的。
如果对可靠性要求高，最好是自建私有镜像仓库，把镜像推送到私有仓库。

可以通过如下命令列出所有需要用到的镜像地址：

```shell
❯ kubeadm config images list --kubernetes-version v1.22.1
k8s.gcr.io/kube-apiserver:v1.22.1
k8s.gcr.io/kube-controller-manager:v1.22.1
k8s.gcr.io/kube-scheduler:v1.22.1
k8s.gcr.io/kube-proxy:v1.22.1
k8s.gcr.io/pause:3.5
k8s.gcr.io/etcd:3.5.0-0
k8s.gcr.io/coredns/coredns:v1.8.4
```

使用 `skopeo` 等工具或脚本将上述镜像拷贝到你的私有仓库，或者图方便（测试环境）也可以考虑网上找找别人同步好的镜像地址。将镜像地址添加到 `kubeadm-config.yaml` 中再部署。


##### 5.1.2 重置集群配置

创建集群的过程中出现任何问题，都可以通过在所有节点上运行 `kubeadm reset` 来还原配置，然后重新走 kubeadm 的集群创建流程。

但是要注意几点：

- `kubeadm reset` 会清除包含 kube-vip 配置在内的所有 static-pod 配置文件，所以 master 节点需要重新跑下前面给的 kube-vip 命令，生成下 kube-vip 配置。
- `kubeadm reset` 不会重置网络接口的配置，master 节点需要手动清理下 kube-vip 添加的 vip: `ip addr del 192.168.122.200/32 dev eth0`.
- 如果你在安装了网络插件之后希望重装集群，顺序如下：
  - 通过 `kubectl delete -f xxx.yaml`/`helm uninstall` 删除所有除网络之外的其他应用配置
  - 删除网络插件
  - 先重启一遍所有节点，或者手动重置所有节点的网络配置
    - 建议重启，因为我不知道该怎么手动重置... 试了 `systemctl restart network` 并不会清理所有虚拟网络接口。

如此操作后，再重新执行集群安装，应该就没啥毛病了。

### 6. 验证集群的高可用性

虽然网络插件还没装导致集群所有节点都还没 ready，但是我们已经可以通过 kubectl 命令来简单验证集群的高可用性了。

首先，我们将前面放置在 k8s-master-0 的认证文件 `$HOME/.kube/config` 以及 kunbectl 安装在另一台机器上，比如我直接放我的宿主机。

然后在宿主机上跑 `kubectl get node` 命令验证集群的高可用性：

- 三个主节点都正常运行时，kubectl 命令也正常
- pause 或者 stop 其中一个 master，kubectl 命令仍然能正常运行
- 再 pause 第二个 master，kubectl 命令应该就会卡住，并且超时，无法使用了
- resume 恢复停掉的两个 master 之一，会发现 kubectl 命令又能正常运行了

到这里 kubeadm 的工作就完成了，接下来再安装网络插件，集群就可用了。

### 7. 安装网络插件

社区有很多种网络插件可选，比较知名且性能也不错的，应该是 Calico 和 Cilium，其中 Cilium 主打基于 eBPF 的高性能与高可观测性。

下面分别介绍这两个插件的安装方法。（注意只能安装其中一个网络插件，不能重复安装。）

需要提前在本机安装好 helm，我这里使用宿主机，因此只需要在宿主机安装:

```shell
# 一行命令安装，也可以自己手动下载安装包，都行
curl https://raw.githubusercontent.com/helm/helm/master/scripts/get-helm-3 | bash

# 或者 opensuse 直接用包管理器安装
sudo zypper in helm
```

#### 7.1 安装 Cilium

>官方文档：https://docs.cilium.io/en/v1.10/gettingstarted/k8s-install-kubeadm/

cilium 通过 eBPF 提供了高性能与高可观测的 k8s 集群网络，
另外 cilium 还提供了比 kube-proxy 更高效的实现，可以完全替代 kube-proxy.

这里我们还是先使用 kube-proxy 模式，先熟悉下 cilium 的使用：

```shell
helm repo add cilium https://helm.cilium.io/
helm search repo cilium/cilium -l | head

helm install cilium cilium/cilium --version 1.10.4 --namespace kube-system
```

可以通过 `kubectl get pod -A` 查看 cilium 的安装进度，当所有 pod 都 ready 后，集群就 ready 了~

cilium 也提供了专用的客户端：

```shell
curl -L --remote-name-all https://github.com/cilium/cilium-cli/releases/latest/download/cilium-linux-amd64.tar.gz{,.sha256sum}
sha256sum --check cilium-linux-amd64.tar.gz.sha256sum
sudo tar xzvfC cilium-linux-amd64.tar.gz /usr/local/bin
rm cilium-linux-amd64.tar.gz{,.sha256sum}
```

然后使用 cilium 客户端检查网络插件的状态：

```shell
 $ cilium status --wait
    /¯¯\
 /¯¯\__/¯¯\    Cilium:         OK
 \__/¯¯\__/    Operator:       OK
 /¯¯\__/¯¯\    Hubble:         disabled
 \__/¯¯\__/    ClusterMesh:    disabled
    \__/

DaemonSet         cilium             Desired: 5, Ready: 5/5, Available: 5/5
Deployment        cilium-operator    Desired: 2, Ready: 2/2, Available: 2/2
Containers:       cilium             Running: 5
                  cilium-operator    Running: 2
Cluster Pods:     2/2 managed by Cilium
Image versions    cilium             quay.io/cilium/cilium:v1.10.4@sha256:7d354052ccf2a7445101d78cebd14444c7c40129ce7889f2f04b89374dbf8a1d: 5
                  cilium-operator    quay.io/cilium/operator-generic:v1.10.4@sha256:c49a14e34634ff1a494c84b718641f27267fb3a0291ce3d74352b44f8a8d2f93: 2
```

cilium 还提供了命令，自动创建 pod 进行集群网络的连接性测试：

```shell
❯ cilium connectivity test
ℹ️  Monitor aggregation detected, will skip some flow validation steps
✨ [kubernetes] Creating namespace for connectivity check...
✨ [kubernetes] Deploying echo-same-node service...
✨ [kubernetes] Deploying same-node deployment...
✨ [kubernetes] Deploying client deployment...
✨ [kubernetes] Deploying client2 deployment...
✨ [kubernetes] Deploying echo-other-node service...
✨ [kubernetes] Deploying other-node deployment...
...
ℹ️  Expose Relay locally with:
   cilium hubble enable
   cilium status --wait
   cilium hubble port-forward&
🏃 Running tests...
...
---------------------------------------------------------------------------------------------------------------------
✅ All 11 tests (134 actions) successful, 0 tests skipped, 0 scenarios skipped.
```

通过 `kubectl get po -A` 能观察到，这个测试命令会自动创建一个 `cilium-test` 名字空间，并在启动创建若干 pod 进行详细的测试。

整个测试流程大概会持续 5 分多钟，测试完成后，相关 Pod 不会自动删除，使用如下命令手动删除：

```shell
kubectl delete namespace cilium-test
```

#### 7.1 安装 Calico

>官方文档：https://docs.projectcalico.org/getting-started/kubernetes/self-managed-onprem/onpremises

也就两三行命令。安装确实特别简单，懒得介绍了，看官方文档吧。

但是实际上 calico 的细节还蛮多的，建议通读下它的官方文档，了解下 calico 的架构。

#### 8. 查看集群状态

官方的 dashboard 个人感觉不太好用，建议直接在本地装个 k9s 用，特别爽。

```shell
sudo zypper in k9s
```

然后就可以愉快地玩耍了。


#### 9. 安装 metrics-server

>这一步可能遇到的问题：[Enabling signed kubelet serving certificates](https://kubernetes.io/docs/tasks/administer-cluster/kubeadm/kubeadm-certs/#kubelet-serving-certs)

如果需要使用 HPA 以及简单的集群监控，那么 metrics-server 是必须安装的，现在我们安装一下它。

首先，跑 kubectl 的监控命令应该会报错：

```shell
❯ kubectl top node
error: Metrics API not available
```

k9s 里面应该也看不到任何监控指标。

现在通过 helm 安装它：

```shell
helm repo add metrics-server https://kubernetes-sigs.github.io/metrics-server/
helm search repo metrics-server/metrics-server -l | head

helm upgrade --install metrics-server metrics-server/metrics-server --version 3.5.0 --namespace kube-system
```

>metrics-server 默认只会部署一个实例，如果希望高可用，请参考官方配置：[metrics-server - high-availability manifests](https://github.com/kubernetes-sigs/metrics-server/tree/master/manifests/high-availability)

等 metrics-server 启动好后，就可以使用 `kubectl top` 命令啦：

```shell
❯ kubectl top node
NAME           CPU(cores)   CPU%   MEMORY(bytes)   MEMORY%   
k8s-master-0   327m         16%    1465Mi          50%       
k8s-master-1   263m         13%    1279Mi          44%       
k8s-master-2   289m         14%    1282Mi          44%       
k8s-worker-0   62m          3%     518Mi           13%       
k8s-worker-1   115m         2%     659Mi           8%        

❯ kubectl top pod
No resources found in default namespace.

❯ kubectl top pod -A
NAMESPACE     NAME                                   CPU(cores)   MEMORY(bytes)   
kube-system   cilium-45nw4                           9m           135Mi           
kube-system   cilium-5x7jf                           6m           154Mi           
kube-system   cilium-84sr2                           7m           160Mi           
kube-system   cilium-operator-78f45675-dp4b6         2m           30Mi            
kube-system   cilium-operator-78f45675-fpm5g         1m           30Mi            
kube-system   cilium-tkhl4                           6m           141Mi           
kube-system   cilium-zxbvm                           5m           138Mi           
kube-system   coredns-78fcd69978-dpxxk               3m           16Mi            
kube-system   coredns-78fcd69978-ptd9p               1m           18Mi            
kube-system   etcd-k8s-master-0                      61m          88Mi            
kube-system   etcd-k8s-master-1                      50m          85Mi            
kube-system   etcd-k8s-master-2                      55m          83Mi            
kube-system   kube-apiserver-k8s-master-0            98m          462Mi           
kube-system   kube-apiserver-k8s-master-1            85m          468Mi           
kube-system   kube-apiserver-k8s-master-2            85m          423Mi           
kube-system   kube-controller-manager-k8s-master-0   22m          57Mi            
kube-system   kube-controller-manager-k8s-master-1   2m           23Mi            
kube-system   kube-controller-manager-k8s-master-2   2m           23Mi            
kube-system   kube-proxy-j2s76                       1m           24Mi            
kube-system   kube-proxy-k6d6z                       1m           18Mi            
kube-system   kube-proxy-k85rx                       1m           23Mi            
kube-system   kube-proxy-pknsc                       1m           20Mi            
kube-system   kube-proxy-xsq4m                       1m           15Mi            
kube-system   kube-scheduler-k8s-master-0            3m           25Mi            
kube-system   kube-scheduler-k8s-master-1            4m           21Mi            
kube-system   kube-scheduler-k8s-master-2            5m           21Mi            
kube-system   kube-vip-k8s-master-0                  4m           17Mi            
kube-system   kube-vip-k8s-master-1                  2m           16Mi            
kube-system   kube-vip-k8s-master-2                  2m           17Mi            
kube-system   metrics-server-559f85484-5b6xf         7m           27Mi    
```


#### 10. 为 etcd 添加定期备份能力

>参考 [etcd 的备份与恢复](/datastore/etcd/etcd%20的备份与恢复.md)


