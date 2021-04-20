## 使用 systemd 部署三节点的 Etcd 集群


### 一、下载 Etcd

参考官方文档，使用如下命令下载：
```shell
ETCD_VER=v3.4.14

DOWNLOAD_URL=https://github.com/etcd-io/etcd/releases/download

curl -L ${DOWNLOAD_URL}/${ETCD_VER}/etcd-${ETCD_VER}-linux-amd64.tar.gz -o /tmp/etcd-${ETCD_VER}-linux-amd64.tar.gz

mkdir -p /tmp/etcd
tar xzvf /tmp/etcd-${ETCD_VER}-linux-amd64.tar.gz -C /tmp/etcd --strip-components=1

mkdir /data/bin
mv /tmp/etcd/etcd* /data/bin
rm -rf /tmp/etcd
```

### 二、部署 Etcd 集群

假设我们把所有数据和配置都存放在 /data 目录下，它可能是一个独立的数据硬盘：


`/data/etcd.env` 内容如下，三个分别节点只有 `ETCD_NAME` 和 `THIS_IP` 两个参数需要修改，其他配置完全一致:

```conf
NAME_1=node1
NAME_2=node2
NAME_3=node3
HOST_1=172.16.238.100
HOST_2=172.16.238.101
HOST_3=172.16.238.102

ETCD_NAME=${NAME_1}
THIS_IP=${HOST_1}

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

ETCD_INITIAL_CLUSTER="${NAME_1}=http://${HOST_1}:2380,${NAME_2}=http://${HOST_2}:2380,${NAME_3}=http://${HOST_3}:2380" 
ETCD_LISTEN_PEER_URLS=http://${THIS_IP}:2380
ETCD_INITIAL_ADVERTISE_PEER_URLS="http://${THIS_IP}:2380"
ETCD_LISTEN_CLIENT_URLS="http://${THIS_IP}:2379"
ETCD_ADVERTISE_CLIENT_URLS="http://${THIS_IP}:2379"
```


`/data/etcd.service` 的内容如下，三个节点的此份配置完全一致，没有任何区别:

```conf
[Unit]
Description=etcd key-value store
Documentation=https://github.com/etcd-io/etcd
After=network.target

[Service]
Type=simple
# EnvironmentFile 不支持使用 ${xxx} 变量插值，这里不适合使用
# EnvironmentFile=/data/etcd.env
# -a 表示传递环境变量
ExecStart=/bin/bash -ac '. /data/etcd.env; /data/bin/etcd'
Restart=always
RestartSec=5s
LimitNOFILE=40000

[Install]
WantedBy=multi-user.target
```

然后在三个节点上分别运行如下指令，即可启动一个 etcd 集群：

```shell
ln -s /data/etcd.service /usr/lib/systemd/system/etcd.service
systemctl daemon-reload
systemctl enable etcd
systemctl start etcd
```


### 三、启动优化

`Type=simple` 模式下，systemd 其实无法获知 etcd 的真正状态，只假设脚本一启动，etcd 就正常运行了。

为了让 etcd 正确通知到 systemd 它的启动状态，可以改用 `Type=notify`，但是这种模式下，就必须使用 `/data/bin/etcd` 自身作为启动程序，不能再使用 `/bin/bash` 了。

示例如下：


`/data/etcd.env` 内容如下，三个分别节点只有 `ETCD_NAME` 和 `THIS_IP` 两个参数需要修改，其他配置完全一致:

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
    --initial-advertise-peer-urls http://${THIS_IP}:2380 \
    --listen-peer-urls http://${THIS_IP}:2380 \
    --advertise-client-urls http://${THIS_IP}:2379 \
    --listen-client-urls http://${THIS_IP}:2379 \
    --initial-cluster "${NAME_1}=http://${HOST_1}:2380,${NAME_2}=http://${HOST_2}:2380,${NAME_3}=http://${HOST_3}:2380"
Restart=always
RestartSec=5s
LimitNOFILE=40000

[Install]
WantedBy=multi-user.target
```

这个方案同时使用了环境变量和命令行两种方式来设置 etcd 参数。

## 参考文档

- [etcd3 multiple nodes - github](https://github.com/etcd-io/etcd/blob/master/contrib/systemd/etcd3-multinode/README.md)
