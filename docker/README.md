# Docker

- [docker_practice](https://github.com/yeasy/docker_practice): 最好的中文 docker 教程
- [Rancher - 主机调优、修改 apt 镜像源、安装 docker](https://docs.rancher.cn/rancher2x/install-prepare/basic-environment-configuration.html#_2-kernel%E6%80%A7%E8%83%BD%E8%B0%83%E4%BC%98)
- [最佳实践 - Docker 调优](https://docs.rancher.cn/rancher2x/install-prepare/best-practices/docker.html)

## docker-compose

- [Docker Docs - docker-compose 配置参考](https://docs.docker.com/compose/compose-file/)


## quay.io/gcr.io/dockerhub.com 的国内镜像

由于 GFW 和国内政策等原因，国内访问上述国际镜像仓库速度堪忧（或者根本无法访问）。

因此使用国内镜像源就显得很有必要了。

1. `gcr.io`: 替换成 `registry.cn-hangzhou.aliyuncs.com/google_containers/`
2. `dockerhub`
   1. 网易镜像源地址：`https://hub-mirror.c.163.com`
   2. [阿里云镜像加速器](https://cr.console.aliyun.com/cn-shenzhen/instances/mirrors)，需要使用阿里云账号登录，登录后会给出一个专用加速地址。
3. `quay.io`: `quay-mirror.qiniu.com`

以上镜像都不一定长期可用。

参考了 [让 K8S 在国内愉快的航行](https://www.cnblogs.com/ants/p/12663724.html?utm_source=tuicool&utm_medium=referral)。


## daemon.json 样例

限制容器日志大小，配置 dockerhub 的国内镜像仓库，信任 harbor 私有镜像仓库。其他参见前面提到的 `Docker 调优`

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
    "insecure-registries" : ["harbor.internal.xxx.com"],
    "registry-mirrors": [
      "https://hub-mirror.c.163.com",
      "https://xd6he1w9.mirror.aliyuncs.com"
    ],
    "storage-driver": "overlay2",
    "storage-opts": [
      "overlay2.override_kernel_check=true"
    ]
}
```

>其中的 aliyun 镜像源地址是我使用账号登录阿里云后得到的，使用时不需要任何验证。仅自用。

其中镜像源地址建议配置多个，因为镜像源可能会不够稳定。

### 远程访问 Docker Engine

如果希望能够远程访问（**危险操作！！！**），可以在上述 json 中再添加属性：

```json
{
    "hosts": ["unix:///var/run/docker.sock", "tcp://0.0.0.0:2375"],
}
```
重启后就能通过 `http://<server-ip>:2375` 访问 [docker remote api](https://docs.docker.com/engine/api/latest/) 了。

注意，这种方式暴露出来的  api 没有任何保护！要添加安全防护，请首先[使用 openssl 生成自己的 tls 证书](https://docs.docker.com/engine/security/https/#create-a-ca-server-and-client-keys-with-openssl)，然后在 `/etc/docker/daemon.json` 中再添加如下字段：

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

详见 [Deploy-and-Secure-a-Remote-Docker-Engine](https://github.com/IcaliaLabs/guides/wiki/Deploy-and-Secure-a-Remote-Docker-Engine)