
## Etcd 集群的备份与恢复

>官方文档：[etcd 3.4 - disaster recovery](https://etcd.io/docs/v3.4.0/op-guide/recovery/)

>此文假设你的 Etcd 集群是按 [./etcd_with_systemd.md](./etcd_with_systemd.md) 给出的方法部署的。

如果 ETCD 集群有超过 (N-1)/2 的节点出现临时性故障，那集群将暂时不可用，直到节点个数恢复到超过 (N-1)/2.

而如果有超过 (N-1)/2 的节点出现永久性故障，数据永远丢失，那集群就炸掉了，无法使用，也不可能恢复正常了。

要避免出现这么悲催的事情，唯一的方法就是多备份，定期跑 snapshot 命令备份数据。

这样如果集群永久性损坏，还可以通过 snapshot 将数据恢复到一个新集群上。

### 一、给 Etcd 节点照快照

快照的命令如下:

```shell
export ETCDCTL_API=3
export ENDPOINT=http://127.0.0.1:2379

# 在只选中一个节点时，才可以执行 snapshot 命令
etcdctl --endpoints $ENDPOINT snapshot save snapshot.db
# 查看备份文件的信息
etcdctl --write-out=table snapshot status snapshot.db
```

### 二、恢复单个 Etcd 节点

在集群下线节点数不超过 (N-1)/2 的情况下，集群仍然能正常提供服务。
下线节点如果数据没丢，启动后会自动上线。

而如果数据丢失，节点就必须以新的 member 身份加入，请严格按照如下操作：

- 移除failure节点：使用 `member remove` 命令剔除错误节点。保证当前集群的健康状况
- 彻底清理数据目录：错误节点必须停止，然后删除data dir。保证 `member` 信息被清理干净，清空 `member` 目录
- 集群添加新 member：使用 `member add` 命令添加步骤1的错误节点
- 启动 etcd 服务：确保节点的 `/data/etcd.env` `/data/etcd.service` 以及 etcd/etcdctl 均配置完成，使用 systemd 启动 etcd 服务


```shell
export ETCDCTL_API=3
export ENDPOINT=http://node2:2379

# 列出所有节点，记录下损坏节点的 ID
etcdctl --endpoints $ENDPOINT member list
# 使用你记录下的 ID，从集群中移除该节点
etcdctl --endpoints $ENDPOINT member remove <id>

# 如果你是将原节点重新加入集群，还需要清理干净数据目录
sudo rm -rf /data/etcd.data

# 现在将该节点加入到 etcd 集群，加入成功后，会打印出一系列新节点需要设置的参数
etcdctl --endpoints=$ENDPOINT member add node1 --peer-urls="http://node1:2380"
```

现在根据上一步提供的新参数，修改 `/data/etcd.env`，如果你的主机 IP 没有变更的话，一般只需要修改 `ETCD_INITIAL_CLUSTER_STATE="existing"` 这一个参数。

最后启动 etcd 服务，应该就正常了。

### 三、灾难恢复

在集群下线节点数超过了 (N-1)/2，并且数据永久丢失的情况下，集群将彻底损坏！！！

这时就只能从 snapshot 快照中，恢复集群的所有数据了！恢复流程如下：

对于仍然可用的节点，将旧的数据移动到别的地方，它基本上已经没用了：

```shell
mv /data/etcd.data /data/etcd.data.old
```

然后确保所有节点上都已经配置好了 `/data/etcd.env` 和 `/data/etcd.service`，但是暂时不要启动 etcd 服务！

现在在所有节点上， 分别使用 snapshot 恢复它们的数据目录：

```shell
export ETCDCTL_API=3
# 获取 etcd 的配置信息
source /data/etcd.env

# 使用 snapshot.db 这个快照，将 etcd 数据恢复到 $ETCD_DATA_DIR 这个目录中
etcdctl snapshot restore snapshot.db \
  --name=$ETCD_NAME \
  --initial-cluster "${NAME_1}=http://${HOST_1}:2380,${NAME_2}=http://${HOST_2}:2380,${NAME_3}=http://${HOST_3}:2380" \
  --initial-advertise-peer-urls http://${THIS_IP}:2380 \
  --data-dir=$ETCD_DATA_DIR \
  --initial-cluster-token=$ETCD_INITIAL_CLUSTER_TOKEN
```

现在再使用 systemctl 启动所有的 etcd 服务，集群应该就恢复到了之前的快照状态。

