# Eclipse Che

>本文未考虑国内网络问题，国内环境请自备网络加速手段。

[Eclipse Che](https://github.com/eclipse/che) 是一个基于 [eclipse-theia](https://github.com/eclipse-theia/theia) 的云 IDE 环境。

与单机的 [code-server](https://github.com/coder/code-server)/[eclipse-theia](https://github.com/eclipse-theia/theia) 相比最大的区别在于，Eclipse Che 天然支持多租户，并且充分利用了 Kubernetes 的动态扩缩容能力。
Eclipse Che 默认会为每个用户开辟一个单独的 Namespace 作为 Workspace，用户的数据使用 PVC 存储。

不过企业相关的功能说实话都比较坑，Eclipse Che 不太好装，为了避免重复劳动，我在这里记录下完整顺畅的安装配置流程。

## 1. 为 K8s 配置 OIDC 认证

前面提了 Eclipse Che 天然支持多租户，而这实质是依赖 K8s 的 OIDC Provider 功能。

根据 K8s 官方文档 [Authenticating - Kubernetes](https://kubernetes.io/docs/reference/access-authn-authz/authentication/#openid-connect-tokens) 描述，K8s 中只有两类用户：

- ServiceAccount: 由 K8s 管理与创建，仅提供给 K8s Pod 使用。
- Normal User: K8s 中虽然存在 normal user，但是 k8s 本身并未提供任何相关的实现，也就是说你无法通过 yaml 定义来创建一个 normal user。
  - normal 的创建方式主要有如下几种：
    - 由 K8s 集群的 CA 证书签名的「数字证书」被认为是已被授权的，其 common name(`\CN=ryan`) 就是 normal user 的用户名，其权限由 RBAC 管理，用户可通过「数字证书」+「私钥」来访问集群的资源。
      - kubeadm/k3s 等私有集群部署工具创建的默认 kubeconfig，其实质就是这种类型的用户。
    - 第三方 OIDC Provider 中的用户，可以通过 OIDC 协议登录到集群中，这些用户同样受 RBAC 管理。不过这需要为 kube-apiserver 添加 OIDC 相关参数后重新启动才行。

对于多人组织而言，使用公私钥作为用户凭证对用户的要求较高，所以一般都是使用 OIDC Provider 的方式来实现用户认证。

最常见的 OIDC Provider 是云厂商：Google Accounts、AWS IAM、AliCloud RAM 等，可以直接找找相关的官方文档了解其细节。

对于本地测试而言，我当然更倾向于能自己管理的 OIDC Provider，这里我选择的是 [dex](https://github.com/dexidp/dex)。
dex 主要是一个 OIDC 认证中间件，将 OIDC 认证与其他不支持 OIDC 协议的认证服务（如 LDAP/SAML/Github/...）连接起来。
不过它也支持在配置中定义静态的用户密码，而我正需要这个功能~

### 1.1 部署 cert-manager 并配置 issuer

跟认证有关的接口基本都会强制使用 HTTPS 协议，并且要求证书能通过验证。

dex 官方的 demo 用的是自签名证书，但是我在测试时遇到很多自签名证书的坑，到处都得把这个证书的 CA 证书整过去，所以我建议直接使用 cert-manager 申请受信任的 Web 证书来进行测试，这能减少很多麻烦。

cert-manager 的部署与证书申请方法请直接看我之前的文章 [Kubernetes 中的证书管理工具 - cert-manager](https://thiscute.world/posts/kubernetes-cert-management/)，这里就略过了。

### 1.2 部署 dex

直接参考官方的 k8s 配置，稍作修改即可：[v2.35.3/examples/k8s/dex.yaml](https://github.com/dexidp/dex/blob/v2.35.3/examples/k8s/dex.yaml)

我做的修改有：

- 测试环境不需要这么多实例，改成 1 个副本
- Github 登录暂时不需要，可以删掉相关配置
- 改下 dex 的域名 `dex.example.com`，使用自己的域名。
- tls 证书直接用 cert-manager 申请，不需要用 dex 给的 shell 脚本搞
- 添加 `staticClients` 跟 `staticPasswords` 用于登录测试

`staticClients` 跟 `staticPasswords` 的配置示例如下：

```yaml
    # ......省略前面的若干配置......
    staticClients:
    - id: kubernetes-oidc
      redirectURIs:
      # 这里填写后面要用到的 che 的回调地址，否则回调时会报错说不允许跳转！
      - 'https://ide.writefor.fun/oauth/callback'  # callback url of eclipse-che
      name: 'Kubernetes OIDC'
      secret: xxx  # 这里请自己生成个随机字符密码
    enablePasswordDB: true
    staticPasswords:
    - email: "ryan@writefor.fun"  # 请填写你自己的邮件地址
      # 这里填写密码的 Bcrypt Hash，请用下面的命令生成
      # echo mypassword | htpasswd -BinC 10 admin | cut -d: -f2
      hash: "$2y$10$Hb.iYiPXMUplO8DakqrTQO9qnEpvngsTx1CKVTF3oVS2HoBrLvym."
      username: "ryan"
      userID: "08a8684b-db88-4b73-90a9-3cd1661f1233"  # ID 请随便改改
```

改完后直接部署，Dex 的部署就完成了。


### 1.3 为 kube-apiserver 添加 OIDC 配置

根据 [Kubernetes Authentication Through Dex](https://dexidp.io/docs/kubernetes/) 描述，需要为 kube-apiserver 添加一些 OIDC 相关参数。

我是使用 K3s 搭建的单节点集群，直接改主节点的 `/etc/systemd/system/k3s.service` 即可，修改后的内容如下：

```conf
# sudo vim /etc/systemd/system/k3s.service
# ......前面省略若干配置......
ExecStart=/usr/local/bin/k3s \
    server \
    --write-kubeconfig-mode=644 \
    --kube-apiserver-arg=oidc-issuer-url='https://dex.writefor.fun:32000' \
    --kube-apiserver-arg=oidc-client-id=kubernetes-oidc \
    --kube-apiserver-arg=oidc-ca-file=/etc/ssl/certs/ca-certificates.crt \
    --kube-apiserver-arg=oidc-username-claim=email \
    --kube-apiserver-arg=oidc-username-prefix=- \
    --kube-apiserver-arg=oidc-groups-claim=groups
```

简单解释下：

1. `oidc-issuer-url`: 很好理解，就 dex 的 API 地址
2. `oidc-client-id`: 跟前面的 `staticClients` 一致就行
3. `oidc-ca-file`: 即 dex API 的 CA 证书地址，由于我是直接使用 cert-manager 申请的 letsenctypt 证书，直接使用 ubuntu 的系统根证书即可，ubuntu 系统根证书地址为 `/etc/ssl/certs/ca-certificates.crt`
   1. 如果你是自签名证书，这里就需要配置为你自签名证书的 CA 证书地址。
4. `oidc-username-claim`: 设为 `email` 表示直接使用 oidc 用户的 `email` 作为用户名
   1. 在我这的配置示例中，k8s 的 username 就对应前面 `staticPasswords` 中设置的 `email`: `ryan@writefor.fun`

改完后重启下 k3s master:

```shell
sudo systemctl daemon-reload
sudo systemctl restart k3s
```

这样就大功告成了。

## 2. 使用 chectl 安装 che-operator 与 che

>官方文档：<https://www.eclipse.org/che/docs/stable/administration-guide/installing-che/>

首先安装 chectl 命令行工具：

```shell
bash <(curl -sL  https://www.eclipse.org/che/chectl/)
# 或者在 github release 页自行下载安装：https://github.com/che-incubator/chectl/releases
```

然后编写如下自定义 patch 配置 `che-patch.yml`:

```yaml
kind: CheCluster
apiVersion: org.eclipse.che/v2
spec:
  networking:
    annotations:
      # 我的 k3s 使用 traefik 作为 ingress controller，需要使用这个注解
      kubernetes.io/ingress.class: traefik
    auth:
      gateway:
        configLabels:
          app: che
          component: che-gateway-config
      
      # 如下三个参数跟 kube-apiserver/dex 的设置一致即可
      identityProviderURL: https://dex.writefor.fun:32000
      oAuthClientName: kubernetes-oidc
      oAuthSecret: xxx
    
    # tls 证书名称，如果不存在，che-operator 会自动生成此 tls secret
    ## 如果使用 cert-manager 生成这个证书，一定要加上这个 label:
    ##    `app.kubernetes.io/part-of: che.eclipse.org`
    ## 否则 che-operator 会不断尝试自动生成 tls secret，并一直失败
    tlsSecretName: ide.writefor.fun.tls
  components:
    cheServer:
      debug: false
      extraProperties:
        # 这里要跟 kubernetes 一致，都使用 email 作为 username
        CHE_OIDC_USERNAME__CLAIM: email
        # admin 用户名称
        CHE_SYSTEM_ADMIN__NAME: ryan@writefor.fun
      logLevel: INFO
    dashboard: {}
    database:
      credentialsSecretName: postgres-credentials
      externalDb: false
      postgresDb: dbche
      postgresHostName: postgres
      postgresPort: "5432"
      pvc:
        claimSize: 1Gi
    devWorkspace: {}
    devfileRegistry: {}
    imagePuller:
      enable: false
      spec: {}
    metrics:
      enable: true
  devEnvironments:
    # 可通过此参数修改默认编辑器
    defaultEditor: che-incubator/che-code/insiders
    defaultNamespace:
      autoProvision: true
      template: che-work-<username>  # 自定义 namespace 的名称格式
    disableContainerBuildCapabilities: true
    secondsOfInactivityBeforeIdling: 1800
    secondsOfRunBeforeIdling: -1
    storage:
      pvcStrategy: per-user
```

改好后直接通过如下命令安装：

```shell
chectl server:deploy --platform k8s --domain ide.writefor.fun \
  --che-operator-cr-patch-yaml che-patch.yaml \
  --skip-cert-manager \
  --skip-oidc-provider-check
```

其中有两个参数需要解释下：

1. `--skip-cert-manager`
   1. 前面已经手动安装过 cert-manager 了，所以这里直接跳过。
2. `--skip-oidc-provider-check`
   1. chectl 检测 oidc 配置的方法是 [`kube.getPodListByLabel('kube-system', 'component=kube-apiserver')`](https://github.com/che-incubator/chectl/blob/7.56.0/src/commands/server/deploy.ts#L376)，而 k3s 的 kube-apiserver 并不以 pod 方式运行，这导致即使已经正确配置了 oidc 参数，检测仍然会失败
   2. 因此必须加这个参数跳过有缺陷的 oidc provider 检查

安装完成后配置好域名解析，直接访问 `https://ide.writefor.fun`，应该就会跳转到 dex 登录界面，输入正确的邮件地址与密码即可登录。

## 常见问题

1. 登录报错 `Login Failed: Unable to find a valid CSRF token. Please try again. `: 
   1. 把 cookie/session 清理掉，换个新页面，或者点击重新登录，多试几次就进来了，原因不明...
2. `User cannot list resource "devworkspaces" in API group "workspace.devfile.io" in the namespace`: 登录后报错没权限 `401`
   1. 这大概率是 k8s 的 RBAC 授权问题，首先检查为用户新建的名字空间的 `rolebinding` 的 user 名称是否正常，比如我前面的示例中，rolebinding 的 user 应该为 `ryan@writefor.fun`
   2. 检查 kube-apiserver 的日志，看看是否有授权失败的日志。如果有，那基本能确认是 apiserver 的配置不正确，请仔细检查看看（比如说 CA 证书是否配对了呢？）。

