
# TLS 协议

我们需要加密网络数据以实现安全通信，但是有一个现实的问题：

1. 非对称加密算法可以方便地对数据进行签名/验证，但是计算速度慢。
2. 对称加密算法（ChaCha20/AES 等）计算速度快，强度高，但是无法安全地生成与保管密钥。

于是 TLS 协议在握手阶段使用非对称算法验证服务端，并安全地生成一个对称密钥，然后使用对称算法进行加密通信。

TLS 通过两个证书来实现服务端身份验证，以及对称密钥生成：

1. CA 证书（公钥）：浏览器/操作系统自带，用于验证服务端的 TLS 证书的签名。保证服务端证书可信。
2. TLS 证书：使用 CA 证书验证了 TLS 证书后，将使用这个 TLS 证书进行协商，以安全地生成一个对称密钥。

CA 证书和 TLS 证书，都只在 TLS 握手阶段有用到，之后的通信就与它们无关了。

## 一、TLS 证书的生成

>[OpenSSL](https://github.com/openssl/openssl) 是目前使用最广泛的网络加密算法库，这里以它为例介绍证书的生成。

首先说明一下，一个 TLS 证书，由两部分组成：

1. TLS 证书：这个是服务端需要配置的数据加密证书。
2. CA 证书：这是根证书，可用于验证所有使用它进行签名的 TLS 证书。

CA 证书的私钥由权威机构持有，客户端则保有 CA 证书的公钥。
在 TLS 连接的建立阶段，客户端（如浏览器）会使用 CA 证书的公钥对服务端的证书签名进行验证，验证成功则说明该证书是受信任的。

如果我们要生成一个面向公共网络的 TLS 证书，那最好的方法，应该是申请一个 [Let's Encrypt 免费证书](https://letsencrypt.org)。
该证书可以手动申请，另外 [Traefik](/network-proxy+web-server/traefik/README.md) 等反向代理也有提供自动生成并更新 TLS 证书的功能。

### 生成自签名证书（或由本地证书签名的证书）

除了公网可用的受信证书，在内网环境，我们需要也使用 TLS 证书保障通信安全，这时我们可能会选择自己生成证书，而不是向权威机构申请证书。
可能的原因如下：

1. 要向权威机构申请证书，那是要给钱的。而在内网环境下，并无必要使用权威证书。
2. 内网环境使用的可能是非公网域名（`xxx.local`/`xxx.lan`/`xxx.srv` 等），权威机构不签发这种域名的证书。（因为没有人唯一地拥有这个域名）

自己生成的证书有两种方类型：

1. 自签名证书（我签我自己）：即 TLS 和 CA 使用同一个密钥，使用 TLS 证书对它自己进行签名。
2. 由本地证书签名的证书：生成两个独立的密钥，一个用作 CA 证书，一个用作 TLS 证书。使用 CA 证书对 TLS 证书进行签名。

一般来说，直接生成一个泛域名的自签名证书就够了，但是它不方便拓展——客户端对每个自签名证书，都需要单独添加一次信任。
而第二种方法生成的证书就没这个问题。

总的来说，使用自签名证书不方便进行拓展，未来可能会遇到麻烦。因此建议使用第二种方法。


另外介绍下这里涉及到的几种文件类型：

1. `xxx.key`: 就是一个私钥，一般是一个 RSA 私钥(SHA256 算法)，长度通常指定为 2048 位。
   - openssl 命令：`openssl genrsa -out xxx.key 2048`
   - CA 证书和 TLS 证书的私钥都是通过这种方式生成的。
1. `xxx.csr`: 即 Certificate Sign Request，证书签名请求。使用 openssl 等工具，通过 TLS 密钥+TLS 证书的相关信息，可生成出一个 CSR 文件。
   - openssl 命令：`openssl req -new -key server.key -out server.csr -config csr.conf`，给定 TLS 密钥 `server.key` 以及证书相关信息 `csr.conf`
   - 域名（Common Name, CN）就是在这里指定的，可以使用泛域名。
   - 用户将 csr 文件发送给 CA 机构，进行进一步处理。
2. `xxx.crt`: 这就是我们所说的 TLS 证书，CA 证书和服务端 TLS 证书都是这个格式。
    - openssl 命令：
        ```shell
        openssl x509 -req -in server.csr -CA ca.crt -CAkey ca.key \
            -CAcreateserial -out server.crt -days 10000 \
            -extensions v3_ext -extfile csr.conf
        ```
    - 使用 CA 证书、CA 密钥对 `csr` 文件进行签名，就能得到最终的服务端 TLS 证书——一个 `crt` 文件。


总结一下，**使用如下命令可生成一个自签名的 TLS 证书（RSA256 算法）**：

```shell
# 1. 生成 2048 位 的 RSA 密钥
openssl genrsa -out server.key 2048
# 2. 生成证书签名请求，需要输入域名(Common Name, CN)等相关信息，也可通过 `-config csr.conf` 指定相关信息
openssl req -new -key server.key -out server.csr 
# 3. 生成最终的证书，这里指定证书有效期 10 年
openssl req -x509 -sha256 -days 3650 -key server.key -in server.csr -out server.crt
```

#### 拓展：基于 ECC 算法的 TLS 证书

>Let's Encrypt 目前也已经支持了 ECC 证书。

ECC(Elliptic Curve Cryptography) 算法被认为是比 RSA 更优秀的算法。与 RSA 算法相比，ECC 算法使用更小的密钥大小，但可提供同样的安全性，这使计算更快，降低了能耗，并节省了内存和带宽。

对于 RSA 密钥，可以提供不同的密钥大小（密钥大小越大，加密效果越好）。
而对于 ECC 密钥，您应选择要用哪种曲线生成密钥对。各个组织（ANSI X9.62、NIST、SECG）命名了多种曲线，可通过如下命名查看 openssl 支持的所有曲线名称：

```shell
openssl ecparam -list_curves
```

生成一个自签名的 ECC 证书：

```shell
# 生成 ec 算法的私钥，使用 prime256v1 算法，密钥长度 256 位。（强度大于 2048 位的 RSA 密钥）
openssl ecparam -genkey -name prime256v1 -out key.pem
# 生成证书签名请求，需要输入域名(Common Name, CN)等相关信息
openssl req -new -sha256 -key key.pem -out csr.csr
# 生成最终的证书，这里指定证书有效期 10 年
openssl req -x509 -sha256 -days 3650 -key key.pem -in csr.csr -out certificate.pem
```


>P.S. 另外还有使用 ECC 进行签名的 ECDSA 算法，被用在了 SSH 协议中，另外 Web 编程中 JWT 的签名也可选用该算法。


## 二、服务端与客户端的证书配置

### 1. 服务端的 TLS 证书配置

服务端需要两个文件：

1. TLS 证书私钥(RSA 密钥或 EC 密钥)：`server.key`
2. TLS 证书（包含公钥）：`server.crt`

一般如 Nginx 等服务端应用，都可以通过配置文件指定这两个文件的位置。修改配置后重新启动，就有 TLS 了，可以通过 https 协议访问测试。


### 2. 客户端的 TLS 证书配置（指自签名证书）

如果你在证书不是权威 CA 机构颁发的（比如是一个自签名证书），那就需要在客户端将这个 TLS 证书（公钥）添加到受信证书列表中。
这个步骤可以在 OS 层面进行——添加到 OS 的默认证书列表中，也可以在代码层面完成——指定使用某个证书进行 TLS 验证。


## 参考

- [Certificates - Kubernetes Docs](https://kubernetes.io/docs/concepts/cluster-administration/certificates/)
- [TLS/HTTPS 证书生成与验证](https://www.cnblogs.com/kyrios/p/tls-and-certificates.html)
- [ECC作为SSL/TLS证书加密算法的优势](https://zhuanlan.zhihu.com/p/57710573)
- [ECC证书的生成和验签](https://cloud.tencent.com/developer/article/1407305)
