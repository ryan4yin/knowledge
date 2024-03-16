# Docker

- [docker_practice](https://github.com/yeasy/docker_practice): 最好的中文 docker 教程

## docker-compose

使用最广泛的单机容器编排工具，简单好用。

因为是 python 写的，可以直接通过 `pip install docker-compose` 来安装它。

- [Docker Docs - docker-compose 配置参考](https://docs.docker.com/compose/compose-file/)：此文档也适
  用于 docker-swarm.

`docker-compose` 为容器添加资源限制的方法：

1. 在 `services.<service-name>.deploy.resources` 中设定好资源限制。
2. 通过 `dockere-compose  --compatibility up` 运行。
   1. `--compatibility` 会尝试将 v3 版本的 docker-compose 参数转换成对应的 non-Swarm 版本。

## Docker Swarm Mode

Docker 的最新的容器集群编排工具（前身是 Classic-Swarm 和 SwarmKit），已经被集成进了 docker 本身。它
和 [k3s](https://github.com/rancher/k3s) 一样简单，装上 docker-ce 然后一两行命令就能启动 docker
swarm 集群。基本上全程看 `docker swarm` 命令的提示就行，文档都不需要看。

而它使用的配置文件也是 `docker-compose.yml`，只是多了一些集群相关的参数（scale 等），这类参数在
[Docker Docs - docker-compose 配置参考](https://docs.docker.com/compose/compose-file/) 有专门注明。

### Swarm vs Kubernetes vs Nomad

1. Swarm Mode: 简单方便，功能也够用。适合个人或简单场景下使用。
1. Kubernetes: 功能强大，生态丰富。企业级首选。
   1. [k3s](https://github.com/rancher/k3s): K8s 极简发行版，部署体验和 Swarm 差不多。(类比
      Manjaro - Arch Linux 的省心版)
1. Nomad: 如果嫌 Kubernetes 太重，那可以试试这个。

## Docker 安全设置

为了保证 docker 的安全性，可以进行如下设置：

1. 不要在容器上挂载敏感的主机系统目录
2. 确保docker.sock不被挂载。否则黑客入侵容器后，就能获得 docker 的完全控制权。
3. 限制容器的内存使用量，防止容器进程用尽宿主机内存。
4. 将容器的根文件系统挂载为只读，避免根文件系统被篡改。
5. 避免使用特权容器：容器默认情况下是没有特权的，尽量不要启用特权。
6. 为Docker启用内容信任: 目前镜像已经支持数字签名，可通过签名验证镜像的正确性。

## quay.io/gcr.io/dockerhub.com 的国内镜像

由于 GFW 和国内政策等原因，国内访问上述国际镜像仓库速度堪忧（或者根本无法访问）。

因此使用国内镜像源就显得很有必要了。

1. `k8s.gcr.io`: 替换成 `registry.cn-hangzhou.aliyuncs.com/google_containers/`
2. `docker.io`
   1. 网易镜像源地址：`https://hub-mirror.c.163.com`
   2. [阿里云镜像加速器](https://cr.console.aliyun.com/cn-shenzhen/instances/mirrors)，需要使用阿里
      云账号登录，登录后会给出一个专用加速地址。
3. `quay.io`: 目前国内基本没有镜像源，唯一的一个 USTC 镜像源特别慢，没法用。建议自己架设一个 quay 代
   理。
   1. 2020/12 月更新，目前 quay 在国内速度很快，不需要镜像源/代理了。

以上镜像都不一定长期可用。

参考了
[让 K8S 在国内愉快的航行](https://www.cnblogs.com/ants/p/12663724.html?utm_source=tuicool&utm_medium=referral)。

### 使用 HTTPS 代理拉取镜像

如果没有可用的镜像仓库，可以考虑设置 HTTPS 代理进行镜像拉取。

代理设置方法是在 `/usr/lib/systemd/system/docker.service` 中添加下列三个 PROXY 通用环境变量：

```shell
[Service]
Environment="HTTP_PROXY=http://<proxy-host>:8889"
Environment="HTTPS_PROXY=http://<proxy-host>:8889"
Environment="NO_PROXY=localhost,127.0.0.1,aliyuncs.com"
```

修改好上述的 systemd 配置文件后，重启 docker 服务就能正常使用了：

```shell
sudo systemctl daemon-reload
sudo systemctl restart docker
```

## daemon.json 样例

限制容器日志大小，配置 dockerhub 的国内镜像仓库，信任 harbor 私有镜像仓库。其他参见前面提到的
`Docker 调优`

```json
{
  "oom-score-adjust": -1000,
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "50m",
    "max-file": "1"
  },
  "max-concurrent-downloads": 10,
  "max-concurrent-uploads": 10,
  "insecure-registries": ["image-registry.svc.local"],
  "registry-mirrors": ["https://xd6he1w9.mirror.aliyuncs.com", "https://hub-mirror.c.163.com"],
  "dns": ["114.114.114.114", "119.29.29.29"],
  "storage-driver": "overlay2",
  "storage-opts": ["overlay2.override_kernel_check=true"]
}
```

> 其中的 aliyun 镜像源地址是我使用账号登录阿里云后得到的，使用时不需要任何验证。仅自用。

其中镜像源地址建议配置多个，因为镜像源可能会不够稳定。

另外还是尽量不要使用 `insecure-registries`，可以使用一个私有 TLS 证书进行加密和身份验证，配置方法参
见 [TLS 协议与 TLS 证书的生成、配置](/network-security/TLS%20协议与%20TLS%20证书的生成、配置.md)

### 远程访问 Docker Engine

如果希望能够远程访问（**危险操作！！！**），可以在上述 json 中再添加属性：

```json
{
  "hosts": ["unix:///var/run/docker.sock", "tcp://0.0.0.0:2375"]
}
```

重启后就能通过 `http://<server-ip>:2375` 访问
[docker remote api](https://docs.docker.com/engine/api/latest/) 了。

注意，这种方式暴露出来的 api 没有任何保护！要添加安全防护，请首
先[使用 openssl 生成自己的 tls 证书](https://docs.docker.com/engine/security/https/#create-a-ca-server-and-client-keys-with-openssl)，
然后在 `/etc/docker/daemon.json` 中再添加如下字段：

```json
{
  "tls": true,
  "tlscacert": "/etc/docker/ca.pem",
  "tlscert": "/etc/docker/server.pem",
  "tlskey": "/etc/docker/server-key.pem",
  "tlsverify": true
}
```

客户端需要配置环境变量：

```shell
export DOCKER_HOST=tcp://[your-remote-server-address]:2376
export DOCKER_CERT_PATH=/path/to/cert  # 现在客户端必须使用 tls 证书才能连接上 daemon！
export DOCKER_TLS_VERIFY=1  # 表示要使用 tls 证书进行通信，否则会被 docker engine 拒绝连接
```

详见
[Deploy-and-Secure-a-Remote-Docker-Engine](https://github.com/IcaliaLabs/guides/wiki/Deploy-and-Secure-a-Remote-Docker-Engine)

## Docker 桥接外部网络

使用 macvlan/ipvlan 的网络驱动即可。
