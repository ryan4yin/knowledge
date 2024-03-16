# [开源的大一统制品库 - sonatype nexus 3](https://github.com/sonatype/docker-nexus3)

nexus3 支持很多主流语言(pypi/nuget/npm/rubygems/maven 等)的包仓库协议、Linux 两个主流的包管理器仓库
apt/yum、docker 容器镜像仓库、Helm 仓库 等等。

简而言之，这就是 The One Repository Rules Them All，国内很多的开源镜像站，都有 nexus3 的影子。

优点：

1. 大一统，降低维护成本。
2. 用户众多，代码是企业维护，稳定性有保障。
3. 统一接入企业的 LDAP 集成验证系统，权限账号管理很方便。
4. 支持配置统一的数据清理策略，不再需要针对每个制品库单独配置。
5. 支持通过配置多节点集群实现高可用，支持以 NFS/OSS 等分布式存储为 Blob Store.
6. 支持设置定时任务(Task) 用于数据备份、清理等工作。

缺点：大一统的制品库对最新协议的支持，往往不如各大社区中那些小而美的制品库。比如 nexus3 对 nuget v3
json api 的支持比社区的 [baget](https://github.com/loic-sharma/BaGet) 晚了一年多。

官方文档：[Sonatype Nexus3 Docs](https://help.sonatype.com/repomanager3)

## Docker 部署单节点 Nexus3

一行命令启动：

```shell
docker-compose up -d
```

## 各制品库的 URL

创建好制品库（pypi/nuget/docker/helm）后，在 repositories 页面就有拷贝 URL 的按钮。

需要注意的点：

1. nuget 的 v3 api 地址为：`http://localhost:8081/repository/nuget-hosted/index.json`，注意末尾需要
   添加 `index.json`！
1. pypi 的仓库地址为:`http://localhost:8081/repository/pypi-hosted/simple`，注意末尾需要添加
   `simple`！

## 从其他制品库迁移到 Nexus3

迁移各语言的依赖包（比如从 pypiserver/baget 迁移到 nexus3）：

1. 找到所有依赖包(.whl/.nupkg)所在的文件夹
2. 编写脚本遍历其中所有的包，使用 `python -m twine upload`/`dotnet nuget push`，将所有包上传到nexus3

对于其他仓库如 Harbor，可以编写脚本通过 api 获取所有包的索引，然后通过客户端工具(如 docker 客户端)拉
包、推送到 nexus3.
