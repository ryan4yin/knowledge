# Git 相关

## 一、Git 命令

### 强制走 ssh 协议

以下命令将对 gitlab.svc.local 的 https 请求，强制转换成 ssh 请求。
```
git config --global url."git@gitlab.svc.local:".insteadOf "https://gitlab.svc.local"
```

在 CI/CD 中可用上述方法强制走 ssh 协议，配合 ssh-agent 插件动态注入 ssh 密钥。
这样你使用 `git clone https://gitlab.svc.local/xxx.git` 时，底层实际上使用的是 ssh 协议。

也可以用同样的手法转换 http/git 协议，但是不能同时转换多种协议。。

### Git 使用指定的私钥

1. 设置环境变量 `GIT_SSH_COMMAND="ssh -i ~/.ssh/id_rsa_example"`
2. 使用 Git 命令 `git config core.sshCommand "ssh -i ~/.ssh/id_rsa_example -F /dev/null"`
3. 使用 ssh-agent: `ssh-agent sh -c 'ssh-add ~/.ssh/id_rsa; git clone git@github.com:xxx/xxx.git'`
4. 修改 `~/.ssh/config`

详见：

- [How to tell git which private key to use?](https://superuser.com/questions/232373/how-to-tell-git-which-private-key-to-use)

## 二、Git 部署方案

1. Gitlab: 企业适用的重量级方案
2. [gitea](https://github.com/go-gitea/gitea): 轻量级的 git 仓库方案，适合小项目/个人。

docker-compose 配置见 gitea/gitlab 两个子文件夹。
