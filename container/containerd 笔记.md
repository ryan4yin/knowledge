# [containerd](https://github.com/containerd/containerd)

在 kubernetes 中使用 dockerd 做运行时，本身是不必要的。

越过 dockerd，直接使用它底层的 containerd 做运行时，削减中间环节，可以提升代码的可维护性，减少 Bug.

各家大厂早就将运行时切换到了 containerd，对安全要求更高的甚至已经切换到了 kata-containers 等安全容器方案。

为此有必要尽快熟悉 containerd，将集群尽快迁移过来。


## 安装与配置

>注意 contaienrd 不会读取 docker 的配置！原来给 docker 配的 `/etc/docker/daemon.json` 已经没用了！

containerd 的默认配置文件位置为 `/etc/containerd/config.toml`，详见

- [containerd for Ops and Admins](https://github.com/containerd/containerd/blob/master/docs/ops.md)

### 1. 配置私有仓库

我们从私有镜像仓库拉取镜像，通常会遇到 tls 证书不可信的问题，镜像仓库的私钥/insecure 配置的文档为：

- [registry - cri-containerd](https://github.com/containerd/cri/blob/master/docs/registry.md)

文档中写到，若要使用私钥连接私有仓库，可向 `/etc/containerd/config.toml` 中添加如下内容：

```toml
# explicitly use v2 config format
version = 2

# The registry host has to be a domain name or IP. Port number is also
# needed if the default HTTPS or HTTP port is not used.
[plugin."io.containerd.grpc.v1.cri".registry.configs."my.custom.registry".tls]
    ca_file   = "ca.pem"
    # 如下密钥对用于双向 TLS 认证，如果不支持 mTLS，请去掉它们
    cert_file = "cert.pem"
    key_file  = "key.pem"
```

如果要跳过 TLS 验证，要添加的配置内容如下：

```toml
# explicitly use v2 config format
version = 2

[plugin."io.containerd.grpc.v1.cri".registry.configs."my.custom.registry".tls]
  insecure_skip_verify = true
```

>注：我们发现 v2 版的 config.toml 设置 `insecure_skip_verify` 时，如果 registry 名称带端口，比如 `resigtry.svc.local:8443`，就无法生效。。退回使用 v1 版的配置，就没问题。

### 2. 配置仓库镜像

在国内的特殊环境下，我们经常需要为 `k8s.gcr.io` 等仓库配置国内镜像，配置如下：

```toml
version = 2

# The 'plugins."io.containerd.grpc.v1.cri"' table contains all of the server options.
[plugins."io.containerd.grpc.v1.cri"]

  # sandbox_image is the image used by sandbox container.
  # 注：此镜像不会走 mirrors！
  sandbox_image = "registry.aliyuncs.com/google_containers/pause:3.2"

[plugin."io.containerd.grpc.v1.cri".registry.mirrors]
  [plugin."io.containerd.grpc.v1.cri".registry.mirrors."docker.io"]
    endpoint = ["https://hub-mirror.c.163.com"]
  [plugin."io.containerd.grpc.v1.cri".registry.mirrors."test.https-registry.io"]
    endpoint = ["https://HostIP1:Port1"]
  # wildcard matching is supported but not required.
  [plugin."io.containerd.grpc.v1.cri".registry.mirrors."*"]
    endpoint = ["https://HostIP3:Port3"]
```


## 常用命令

命令行工具这方面现在主要有三个选择：

- containerd 提供的 `ctr`: 很难用，直接排除
- CRI 提供的 `crictl` 稍微好用一点点，可以考虑
- containerd 开发的新工具 `nerdctl`: 好用，强烈推荐

### crictl

其命令行参数和 `docker-cli` 基本一致，但是:

1. 只提供和容器/镜像相关的命令，并添加了 pod 相关命令
2. 不支持 build 镜像，作为单纯的 k8s 运行时调试工具，不需要提供这个功能

crictl 支持连接任何兼容 cri 的运行时，它默认情况下按顺序尝试连接如下几个 endpoint(on linux):

- `unix:///var/run/dockershim.sock`
- `unix:///run/containerd/containerd.sock`
- `unix:///run/crio/crio.sock`

endpoint 也可以通过命令行参数/环境变量/配置文件手动设置，详见 [docs/crictl](https://github.com/kubernetes-sigs/cri-tools/blob/master/docs/crictl.md)


### [nerdctl](https://github.com/containerd/nerdctl)

nerdctl 提供和 docker 完全兼容的指令，而且支持 docker-compose.yml（`nerdctl compose up`） 及其中的大部分参数。

注意点：
- nerdctl 对网络的支持不如 docker
- nerdctl 与 kubernetes 的容器、镜像是隔离的，使用 nerdctl 查看不了 kubernetes 的容器与镜像，反之亦然。



