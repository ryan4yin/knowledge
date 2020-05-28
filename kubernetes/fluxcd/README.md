# [Flux](https://github.com/fluxcd/flux)

Flux 是一个 K8s 集群的配置同步工具，
它遵循 GitOps 理念，以一个 Git 仓库为数据来源，始终保持集群状态和 Git 仓库中的配置描述一致。

使用了 Flux 之后，集群管理员（一般情况下）就不需要直接通过 `kubectl` 去操控集群了。只需要修改 Git 仓库的配置，然后 Commit+Push，
Flux 就会帮你完成接下来的一切工作。

>[Flux+Flagger+Istio](https://github.com/stefanprodan/gitops-istio)，可以完成应用的自动灰度更新，自动根据监控指标增加灰度或回滚。

## 一、安装使用 Flux

### 1. 生成 ssh 密钥对

Flux 通过 ssh 协议定时 pull Git 仓库，因此需要首先生成一个密钥对：

```shell
ssh-keygen -C "ssh key for flux test" -f id_rsa_flux
```

直接回车跳过 `passphrase` （密钥的密码）的设置，然后当前目录下就会多出如下两个文件：

```
id_rsa_flux  id_rsa_flux.pub
```

以 `.pub` 结尾的是公钥，另一个是私钥。私钥请妥善保管，千万别泄漏了！

### 2. 新建 Git 配置仓库，配置 SSH 公钥

>注：Gitee 码云的「部署公钥(Deploy Keys)」不支持写入，你可能需要配置账户全局的 SSH 公钥。

在 Github/Gitlab/Gitee 或者你私有的 Git 平台中新建一个专门存放 Kubernetes 集群配置的仓库（可以使用 [flux-get-started](https://github.com/fluxcd/flux-get-started) 中的配置进行测试），
同时在「Settings」-「Deploy Keys」设置仓库专属的 SSH 公钥。


### 3. 扫描 Git 平台的 SSH 指纹

SSH 协议会使用 SSH 指纹对服务端进行验证，防止中间人攻击。
但是 Flux 只内置了 Github/Gitlab/BitBukit 等平台的 SSH 指纹，如果你使用的 Git 服务不在该范围内（比如私有 Git 仓库、国内的 Gitee 等），
那就需要手动将仓库的指纹添加到 Flux 的配置中。

通过如下命令扫描出指纹：

```shell
# 请替换示例域名
ssh-keyscan gitlab.svc.local >> known_hosts
```

### 4. 将部署 Flux 部署到集群中

接下来将 flux 部署到一个专用名字空间 `flux` 中，需要提前安装好 `helm3` 和 `fluxctl`

```shell
# 创建名字空间
kubectl create ns flux
# 使用生成好的 SSH 私钥创建 k8s secret，后面 flux 会挂载这个 secret
kubectl create --namespace flux secret generic flux-git-deploy --from-file=identity=id_rsa_flux

# 下载 flux 的 charts，我们需要修改其中一些配置
helm repo add fluxcd https://charts.fluxcd.io
helm pull fluxcd/flux --untar  # 下载并解压 chart
cd flux  # 进入 chart 文件夹修改 values.yaml
```

`values.yaml` 需要修改如下这些属性（略过了不需要修改的部分）：

```yaml
git:
  # URL of git repo with Kubernetes manifests; e.g. git.url=ssh://git@github.com/fluxcd/flux-get-started
  url: "ssh://git@github.com/fluxcd/flux-get-started"
  # Branch of git repo to use for Kubernetes manifests
  branch: "master"
  # Path within git repo to locate Kubernetes manifests (relative path)
  path: "workloads"
  # Set to `true` if you intend for Flux to not be able to push changes to git.
  # Also configure state.mode to `secret` since storing state in a git tag will no longer be possible.
  readonly: false
  # Username to use as git committer
  user: "Weave Flux"
  # Email to use as git committer
  email: "support@weave.works"
  # Period at which to poll git repo for new commits
  pollInterval: "5m"
  # Duration after which git operations time out
  timeout: "20s"
  # The secret name can be used to supply your own SSH key, instead of
  # relying on Flux to generate one for you:
  # 1. Generate a SSH key named identity: ssh-keygen -q -N "" -f ./identity
  # 2. Create a Kubernetes secret: kubectl -n flux create secret generic flux-ssh --from-file=./identity
  # 3. Delete the private key: rm ./identity
  # 4. Add ./identity.pub as a deployment key with write access in your Git repo
  # 5. Set the secret name (flux-ssh) below
  secretName: "flux-git-deploy"  # 和前面使用 ssh key 创建的 secret 名称一致


# SSH 主机指纹
ssh:
  # 这里填之前扫描得到的 known_hosts 文件的内容，注意多行文字要缩进两个空格。
  # 这里我以 gitlab 为例，请使用自己的 known_hosts 替换掉它！
  known_hosts: |
    github.com ssh-rsa AAAAB3NzaC1yc2EAAAABIwAAAQEAq2A7hRGmdnm9tUDbO9IDSwBK6TbQa+PXYPCPy6rbTrTtw7PHkccKrpp0yVhp5HdEIcKr6pLlVDBfOLX9QUsyCOV0wzfjIJNlGEYsdlLJizHhbn2mUjvSAHQqZETYP81eFzLQNnPHt4EVVUh7VfDESU84KezmD5QlWpXLmvU31/yMf+Se8xhHTvKSCZIFImWwoG6mbUoWf9nzpIoaSjB+weqqUUmpaaasXVal72J+UX2B+2RPW3RcT0eOzQgqlJL3RKrTJvdsjE3JEAvGq3lGHSZXy28G3skua2SmVi/w4yCE6gbODqnTWlg7+wC604ydGXA8VJiS5ap43JXiUFFAaQ==
    gitlab.com ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQCsj2bNKTBSpIYDEGk9KxsGh3mySTRgMtXL583qmBpzeQ+jqCMRgBqB98u3z++J1sKlXHWfM9dyhSevkMwSbhoR8XIq/U0tCNyokEi/ueaBMCvbcTHhO7FcwzY92WK4Yt0aGROY5qX2UKSeOvuP4D6TPqKF1onrSzH9bx9XUf2lEdWT/ia1NEKjunUqu1xOB/StKDHMoX4/OKyIzuS0q/T1zOATthvasJFoPrAjkohTyaDUz2LN5JoH839hViyEG82yB+MjcFV5MU3N1l1QL3cVUCh93xSaua1N85qivl+siMkPGbO5xR/En4iEY6K2XPASUEMaieWVNTRCtJ4S8H+9
    gitlab.com ecdsa-sha2-nistp256 AAAAE2VjZHNhLXNoYTItbmlzdHAyNTYAAAAIbmlzdHAyNTYAAABBBFSMqzJeV9rUzU4kWitGjeR4PWSa29SPqJ1fVkhtj3Hw9xjLVXVYrU9QlYWrOLXBpQ6KWjbjTDTdDkoohFzgbEY=
    gitlab.com ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIAfuCHKVTjquxvt6CM6tdG4SLp1Btn/nOeHHE5UOzRdf

# 如果你使用的镜像仓库不是 dockerhub，就关掉镜像仓库的扫描 
registry:
  disableScanning: true
memcached:  # 镜像仓库元信息存放位置，关掉
  enabled: false

# 其他参数请按需修改
```

最后使用 helm 进行部署：

```shell
helm install flux . --namespace flux
```

接下来可以使用 `fluxctl` 同步仓库配置了：

```shell
# 查看 flux 的 ssh 公钥，验证 ssh 密钥配置正确
fluxctl identity --k8s-fwd-ns flux

# 立即同步 git 仓库配置到 k8s 集群中（默认是 5m 同步一次）
fluxctl sync

# 查看所有 flux 管理的工作负载
fluxctl list-workloads --all-namespaces
```

现在尝试修改 git 仓库的配置，然后观察 flux 的工作状况。
可以手动修改 flux 的同步间隔以快速查看效果。

修改了 `values.yaml` 后可以通过如下命令快速部署该修改：

```shell
helm upgrade flux . --namespace flux
```

## 二、flux 升级

使用 helm 升级 flux 自身。

待续


