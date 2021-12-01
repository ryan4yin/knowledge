# Kubernetes

## 视频

- [KubeCon + CloudNativeCon North America 2020 - Virtual](https://www.youtube.com/playlist?list=PLj6h78yzYM2Pn8RxfLh2qrXBDftr6Qjut): 全球大厂共享出来的 200+ 个视频，全都是干货。光看目录就能知道 2020 年 kubernetes 社区的热点与新兴技术。


## Kubernetes 相关项目

开发与调试：

- [telepresence](https://github.com/telepresenceio/telepresence): 通过 proxy 将你的本机加入到 kubernetes 虚拟网络中，方便本地开发与调试微服务。但是本地环境跟容器环境仍然存在差异，这是它的问题所在。
- [nocalhost](https://github.com/nocalhost/nocalhost): 它比 telepresence 更进一步，只在本地 IDE (JetBrains/VSCode)里编写代码，然后直接同步到 Kubernetes 的容器中运行，容器由项目的 Dockerfile 构建（会自动修改 entrypoint）

- [eclipse/che](https://github.com/eclipse/che): 比 nocalhost 更进一步，直接把 IDE 也整进了 Kubernetes 容器，che 底层使用 theia 作为它的 Web IDE。它可以自动为每个用户按需创建 Workspace，通过 PV 为用户持久化数据。

## 技术文章收藏

- [一文带你检查Kubernetes应用是否为最佳实践](https://juejin.im/post/6844904024911642637)
- [京东云原生之路](https://developer.jdcloud.com/article/1163)
- [京东如何打造K8s全球最大集群支撑万亿电商交易](https://developer.jdcloud.com/article/1160)

Github:

- [赵化冰](https://github.com/zhaohuabing): Istio 贡献者，它的个人仓库和个人博客很多的干货。
- [宋净超](https://github.com/rootsongjc): Istio/Kubernetes 国内最前沿的领军人物。


## 值得关注的云原生项目

- [openkruise](https://github.com/openkruise/kruise): 阿里开源的一套增强 Kubernetes 功能的系统，对 k8s 的 Deployment/StatefulSet/Job/DaemonSet 均提供了对应的增强版，而且增强的特性很吸引人。
