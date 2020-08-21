# Horizontal Pod Autoscaler - Pod 自动扩缩容

Kubernetes 的 HPA 可以通过 CPU/RAM 进行 Pod 伸缩，另外也支持自定义指标（如每秒请求数等）。

注意事项：

1. HPA 的「目标指标」可以使用两种形式：绝对度量指标和资源利用率。
    - 绝对度量指标：比如 CPU，就是设定绝对核数。
    - 资源利用率（资源使用量/资源请求 * 100%）：在 Pod 设置了资源请求时，可以使用资源利用率进行 Pod 伸缩。


HPA 的扩缩容算法为：

```
期望副本数 = ceil[当前副本数 * ( 当前指标 / 目标指标 )]
```

从上面的参数可以看到：

1. 只要「当前指标」超过了目标指标，就一定会发生扩容。
2. `当前指标 / 目标指标`要小到一定的程度，才会触发缩容。
   1. 比如双副本的情况下，上述比值要小于等于 1/2，才会缩容到单副本。
   2. 三副本的情况下，上述比值的临界点是 2/3。
   3. 五副本时临界值是 4/5，100副本时临界值是 99/100，依此类推。
   4. 如果 `当前指标 / 目标指标` 从 1 降到 0.5，副本的数量将会减半。（虽然说副本数越多，发生这么大变化的可能性就越小。）
3. `当前副本数 / 目标指标`的值越大，「当前指标」的波动对「期望副本数」的影响就越大。


为了防止扩缩容过于敏感，它还有几个延时相关的参数。

## 前置条件 - [metrics-server](https://github.com/kubernetes-sigs/metrics-server)

HPA 需要从 metrics-server 获取监控指标，因此 kubernetes 集群一定要部署好 metrics-server.

metrics-server 是 k8s 官方的一个轻量级指标收集器，负责收集集群中的 CPU/RAM 两项指标，提供给 HPA 等自动伸缩器使用，
另外也提供对 k8s 集群的简单监控，比如 `kubectl top po` 命令以及 dashboard。

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


## 参考

- [Pod 水平自动伸缩 - Kubernetes Docs](https://kubernetes.io/zh/docs/tasks/run-application/horizontal-pod-autoscale/)
- [Horizontal Pod Autoscaler演练 - Kubernetes Docs](https://kubernetes.io/zh/docs/tasks/run-application/horizontal-pod-autoscale-walkthrough/)

