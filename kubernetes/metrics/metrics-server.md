
## [metrics-server](https://github.com/kubernetes-sigs/metrics-server)

metrics-server 是 k8s 官方的一个轻量级指标收集器，负责收集集群中的 CPU/RAM 两项指标，提供给 HPA 等自动伸缩器使用，另外也提供对 k8s 集群的简单监控，比如 `kubectl top po` 命令以及 dashboard.

>metrics-server 不会提供 metrics api，也就是说 prometheus 不能通过它采集集群的 CPU/MEM 信息.

自己使用 kubeadm 等方式搭建的集群，是没有 metrics-server 的，需要另行部署。

metrics-server 实质上是一个 kube-apiserver 的 api 扩展，针对它的请求需要由 kube-apiserver 转发。

另外 metrics-server 是通过访问每个节点的 kubelet 来拉取 CPU/MEM 指标的。
安全起见还需要为 metrics-server 配 kubelet 双向 TLS 认证的证书，通常云服务提供商的集群都已经自动处理好了这些操作。
而如果是自己使用 kubeadm 部署的集群，就需要手动 approve 下证书。

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


## 获取裸数据

通过如下命令，能查到由 metrics-server 抓取到的 node/pod 的 CPU/MEM 信息：

```shell
kubectl get --raw "/apis/metrics.k8s.io/v1beta1/nodes" | jq
kubectl get --raw "/apis/metrics.k8s.io/v1beta1/pods" | jq
```

而自定义指标，如 Kubernetes 官方文档给的 `packets-per-second` `requests-per-second`，则需要借助 [prometheus-adaptor](./../autoscaling/prometheus-adapter.md) 等第三方工具实现，或者你自己写个实现。
