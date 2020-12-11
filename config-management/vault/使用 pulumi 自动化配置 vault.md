# 使用 pulumi 自动化配置 vault

使用 pulumi 管理 vault 配置的优势是很大的，因为云上资源的敏感信息（数据库账号密码、资源 ID、RAM子账号）都是 pulumi 创建的。

再结合使用 pulumi_valut，就能实现敏感信息自动生成后，立即保存到 vault 中，实现完全自动化。

后续微服务就可以通过 kubernetes 认证，直接从 vault 读取敏感信息。

或者是写入到本地的 vault 中留做备份，在需要的时候，管理员能登入进去查看相关敏感信息。


## Token 的生成

pulumi_vault 本身挺简单的，声明式的配置嘛，直接用就是了。

但是它一定要求提供 `VAULT_TOKEN` 作为身份认证的凭证（实测 userpass/approle 都不能直接使用，会报错 `no vault token found`），而且 pulumi 还会先生成临时用的 child token，然后用这个 child token
进行后续的操作。

首先安全起见，肯定不应该直接提供 root token！root token 应该封存，除了紧急情况不应该启用。

那么应该如何生成一个权限有限的 token 给 vault 使用呢？
我的方法是创建一个 userpass 账号，通过 policy 给予它有限的权限。
然后先手动(或者自动)登录获取到 token，再将 token 提供给 pulumi_vault 使用。

这里面有个坑，就是必须给 userpass 账号创建 child token 的权限：

```hcl
path "local/*" {
  capabilities = ["read", "list"]
}

// 允许创建 child token
path "auth/token/create" {
  capabilities = ["create", "read", "update", "delete", "list"]
}
```

不给这个权限，pulumi_vault 就会一直报错。。
