# cert-manager 证书管理

>https://github.com/jetstack/cert-manager

cert-manager 用于在 Kubernetes 集群中，自动化颁发与管理各种来源的 TLS 证书。

它将确保证书有效，并在合适的时间自动更新证书。


## 一、部署

>https://cert-manager.io/docs/installation/helm/

官方提供了多种部署方式，使用 helm3 安装的方法如下：


```shell
# 查看版本号
helm search repo jetstack/cert-manager -l | head
# 下载并解压 chart，目的是方便 gitops 版本管理
helm pull jetstack/cert-manager --untar --version 1.8.2
helm install \
  cert-manager ./cert-manager \
  --namespace cert-manager \
  --create-namespace \
  # 这会导致使用 helm 卸载的时候会删除所有 CRDs，可能导致所有 CRDs 资源全部丢失！要格外注意
  --set installCRDs=true
```

## 二、创建 Issuer

### 1. 通过权威机构创建公网受信证书

通过权威机构创建的公网受信证书，可以直接应用在边界网关上，用于给公网用户提供 TLS 加密访问服务，比如各种 HTTPS 站点、API。
这是需求最广的一类数字证书服务。

cert-manager 支持两种申请公网受信证书的方式：

- [ACME（Automated Certificate Management Environment (ACME) Certificate Authority server）](https://en.wikipedia.org/wiki/Automatic_Certificate_Management_Environment)证书自动化申请与管理协议。
- [venafi-as-a-service](https://cert-manager.io/docs/configuration/venafi/#creating-a-venafi-as-a-service-issuer): venafi 是一个证书的集中化管理平台，它也提供了 cert-manager 插件，可用于自动化申请 DigiCert/Entrust/GlobalSign/Let's Encrypt 四种类型的公网受信证书。

这里主要介绍使用 ACMEv2 协议申请公网证书，支持使用此开放协议申请证书的权威机构有：

- 免费服务
  - Let's Encrypt: 众所周知，它提供三个月有效期的免费证书。
  - [ZeroSSL](https://zerossl.com/documentation/acme/):  貌似也是一个比较有名的 SSL 证书服务
    - 通过 ACME 协议支持不限数量的 90 天证书，也支持多域名证书与泛域名证书。
- 付费服务
  - DigiCert: 这个非常有名（但也是相当贵），官方文档 [Digicert - Third-party ACME client automation](https://docs.digicert.com/certificate-tools/Certificate-lifecycle-automation-index/acme-user-guide/)
  - Google Trust Services: Google 推出的公网证书服务，也是三个月有效期，其根证书交叉验证了 GlobalSign。官方文档 [Automate Public Certificates Lifecycle Management via RFC 8555 (ACME)](https://cloud.google.com/blog/products/identity-security/automate-public-certificate-lifecycle-management-via--acme-client-api)
  - Entrust: 官方文档 [Entrust's ACME implementation](https://www.entrust.com/knowledgebase/ssl/how-to-use-acme-to-install-ssl-tls-certificates-in-entrust-certificate-services-apache#step1)
  - GlobalSign: 官方文档 [GlobalSign ACME Service](https://www.globalsign.com/en/acme-automated-certificate-management)

这里也顺便介绍下收费证书服务对证书的分级，以及该如何选用：

- Domain Validated（DV）证书
  - **仅验证域名所有权**，验证步骤最少，价格最低，仅需要数分钟即可签发。
  - 优点就是易于签发，很适合做自动化。
  - 各云厂商（AWS/GCP/Cloudflare，以及 Vercel/Github 的站点服务）给自家服务提供的免费证书都是 DV 证书，Let's Encrypt 的证书也是这个类型。
    - 很明显这些证书的签发都非常方便，而且仅验证域名所有权。
    - 但是 AWS/GCP/Cloudflare/Vercel/Github 提供的 DV 证书都仅能在它们的云服务上使用，不提供私钥功能！
- Organization Validated (OV) 证书
  - 是企业 SSL 证书的首选，通过企业认证确保企业 SSL 证书的真实性。
  - 除域名所有权外，CA 机构还会审核组织及企业的真实性，包括注册状况、联系方式、恶意软件等内容。
  - 如果要做合规化，可能至少也得用 OV 这个级别的证书。
- Extended Validation（EV）证书
  - 最严格的认证方式，CA 机构会深度审核组织及企业各方面的信息。
  - 被认为适合用于大型企业、金融机构等组织或企业。
  - 而且仅支持签发单域名、多域名证书，不支持签发泛域名证书，安全性杠杠的。

ACME 支持 HTTP01 跟 DNS01 两种域名验证方式，其中 DNS01 是最简便的方法。下面以 AWS Route53 为例介绍如何申请一个 Let's Encrypt 证书。

>https://cert-manager.io/docs/configuration/acme/dns01/route53/

#### 1.1 IAM 授权

首先需要为 EKS 集群创建 OIDC provider，参见 [aws-iam-and-kubernetes](./aws-iam-and-kubernetes.md)，这里不再赘述。

cert-manager 需要查询与更新 Route53 记录的权限，因此需要使用如下配置创建一个 IAM Policy，可以命名为 `<ClusterName>CertManagerRoute53Access`（注意替换掉 `<ClusterName>`）：

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": "route53:GetChange",
      "Resource": "arn:aws:route53:::change/*"
    },
    {
      "Effect": "Allow",
      "Action": [
 "route53:ChangeResourceRecordSets",
 "route53:ListResourceRecordSets"
      ],
      "Resource": "arn:aws:route53:::hostedzone/*"
    },
    {
      "Effect": "Allow",
      "Action": "route53:ListHostedZonesByName",
      "Resource": "*"
    }
  ]
}
```

比如使用命令创建：

```shell
aws iam create-policy \
  --policy-name XxxCertManagerRoute53Access \
  --policy-document file://cert-manager-route53-access.json
```

然后通过上述配置创建一个 IAM Role 并自动给 cert-manager 所在的 EKS 集群添加信任关系：

```shell
export CLUSTER_NAME="xxx"
export AWS_ACCOUNT_ID="112233445566"

# 使用 eksctl 自动创建对应的 role 并添加信任关系
eksctl create iamserviceaccount \
  --cluster "${CLUSTER_NAME}" --name cert-manager --namespace cert-manager \
  --role-name "${CLUSTER_NAME}-cert-manager-route53-role" \
  --attach-policy-arn "arn:aws:iam::${AWS_ACCOUNT_ID}:policy/<ClusterName>CertManagerRoute53Access" \
  --role-only \
  --approve
```

之后需要为 cert-manager 的 ServiceAccount 添加注解来绑定上面刚创建好的 IAM Role，首先创建如下 helm values 文件 `cert-manager-values.yaml`:

```yaml
# 如果把这个改成 false，也会导致 cert-manager 的所有 CRDs 及相关资源被删除！
installCRDs: true

serviceAccount:
  annotations:
    # 注意修改这里的 ${AWS_ACCOUNT_ID} 以及 ${CLUSTER_NAME}
    eks.amazonaws.com/role-arn: >-
      arn:aws:iam::${AWS_ACCOUNT_ID}:role/${CLUSTER_NAME}-cert-manager-route53-role

securityContext:
  enabled: true
  # 根据官方文档，还得修改下这个，允许 cert-manager 读取 ServiceAccount Token，从而获得授权
  fsGroup: 1001
```

然后重新部署 cert-manager:

```shell
helm upgrade -i cert-manager ./cert-manager -n cert-manager -f cert-manager-values.yaml
```

这样就完成了授权。

#### 1.2 创建 ACME Issuer

在 xxx 名字空间创建一个 Iusser：

```yaml
apiVersion: cert-manager.io/v1
kind: Issuer
metadata:
  name: letsencrypt-prod
  namespace: xxx
spec:
  acme:
    # 用于接受域名过期提醒的邮件地址
    email: user@example.com
    # ACME 服务器，比如 let's encrypt、Digicert 等
    # let's encrypt 的测试 URL，可用于测试配置正确性
    server: https://acme-staging-v02.api.letsencrypt.org/directory
    # let's encrypt 的正式 URL，有速率限制
    # server: https://acme-v02.api.letsencrypt.org/directory

    # 用于存放 ACME 账号私钥的 Secret 名称，Issuer 创建时会自动生成此 secret
    privateKeySecretRef:
      name: letsencrypt-staging
    
    # DNS 验证设置
    solvers:
    - selector:
        # 在有多个 solvers 的情况下，会根据每个 solvers 的 selector 来确定优先级，选择其中合适的 solver 来处理证书申请事件
        # 以 dnsZones 为例，越长的 Zone 优先级就越高
        # 比如在为 www.sys.exapmle.com 申请证书时，sys.example.org 的优先级就比 example.org 更高
        dnsZones:
        - "example.org"
      dns01:
        # 使用 route53 进行验证
        route53:
          region: us-east-1
          # cert-manager 已经通过 ServiceAccount 绑定了 IAM Role
          # 这里不需要补充额外的 IAM 授权相关信息！
```

#### 1.3 创建 ACME 证书

>https://cert-manager.io/docs/usage/certificate/#creating-certificate-resources

使用如下配置创建证书，并将证书保存到指定的 Secret 中：

```yaml
apiVersion: cert-manager.io/v1
kind: Certificate
metadata:
  name: example-com
  namespace: xxx
spec:
  # Secret names are always required.
  # Istio Gateway/Ingress/Gateway API 都可以通过直接引用这个 secret 来添加 TLS 加密。
  secretName: tls-example.com

  # secretTemplate is optional. If set, these annotations and labels will be
  # copied to the Secret named tls-example.com. These labels and annotations will
  # be re-reconciled if the Certificate's secretTemplate changes. secretTemplate
  # is also enforced, so relevant label and annotation changes on the Secret by a
  # third party will be overwriten by cert-manager to match the secretTemplate.
  secretTemplate:
    annotations:
      my-secret-annotation-1: "foo"
      my-secret-annotation-2: "bar"
    labels:
      my-secret-label: foo

  duration: 2160h # 90d
  renewBefore: 360h # 15d
  # https://cert-manager.io/docs/reference/api-docs/#cert-manager.io/v1.CertificatePrivateKey
  privateKey:
    algorithm: ECDSA  # RSA/ECDSA/Ed25519，其中 RSA 应用最广泛，Ed25519 被认为最安全
    encoding: PKCS1  # 对于 TLS 加密，通常都用 PKCS1 格式
    size: 256  # RSA 默认为 2048，ECDSA 默认为 256，而 Ed25519 不使用此属性！
    rotationPolicy: Always  # renew 时总是重新创建新的私钥
  # The use of the common name field has been deprecated since 2000 and is
  # discouraged from being used.
  commonName: example.com
  # At least one of a DNS Name, URI, or IP address is required.
  dnsNames:
    - example.com
    - '*.example.com'
  isCA: false
  usages:
    - server auth
    - client auth
  # uris:  # 如果想在证书的 subjectAltNames 中添加 URI，就补充在这里
  #   - spiffe://cluster.local/ns/sandbox/sa/example
  # ipAddresses:  # 如果想在证书的 subjectAltNames 添加 ip 地址，就补充在这里
  #   - 192.168.0.5
  subject:
    # 证书的补充信息
    # 字段索引：https://cert-manager.io/docs/reference/api-docs/#cert-manager.io/v1.X509Subject
    organizations:
      - xxx
  # Issuer references are always required.
  issuerRef:
    name: letsencrypt-prod
    # We can reference ClusterIssuers by changing the kind here.
    # The default value is Issuer (i.e. a locally namespaced Issuer)
    kind: Issuer
    # This is optional since cert-manager will default to this value however
    # if you are using an external issuer, change this to that issuer group.
    group: cert-manager.io
```

部署好 Certificate 后，describe 它就能看到当前的进度：

```
Events: 
  Type    Reason     Age   From    Message 
  ----    ------     ----  ----    ------- 
  Normal  Issuing    117s  cert-manager-certificates-trigger   Issuing certificate as Secret does not exist      
  Normal  Generated  116s  cert-manager-certificates-key-manager      Stored new private key in temporary Secret resource "example.com-f044j"     
  Normal  Requested  116s  cert-manager-certificates-request-manager  Created new CertificateRequest resource "example.com-unv3d"   
  Normal  Issuing    20s   cert-manager-certificates-issuing   The certificate has been successfully issued
```

如果发现证书长时间未 Ready，可以参照[官方文档 - Troubleshooting Issuing ACME Certificates](https://cert-manager.io/docs/faq/acme/)，按证书申请流程进行逐层排查：

- 首先 cert-manager 发现 Certificate 描述的 Secret 不存在，于是启动证书申请流程
- 首先生成私钥，存放在一个临时 Secret 中
- 然后通过私钥以及 Certificate 资源中的其他信息，生成 CSR 证书申请请求文件
  - 这也是一个 CRD 资源，可以通过 `kubectl get csr -n xxx` 查看
- 接着将 CSR 文件提交给 ACME 服务器，申请权威机构签发证书
  - 这对应 CRD 资源 `kubectl get order`
- 对于上述 ACME 证书申请流程，Order 实际上会生成一个 DNS1 Challenge 资源
  - 可以通过 `kubectl get challenge` 检查此资源
- challenge 验证通过后会逐层往回走，前面的 Order CSR 状态都会立即变成 valid
- 最终证书签发成功，Certificate 状态变成 Ready，所有 Order CSR challenge 资源都被自动清理掉。

#### 1.4 通过 csi-driver 创建证书

>https://cert-manager.io/docs/projects/csi-driver/

直接使用 `Certificate` 资源创建的证书，会被存放在 Kubernetes Secrets 中，被认为并非足够安全。
而 cert-manager csi-driver 则避免了这个缺陷，具体而言，它提升安全性的做法有：

- 确保私钥仅保存在对应的节点上，并挂载到对应的 Pod，完全避免私钥被通过网络传输。
- 应用的每个副本都使用自己生成的私钥，并且能确保在 Pod 的生命周期中证书跟私钥始终存在。
- 自动 renew 证书
- 副本被删除时，证书就会被销毁

总的说 csi-driver 主要是用来提升安全性的，有需要可以自己看文档，就不多介绍了。

### 2. 通过私有 CA 颁发证书

Private CA 是一种企业自己生成的 CA 证书，通常企业用它来构建自己的 PKI 基础设施。
它颁发的证书仅适合在企业内部使用，必须在客户端安装上这个 CA 证书，才能正常访问由它签名的数字证书加密的 Web API 或者站点。**Private CA 签名的数字证书在公网上是不被信任的**！

cert-manager 提供的 Private CA 服务有：

- [Vault](https://cert-manager.io/docs/configuration/vault/): 鼎鼎大名了，Vault 是一个密码即服务工具，可以部署在 K8s 集群中，提供许多密码、证书相关的功能。
  - 开源免费
- [AWS Certificate Manager Private CA](https://github.com/cert-manager/aws-privateca-issuer): 跟 Vault 的 CA 功能是一致的，区别是它是托管的，由 AWS 负责维护。
  - 每个 Private CA 证书：$400/month
  - 每个签发的证书（仅读取了私钥及证书内容后才会收费）：按梯度一次性收费，0-1000 个以内是 $0.75 每个

TO BE DONE

## cert-manager 与 istio/ingress 等网关集成

cert-manager 提供的 `Certificate` 资源，会将生成好的公私钥存放在 Secret 中，而 Istio/Ingress 都支持这种格式的 Secret，所以使用还是挺简单的。

以 Istio Gateway 为例，直接在 Gateway 资源上指定 Secret 名称即可：

```yaml
apiVersion: networking.istio.io/v1alpha3
kind: Gateway
metadata:
  name: example-gateway
spec:
  selector:
    istio: ingressgateway
  servers:
  - port:
      number: 8080
      name: http
      protocol: HTTP
    hosts:
    - product.example.com
    tls:
      httpsRedirect: true # sends 301 redirect for http requests
  - port:
      number: 8443
      name: https
      protocol: HTTPS
    tls:
      mode: SIMPLE # enables HTTPS on this port
      credentialName: tls-example.com # This should match the Certificate secretName
    hosts:
    - product.example.com # This should match a DNS name in the Certificate
---
apiVersion: networking.istio.io/v1alpha3
kind: VirtualService
metadata:
  name: product
spec:
  hosts:
  - product.example.com
  gateways:
  - example-gateway
  http:
  - route:
    - destination:
        host: product
        port:
          number: 8080
---
apiVersion: v1
kind: Service
metadata:
  labels:
    app: product
  name: product
  namespace: prod
spec:
  ports:
  - name: grpc
    port: 9090
    protocol: TCP
    targetPort: 9090
  - name: http
    port: 8080
    protocol: TCP
    targetPort: 8080
  selector:
    app: product
  sessionAffinity: None
  type: ClusterIP
---
apiVersion: networking.istio.io/v1alpha3
kind: DestinationRule
metadata:
  name: product
spec:
  host: product
  # 定义了两个 subset
  subsets:
  - labels:
      version: v1
    name: v1
  - labels:
      version: v2
    name: v2
---
# 其他 deployment 等配置
```

之后再配合 VirtualService 等资源，就可以将 Istio 跟 cert-manager 结合起来啦。

## 将 cert-manager 证书挂载到自定义网关中

>注意，千万别使用 `subPath` 挂载，根据[官方文档](https://kubernetes.io/docs/concepts/configuration/secret/#mounted-secrets-are-updated-automatically)，这种方式挂载的 Secret 文件不会自动更新！

既然证书被存放在 Secret 中，自然可以直接当成数据卷挂载到 Pods 中，示例如下：

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: nginx
spec:
  containers:
  - name: nginx
    image: nginx:latest
    volumeMounts:
    - name: tls-example.com
      mountPath: "/certs/example.com"
      readOnly: true
  volumes:
  - name: tls-example.com
    secret:
      secretName: tls-example.com
      optional: false # default setting; "mysecret" must exist
```

对于 nginx 而言，可以简单地搞个 sidecar 监控下，有配置变更就 reload 下 nginx，实现证书自动更新。

或者可以考虑直接写个 k8s informer 监控 secret 的变更，有变更就直接 reload 所有 nginx 实例，总之实现的方式有很多种。

## 注意事项

### OCSP 证书验证协议会大幅拖慢 HTTPS 协议的响应速度

如果客户端直接通过 OCSP 协议去请求 CA 机构的 OCSP 服务器验证证书状态，这会大幅拖慢 HTTPS 协议的响应速度，而且 CA 机构的 OCSP 站点本身的性能也会有很大的影响。

解决方法：HTTPS 服务器一定要启用 OCSP stapling 功能，它使服务器提前访问 OCSP 获取证书状态信息并缓存到本地，
在客户端使用 TLS 协议访问时，直接在握手阶段将缓存的 OCSP 信息发送给客户端，这样就完成了证书状态的校验。
因为 OCSP 信息会带有 CA 证书的签名及有效期，服务端不可能伪造它，这样也能确保安全性。
