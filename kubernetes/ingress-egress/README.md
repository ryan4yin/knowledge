# Ingress - 入口网关

>网关如何暴露到集群外部：[kubernetes 如何将服务暴露到外部](../kubernetes%20如何将服务暴露到外部.md)


## 基础概念

网关 Gateway，就是指一个流量的集中式出入口，网关有两种类型：

1. Ingress Gateway: 入网网关，所有请求都应该从这里进入集群。
2. Egress Gateway: 出口网关，顾名思义，它用于控制所有从集群出去的流量。

对于一个独立的网络，我们通常对入口的管控要求比较严格，而对出口的要求不高，Kubernetes 原生也没有提供 Egress Gateway 这项功能。
我想到的几个原因如下：

1. 技术问题：目前已有的方案里，只有通过服务网格，才能实现 Egress Gateway, 比如 Istio.
2. 成本问题：前面讲了添加 Egress Gateway 需要 Istio，这会带来性能下降。
3. 繁琐程度：Egress Gateway 要求声明好所有需要访问的外部服务，比较繁琐。
4. 懒？：很多人觉得内网已经足够安全了，只要在入口安全性做好了，内网是安全的，出口就不需要管控。


## Kubernetes Ingress

Kubernetes 官方提供的网关抽象，叫 Ingress。Ingress 配置会被一个叫 Ingress Controller 的控制器读取，并负责具体的实现 。

Ingress Controller 有很多的社区实现可供选择，官方提供的是 Nginx-Ingress-Controller，但是它的功能欠佳。

这里着重介绍几个比较流行的社区实现，它们大都提供了一些更高级的特性，比如 JWT 身份验证、来源限流、或者直接提供了插件系统。

详细介绍参见：[API Gateway vs Service Mesh](https://www.cnblogs.com/kirito-c/p/12394038.html)

## 一、Ingress

目前最流行的貌似是 Traefik.

## 二、API Gateway

Kubernetes 上的 API Gateway，[CNCF Cloud Native Interactive Landscape](https://landscape.cncf.io/) 上有一个专门的「API Gateway」部分，其中大部分的项目都是基于 Envoy 的，少部分基于 Nginx.

这里面我只试用过 Kong，基于 CR 自定义资源的配置方式，体验还不错。

