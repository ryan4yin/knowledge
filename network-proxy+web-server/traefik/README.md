# [Traefik](https://github.com/containous/traefik/) 配置

我接触过的三种用法：

1. Docker 单机方式：代理本机 Docker 上其他容器的流量，官方 sample 第一个就是。
1. File 方式：通过 yaml 文件配置路由策略，支持动态更新，不需要重启。
1. Kubernetes Ingress Controller 方式：用做 k8s 的入口网关。

## 流量属性

traefik 可以在第 4 层(tcp/udp)和第 5 层(http/tls/websocket/grpc)进行流量转发。

但是不支持 ftp/mysql/redis 等协议，这类协议当成第 4 层流量进行转发。设置这种转发意义不大，因为第 4 层只有两个可用信息：端口号和 IP，无法灵活地配置 LoadBalancer 等转发规则。个人感觉是弊大于利。

