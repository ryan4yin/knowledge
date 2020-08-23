# [rook](https://github.com/rook/rook)

Kubernetes 存储编排工具，这里主要记录 rook-ceph 相关内容。


## 一、使用 rook 在集群内部署 ceph 分布式存储

部署流程中需要使用到 git 仓库中的部分 yaml 配置，请提前拉取仓库：

```shell
git clone --single-branch --branch release-1.4 https://github.com/rook/rook.git
# 后续需要用到的所有 yaml 配置文件都在这个文件夹下
cd rook/cluster/examples/kubernetes/ceph
```

具体而言，需要用到的配置文件大概有：

1. `cluster.yaml`: 创建 ceph cluster
2. `toolbox.yaml`: ceph 的 cli 工具箱，用于操作 ceph
3. `csi/rbd/storageclass.yaml`: 创建 CephBlockPool 和 StorageClass
4. `csi/rbd/pvc.yaml`: 创建 PersistenceVolumeClaim

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

这是因为上面的 `cluster.yaml` 有这样一个配置项：`useAllDevices: true`，于是 rook 会自动发现并使用挂载在 node 的 `/dev` 路径下的裸硬盘（`raw disks`）.

### 4. 问题排查

可以使用 DashBoard 进行问题排查，也可以使用 CLI：

```shell
kubectl apply -f toolbox.yaml
```

之后通过登入 toolbox 容器中，就可以进行问题排查了。


## 二、使用 Ceph 做集群内部的块存储

rook-ceph 部署完成后，要通过它的块存储提供数据卷给容器，配置及依赖关系如下：

```shell
CephBlockPool -> StorageClass -> PersistenceVolumeClaim （动态生成 PersistemceVolume）-> Pod(volume -> volumeMount) 
```

首先创建 CephBlockPool 和 StorageClass:

```shell
# 详细的 yaml 定义请自行查看。
# CephBlockPool 的关键参数：副本个数（一般定义为 3）
# StorageClass 的 reclaimPolicy 为 Delete 时，删除 PVC 会导致数据被删除。
kubectl create -f csi/rbd/storageclass.yaml
```

OK，现在就可以定义 PVC+Pod 来使用这个 storageclass 了。

```shell
cd ..  # cd 到仓库的 cluster/examples/kubernetes 文件夹中

# 创建 mysql 的 pvc+pod
# 需要注意的主要有 pvc 的 Capacity（容量），这里设了 20Gi
kubectl create -f mysql.yaml
# 创建 wordpress 的 pvc+pod
kubectl create -f wordpress.yaml
```

创建完成后，可以通过 k9s/kubectl 查看 default 名字空间中的 PVC 和 Pod 内容。


## 三、注意事项

和状态有关的东西，都比较娇贵。因此服务器的关机、重启、异常宕机，都可能导致 ceph 集群出现问题。
另外 Pod 自身的异常，也可能导致数据损坏。

我测试 rook-ceph 遇到的问题有：

1. [node-hangs-after-reboot](https://rook.io/docs/rook/v1.4/ceph-common-issues.html#node-hangs-after-reboot): 先 drain 掉异常节点，重启节点，最后 uncordon 节点。

可能和我使用的是 centos7(内核版本 3.10) 有关，内核版本太低，导致 rook-ceph 很不稳定，仅测试就出了一堆问题。rook-ceph 写明推荐的内核版本为 `4.17+`
