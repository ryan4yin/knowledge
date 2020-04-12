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
1. `dockerhub`: `https://reg-mirror.qiniu.com` 和 `https://hub-mirror.c.163.com`，以及阿里云镜像加速器（要登录阿里账号）。
1. `quay.io`: `quay-mirror.qiniu.com`

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
      "https://reg-mirror.qiniu.com"
    ],
    "storage-driver": "overlay2",
    "storage-opts": [
      "overlay2.override_kernel_check=true"
    ]
}
```
