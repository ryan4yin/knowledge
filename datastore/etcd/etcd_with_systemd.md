## 使用 systemd 部署三节点的 Etcd 集群

### 一、下载 Etcd

参考官方文档，使用如下命令下载：

```shell
# 运行以下命令前请先退出 root 模式！
ETCD_VER=v3.5.9

# choose either URL
GOOGLE_URL=https://storage.googleapis.com/etcd
GITHUB_URL=https://github.com/etcd-io/etcd/releases/download
DOWNLOAD_URL=${GOOGLE_URL}
TAR_NAME=etcd-${ETCD_VER}-linux-arm64.tar.gz

rm -f /tmp/etcd-${ETCD_VER}-linux-amd64.tar.gz
rm -rf /tmp/etcd-downloaded && mkdir -p /tmp/etcd-downloaded

curl -L ${DOWNLOAD_URL}/${ETCD_VER}/${TAR_NAME} -o /tmp/${TAR_NAME}
tar xzvf /tmp/${TAR_NAME} -C /tmp/etcd-downloaded --strip-components=1
rm -f /tmp/etcd-${ETCD_VER}-linux-amd64.tar.gz

/tmp/etcd-downloaded/etcd --version
/tmp/etcd-downloaded/etcdctl version

mkdir /data/bin
mv /tmp/etcd-downloaded/etcd* /data/bin
rm -rf /tmp/etcd-downloaded
```

### 二、部署 Etcd 集群

假设我们把所有数据和配置都存放在 /data 目录下，它可能是一个独立的数据硬盘：

`/data/etcd.env` 内容如下，三个分别节点只有 `ETCD_NAME` 和 `THIS_IP` 两个参数需要修改，其他配置完全
一致:

```conf
# 不支持使用 ${xxx} 做变量插值！

# 可以考虑设置 TLS 双向认证增强安全性
# ETCD_TRUSTED_CA_FILE="/etc/etcd/etcd-ca.crt"
# ETCD_CERT_FILE="/etc/etcd/server.crt"
# ETCD_KEY_FILE="/etc/etcd/server.key"
# ETCD_PEER_CLIENT_CERT_AUTH=true
# ETCD_PEER_TRUSTED_CA_FILE="/etc/etcd/etcd-ca.crt"
# ETCD_PEER_KEY_FILE="/etc/etcd/server.key"
# ETCD_PEER_CERT_FILE="/etc/etcd/server.crt"

ETCD_INITIAL_CLUSTER_TOKEN=<random_token>
ETCD_INITIAL_CLUSTER_STATE=new
ETCD_DATA_DIR=/data/etcd.data

ETCD_NAME=node1
THIS_IP=172.16.238.100

NAME_1=node1
NAME_2=node2
NAME_3=node3
HOST_1=172.16.238.100
HOST_2=172.16.238.101
HOST_3=172.16.238.102
```

`/data/etcd.service` 的内容如下，三个节点的此份配置完全一致，没有任何区别:

> 为了让 etcd 正确通知到 systemd 它的启动状态，这里用 `Type=notify`，但是这种模式下，就必须使用
> `/data/bin/etcd` 自身作为启动程序

```conf
[Unit]
Description=etcd key-value store
Documentation=https://github.com/etcd-io/etcd
After=network.target

[Service]
Type=notify
EnvironmentFile=/data/etcd.env
# ExecXXX 的命令中是可以使用 ${Xxx} 插值语法的
ExecStart=/data/bin/etcd \
    --listen-client-urls http://${THIS_IP}:2379 \
    --advertise-client-urls http://${THIS_IP}:2379 \
    --listen-peer-urls http://${THIS_IP}:2380 \
    --initial-advertise-peer-urls http://${THIS_IP}:2380 \
    --initial-cluster "${NAME_1}=http://${HOST_1}:2380,${NAME_2}=http://${HOST_2}:2380,${NAME_3}=http://${HOST_3}:2380"
Restart=always
RestartSec=5s
LimitNOFILE=40000

[Install]
WantedBy=multi-user.target
```

然后在三个节点上分别运行如下指令，即可启动一个 etcd 集群：

```shell
# 注意这里不能用 `ln -s`，会导致系统重启后 systemd 无法识别，报很奇怪的错误！
cp /data/etcd.service /usr/lib/systemd/system/etcd.service
systemctl daemon-reload
systemctl enable etcd

# 前两台节点上，这个命令会卡住，因为 etcd 尚未就绪，要等到第三台节点启动后，三台节点才会一起 healthy
systemctl start etcd

systemctl status etcd
```

## 参考文档

- [etcd3 multiple nodes - github](https://github.com/etcd-io/etcd/blob/master/contrib/systemd/etcd3-multinode/README.md)
