# [Flux v1](https://github.com/fluxcd/flux)

>Flux 基本没有可视化，目前提供的唯一 UI 还需要用到 grafana，不是很方便。
而且只支持单仓库单集群，可以说是很简陋。

Flux 是一个 K8s 集群的配置同步工具，
它遵循 GitOps 理念，以一个 Git 仓库为数据来源，始终保持集群状态和 Git 仓库中的配置描述一致。

使用了 Flux 之后，集群管理员（一般情况下）就不需要直接通过 `kubectl` 去操控集群了。只需要修改 Git 仓库的配置，然后 Commit+Push，
Flux 就会帮你完成接下来的一切工作。

>[Flux+Flagger+Istio](https://github.com/stefanprodan/gitops-istio)，可以完成应用的自动灰度更新，自动根据监控指标增加灰度或回滚。

## 一、安装 Flux

### 1. 生成 ssh 密钥对

Flux 通过 ssh 协议定时 pull Git 仓库，因此需要首先生成一个密钥对：

```shell
# -t 算法 dsa | ecdsa | ed25519 | rsa
# -m 私钥使用 pem 格式
# -C 描述
ssh-keygen -t cd25519 -f id_rsa_flux -m pem -C "ssh key for flux test"
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

扫描得到的 known_hosts 文件的内容，需要配置在 `custom-values.yaml` 的 `ssh.known_hosts` 属性中，后续部署会使用到这个配置文件。

### 4. 将部署 Flux 部署到集群中

接下来将 flux 部署到一个专用名字空间 `flux` 中，需要提前安装好 `helm3` 和 `fluxctl`

```shell
# 创建名字空间
kubectl create ns flux
# 使用生成好的 SSH 私钥创建 k8s secret，后面 flux 会挂载这个 secret
kubectl create --namespace flux secret generic flux-git-deploy --from-file=identity=id_rsa_flux

# 部署 flux 的自定义资源
kubectl apply -f https://raw.githubusercontent.com/fluxcd/helm-operator/master/deploy/crds.yaml
```

最后使用 helm 进行部署：

```shell
# 下载 flux 的 charts，我们需要修改其中一些配置
helm repo add fluxcd https://charts.fluxcd.io
# 查看历史版本
helm search repo fluxcd/flux -l | head
# 下载并解压 chart
helm pull fluxcd/flux --untar --version 1.5.0

# 查看生成出的 kubernetes yaml 内容
helm template ./flux --namespace flux -f custom-values.yaml > flux-all.yaml


# 安装或更新
helm upgrade --install flux --namespace flux -f custom-values.yaml ./flux

# 卸载
helm uninstall flux --namespace flux
```

部署中用到了自定义配置文件 `custom-values.yaml`，请自行查看详细内容。

接下来可以使用 `fluxctl` 同步仓库配置了：

```shell
# 查看 flux 的 ssh 公钥，验证 ssh 密钥配置正确
fluxctl identity --k8s-fwd-ns flux

# 立即同步 git 仓库配置到 k8s 集群中（默认是 5m 同步一次）
fluxctl sync --k8s-fwd-ns flux

# 查看所有 flux 管理的工作负载
fluxctl list-workloads --all-namespaces
```

现在尝试修改 git 仓库的配置，然后观察 flux 的工作状况。
可以手动修改 flux 的同步间隔以快速查看效果。

修改了 `values.yaml` 或者升级了 flux 版本后，可以通过如下命令快速部署该修改：

```shell
helm upgrade flux --namespace flux -f custom-values.yaml ./flux
```

## 二、使用 Flux

```shell
# 测试阶段可以暴露 api 端口出来，这样不需要 kubeconfig 就能使用 fluxctl
export FLUX_URL=http://flux.k8s.local:3030/api/flux

# 连接 Flux 实例所在的命名空间 flux
fluxctl --k8s-fwd-ns=flux list-workloads
 
# 查询 Flux 使用的 SSH 密钥，flux 容器日志中也可以查看
fluxctl identity --k8s-fwd-ns flux
 
# Flux 同步 git 仓库默认为5分钟，此命令可立即同步
fluxctl sync --k8s-fwd-ns flux
```


