
# TLS 证书的生成

在内网环境，我们需要使用自签名证书保障通信安全。

## [CFSSL（推荐）](https://github.com/cloudflare/cfssl)

cfssl 是 cloudflare 开源的一个 PKI 与 TLS 工具包，官方文档宣称它是 cloudflare 的 PKI/TLS 瑞士军刀。
这里我们可以使用它进行 TLS 证书的生成与打包。

详细使用方法见参考文档。。

## [OpenSSL](https://github.com/openssl/openssl)

目前使用最广泛的 TLS 加密库。但是使用起来比较复杂。

## 参考

- [Certificates - Kubernetes Docs](https://kubernetes.io/docs/concepts/cluster-administration/certificates/)

- [[转]如何创建一个自签名的SSL证书(X509)](https://www.cnblogs.com/lihuang/articles/4205540.html)
