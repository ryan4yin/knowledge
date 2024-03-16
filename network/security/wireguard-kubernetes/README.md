# 通过 Kubernetes 部署 WireGuard

此项目在每个 Kubernetes 节点上部署一个单独的 WireGuard Server，通过 hostPort 暴露出 WireGuard 端口，
通过 sdiecar 提供的 API 来动态管理 WireGuard 配置。

注意此项目的 WireGuard 是提供给外部客户端连接的，比如用做代理，不是用于集群组网。
