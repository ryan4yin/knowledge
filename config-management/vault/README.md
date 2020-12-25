# [Vault](https://github.com/hashicorp/vault)

Vault 和 Apollo 相比，最大的特点是它对敏感信息的支持非常完善：

1. 支持保存各种自定义信息、自动生成各类密钥，vault 自动生成的密钥还能自动轮转(rotate)
2. 认证方式：支持接入各大云厂商的账号权限体系（比如阿里云RAM子账号体系）或者 LDAP 等进行身份验证，不需要创建额外的账号体系。
3. 密钥引擎：也支持接入各大云厂商的账号体系（比如阿里云RAM子账号体系），实现 APIKey/APISecret 的自动轮转。
4. 支持接入 kubernetes rbac 权限体系，通过 serviceaccount+role 为每个 Pod 单独配置权限。

本文主要介绍 vault 的部署安装，vault 是一个复杂的 secret 工具，其中细节参见 [Vault 基础概念](./Vault%20基础概念.md)

## 一、部署 Vault

### 1. docker-compose 部署

>推荐用于本地开发测试环境，或者其他不需要高可用的环境。

配置参见 [docker-vault](docker-vault/docker-compose.yml)

启动后的初始化流程和 helm 一致，都需要先初始化，再解封。

### 2. 通过 helm 部署 vault 

>推荐用于生产环境

官方建议[通过 Helm 部署 vault](https://www.vaultproject.io/docs/platform/k8s/helm/run)，大概流程：

1. 在 `custom-vaults.yaml` 中添加自定义的 vault 配置，通过 helm 部署。
2. 初始化/解封 vault: vault 安全措施，每次重启必须解封。

vault 支持很多的数据存储方式，简单起见，下面的示例与 Apollo 一样使用 MySQL 做数据存储。

以 mysql 为后端存储的 HA 高可用的 `custom-vault.yaml` 可以在此文件夹中找到。

通过 helm 部署：

```
# 添加 valut 仓库
helm repo add hashicorp https://helm.releases.hashicorp.com
# 查看 vault 版本号
helm search repo hashicorp/vault -l | head
# 下载某个版本号的 vault
helm pull hashicorp/vault --version 0.7.0 --untar
# 安装/升级 valut
helm upgrade --install vault ./vault --namespace vault -f custom-values.yaml
```

### 2. 初始化(initalize)并解封(unseal) vault

>官方文档：[Initialize and unseal Vault - Vault on Kubernetes Deployment Guide](https://learn.hashicorp.com/tutorials/vault/kubernetes-raft-deployment-guide?in=vault/kubernetes#install-vault)

通过 helm 部署 vault，默认会部署一个三副本的 StatefulSet，但是这三个副本都会处于 NotReady 状态，
接下来还需要手动初始化(initalize)并解封(unseal) vault，才能 `Ready`:

1. 第一步：从三个副本中随便选择一个，运行 vault 的初始化命令：`kubectl exec -ti vault-0 -- vault operator init`
   1. 初始化操作会返回 5 个 unseal keys，以及一个 Initial Root Token，这些数据非常敏感非常重要，一定要保存到安全的地方！
2. 第二步：在每个副本上，使用任意三个 unseal keys 进行解封操作。
   1. 一共有三个副本，也就是说要解封 3*3 次，才能完成 vault 的完整解封！

```shell
# 每个实例都需要解封三次！
## Unseal the first vault server until it reaches the key threshold
$ kubectl exec -ti vault-0 -- vault operator unseal # ... Unseal Key 1
$ kubectl exec -ti vault-0 -- vault operator unseal # ... Unseal Key 2
$ kubectl exec -ti vault-0 -- vault operator unseal # ... Unseal Key 3
```

这样就完成了部署，但是要注意，**vault 实例每次重启后，都需要重新解封！也就是重新进行第二步操作！**

### 3. 设置自动解封

每次重启都要手动解封所有 vault 实例，实在是很麻烦，在云上自动扩缩容的情况下，vault 实例会被自动调度，这种情况就更麻烦了。

为了简化这个流程，可以考虑配置 auto unseal 让 vault 自动解封。

自动解封目前有两种方法：

1. 使用阿里云/AWS/Azure 等云服务提供的密钥库来管理 encryption key，阿里云的相关配置方法：[alicloudkms Seal](https://www.vaultproject.io/docs/configuration/seal/alicloudkms)
2. 如果你不想用云服务，那可以考虑 [autounseal-transit](https://learn.hashicorp.com/tutorials/vault/autounseal-transit)


## 二、在 Kubernetes 中使用 vault 注入敏感配置

### 1. 向 vault 中添加敏感信息

vault 提供三种添加/更新敏感信息的方式：Web UI、HTTP API 以及 CLI。

比较方便的自动化方法，应该是使用 vault 的 python sdk: [hvac](https://github.com/hvac/hvac)

Web UI 适合手工操作，sdk 则适合用于搭建与更新测试环境的 vault 配置。

### 2. 将 vault 配置注入到 Pod 中

#### 2.1 部署并配置 vault

前面提到过 vault 支持通过 Kubernetes 的 ServiceAccount + Role 为每个 Pod 单独分配权限。

首先启用启用 Kubernetes 身份验证:

```shell
# 配置身份认证需要在 vault pod 中执行，启动 vault-0 的交互式会话
kubectl exec -n vault -it vault-0 -- /bin/sh
export VAULT_TOKEN='<your-root-token>'
export VAULT_ADDR='http://localhost:8200'
 
# 启用 Kubernetes 身份验证
vault auth enable kubernetes
 
# 添加 vault 用于访问 kube-apiserver API 的配置：jwt 内容、apiserver url、CA证书
vault write auth/kubernetes/config \
    token_reviewer_jwt="$(cat /var/run/secrets/kubernetes.io/serviceaccount/token)" \
    kubernetes_host="https://$KUBERNETES_PORT_443_TCP_ADDR:443" \
    kubernetes_ca_cert=@/var/run/secrets/kubernetes.io/serviceaccount/ca.crt
```

#### 2.2 关联 k8s rbac 权限系统和 vault

接下来需要做的事：

2. 通过 vault policy 定义好每个 role（微服务）能访问哪些资源。
3. 为每个微服务生成一个 role，这个 role 需要绑定对应的 vault policy 及 kubernetes serviceaccount
   1. 这个 role 是 vault 的 kubernetes 插件自身的属性，它和 kubernetes role 没有半毛钱关系。
4. 创建一个 ServiceAccount，并使用这个 使用这个 ServiceAccount 部署微服务

其中第一步和第二步都可以通过 vault api 自动化完成.
第三步可以通过 kubectl 部署时完成。

方便起见，vault policy / role / k8s serviceaccount 这三个配置，都建议和微服务使用相同的名称。

>上述配置中，role 起到一个承上启下的作用，它关联了 k8s serviceaccount 和 vault policy 两个配置。

比如创建一个名为 `my-app-policy` 的 vault policy，内容为:

```hcl
# 命名规则："<engine-name>/data/<path>/*"
path "my-app/data/*" {
   # 只读权限
   capabilities = ["read", "list"]
}
```

然后在 vault 中创建 k8s role `my-app-role`:
1. 关联 k8s default 名字空间中的 serviceaccount `my-app-account`，并创建好这个 serviceaccount.
2. 关联 vault token policy，这就是前面创建的 `my-app-policy`
3. 设置 token period（有效期）

这之后，每个微服务就能通过 serviceaccount 从 vault 中读取 `my-app` 中的所有信息了。

#### 2.3 部署 Pod

>参考文档：https://www.vaultproject.io/docs/platform/k8s/injector

下一步就是将配置注入到微服务容器中，这需要使用到 Agent Sidecar Injector。
vault 通过 sidecar 实现配置的自动注入与动态更新。

具体而言就是在 Pod 上加上一堆 Agent Sidecar Injector 的注解，如果配置比较多，也可以使用 configmap 保存，在注解中引用。

需要注意的是 vault-inject-agent 有两种运行模式：

1. init 模式: 仅在 Pod 启动前初始化一次，跑完就退出（Completed）
2. 常驻模式: 容器不退出，持续监控 vault 的配置更新，维持 Pod 配置和 vualt 配置的同步。

示例：

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  labels:
    app: my-app
  name: my-app
  namespace: default
spec:
  minReadySeconds: 3
  progressDeadlineSeconds: 60
  revisionHistoryLimit: 3
  selector:
    matchLabels:
      app: my-app
  strategy:
    rollingUpdate:
      maxUnavailable: 1
    type: RollingUpdate
  template:
    metadata:
      annotations:
        vault.hashicorp.com/agent-configmap: my-app-vault-config
        vault.hashicorp.com/agent-init-first: 'true'  # 是否提前初始化
        vault.hashicorp.com/agent-inject: 'true'
        vault.hashicorp.com/agent-limits-cpu: 250m
        vault.hashicorp.com/agent-requests-cpu: 100m
        vault.hashicorp.com/secret-volume-path: /app/secrets
      labels:
        app: my-app
    spec:
      containers:
      - image: registry.svc.local/xx/my-app:latest
        imagePullPolicy: IfNotPresent
        # 此处省略若干配置...
      serviceAccountName: my-app-account
```

#### vault agent 配置

vault-agent 的配置，需要注意的有：

1. 如果使用 configmap 提供完整的 `config.hcl` 配置，注意 `agent-init`

vautl-agent 的 template 说明：

目前来说最流行的配置文件格式应该是 json/yaml，以 json 为例，
对每个微服务的 kv 数据，可以考虑将它所有的个性化配置都保存在 `<engine-name>/<service-name>/` 下面，然后使用如下 template 注入配置：

```consul-template
{
    [[ range secrets "<engine-name>/metadata/<service-name>/" ]]
        "[[ printf "%s" . ]]": 
        [[ with secret (printf "<engine-name>/<service-name>/%s" .) ]]
        [[ .Data.data | toJSONPretty ]],
        [[ end ]]
    [[ end ]]
}
```
>template 的详细语法参见: https://github.com/hashicorp/consul-template#secret

>注意：v2 版本的 kv secrets，它的 list 接口有变更，因此在遍历 v2 kv secrets 时，
必须要写成 `range secrets "<engine-name>/metadata/<service-name>/"`，也就是中间要插入 `metadata`。
官方文档完全没提到这一点，我通过 wireshark 抓包调试，对照官方的 [KV Secrets Engine - Version 2 (API)](https://www.vaultproject.io/api-docs/secret/kv/kv-v2) 才搞明白这个。

这样生成出来的内容将是 json 格式，不过有个不兼容的地方：最后一个 secrets 的末尾有逗号 `,`
渲染出的效果示例：

```json
{
    "secret-a": {
  "a": "b",
  "c": "d"
},
    "secret-b": {
  "v": "g",
  "r": "c"
},
}
```

因为存在尾部逗号(trailing comma)，直接使用 json 标准库解析它会报错。
那该如何去解析它呢？我在万能的 stackoverflow 上找到了解决方案：**yaml 完全兼容 json 语法，并且支持尾部逗号！**

以 python 为例，直接 `yaml.safe_load()` 就能完美解析 vault 生成出的 json 内容。
