
## [metrics-server](https://github.com/kubernetes-sigs/metrics-server)

metrics-server 是 k8s 官方的一个轻量级指标收集器，负责收集集群中的 CPU/RAM 两项指标，提供给 HPA 等自动伸缩器使用，另外也提供对 k8s 集群的简单监控，比如 `kubectl top po` 命令以及 dashboard.

>metrics-server 不会提供 metrics api，也就是说 prometheus 不能通过它采集集群的 CPU/MEM 信息.

自己使用 kubeadm 等方式搭建的集群，是没有 metrics-server 的，需要另行部署。

metrics-server 实质上是一个 kube-apiserver 的 api 扩展，针对它的请求需要由 kube-apiserver 转发。
也就是说要想完整地安装 metrics-server，还需要修改 kube-apiserver 的配置。安全起见还需要为 kube-apiserver 和 metrics-server 配双向 TLS 认证，比较麻烦。

测试环境不考虑安全性的话，可以一行命令部署 metrics-server:

```shell
kubectl apply -f https://addons.kuboard.cn/metrics-server/0.3.7/metrics-server.yaml
```

上面给出的 metrics-server 部署命令拷贝自 kuboard 的安装文档，经对比发现它只修改了 `metrics-server` 官方部署 yaml，添加了两个参数：

```shell
        args:
          - --cert-dir=/tmp
          - --secure-port=4443
          # 下面两个参数是 kuboard 添加的
          - --kubelet-insecure-tls=true
          - --kubelet-preferred-address-types=InternalIP,Hostname,InternalDNS,externalDNS
```

另外 metircs-server 镜像地址也被 kuboard 换成了 dockerhub 源，避免被墙。

别的注意事项：

1. metrics-server 抓取数据的间隔默认为 60s，可通过 `metrics-resolution` 修改这个间隔，但是不建议低于 15s
2. metrics-server 占用资源小，而且只会缓存 HPA 用得到的数据（也许就缓存几分钟的数据？反正不需要担心它吃存储）。
