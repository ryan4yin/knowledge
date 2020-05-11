
# TLS 证书的生成

## 一、生成自签名证书

在内网环境，我们需要使用自签名证书保障通信安全。

### 1. [CFSSL（推荐）](https://github.com/cloudflare/cfssl)

cfssl 是 cloudflare 开源的一个 PKI 与 TLS 工具包，官方文档宣称它是 cloudflare 的 PKI/TLS 瑞士军刀。
这里我们可以使用它进行 TLS 证书的生成与打包。

此工具需要手动安装，详细安装使用方法见参考文档。。

### 2. [OpenSSL](https://github.com/openssl/openssl)

目前使用最广泛的 TLS 加密库。但是使用起来比较复杂。
所有操作系统 (Linux/Windows/MacOS) 应该都自带 opensshl 工具（不过以下示例不支持 windows）

## 二、生成 Let's Encrypt 免费证书

待续

## 参考

- [Certificates - Kubernetes Docs](https://kubernetes.io/docs/concepts/cluster-administration/certificates/)

- [TLS/HTTPS 证书生成与验证](https://www.cnblogs.com/kyrios/p/tls-and-certificates.html)
