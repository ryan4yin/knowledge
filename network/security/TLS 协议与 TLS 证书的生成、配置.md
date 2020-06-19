>这里不详细说明 TLS 协议的内容，请另行查阅文档

>画外：由于 RSA/ECC 两类非对称加密算法被广泛的应用在各类加密通讯中，因此下面说明的证书生成、签名过程，
同样也适用于其他场景，比如 SSH 密钥对生成、JWT 密钥对生成等等。

# TLS 协议

我们需要加密网络数据以实现安全通信，但是有一个现实的问题：

1. 非对称加密算法（RSA/ECC 等）可以方便地对数据进行签名/验证，但是计算速度慢。
2. 对称加密算法（ChaCha20/AES 等）计算速度快，强度高，但是无法安全地生成与保管密钥。

于是 TLS 协议在握手阶段使用非对称算法验证服务端，并安全地生成一个对称密钥，然后使用对称算法进行加密通信。
这里讲「安全地生成一个对称密钥」（Elliptic Curve Diffie-Hellman (ECDHE) key exchange），提供了「完美前向保密（Perfect Forward Secrecy）」特性，前向保密能够保护过去进行的通讯不受密码或密钥在未来暴露的威胁。（tls1.1/tls1.2 也可以使用非前向安全的算法！要注意！）

TLS 通过两个证书来实现服务端身份验证，以及对称密钥的安全生成：

1. CA 证书（公钥）：浏览器/操作系统自带，用于验证服务端的 TLS 证书的签名。保证服务端证书可信。
2. TLS 证书：使用 CA 证书验证了 TLS 证书后，将使用这个 TLS 证书进行协商，以安全地生成一个对称密钥。

CA 证书和 TLS 证书，都只在 TLS 握手阶段有用到，之后的通信就与它们无关了。

## 一、TLS 证书支持保护的域名类型

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

## 二、TLS 证书的生成

>[OpenSSL](https://github.com/openssl/openssl) 是目前使用最广泛的网络加密算法库，这里以它为例介绍证书的生成。
另外也可以考虑使用 [cfssl](https://github.com/cloudflare/cfssl).

前面讲到了 TLS 协议的握手需要使用到两个证书：

1. TLS 证书（服务端证书）：这个是服务端需要配置的数据加密证书。
    - 服务端需要持有这个 TLS 证书本身，以及证书的私钥。
    - 握手时服务端需要将 TLS 证书发送给客户端。
2. CA 证书：这是受信的根证书，客户端可用于验证所有使用它进行签名的 TLS 证书。
   - CA 证书的私钥由权威机构持有，客户端（比如浏览器）则保有 CA 证书的公钥。

在 TLS 连接的建立阶段，客户端（如浏览器）会使用 CA 证书的公钥对服务端的证书签名进行验证，验证成功则说明该证书是受信任的。

### 0. TLS 证书的类型

证书有两种类型：

1. 向权威CA机构申请得到的 TLS 证书：这类证书会被浏览器、小程序等第三方应用/服务商信任。申请证书时需要验证你的所有权，也就使证书无法伪造。
   - 如果你的 API 需要提供给这些第三方应用/服务商访问，那就必须申请此类证书。
2. 由本地 CA 证书签名的 TLS 证书：这类证书不会被浏览器、小程序等第三方应用/服务商信任，证书就可以被伪造。
   - 这类证书的缺点是无法与第三方应用/服务商建立安全的连接。
   - 如果客户端是完全可控的（比如是自家的 APP），那可以自行验证证书的可靠性（公钥锁定、双向 TLS 验证）。这种场景下自签名证书是安全可靠的。可以不使用权威CA机构颁发的证书。

总的来说，权威CA机构颁发的证书，可以被第三方的应用信任，但是自己生成的不行。
而越贵的权威证书，安全性与可信度就越高，或者可以保护更多的域名。

在客户端可控的情况下，可以考虑使用自签名证书（方便、省钱），将这个证书预先埋入客户端中用于验证。


### 1. 向权威CA机构申请受信 TLS 证书

免费的 TLS 证书有两种方式获取：

1. 部分 TLS 提供商有提供免费证书的申请，有效期为一年，但是不支持泛域名。
1. 申请 [Let's Encrypt 免费证书](https://letsencrypt.org)
   - 很多代理工具都有提供 Let's Encrypt 证书的 Auto Renewal，比如:
     - [Traefik](/network-proxy+web-server/traefik/README.md)
     - [Caddy](https://github.com/caddyserver/caddy)
     - [docker-letsencrypt-nginx-proxy-companion](https://github.com/nginx-proxy/docker-letsencrypt-nginx-proxy-companion)
   - 网上也有一些 [certbot](https://github.com/certbot/certbot) 插件，可以通过 DNS 提供商的 API 进行 Let's Encrypt 证书的 Auto Renewal，比如：
     - [certbot-dns-aliyun](https://github.com/tengattack/certbot-dns-aliyun)

收费证书可以在各 TLS 提供商处购买，比如国内的阿里云腾讯云等。

### 1. 生成由本地 CA 证书签名的 TLS 证书

除了公网可用的受信证书，在内网环境，我们需要也使用 TLS 证书保障通信安全，这时我们可能会选择自己生成证书，而不是向权威机构申请证书。
可能的原因如下：

1. 要向权威机构申请证书，那是要给钱的。而在内网环境下，并无必要使用权威证书。
2. 内网环境使用的可能是非公网域名（`xxx.local`/`xxx.lan`/`xxx.srv` 等），权威机构不签发这种域名的证书。（因为没有人唯一地拥有这个域名）

自己生成的证书有两种方类型：

1. 自签名 TLS 证书（我签我自己）：可以认为是 TLS 证书和 CA 证书都使用同一个密钥对，使用 TLS 证书对它自己进行签名。
   - 测试发现这种方式得到的证书貌似不包含 SAN 属性！因此不支持多域名。
2. 由本地 CA 证书签名的 TLS 证书：生成两个独立的密钥，一个用作 CA 证书，一个用作 TLS 证书。使用 CA 证书对 TLS 证书进行签名。

一般来说，直接生成一个泛域名的自签名证书就够了，但是它不方便拓展——客户端对每个自签名证书，都需要单独添加一次信任。
而第二种方法生成的证书就没这个问题。

总的来说，使用自签名证书不方便进行拓展，未来可能会遇到麻烦。因此建议使用第二种方法。


另外介绍下这里涉及到的几种文件类型：

1. `xxx.key`: 就是一个私钥，一般是一个 RSA 私钥，长度通常指定为 2048 位。
   - CA 证书和 TLS 证书的私钥都是通过这种方式生成的。
2. `xxx.csr`: 即 Certificate Sign Request，证书签名请求。使用 openssl 等工具，通过 TLS 密钥+TLS 证书的相关信息，可生成出一个 CSR 文件。
   - 域名（Common Name, CN）就是在这里指定的，可以使用泛域名。
   - 用户将 csr 文件发送给 CA 机构，进行进一步处理。
3. `xxx.crt`: 这就是我们所说的 TLS 证书，CA 证书和服务端 TLS 证书都是这个格式。
    - 使用 CA 证书、CA 密钥对 `csr` 文件进行签名，就能得到最终的服务端 TLS 证书——一个 `crt` 文件。


总结一下，**生成一个自签名的 TLS 证书（RSA256 算法）有两个步骤**：

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
    CN = *.xxx.local  # 泛域名

    [ alt_names ]
    DNS.1 = *.xxx.local  # 一级泛域名
    DNS.1 = *.aaa.xxx.local  # 二级泛域名
    DNS.1 = *.bbb.xxx.local  # 二级泛域名

    [ req_ext ]
    subjectAltName = @alt_names

    [ v3_ext ]
    subjectAltName=@alt_names  # Chrome 要求必须要有 subjectAltName(SAN)
    authorityKeyIdentifier=keyid,issuer:always
    basicConstraints=CA:FALSE
    keyUsage=keyEncipherment,dataEncipherment,digitalSignature
    extendedKeyUsage=serverAuth,clientAuth
    ```
2. 生成证书：
    ```shell
    # 1. 生成 2048 位 的 RSA 密钥
    openssl genrsa -out server.key 2048
    # 2. 通过第一步编写的配置文件，生成证书签名请求
    openssl req -new -key server.key -out server.csr -config csr.conf
    # 3. 生成最终的证书，这里指定证书有效期 10000 天
    ## 3.1 方法一：使用 server.key 进行自签名。这种方式得到的证书不包含 SAN！不支持多域名！
    openssl req -x509 -sha256 -days 3650 -key server.key -in server.csr -out server.crt
    ## 3.2 方法二：生成 ca 证书，并且使用 CA 证书、CA 密钥对 `csr` 文件进行签名
    ### ca 私钥
    openssl genrsa -out ca.key 2048
    ### ca 公钥
    openssl req -x509 -new -nodes -key ca.key -subj "/CN=xxx.local" -days 10000 -out ca.crt
    ### 签名
    openssl x509 -req -in server.csr -CA ca.crt -CAkey ca.key \
    -CAcreateserial -out server.crt -days 10000 \
    -extensions v3_ext -extfile csr.conf
    ```

#### 1.1 拓展1：基于 ECC 算法的 TLS 证书

>Let's Encrypt 目前也已经支持了 ECC 证书。

ECC(Elliptic Curve Cryptography) 算法被认为是比 RSA 更优秀的算法。与 RSA 算法相比，ECC 算法使用更小的密钥大小，但可提供同样的安全性，这使计算更快，降低了能耗，并节省了内存和带宽。

对于 RSA 密钥，可以提供不同的密钥大小（密钥大小越大，加密效果越好）。
而对于 ECC 密钥，您应选择要用哪种曲线生成密钥对。各个组织（ANSI X9.62、NIST、SECG）命名了多种曲线，可通过如下命名查看 openssl 支持的所有椭圆曲线名称：

```shell
openssl ecparam -list_curves
```

生成一个自签名的 ECC 证书：

```shell
# 生成 ec 算法的私钥，使用 prime256v1 算法，密钥长度 256 位。（强度大于 2048 位的 RSA 密钥）
openssl ecparam -genkey -name prime256v1 -out key.pem
# 生成证书签名请求，需要输入域名(Common Name, CN)等相关信息
openssl req -new -sha256 -key key.pem -out csr.csr -config csr.conf
# 生成最终的证书，这里指定证书有效期 10 年
## 方法一：自签名
openssl req -x509 -sha256 -days 3650 -key key.pem -in csr.csr -out certificate.pem
## 方法二：使用 ca 进行签名，方法参考前面
```


>P.S. 另外还有使用 ECC 进行签名的 ECDSA 算法，被用在了 SSH 协议中，另外 Web 编程中 JWT 的签名也可选用该算法。
JWT 选用 ECDSA(如 ES256) 的最大好处，就是签名变短了，JWT 本身也就变短了，比 RS256 更节约流量，而且具有同等的安全性（这个不 100% 确定）。


#### 1.2 拓展2：使用 OpenSSL 生成 SSH 密钥对

我们通常都会使用 `ssh-keygen` 生成 SSH 密钥对（默认 RSA 算法），它是 OpenSSH 的一个命令。

既然使用的是相同的算法，那按理说 SSH 密钥对应该也可以通过 OpenSSL 生成出来。

- [ssh-keygen and openssl gives two different public keys](https://stackoverflow.com/questions/46870569/ssh-keygen-and-openssl-gives-two-different-public-keys)

## 三、服务端与客户端的证书配置

### 1. 服务端的 TLS 证书配置

服务端需要两个文件：

1. TLS 证书私钥(RSA 密钥或 EC 密钥)：`server.key`
2. TLS 证书（包含公钥）：`server.crt`

一般如 Nginx 等服务端应用，都可以通过配置文件指定这两个文件的位置。修改配置后重新启动，就有 TLS 了，可以通过 https 协议访问测试。

#### 1.1 完美前向保密

旧版本的 TLS 协议并不一定能保证前向保密，为了保证前向安全，需要在服务端配置中进行一定设置。
具体的设置方法参见 [ssl-config - mozilla](https://ssl-config.mozilla.org/#server=nginx)，该网站提供三个安全等级的配置：

1. 「Intermediate」：查看生成出的 `ssl-cipher` 属性，发现它只支持 `ECDHE`/`DHE` 开头的算法。因此它保证前向保密。
   - 对于需要通过浏览器访问的 API，推荐选择这个等级。
1. 「Mordern」：只支持 `TLSv1.3`，该协议废弃掉了过往所有不安全的算法（包括），安全性极高。
   - 对于不需要通过浏览器等旧终端访问的 API，请直接选择这个等级。
1. 「Old」：除非你的用户使用非常老的终端进行访问，否则请不要考虑这个选项！

另外阿里云负载均衡器配置前向保密的方法参见：[管理TLS安全策略 - 负载均衡 - 阿里云文档](https://help.aliyun.com/document_detail/90740.html)

#### 1.2 TLS 双向认证(Mutual TLS authentication, mTLS)

TLS 协议（tls1.1+，RFC: [TLS1.2 - RFC5246](https://tools.ietf.org/html/rfc5246#section-7.4.4)）中，定义了服务端请求验证客户端证书的方法。这
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
2. 客户端证书：它和服务端证书的相同点是——域名必须能匹配上。而别的信息，则可以修改为客户端相关的信息。

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


### 2. 客户端的 TLS 证书配置（针对本地签名的证书）

如果你在证书不是权威 CA 机构颁发的（比如是一个自签名证书），那就需要在客户端将这个 TLS 证书（公钥）添加到受信证书列表中。
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

TLS 证书其实就是公钥+申请者(你)和颁发者(CA)的信息+签名(使用 CA 私钥加密)，因此我们也可以考虑只锁定其中的公钥。

「公钥锁定」比「证书锁定」更灵活，这样证书本身其实就可以直接轮转了（证书有过期时间），而不需要一个旧证书和新证书共存的中间时期。

**如果不考虑实现难度的话，「公钥锁定」是更推荐的技术。**

#### 2.3 TLS 双向认证(Mutual TLS authentication, mTLS)


如果将 mTLS 用在 App 安全上，存在的风险是：

1. 客户端中隐藏的证书是否可以被提取出来，或者黑客能否 Hook 进 App 中，直接使用证书发送信息。
2. 如果客户端私钥设置了「密码（passphrase）」，那这个密码是否能很容易被逆向出来？

mTLS 和「公钥锁定/证书锁定」对比：

1. 公钥锁定/证书锁定：只在客户端进行验证。
   1. 但是在服务端没有进行验证。这样就无法鉴别并拒绝第三方应用（爬虫）的请求。
   2. 加强安全的方法，是通过某种算法生成动态的签名。爬虫生成不出来这个签名，请求就被拒绝。
2. mTLS: 服务端和客户端都要验证对方。
   1. 保证双边可信，在客户端证书不被破解的情况下，就能 Ban 掉所有的爬虫或代理技术。

#### 2.4 客户端逆向/破解手段总结

要获取一个应用的数据，有两个方向：

1. 服务端入侵：现代应用的服务端突破难度通常都比较客户端高，注入等漏洞底层框架就有处理。
2. 客户端逆向+爬虫：客户端是离用户最近的地方，也是最容易被突破的地方。
   1. mTLS 常见的破解手段，是找到老版本的安装包，发现很容易就能提取出客户端证书。。

待续


## 四、通过 OpenSSL 对 TLS 证书进行 CURD（增删查改）

### 1. 查询与验证

```shell
# 查看证书(crt)信息
openssl x509 -noout -text -in ca.crt

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
# pem 格式转 pkcs12
openssl pkcs12 -export -in clientprivcert.pem -out clientprivcert.p12
```

微信/支付宝等支付相关的数字证书，通常就使用 pkcs12 格式，后缀为 `.p12`


## 参考

- [Certificates - Kubernetes Docs](https://kubernetes.io/docs/concepts/cluster-administration/certificates/)
- [TLS/HTTPS 证书生成与验证](https://www.cnblogs.com/kyrios/p/tls-and-certificates.html)
- [ECC作为SSL/TLS证书加密算法的优势](https://zhuanlan.zhihu.com/p/57710573)
- [ECC证书的生成和验签](https://cloud.tencent.com/developer/article/1407305)
- [前向保密(Forward Secrecy) - WikiPedia](https://zh.wikipedia.org/wiki/%E5%89%8D%E5%90%91%E4%BF%9D%E5%AF%86)

- [证书选型和购买 - 阿里云文档](https://help.aliyun.com/document_detail/28542.html)

另外两个关于 CN(Common Name) 和 SAN(Subject Altnative Name) 的问答：

- [Can not get rid of `net::ERR_CERT_COMMON_NAME_INVALID` error in chrome with self-signed certificates](https://serverfault.com/questions/880804/can-not-get-rid-of-neterr-cert-common-name-invalid-error-in-chrome-with-self)
- [SSL - How do Common Names (CN) and Subject Alternative Names (SAN) work together?](https://stackoverflow.com/questions/5935369/ssl-how-do-common-names-cn-and-subject-alternative-names-san-work-together)


关于证书锁定/公钥锁定技术：

- [Certificate and Public Key Pinning - OWASP](https://owasp.org/www-community/controls/Certificate_and_Public_Key_Pinning)
- [Difference between certificate pinning and public key pinning](https://security.stackexchange.com/questions/85209/difference-between-certificate-pinning-and-public-key-pinning)


加密/签名算法相关：

- [RSA算法原理（二）](http://www.ruanyifeng.com/blog/2013/07/rsa_algorithm_part_two.html)

其他：

- [openssl 查看证书](https://www.jianshu.com/p/f5f93c89155e)
