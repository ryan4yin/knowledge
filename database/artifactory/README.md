# Artifactory - 制品库

制品库用以管理源代码编译后的构建产物，如 Docker 镜像、各类语言的依赖包、软件安装包等。

## 1. [开源的大一统制品库 - sonatype nexus 3](https://github.com/sonatype/docker-nexus3)

nexus3 支持很多主流语言(pypi/nuget/npm/rubygems/maven 等)的包仓库协议、Linux 两个主流的包管理器仓库 apt/yum、docker 容器镜像仓库、Helm 仓库 等等。

简而言之，这就是 The One Repository Rules Them All.

优点：

1. 大一统，降低维护成本
2. 用户众多，代码是企业维护，稳定性有保障。

缺点：大一统的制品库对最新协议的支持，往往不如各大社区中那些小而美的制品库。比如 nexus3 对 nuget v3 json api 的支持比社区的 [baget](https://github.com/loic-sharma/BaGet) 晚了一年多。

## 2. Harbor 容器镜像仓库

Harbor 支持存储容器镜像以及 Helm Chart.



