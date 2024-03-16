# Git 相关

## 一、Git 命令

### 强制走 ssh 协议

以下命令将对 gitlab.svc.local 的 https 请求，强制转换成 ssh 请求。

```
git config --global url."git@gitlab.svc.local:".insteadOf "https://gitlab.svc.local"
```

在 CI/CD 中可用上述方法强制走 ssh 协议，配合 ssh-agent 插件动态注入 ssh 密钥。这样你使用
`git clone https://gitlab.svc.local/xxx.git` 时，底层实际上使用的是 ssh 协议。

也可以用同样的手法转换 http/git 协议，但是不能同时转换多种协议。。

### 为不同的 Git URL 使用不同的 email/username

如果我们用同一台电脑为开源项目（或个人项目）和公司项目提交代码，就可能会遇到的一个问题：公司的 Git
仓库应该使用企业邮箱提交代码，而个人开源项目我们希望使用个人邮箱，如何自动切换呢？

这个问题，目前比较好的解法是使用 `conditional includes`，添加或修改如下两个文件：

```conf
# ~/.gitconfig
[user]
    name = ryan4yin
    email = ryan4yin@ryan4yin.space

[includeIf "gitdir:~/work/"]
    path = ~/work/.gitconfig
```

```conf
# ~/work/.gitconfig
[user]
    email = ryan4yin@company.tld
```

这样设置好后，所有 `~/work` 中的 git 仓库，都将默认使用企业邮箱。

而其他的 git 仓库，仍然使用个人邮箱。

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
