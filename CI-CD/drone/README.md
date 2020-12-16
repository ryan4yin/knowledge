# Drone

Drone 是目前 Github 上 stars 最多的容器化 CI/CD 工具。

它的优点和缺点应该都是一个：简单易用。


## 与 Gitlab 集成部署

1. 在 Gitlab 的 [User Settings] 中创建 Application，把 client id/secret 填入 docker-compose 中。
2. 生成并修改 `<random-rpc-secret>`，它被用于 runner 和 drone 通信。
3. 启动 drone: `docker-compose up -d`
4. 设置 `drone.svc.local` 的本地域名解析，访问 `http://drone.svc.local`，会跳转到 Gitlab 授权。
5. 在 Gitlab 网络管理页面 `http://gitlab.svc.local/admin/application_settings/network` 的 `Outbound requests` 中，添加白名单 `drone.svc.local`，并勾选 `Allow requests to the local network from system hooks`.
6. 在 drone 中激活需要的 git 仓库。

其中第五步不设置，将无法激活 Git 仓库。

>另外，Drone 不支持 Gitlab 的 SubGroup，也就是 Git 仓库的父路径层数只能为 1，Drone 不支持嵌套路径。

## 通过 Kubernetes 实现 Runner 的自动伸缩

待续

## 使用主机数据卷做缓存

在构建各类应用时，经常会需要拉取各类依赖缓存到本地，第二次构建时就能直接使用本地缓存。
比如安卓的 .gradle 文件夹，dotnet 的 .nuget 文件夹等等。

在 kubernetes/docker pipeline 中可以使用主机数据卷做持久化的缓存，在多次构建中共享这个缓存数据卷，避免重复拉取依赖。
