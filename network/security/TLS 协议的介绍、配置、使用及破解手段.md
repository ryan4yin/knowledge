## 一、TLS 协议

我们需要加密网络数据以实现安全通信，但是有一个现实的问题：

1. 非对称加密算法（RSA/ECC 等）可以方便地对数据进行签名/验证，但是计算速度慢。
2. 对称加密算法（ChaCha20/AES 等）计算速度快，强度高，但是无法安全地生成与保管密钥。

于是 TLS 协议在握手阶段使用非对称算法验证服务端，并安全地生成一个对称密钥，然后使用对称算法进行加密通信。
这里讲「安全地生成一个对称密钥」（Elliptic Curve Diffie-Hellman (ECDHE) key exchange），提供了「完美前向保密（Perfect Forward Secrecy）」特性，前向保密能够保护过去进行的通讯不受密码或密钥在未来暴露的威胁。（tls1.1/tls1.2 也可以使用非前向安全的算法！要注意！）

>本文的主要介绍 TLS 协议在使用方面的内容，ECDHE 等算法及 TLS 握手流程的详细内容，请查阅其他文档。

TLS 通过两个证书来实现服务端身份验证，以及对称密钥的安全生成：

1. CA 证书：浏览器/操作系统自带，用于验证服务端的 TLS 证书的签名。保证服务端证书可信。
2. TLS 证书：使用 CA 证书验证了 TLS 证书可信后，将使用这个 TLS 证书进行协商，以安全地生成一个对称密钥。

CA 证书和 TLS 证书，都只在 TLS 握手阶段有用到，之后的通信就与它们无关了。

## 二、TLS 证书介绍

### 1. 证书是什么？

证书，其实就是非对称加密中的公钥，加上一些别的信息组成的一个文件。

比如 CA 证书，就是 CA 公钥+CA机构相关信息构成的一个文件。

而 TLS 证书，则包含公钥+申请者信息(你)，颁发者(CA)的信息+签名(使用 CA 私钥加密)

CA 证书中的公钥，能用于验证 TLS 证书中签名的正确性，也就能用于判断证书是否可信。

### 2. TLS 证书支持保护的域名类型

TLS 证书支持配置多个域名，并且支持所谓的通配符（泛）域名。
但是通配符域名证书的匹配规则，**和 DNS 解析中的匹配规则并不一致**！

根据[证书选型和购买 - 阿里云文档](https://help.aliyun.com/document_detail/28542.html) 的解释，**通配符证书只支持同级匹配**，详细说明如下：

1. 一级通配符域名：可保护该通配符域名（主域名）自身和该域名所有的一级子域名。
   - 例如：一级通配符域名 `*.aliyun.com` 可以用于保护 `aliyun.com`、`www.aliyun.com` 以及其他所有一级子域名。
     但是不能用于保护任何二级子域名，如 `xx.aa.aliyun.com`
2. 二级或二级以上通配符域名：只能保护该域名同级的所有通配域名，不支持保护该通配符域名本身。
   - 例如：`*.a.aliyun.com` 只支持保护它的所有同级域名，不能用于保护三级子域名。

要想保护多个二三级子域，只能在生成 TLS 证书时，添加多个通配符域名。
因此设计域名规则时，要考虑到这点，尽量不要使用层级太深的域名！有些信息可以通过 `-` 来拼接以减少域名层级，比如阿里云的 oss 域名：

1. 公网：`oss-cn-shenzhen.aliyuncs.com`
2. 内网：`oss-cn-shenzhen-internal.aliyuncs.com`

## 三、TLS 证书的生成

>[OpenSSL](https://github.com/openssl/openssl) 是目前使用最广泛的网络加密算法库，这里以它为例介绍证书的生成。
另外也可以考虑使用 [cfssl](https://github.com/cloudflare/cfssl).

前面讲到了 TLS 协议的握手需要使用到两个证书：

1. TLS 证书（服务端证书）：这个是服务端需要配置的数据加密证书。
    - 服务端需要持有这个 TLS 证书本身，以及证书的私钥。
    - 握手时服务端需要将 TLS 证书发送给客户端。
2. CA 证书：这是受信的根证书，客户端可用于验证所有使用它进行签名的 TLS 证书。
   - CA 证书的私钥由权威机构持有，客户端（比如浏览器）则保有 CA 证书自身。

在 TLS 连接的建立阶段，客户端（如浏览器）会使用 CA 证书的公钥对服务端的证书签名进行验证，验证成功则说明该证书是受信任的。

### 1. TLS 证书的类型

按照证书的生成方式进行分类，证书有三种类型：

1. 由权威 CA 机构签名的 TLS 证书：这类证书会被浏览器、小程序等第三方应用/服务商信任。申请证书时需要验证你的所有权，也就使证书无法伪造。
   - 如果你的 API 需要提供给第三方应用/服务商/浏览器访问，那就必须向权威 CA 机构申请此类证书。
2. 本地签名证书 - `tls_locally_signed_cert`：即由本地 CA 证书签名的 TLS 证书
   - 本地 CA 证书，就是自己使用 `openssl` 等工具生成的 CA 证书。
   - 这类证书不会被浏览器/小程序等第三方应用/服务商信任，证书就可以被伪造。
   - 这类证书的缺点是无法与第三方应用/服务商建立安全的连接。
   - 如果客户端是完全可控的（比如是自家的 APP），那可以自行验证证书的可靠性（公钥锁定、双向 TLS 验证）。这种场景下使用此类证书是安全可靠的。可以不使用权威CA机构颁发的证书。
3. 自签名证书 - `tls_self_signed_cert`: 和 `tls_locally_signed_cert` 类似，但使用 TLS 证书自己充当 CA 证书（我签我自己），生成出的证书就叫自签名证书。
   - 注意:**更广义地讲，自签名证书，就是「并非由权威 CA 机构签名的 TLS 证书」**，也就是同时指代了 `tls_self_signed_cert` 和 `tls_locally_signed_cert`。这也是「自签名证书」应用最广泛的一种含义。

总的来说，权威CA机构颁发的证书，可以被第三方的应用信任，但是自己生成的不行。
而越贵的权威证书，安全性与可信度就越高，或者可以保护更多的域名。

在客户端可控的情况下，可以考虑使用「本地签名证书」（方便、省钱），将这个证书预先埋入客户端中用于验证。

而「自签名证书」主要是方便，能不用还是尽量不要使用。

### 2. 向权威CA机构申请「受信 TLS 证书」

免费的 TLS 证书有两种方式获取：

1. 部分 TLS 提供商有提供免费证书的申请，有效期为一年，但是不支持泛域名。
1. 申请 [Let's Encrypt 免费证书](https://letsencrypt.org)
   - 很多代理工具都有提供 Let's Encrypt 证书的 Auto Renewal，比如:
     - [Traefik](/network-proxy+web-server/traefik/README.md)
     - [Caddy](https://github.com/caddyserver/caddy)
     - [docker-letsencrypt-nginx-proxy-companion](https://github.com/nginx-proxy/docker-letsencrypt-nginx-proxy-companion)
   - 网上也有一些 [certbot](https://github.com/certbot/certbot) 插件，可以通过 DNS 提供商的 API 进行 Let's Encrypt 证书的 Auto Renewal，比如：
     - [certbot-dns-aliyun](https://github.com/tengattack/certbot-dns-aliyun)
   - terraform 也有相关 provider: [terraform-provider-acme](https://github.com/vancluever/terraform-provider-acme)

收费证书可以在各 TLS 提供商处购买，比如国内的阿里云腾讯云等。


### 3. 生成「本地签名证书」或者「自签名证书」

除了被第三方信任的「受信 TLS 证书」，在内网环境，我们需要也使用 TLS 证书保障通信安全，这时我们可能会选择自己生成证书，而不是向权威机构申请证书。

可能的原因如下：

1. 要向权威机构申请证书，那是要给钱的。而在内网环境下，并无必要使用权威证书。
2. 内网环境使用的可能是非公网域名（`xxx.local`/`xxx.lan`/`xxx.srv` 等），权威机构不签发这种域名的证书。（因为没有人唯一地拥有这个域名）

前面介绍过，自己生成的证书有两种方类型：

1. 本地签名证书：生成两个独立的密钥对，一个用于 CA 证书，另一个用于 TLS 证书。使用 CA 证书对 TLS 证书进行签名。
2. 自签名证书（我签我自己）：TLS 证书和 CA 证书都使用同一个密钥对，使用 TLS 证书对它自己进行签名。
   - 测试发现这种方式得到的证书貌似不包含 SAN 属性！因此不支持多域名。

一般来说，直接生成一个泛域名的「自签名证书」就够了，但是它不方便拓展——客户端对每个「自签名证书」，都需要单独添加一次信任。
而「本地签名证书」就没这个问题，one `ca.crt` rules them all.

总的来说，使用「自签名证书」不方便进行拓展，未来可能会遇到麻烦。因此建议使用「本地签名证书」。


另外介绍下这里涉及到的几种文件类型：

1. `xxx.key`: 就是一个私钥，一般是一个 RSA 私钥，长度通常指定为 2048 位。
   - CA 证书和 TLS 证书的私钥都是通过这种方式生成的。
2. `xxx.csr`: 即 Certificate Sign Request，证书签名请求。使用 openssl 等工具，通过 TLS 密钥+TLS 证书的相关信息，可生成出一个 CSR 文件。
   - 域名（Common Name, CN）就是在这里指定的，可以使用泛域名。
   - 用户将 csr 文件发送给 CA 机构，进行进一步处理。
3. `xxx.crt`: 这就是我们所说的 TLS 证书，CA 证书和服务端 TLS 证书都是这个格式。
    - 使用 CA 证书、CA 密钥对 `csr` 文件进行签名，就能得到最终的服务端 TLS 证书——一个 `crt` 文件。


生成一个「自签名证书」或者「本地签名证书」（RSA256 算法），有两个步骤：

1. 编写证书签名请求的配置文件 `csr.conf`:
    ```conf
    [ req ]
    default_bits = 2048
    prompt = no
    default_md = sha256
    req_extensions = req_ext
    distinguished_name = dn

    [ dn ]
    C = CN  # Contountry
    ST = <state>
    L = <city>
    O = <organization>
    OU = <organization unit>
    CN = *.svc.local  # 泛域名，这个字段已经被 chrome/apple 弃用了。

    [ alt_names ]  # 备用名称，chrome/apple 目前只信任这里面的域名。
    DNS.1 = *.svc.local  # 一级泛域名
    DNS.2 = *.aaa.svc.local  # 二级泛域名
    DNS.3 = *.bbb.svc.local  # 二级泛域名

    [ req_ext ]
    subjectAltName = @alt_names

    [ v3_ext ]
    subjectAltName=@alt_names  # Chrome 要求必须要有 subjectAltName(SAN)
    authorityKeyIdentifier=keyid,issuer:always
    basicConstraints=CA:FALSE
    keyUsage=keyEncipherment,dataEncipherment,digitalSignature
    extendedKeyUsage=serverAuth,clientAuth
    ```
   - 此文件的详细文档：[OpenSSL file formats and conventions](https://www.openssl.org/docs/man1.1.1/man5/)
2. 生成证书：
    ```shell
    # 1. 生成 2048 位 的 RSA 密钥
    openssl genrsa -out server.key 2048
    # 2. 通过第一步编写的配置文件，生成证书签名请求（公钥+申请者信息）
    openssl req -new -key server.key -out server.csr -config csr.conf
    # 3. 生成最终的证书，这里指定证书有效期 3650 天
    ## 3.1 方法一（自签名）：使用 server.key 进行自签名。这种方式得到的证书不包含 SAN！不支持多域名！
    openssl req -x509 -sha256 -days 3650 -key server.key -in server.csr -out server.crt
    ## 3.2 方法二（本地签名）：生成 ca 证书，并且使用 CA 证书、CA 密钥对 `csr` 文件进行签名
    ### 3.2.1 ca 私钥
    openssl genrsa -out ca.key 2048
    ### 3.2.2 ca 证书，ca 证书的有效期尽量设长一点，因为不方便更新换代。
    openssl req -x509 -new -nodes -key ca.key -subj "/CN=MyLocalRootCA" -days 10000 -out ca.crt
    ### 3.2.3 签名，得到最终的 TLS 证书，它包含四部分内容：公钥+申请者信息 + 颁发者(CA)的信息+签名(使用 CA 私钥加密)
    openssl x509 -req -in server.csr -CA ca.crt -CAkey ca.key \
      -CAcreateserial -out server.crt -days 3650 \
      -extensions v3_ext -extfile csr.conf
    ```

上述流程生成一个 x509 证书链，详细的参数说明，参见 [RFC5280 - Internet X.509 Public Key Infrastructure Certificate and Certificate Revocation List (CRL) Profile](https://tools.ietf.org/html/rfc5280)

### 4. 关于证书寿命

对于公开服务，服务端证书的有效期不要超过 825 天（27 个月）！而 2020 年 11 月起，新申请的服务端证书有效期缩短到了 398 天（13 个月）。目前 Apple/Mozilla/Chrome 都发表了相应声明，证书有效期超过上述限制的，将被浏览器/Apple设备禁止使用。

对于其他用途的证书，如果更换起来很麻烦，可以考虑放宽条件。
比如 kubernetes 集群的加密证书，可以考虑有效期设长一些，比如 10 年。

据[云原生安全破局｜如何管理周期越来越短的数字证书？](https://mp.weixin.qq.com/s?__biz=MzA4MTQ2MjI5OA==&mid=2664079008&idx=1&sn=dede1114d5705880ea757f8d9ae4c92d)所述，大量知名企业如 特斯拉/微软/领英/爱立信 都曾因未及时更换 TLS 证书导致服务暂时不可用。

因此 TLS 证书最好是设置自动轮转！人工维护不可靠！
目前很多 Web 服务器/代理，都支持自动轮转 Let's Encrypt 证书。
另外 Vault 等安全工具，也支持自动轮转私有证书。

### 5. 拓展1：基于 ECC 算法的 TLS 证书

>Let's Encrypt 目前也已经支持了 ECC 证书。

ECC(Elliptic Curve Cryptography) 算法被认为是比 RSA 更优秀的算法。与 RSA 算法相比，ECC 算法使用更小的密钥大小，但可提供同样的安全性，这使计算更快，降低了能耗，并节省了内存和带宽。

对于 RSA 密钥，可以提供不同的密钥大小（密钥大小越大，加密效果越好）。
而对于 ECC 密钥，您应选择要用哪种曲线生成密钥对。各个组织（ANSI X9.62、NIST、SECG）命名了多种曲线，可通过如下命名查看 openssl 支持的所有椭圆曲线名称：

```shell
openssl ecparam -list_curves
```

生成一个自签名的 ECC 证书的命令示例如下：

```shell
# 生成 ec 算法的私钥，使用 prime256v1 算法，密钥长度 256 位。（强度大于 2048 位的 RSA 密钥）
openssl ecparam -genkey -name prime256v1 -out key.pem
# 生成证书签名请求，需要输入域名(Common Name, CN)等相关信息
openssl req -new -sha256 -key key.pem -out csr.csr -config csr.conf
# 生成最终的证书，这里指定证书有效期 10 年
## 方法一：自签名证书
openssl req -x509 -sha256 -days 3650 -key key.pem -in csr.csr -out certificate.pem
## 方法二：使用 ca 进行签名，方法参考前面
```

### 6. 拓展2：使用 OpenSSL 生成 SSH/JWT 密钥对

RSA/ECC 这两类非对称加密算法被广泛的应用在各类加密通讯中。
SSH/JWT 都支持 RSA-SHA256 及 ECDSA-SHA256 等基于 RSA/ECDSA 的签名算法，因此使用 OpenSSL 生成的密钥对，也应该能用于 SSH 协议加密、JWT 签名等场景。

>ECDSA 是一种基于 ECC 和 DSA 的加密算法

既然 SSH/TLS/JWT 使用的是相同的算法，那理所当然地，SSH/JWT 密钥对应该也可以通过 OpenSSL 生成出来。

生成 RSA 密钥对的命令如下：

```shell
# 1. 生成 2048 位（不是 256 位）的 RSA 密钥
openssl genrsa -out rsa-private-key.pem 2048

# 2. 通过密钥生成公钥，JWT 使用此公钥验证签名
openssl rsa -in rsa-private-key.pem -pubout -out rsa-public-key.pem

# 3. SSH 使用专用的公钥格式，需要使用 ssh-keygen 转换下格式
ssh-keygen -i -mPKCS8 -f rsa-public-key.pem -y > rsa-public.pub
```

生成 ECC 密钥对的命令如下：

```shell
# 1. 生成 ec 算法的私钥，使用 prime256v1 算法，密钥长度 256 位。（强度大于 2048 位的 RSA 密钥）
openssl ecparam -genkey -name prime256v1 -out ecc-private-key.pem
# 2. 通过密钥生成公钥
openssl ec -in ecc-private-key.pem -pubout -out ecc-public-key.pem

# 3. SSH 使用专用的公钥格式，需要使用 ssh-keygen 转换下格式
ssh-keygen -i -mPKCS8 -f ecc-public-key.pem -y > ecc-public.pub
```

JWT 签名及验证只需要使用标准的私钥-公钥对，即 `ecc-private-key.pem`/`ecc-public-key.pem`.

而 SSH 需要使用专用的公钥格式，因此它的使用的密钥对应该是 `ecc-private-key.pem`/`ecc-public.pub`

注：SSH 目前推荐使用 ed25519 算法，而 JWT 目前推荐使用 ECDSA 算法。

## 四、服务端与客户端的证书配置

### 1. 服务端的 TLS 证书配置

要支持 HTTPS 协议，服务端需要两个文件：

1. TLS 证书私钥(RSA 私钥或 EC 私钥)：`server.key`
2. TLS 证书（包含公钥）：`server.crt`

一般如 Nginx 等服务端应用，都可以通过配置文件指定这两个文件的位置。修改配置后重新启动，就有 TLS 了，可以通过 https 协议访问测试。

#### 1.1 完美前向保密

旧版本的 TLS 协议并不一定能保证前向保密，为了保证前向安全，需要在服务端配置中进行一定设置。
具体的设置方法参见 [ssl-config - mozilla](https://ssl-config.mozilla.org/#server=nginx)，该网站提供三个安全等级的配置：

1. 「Intermediate」：查看生成出的 `ssl-cipher` 属性，发现它只支持 `ECDHE`/`DHE` 开头的算法。因此它保证前向保密。
   - 对于需要通过浏览器访问的 API，推荐选择这个等级。
2. 「Mordern」：只支持 `TLSv1.3`，该协议废弃掉了过往所有不安全的算法，保证前向保密，安全性极高，性能也更好。
   - 对于不需要通过浏览器等旧终端访问的 API，请直接选择这个等级。
3. 「Old」：除非你的用户使用非常老的终端进行访问，否则请不要考虑这个选项！

另外阿里云负载均衡器配置前向保密的方法参见：[管理TLS安全策略 - 负载均衡 - 阿里云文档](https://help.aliyun.com/document_detail/90740.html)


### 2. 客户端的 TLS 证书配置（针对本地签名的证书）

如果你在证书不是权威 CA 机构颁发的（比如是一个自签名证书），那就需要在客户端将这个 TLS 证书添加到受信证书列表中。
这个步骤可以在 OS 层面进行——添加到 OS 的默认证书列表中，也可以在代码层面完成——指定使用某个证书进行 TLS 验证。

1. Linux: 使用如下命令安装证书
    ```shell
    sudo cp ca.crt /usr/local/share/ca-certificates/server.crt
    sudo update-ca-certificates
    ```
2. Windows: 通过证书管理器 `certmgr.msc` 将证书安装到 `受信任的根证书颁发机构`，Chrome 的小锁就能变绿了。
3. 编程：使用 HTTPS 客户端的 api 指定使用的 TLS 证书
4. Docker-Client: 参见 [Use self-signed certificates - Docker Docs](https://docs.docker.com/registry/insecure/#use-self-signed-certificates)

#### 2.1 证书锁定(Certifacte Pining)技术

即使使用了 TLS 协议对流量进行加密，并且保证了前向保密，也无法保证流量不被代理！

这是因为客户端大多是直接依靠了操作系统内置的证书链进行 TLS 证书验证，而 Fiddler 等代理工具可以将自己的 TLS 证书添加到该证书链中。

为了防止流量被 Fiddler 等工具使用上述方式监听流量，出现了「证书锁定」技术。
方法是在客户端中硬编码证书的指纹（Hash值，或者直接保存整个证书的内容也行），在建立 TLS 连接前，先计算使用的证书的指纹是否匹配，否则就中断连接。

这种锁定方式需要以下几个前提才能确保流量不被监听：

1. 客户端中硬编码的证书指纹不会被篡改。
2. 指纹验证不能被绕过。
   1. 目前有公开技术（XPosed+JustTrustMe）能破解 Android 上常见的 HTTPS 请求库，直接绕过证书检查。
   2. 针对上述问题，可以考虑加大绕过的难度。或者 App 检测自己是否运行在 Xposed 等虚拟环境下。
3. 用于 TLS 协议的证书不会频繁更换。（如果更换了，指纹就对不上了。）

而对于第三方的 API，因为我们不知道它们会不会更换 TLS 证书，就不能直接将证书指纹硬编码在客户端中。
这时可以考虑从服务端获取这些 API 的证书指纹（附带私钥签名用于防伪造）。

为了实现证书的轮转(rotation)，可以在新版本的客户端中包含多个证书指纹，这样能保证同时有多个可信证书，达成证书的轮转。（类比 JWT 的公钥轮转机制）

>证书锁定技术几乎等同于 SSH 协议的 `StrictHostKeyChecking` 选项，客户端会验证服务端的公钥指纹（key fingerprint），验证不通过则断开连接。


#### 2.2 公钥锁定(Public Key Pining)

前面提到过，TLS 证书其实就是公钥+申请者(你)和颁发者(CA)的信息+签名(使用 CA 私钥加密)，因此我们也可以考虑只锁定其中的公钥。

「公钥锁定」比「证书锁定」更灵活，这样证书本身其实就可以直接轮转了（证书有过期时间），而不需要一个旧证书和新证书共存的中间时期。

**如果不考虑实现难度的话，「公钥锁定」是更推荐的技术。**


## 五、TLS 双向认证(Mutual TLS authentication, mTLS)

TLS 协议（tls1.0+，RFC: [TLS1.2 - RFC5246](https://tools.ietf.org/html/rfc5246#section-7.4.4)）中，定义了服务端请求验证客户端证书的方法。这
个方法是可选的。如果使用上这个方法，那客户端和服务端就会在 TLS 协议的握手阶段进行互相认证。这种验证方式被称为双向 TLS 认证(mTLS, mutual TLS)。

传统的「TLS 单向认证」技术，只在客户端去验证服务端是否可信。
而「TLS 双向认证（mTLS）」，则添加了服务端验证客户端是否可信的步骤（第三步）：

1. 客户端发起请求
2. 「验证服务端是否可信」：服务端将自己的 TLS 证书发送给客户端，客户端通过自己的 CA 证书链验证这个服务端证书。
3. 「验证客户端是否可信」：客户端将自己的 TLS 证书发送给服务端，服务端使用它的 CA 证书链验证该客户端证书。
4. 协商对称加密算法及密钥
5. 使用对称加密进行后续通信。

因为相比传统的 TLS，mTLS 只是添加了「验证客户端」这样一个步骤，所以这项技术也被称为「Client Authetication」.

mTLS 需要用到两套 TLS 证书：

1. 服务端证书：这个证书签名已经介绍过了。
2. 客户端证书：客户端证书貌似对证书信息（如 CN/SAN 域名）没有任何要求，只要证书能通过 CA 签名验证就行。

使用 openssl 生成 TLS 客户端证书（ca 和 csr.conf 可以直接使用前面生成服务端证书用到的，也可以另外生成）：

```shell
# 1. 生成 2048 位 的 RSA 密钥
openssl genrsa -out client.key 2048
# 2. 通过第一步编写的配置文件，生成证书签名请求
openssl req -new -key client.key -out client.csr -config csr.conf
# 3. 生成最终的证书，这里指定证书有效期 3650 天
### 使用前面生成的 ca 证书对客户端证书进行签名（客户端和服务端共用 ca 证书）
openssl x509 -req -in client.csr -CA ca.crt -CAkey ca.key \
   -CAcreateserial -out client.crt -days 3650 \
   -extensions v3_ext -extfile csr.conf
```

mTLS 的应用场景主要在「零信任网络架构」，或者叫「无边界网络」中。
比如微服务之间的互相访问，就可以使用 mTLS。
这样就能保证每个 RPC 调用的客户端，都是其他微服务（或者别的可信方），防止黑客入侵后为所欲为。


目前查到如下几个Web服务器/代理支持 mTLS:

1. Traefik: [Docs - Client Authentication (mTLS)](https://docs.traefik.io/v2.0/https/tls/#client-authentication-mtls)
2. Nginx: [Using NGINX Reverse Proxy for client certificate authentication](https://community.openhab.org/t/using-nginx-reverse-proxy-for-client-certificate-authentication-start-discussion/43064)
   1. 主要参数是两个：`ssl_client_certificate /etc/nginx/client-ca.pem` 和 `ssl_verify_client on`


### mTLS 的安全性

如果将 mTLS 用在 App 安全上，存在的风险是：

1. 客户端中隐藏的证书是否可以被提取出来，或者黑客能否 Hook 进 App 中，直接使用证书发送信息。
2. 如果客户端私钥设置了「密码（passphrase）」，那这个密码是否能很容易被逆向出来？

mTLS 和「公钥锁定/证书锁定」对比：

1. 公钥锁定/证书锁定：只在客户端进行验证。
   1. 但是在服务端没有进行验证。这样就无法鉴别并拒绝第三方应用（爬虫）的请求。
   2. 加强安全的方法，是通过某种算法生成动态的签名。爬虫生成不出来这个签名，请求就被拒绝。
2. mTLS: 服务端和客户端都要验证对方。
   1. 保证双边可信，在客户端证书不被破解的情况下，就能 Ban 掉所有的爬虫或代理技术。

## 六 TLS 协议的破解手段

### 1. 客户端逆向/破解手段总结

要获取一个应用的数据，有两个方向：

1. 服务端入侵：现代应用的服务端突破难度通常都比较客户端高，注入等漏洞底层框架就有处理。
2. 客户端逆向+爬虫：客户端是离用户最近的地方，也是最容易被突破的地方。
   1. mTLS 常见的破解手段，是找到老版本的安装包，发现很容易就能提取出客户端证书。。

待续


## 七、通过 OpenSSL 对 TLS 证书进行 CURD（增删查改）

### 1. 查询与验证

```shell
# 查看证书(crt)信息
openssl x509 -noout -text -in server.crt

# 查看证书请求(csr)信息
openssl req -noout -text -in server.csr

# 查看 RSA 私钥(key)信息
openssl rsa -noout -text -in server.key

# 验证证书是否可信
## 1. 使用系统的证书链进行验证。因为是自签名证书，会验证失败
openssl verify server.crt
## 2. 使用 ca.crt 进行验证。验证成功。
openssl verify -CAfile ca.crt server.crt
```

### 2. 证书格式转换

openssl 模式使用 PEM 格式的证书，这个证书格式将证书编码为 base64 格式进行保存。
另外一类使用广泛的证书，是 PKCS#12、PKCS#8，以及 Windows 上常用的 DER 格式。

```shell
# pem 格式转 pkcs12，公钥和私钥都放里面
openssl pkcs12 -export -in client.crt -inkey client.key -out client.p12
# 按提示输入保护密码
```

或者 p12 转 pem:

```shell
openssl pkcs12 -in xxx.p12 -out xxx.crt -clcerts -nokeys
openssl pkcs12 -in xxx.p12 -out xxx.key -nocerts -nodes
```

微信/支付宝等支付相关的数字证书，通常就使用 pkcs12 格式，使用商户号做加密密码，然后编码为 base64 再提供给用户。


## 参考

- [Certificates - Kubernetes Docs](https://kubernetes.io/docs/concepts/cluster-administration/certificates/)
- [TLS/HTTPS 证书生成与验证](https://www.cnblogs.com/kyrios/p/tls-and-certificates.html)
- [ECC作为SSL/TLS证书加密算法的优势](https://zhuanlan.zhihu.com/p/57710573)
- [ECC证书的生成和验签](https://cloud.tencent.com/developer/article/1407305)
- [前向保密(Forward Secrecy) - WikiPedia](https://zh.wikipedia.org/wiki/%E5%89%8D%E5%90%91%E4%BF%9D%E5%AF%86)

- [证书选型和购买 - 阿里云文档](https://help.aliyun.com/document_detail/28542.html)
- [云原生安全破局｜如何管理周期越来越短的数字证书？](https://mp.weixin.qq.com/s?__biz=MzA4MTQ2MjI5OA==&mid=2664079008&idx=1&sn=dede1114d5705880ea757f8d9ae4c92d)

另外两个关于 CN(Common Name) 和 SAN(Subject Altnative Name) 的问答：

- [Can not get rid of `net::ERR_CERT_COMMON_NAME_INVALID` error in chrome with self-signed certificates](https://serverfault.com/questions/880804/can-not-get-rid-of-neterr-cert-common-name-invalid-error-in-chrome-with-self)
- [SSL - How do Common Names (CN) and Subject Alternative Names (SAN) work together?](https://stackoverflow.com/questions/5935369/ssl-how-do-common-names-cn-and-subject-alternative-names-san-work-together)


关于证书锁定/公钥锁定技术：

- [Certificate and Public Key Pinning - OWASP](https://owasp.org/www-community/controls/Certificate_and_Public_Key_Pinning)
- [Difference between certificate pinning and public key pinning](https://security.stackexchange.com/questions/85209/difference-between-certificate-pinning-and-public-key-pinning)


加密/签名算法相关：

- [RSA算法原理（二）](http://www.ruanyifeng.com/blog/2013/07/rsa_algorithm_part_two.html)

其他：

- [OpenSSL ManPage](https://www.openssl.org/docs/man1.1.1/)
- [openssl 查看证书](https://www.jianshu.com/p/f5f93c89155e)
