# 网络安全

作为一个 DevOps，当然也需要了解网络安全相关的知识。

1. 网络环境扫描
2. 代码扫描
3. Docker 镜像扫描
4. 服务器漏洞扫描

## 我的博客

- [TLS 协议、TLS 证书、TLS 证书的配置方法、TLS 加密的破解手段](https://thiscute.world/posts/about-tls-cert/)

## 相关工具

- [vuls](https://github.com/future-architect/vuls): 基于 SSH 协议的漏洞扫描服务。
- [scapy](https://github.com/secdev/scapy/): Python 网络安全工具包。
- [lynis](https://github.com/CISOfy/lynis): 功能和 vuls 类似，不过是 shell 脚本写的。

## Awesome 系列

- [awesome-pentest](https://github.com/enaqx/awesome-pentest): 渗透测试资源大全
- [tpotce](https://github.com/telekom-security/tpotce): 集成了应对各种主流攻击手段的蜜罐，可
  docker-compose 部署。
  - 所谓蜜罐，就是指一个把自己伪装成 ssh/http/ldap/smb/loT 等各种软硬件并提供服务的程序。一个伪装得
    很好的蜜罐，可以诱使攻击者访问，从而获取到攻击者的信息，然后及时向用户发出告警，甚至执行反制措
    施。
- [HFish](https://github.com/hacklcx/HFish): 国内微步开发的一款蜜罐系统，同样是集成了应对各种常见攻
  击手段的蜜罐，但是比 `tpotce` 要更复杂（毕竟企业级），功能或许也更强大些吧。

## 参考

- [The Secret Security Wiki](https://doubleoctopus.com/security-wiki/)
