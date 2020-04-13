# [Traefik](https://github.com/containous/traefik/) 配置

我接触过的三种用法：

1. Docker 单机方式：代理本机 Docker 上其他容器的流量，官方 sample 第一个就是。
1. File 方式：通过 yaml 文件配置路由策略，支持动态更新，不需要重启。
1. Kubernetes Ingress Controller 方式：用做 k8s 的入口网关。
