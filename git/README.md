# Git 部署方案

## Gitlab

1. [官方镜像：gitlab-ce](https://docs.gitlab.com/omnibus/docker/#install-gitlab-using-docker-compose)
    - 官方镜像，一个 all-in-one 的镜像。
    - 好处是部署方便。但是难以拓展，适合小项目/个人。
    - 另外官方已经推出了 Kubernetes 集群版，应该比单机部署可靠很多。（前面给的官方文档，靠后部分有说明）
1. [第三方部署方案：docker-gitlab](https://github.com/sameersbn/docker-gitlab)
    - 通过 docker-compose 组合 redis/postgresql/gitlab-ce 等镜像协同工作。
    - 相比官方镜像，它更灵活，拓展性也更好。文档也相当详细。
    - 但是毕竟是非官方的，作为第二选项。
    
Gitlab 很庞杂，启动很慢，每次重启都要好几分钟。

### Gitlab 配置相关

- [Gitlab System Hooks](https://docs.gitlab.com/ee/system_hooks/system_hooks.html): 系统钩子，通常用于通知别的程序一个 Gitlab Event 发生了。
    - Web Hooks: Gitlab Event 发生时通知某个 URL
    - File Hooks: 和 Web Hooks 类似，只是它不调用 URL，而是调用一个 Gitlab 本地的脚本/可执行文件。
- [Gitlab Server Hooks: 自定义 repo/global 级别的钩子](https://docs.gitlab.com/ce/administration/server_hooks.html)
    - 服务端钩子，比 System Hooks 更强大的一点是，Server Hooks 可以通过返回非 0 值，使 Gitlab Event 终止。（比如拒绝 git push）

另外将如果 Gitlab 的数据映射到宿主机文件夹后，首次启动（创建目录）时容易遇到权限问题。

## 其他项目

- [gitea/gogs](https://github.com/gogs/gogs): 轻量级的 git 仓库方案，适合小项目/个人。
