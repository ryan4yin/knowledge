# [rook](https://github.com/rook/rook)

Kubernetes 存储编排工具。


## 使用 rook 在集群内部署 ceph 分布式存储

### 1. 预留存储空间

In order to configure the Ceph storage cluster, at least one of these local storage options are required:

1. Raw devices (no partitions or formatted filesystems)
2. Raw partitions (no formatted filesystem)
1. PVs available from a storage class in block mode

我特意为所有 worker 节点分别添加了一个 20G 的硬盘:

```shell
$ lsblk
NAME                                                                                                 MAJ:MIN RM  SIZE RO TYPE MOUNTPOINT
sr0                                                                                                   11:0    1 1024M  0 rom  
vda                                                                                                  252:0    0   20G  0 disk 
├─vda1                                                                                               252:1    0    1G  0 part /boot
└─vda2                                                                                               252:2    0   19G  0 part 
  ├─centos-root                                                                                      253:0    0   17G  0 lvm  /
  └─centos-swap                                                                                      253:1    0    2G  0 lvm  
vdb                                                                                                  252:16   0   20G  0 disk 
```

上面的 vdb 就是我新加的裸硬盘。

### 2. 部署 ceph-operator

使用 helm 部署 ceph-operator:

```sehll
# 1. 创建名字空间
kubectl create ns rook-ceph

# 2. 获取 helm chart
helm repo add rook-release https://charts.rook.io/release
helm pull rook-release/rook-ceph --untar # 下载并解压 chart

# 3. 查看 chart 的 values.yaml 内容，将需要自定义的参数写入 self-values.yaml 中

# 4. 安装 chart
helm install --namespace rook-ceph rook-release/rook-ceph -f self-values.yaml
```

> 注意：ceph 和 kubernetes 存储组件的很多镜像都托管在 quay.io 中，因此在安装 chart 前，可以考虑先使用 [container/sync_images.py](/container/sync_images.py) 通过代理下载 quay 镜像，导入到所有 worker 节点。

### 3. 创建 ceph cluster

使用 [cluster.yaml] 创建一个生产级别的 ceph cluster:

```shell
wget https://raw.githubusercontent.com/rook/rook/release-1.4/cluster/examples/kubernetes/ceph/cluster.yaml
kubectl apply -f cluter.yaml
```

集群创建完成后，应该能观察到新创建了 rook-ceph-mon, rook-ceph-mgr, rook-ceph-osd 三类 Pod。

现在可以将 Service `rook-ceph-mgr-dashboard` 修改为 NodePort 暴露到外部，然后就能通过 HTTPS 协议访问 Ceph 的 Dashboard 页面了。
Dashboard 的管理员账号是 `admin`，密码在 Secret `rook-ceph-dashboard-password` 中，查看命令：

```shell
kubectl -n rook-ceph get secret rook-ceph-dashboard-password -o jsonpath="{['data']['password']}" | base64 --decode && echo
```

DashBoard 应该显示 HEALTH_OK。

现在再查看各 worker 节点上的硬盘状态，会发现原来的裸磁盘已经被 ceph 使用了：

```shell
$  lsblk
NAME                                                                                                 MAJ:MIN RM  SIZE RO TYPE MOUNTPOINT
sr0                                                                                                   11:0    1 1024M  0 rom  
vda                                                                                                  252:0    0   20G  0 disk 
├─vda1                                                                                               252:1    0    1G  0 part /boot
└─vda2                                                                                               252:2    0   19G  0 part 
  ├─centos-root                                                                                      253:0    0   17G  0 lvm  /
  └─centos-swap                                                                                      253:1    0    2G  0 lvm  
vdb                                                                                                  252:16   0   20G  0 disk 
└─ceph--70212ffb--ab90--40d6--b574--3c8a3c698ea1-osd--data--7b6eafa3--a0c2--474f--a865--eb0767390c91 253:2    0   20G  0 lvm  
```
