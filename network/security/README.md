# 网络安全

作为一个 DevOps，当然也需要了解网络安全相关的知识。

1. 网络环境扫描
2. 代码扫描
3. Docker 镜像扫描
4. 服务器漏洞扫描

## 一、认证授权与数字加密

## 1. 数字证书(digital certificate)

数字证书是利用非对称加密算法进行加密、解密、数字签名、签名认证的安全技术。

数字证书技术的两个标准：

1. PKI(Public Key Infrastructure): 公钥基础设施，指代所有 PKI 标准内的所有安全技术。
2. CA(Catificate Authority): 权威证书机构。

应用：

1. 个人身份验证（个人证书）：比如安卓的 App 签名证书，就是用于验证 App 来源的。
   1. 主要包含证书所有者的信息、证书所有者的公开密钥和证书颁发机构的签名等内容。用户使用此证书在互联网中标识证书持有人的数字身份，用来保证信息在互联网传输过程中的安全性和完整性。
2. 网络数据加密与身份认证（TLS 证书）：目前所有主流网站基本都已经用上了 HTTPS
3. 身份授权管理：企业等机构使用数字证书进行用户/程序的授权与身份验证。

## 2. 动态口令

也就是我们目前常用的两步验证，有效期只有几分钟。
扫一个二维码就能把动态口令加载到「身份验证器」中，非常方便，也够安全。

身份验证器本身可以通过智能手机的指纹识别、面部识别等技术进行更智能的身份认证。

## 3. 硬件证书：USB Key（FIDO/U2F）

USB Key 也称为硬件证书，具备不可复制性。

USB Key 就像一个黑箱子，它将数字证书封装在硬件内部，所有的数字证书相关操作，都只能在 USB Key 内部进行。
这样就使得黑客无法得知黑箱子内部的数字证书内容。

FIDO/U2F 是一个开源开放的硬件两步验证标准，目前主流浏览器均已支持该项标准，Github 已经支持使用 FIDO/U2F 进行身份验证。

- [开源 FIDO U2F 安全密钥：nRF52-U2F](https://zhuanlan.zhihu.com/p/47577107)

## 相关工具

- [vuls](https://github.com/future-architect/vuls): 基于 SSH 协议的漏洞扫描服务。
- [scapy](https://github.com/secdev/scapy/): Python 网络安全工具包。
- [lynis](https://github.com/CISOfy/lynis): 功能和 vuls 类似，不过是 shell 脚本写的。

## Awesome 系列

- [awesome-pentest](https://github.com/enaqx/awesome-pentest)

