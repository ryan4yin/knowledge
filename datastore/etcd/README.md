# [ETCD](https://github.com/etcd-io/etcd)

## 搭建 etcd 集群

可以使用本文件夹中的 `docker-compose.yml` 启动一个多节点的 etcd 集群，或者也可以跟随 [使用 systemd 部署三节点的 Etcd 集群](./etcd_with_systemd.md) 这篇文档使用二进制文件部署 Etcd 集群。


```shell
# 连上所有节点，就一定可以找到 leader
HOST_1=xxx
HOST_2=xxx
HOST_3=xxx
export ETCDCTL_API=3
export ENDPOINT=http://$HOST_1:2379
export ENDPOINTS=http://$HOST_1:2379,http://$HOST_2:2379,http://$HOST_3:2379
etcdctl --endpoints $ENDPOINTS endpoint status --write-out=table
```

## 使用 etcdctl 直接修改/查看 kubernetes 数据

>官方文档：[Interacting with etcd](https://etcd.io/docs/v3.4.0/dev-guide/interacting_v3/)

以容器方式部署的 etcd，可以直接通过 `kubectl exec` 进入 etcd 容器执行命令：

```shell
$ kubectl -n kube-system exec -it etcd-<node-name> -- sh
```

然后使用容器中自带的 etcdctl 操作 etcd 数据：

```shell
# 使用最新版的 etcd api
$ export ETCDCTL_API=3
$ etcdctl version
etcdctl version: 3.3.15
API version: 3.3

# kubernetes 的 etcd 默认启用双向 tls 认证
$ cd /etc/kubernetes/pki/etcd/
$ ls
ca.crt  ca.key  healthcheck-client.crt  healthcheck-client.key  peer.crt  peer.key  server.crt  server.key
# 列出所有数据
$ etcdctl --cacert ca.crt --cert peer.crt --key peer.key get / --prefix --keys-only
# 列出所有名字空间
$ etcdctl --cacert ca.crt --cert peer.crt --key peer.key get /registry/namespaces --prefix --keys-only
# 列出所有 deployments
$ etcdctl --cacert ca.crt --cert peer.crt --key peer.key get /registry/deployments --prefix --keys-only
# 查看 kube-system 空间的详细信息
$ etcdctl --cacert ca.crt --cert peer.crt --key peer.key --write-out="json" get /registry/namespaces/kube-system

# （谨慎操作！！！）强制删除名字空间 `monitoring`，有可能导致某些资源无法被 GC。
$ etcdctl --cacert ca.crt --cert peer.crt --key peer.key del /registry/namespaces/monitoring
```

## 密码验证

> https://etcd.io/docs/v3.5/op-guide/authentication/rbac/#enabling-authentication

etcd 支持启用密码验证，在启用之前必须先创建 root 用户，该用户将拥有所有权限。

```shell
# 创建 root 用户
$ etcdctl --cacert ca.crt --cert peer.crt --key peer.key --endpoints $ENDPOINTS user add root
Password of root:

# The root user must have the root role and is allowed to change anything inside etcd.
$ etcdctl --cacert ca.crt --cert peer.crt --key peer.key --endpoints $ENDPOINTS user grant-role root root

# 启用访问认证功能
$ etcdctl --cacert ca.crt --cert peer.crt --key peer.key --endpoints $ENDPOINTS auth enable


# 后续的所有操作都需要使用用户名和密码
$ etcdctl --cacert ca.crt --cert peer.crt --key peer.key --endpoints $ENDPOINTS --user root user list
Password of root:
```

## Etcd 集群运维需知

1. Etcd 集群的节点数量越多，写入速度越慢。因为 raft 协议要求超过 1/2 的节点写入成功，才算是一次成功的写操作。
   1. 因此通常使用 3/5/7 个 etcd 节点。
2. 集群节点在线数低于 1/2，将无法进行写入，也无法进行读取！！！因为任何对集群的读/写操作，都需要超过 1/2 的节点进行确认/完成写入。
   1. [Etcd 的线性一致读](https://zhuanlan.zhihu.com/p/31050303)

官方运维文档：[etcd 3.4 - operations guide](https://etcd.io/docs/v3.4.0/op-guide)

