## 方案一：使用 http/https 协议

企业用的私有仓库通常都在内网，个人用户基本都偏爱 https 协议——因为这不需要配置 ssh 密钥，而且账号密码保存在 Windows 的凭据管理器或者 MacOS 的 keychain 里面，也还算安全。

但是使用账号密码进行验证，不适合给 CI/CD 使用。Linux 下没有完善的密钥保管工具，有限的几个也感觉很难用。

网上流传比较广的 linux 下保存 git 凭据的方法，是使用如下方式：

```
# 内网仓库使用自签名 ssl 证书，无法通过 ssl 验证（不安全）
git config --global http.sslVerify false
# 将 git 账号密码直接保存到 ~/.git-credentials 中（明文！不安全）
git config --global credential.helper store
# 直接将密码注入到 ~/.git-credentials
echo "https://${GIT_USER}:${GIT_PASSWD}@<private-git-url>.com" >> .git-credentials
```

显然这非常暴力。。安全性约等于零。。

## 方案二：ssh 协议

ssh 协议使用 ssh 密钥进行验证，相对而言更安全——并不能通过密钥登录 Gitlab 页面进行其他操作。

因此 ssh 协议很适合给 CI/CD 使用。

为了让 CI/CD 服务器在拉取 Go 依赖时，默认使用 ssh 协议，你需要运行下面这一行命令：

```shell
# for github，私有仓库的话，改下域名就行。
git config --global url."git@github.com:".insteadOf "https://github.com/"
```

然后再设置好 ssh 密钥，就能安全地拉取依赖了。密钥可以通过 jenkins 等 CI/CD 工具进行管理，阅后即焚，进一步提升安全性。


## 参考

- [whats-the-proper-way-to-go-get-a-private-repository](https://stackoverflow.com/questions/27500861/whats-the-proper-way-to-go-get-a-private-repository)