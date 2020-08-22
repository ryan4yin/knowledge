# [rook](https://github.com/rook/rook)

Kubernetes 存储编排工具。


## 使用 rook 在集群内部署 ceph 分布式存储

首先，使用 helm 部署 ceph-operator:

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

ceph 和 kubernetes 存储组件的很多镜像都托管在 quay.io 中，因此在安装 chart 前，可以考虑先使用 [container/sync_images.py](/container/sync_images.py) 通过代理下载 quay 镜像，导入到所有 worker 节点。
