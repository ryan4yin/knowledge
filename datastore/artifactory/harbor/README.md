# [Harbor](https://github.com/goharbor/harbor)

Harbor 是一个云原生 artifactory，支持存储容器镜像（container images）和 Helm charts.

单纯用来存容器镜像和 helm charts 的话，harbor 要比 nexus3 受欢迎很多。nexus3 是一个很有历史的项目，Web UI、codebase 和 抽象结构都不够「云原生」。

## 一、部署

### 单机部署

在 Github 上下载官方提供的 `harbor-online-installer.tgz`/`harbor-offline-installer.tgz`，然后按照官方文档的提示操作即可。

### 高可用部署

Harbor 可以借助 Kubernetes + Helm 实现高可用部署，当然前提是你有高可用的分布式存储！

数据通过 Kubernetes 提供的接口存到分布式存储中，而 Harbor 的所有组件都以无状态服务的形式运行在 Kubernetes 中。

详细部署流程参见官方文档，反正就改几个 helm values.yaml 的参数。

### 镜像清理策略

harbor 目前已经通过「镜像保留策略」支持了镜像的定期清理，不需要自己写脚本调用 API 了。
另外提供了非阻塞 GC 支持，清理镜像不需要重启 Harbor.

### 镜像安全：漏洞扫描与签名校验

待续

## 二、升级

请仔细阅读 Harbor 官方的升级指南，大概升级策略如下：

1. 如果 RESTful API 没有变更的话，优先考虑通过「复制」功能，将镜像直接「复制」到新 Harbor 仓库。然后将 DNS 解析到新仓库。
   1. 好处是旧仓库不受影响。
2. 如果没有不兼容变更，可以直接原地升级。
3. 如果存在不兼容变更，请按照官方文档的说明进行升级。

