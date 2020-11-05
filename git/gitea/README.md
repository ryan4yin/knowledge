# Gitea - 轻量 Git 仓库

gitea 是 gogs 的分支项目，社区活跃，目前功能已经比最初的 gogs 更强了，开发也更活跃，而且文档详尽。

`docker-compose.yml` 拷贝自 gitea 官方文档：[Installation with Docker - Gitea](https://docs.gitea.io/en-us/install-with-docker/)

gitea 提供的默认 docker-compose 使用 sqlite3 文件数据库存数据，非常节约资源。
可如果你需要更高的性能，官方文档也提供了使用 mysql/postgresql 数据库的 `docker-compose.yml` 供使用。

mysql 和 postgresql 选哪个？答案是你熟悉哪个就选哪个。都不熟悉就选 mysql，毕竟 mysql 目前应用最广泛。

