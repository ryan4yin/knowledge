
# TLS 协议

我们需要加密网络数据以实现安全通信，但是有一个现实的问题：

1. 非对称加密算法可以方便地对数据进行签名/验证，但是计算速度慢。
2. 对称加密算法（ChaCha20/AES 等）计算速度快，强度高，但是无法安全地生成与保管密钥。

于是 TLS 协议在握手阶段使用非对称算法验证服务端，并安全地生成一个对称密钥，然后使用对称算法进行加密通信。

TLS 通过两个证书来实现服务端身份验证，以及对称密钥生成：

1. CA 证书（公钥）：浏览器/操作系统自带，用于验证服务端的 TLS 证书的签名。保证服务端证书可信。
2. TLS 证书：使用 CA 证书验证了 TLS 证书后，将使用这个 TLS 证书进行协商，以安全地生成一个对称密钥。

CA 证书和 TLS 证书，都只在 TLS 握手阶段有用到，之后的通信就与它们无关了。

# TLS 证书的生成

首先说明一下，一个 TLS 证书，由两部分组成：

2. TLS 证书：这个是服务端需要配置的数据加密证书。
1. CA 证书：这是根证书，可用于验证所有使用它进行签名的 TLS 证书。

CA 证书的私钥由权威机构持有，客户端则保有 CA 证书的公钥。
在 TLS 连接的建立阶段，客户端（如浏览器）会使用 CA 证书的公钥对服务端的证书签名进行验证，验证成功则说明该证书是受信任的。

## 一、生成自签名证书（或由本地证书签名的证书）

在内网环境，我们需要也使用 TLS 证书保障通信安全，这时一般都会选择自己生成证书，而不是向权威机构申请证书。
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
   - 域名（CN）就是在这里指定的。
   - 用户将 csr 文件发送给 CA 机构，进行进一步处理。
2. `xxx.crt`: 这就是我们所说的 TLS 证书，CA 证书和服务端 TLS 证书都是这个格式。
    - openssl 命令：
        ```shell
        openssl x509 -req -in server.csr -CA ca.crt -CAkey ca.key \
            -CAcreateserial -out server.crt -days 10000 \
            -extensions v3_ext -extfile csr.conf
        ```
    - 使用 CA 证书、CA 密钥对 `csr` 文件进行签名，就能得到最终的服务端 TLS 证书——一个 `crt` 文件。


### 1. [CFSSL（推荐）](https://github.com/cloudflare/cfssl)

cfssl 是 cloudflare 开源的一个 PKI(Public Key Infrastructure) 与 TLS 工具包，官方文档宣称它是 cloudflare 的 PKI/TLS 瑞士军刀。
这里我们可以使用它进行 TLS 证书的生成与打包。

此工具需要手动安装，详细安装使用方法见参考文档。。

### 2. [OpenSSL](https://github.com/openssl/openssl)

目前使用最广泛的 TLS 加密库。但是使用起来比较复杂。
所有操作系统 (Linux/Windows/MacOS) 应该都自带 opensshl 工具（不过以下示例不支持 windows）

用法见参考文档。。

## 二、生成 Let's Encrypt 免费证书

待续


## 拓展：基于 ECC 算法的 TLS 证书

ECC 算法被认为是比 RSA 更强的算法，相同算法强度下 ECC 的密钥长度要比 RSA 短很多。
可以预测的是，未来 RSA 的某些应用会渐渐被 ECC 取代。Let's Encrypt 目前也已经支持了 ECC 证书。

生成一个自签名的 ECC 证书：

```shell
# 生成 ec 算法的私钥
openssl ecparam -genkey -name prime256v1 -out key.pem
# 
openssl req -new -sha256 -key key.pem -out csr.csr
openssl req -x509 -sha256 -days 365 -key key.pem -in csr.csr -out certificate.pem
```

## 参考

- [Certificates - Kubernetes Docs](https://kubernetes.io/docs/concepts/cluster-administration/certificates/)
- [TLS/HTTPS 证书生成与验证](https://www.cnblogs.com/kyrios/p/tls-and-certificates.html)
- [ECC作为SSL/TLS证书加密算法的优势](https://zhuanlan.zhihu.com/p/57710573)
- [ECC证书的生成和验签](https://cloud.tencent.com/developer/article/1407305)
