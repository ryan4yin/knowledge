# 网络安全

作为一个 DevOps，当然也需要了解网络安全相关的知识。

1. 网络环境扫描
2. 代码扫描
3. Docker 镜像扫描
4. 服务器漏洞扫描


## 数字证书(digital certificate)

数字证书是利用非对称加密算法进行加密、解密、数字签名、签名认证的安全技术。

数字证书技术的两个标准：

1. PKI(Public Key Infrastructure): 公钥基础设施，指代所有 PKI 标准内的所有安全技术。
2. CA(Catificate Authority): 权威证书机构。

应用：

1. 个人身份验证（个人证书）：比如安卓的 App 签名证书，就是用于验证 App 来源的。
   1. 主要包含证书所有者的信息、证书所有者的公开密钥和证书颁发机构的签名等内容。用户使用此证书在互联网中标识证书持有人的数字身份，用来保证信息在互联网传输过程中的安全性和完整性。
2. 网络数据加密与身份认证（TLS 证书）：目前所有主流网站基本都已经用上了 HTTPS
3. 身份授权管理：企业等机构使用数字证书进行用户/程序的授权与身份验证。

## 相关工具

- [vuls](https://github.com/future-architect/vuls): 基于 SSH 协议的漏洞扫描服务。
- [scapy](https://github.com/secdev/scapy/): Python 网络安全工具包。
- [lynis](https://github.com/CISOfy/lynis): 功能和 vuls 类似，不过是 shell 脚本写的。

## Awesome 系列

- [awesome-pentest](https://github.com/enaqx/awesome-pentest)

