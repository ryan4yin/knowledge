# Kubevirt 虚拟化管理平台

> https://kubevirt.io/user-guide/architecture/

KubeVirt 顾名思义，就是用 Kubernetes 来管理虚拟机，它跟 Proxmox VE 以及 Openstack 一样，都是构建在
QEMU-KVM 与 libvirt 之上的虚拟化平台。

据晋涛老师的文章
[耗时 7 年终将虚拟机带入 Kubernetes 世界](https://moelove.info/2023/09/01/%E8%80%97%E6%97%B6-7-%E5%B9%B4%E7%BB%88%E5%B0%86%E8%99%9A%E6%8B%9F%E6%9C%BA%E5%B8%A6%E5%85%A5-Kubernetes-%E4%B8%96%E7%95%8C/)
所言，KubeVirt 已经于 2023 年 7 月发布了 v1.0.0 版本，另一方面我最近又在折腾 Proxmox VE + LUKS 时遇
到许多烦人的问题，于是干脆就决定把 Homelab 从 Proxmox VE 全部迁移到 KubeVirt 上来试试。

## KubeVirt 与传统虚拟化方案的主要区别

优势：

1. 声明式 API，通过 yaml 文件来定义虚拟机的配置，而不是通过图形界面或者命令行工具。

不兼容变更：

1. 虚拟机镜像的用法不一样，它提供这几种方式引入虚拟机的基础镜像
   （[Filesystems, Disks and Volumes](https://kubevirt.io/user-guide/virtual_machines/disks_and_volumes/)）：
   1. 通过 `hostDisk` 指定物理机上的 `.img` 磁盘映像。（这可能会导致无法热迁移？）
   1. 通过 [cdi](https://github.com/kubevirt/containerized-data-importer) 组件从如下几种方式导入镜
      像：
      1. 通过 `dataVolumeTemplates` 导入 qcow2/iso 文件，文件地址为一个 HTTP URL
      1. 在安装好 cdi 并将其 uploadProxy 暴露出来后，可以通过如下命令将 qcow2 镜像上传到一个 pvc
         中：
         - `virtctl image-upload --uploadproxy-url=https://cdi-uploadproxy.exam.com --pvc-name=upload-pvc --pvc-size=10Gi --image-path=./xxx.qcow2`
      1. 从容器镜像仓库拉取镜像，这要求将 qcow2 镜像文件放在容器镜像的 `/disk` 目录下，
1. 存储
   1. 与 K8s Pod 一样，默认不保留状态，重启虚拟机将使数据丢失。需要使用 PVC 来保留数据。
   1. 虚拟机热迁移的前提是，虚拟机的 PVC 必须是 ReadWriteMany 的，也就是说不能使用本地存储了。
1. 网络
   1. KubeVirt 默认使用 k8s 的 Pod 网络（一般都是 overlay 网络），跟物理网络不互通，必须借助
      NodePort/LoadBalancer/Ingress 等方式才能使虚拟机对外可访问。
   1. Pod 网络是动态的，这会导致虚拟机重启和热迁移后 IP 发生改变。

解决方法：

1. 存储：
   1. 使用 Longhorn 等分布式存储系统，或者使用 NFS 等网络存储来提供 ReadWriteMany 的 PVC.
1. 网络：
   1. 使用 flannel/calico/cilium 等网络插件将 pod 网络直接改为 underlay 网络。此方案的缺点是：
      1. 这会导致所有 pod 都直接加入到物理网络中，我的局域网网段需要重新规划才能满足需求。
      1. 它无法解决 IP 变动的问题。
   1. 使用额外的 OVS 网络插件来为虚拟机额外添加一个 underlay 网络接口，并分配一个固定的 IP 地址，这
      样 Pod IP 变动也不会影响虚拟机的访问。

## KubeVirt 的 CRDs

首先是虚拟机：

1. `VirtualMachineInstance`：类似 `Pod` 的资源，它是一个在运行的虚拟机实例，不可关闭。
1. `VirtualMachine`：类似 `spec.replicas = 1` 的 DaemonSet，它保证始终有一个 VirtualMachineInstance
   在运行，并控制它的生命周期（stop/running）。

然后 KubeVirt 也提供了一些类似虚拟机模板的资源：

1. `VirtualMachineInstancetype`: 类似云主机的规格（c7i.2xlarge 这种），定义了虚拟机的 CPU/RAM/磁盘等
   资源大小，`VirtualMachine` 可通过 `spec.instancetype` 引用这个资源来继承这个规格，并且不可修改规
   格中定义的参数。
1. `VirtualMachinePreference`: 定义了一些虚拟机的默认参数，比如默认的硬盘总线、网络模式
   等，`VirtualMachine` 可通过 `spec.preference` 引用这个资源来继承这些默认参数，也可以修改覆盖这些
   默认值。

## 虚拟机镜像上传

> https://kubevirt.io/user-guide/operations/containerized_data_importer/#certificate-signed-by-unknown-authority

TODO

## 访问 VM

```bash
# 查看有哪些 VM
kubectl get vmi -n xxx

# 连接到 VM
virtctl console xxx
```

## 热迁移

> https://kubevirt.io/user-guide/operations/live_migration/

TODO

## 快照备份与恢复

> https://kubevirt.io/user-guide/operations/snapshot_restore_api/

TODO
