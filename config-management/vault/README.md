# [Vault](https://github.com/hashicorp/vault)

Vault 和 Apollo 相比，最大的特点是它对敏感信息的支持非常完善：

1. 支持保存各种自定义信息、自动生成各类密钥，vault 自动生成的密钥还能自动轮转(rotate)
2. 认证方式：支持接入各大云厂商的账号权限体系（比如阿里云RAM子账号体系）或者 LDAP 等进行身份验证，不需要创建额外的账号体系。
3. 密钥引擎：也支持接入各大云厂商的账号体系（比如阿里云RAM子账号体系），实现 ACCESS_KEY/SECRET_KEY 的自动轮转。
4. 支持接入 kubernetes rbac 权限体系，通过 serviceaccount+role 为每个 Pod 单独配置权限。

详细内容已迁移至：<https://ryan4yin.space/posts/expirence-of-vault/>
