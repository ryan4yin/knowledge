# Horizontal Pod Autoscaler - Pod 自动扩缩容

Kubernetes 的 HPA 可以通过 CPU/RAM 进行 Pod 伸缩，另外也支持自定义指标（如每秒请求数等）。

注意事项：

1. HPA 的「目标指标」可以使用两种形式：绝对度量指标和资源利用率。
    - 绝对度量指标：比如 CPU，就是设定绝对核数。
    - 资源利用率（资源使用量/资源请求 * 100%）：在 Pod 设置了资源请求时，可以使用资源利用率进行 Pod 伸缩。
1. HPA 的「当前指标」是一段时间内所有 Pods 的平均值，不是峰值。Pod 的指标是其中所有容器指标之和。


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


为了防止扩缩容过于敏感，它还有几个延时相关的参数：

1. HPA Loop 延时：默认 15 秒，每 15 秒钟进行一次 HPA 扫描。
2. `--horizontal-pod-autoscaler-cpu-initialization-period`: 
3. 缩容冷却时间：默认 5 分钟。

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


## 问题

### 1. Pod 扩容 - 预热陷阱

>预热：Java/C# 这类运行在虚拟机上的语言，第一次使用到某些功能时，往往需要初始化一些资源，例如「JIT 即时编译」。
这导致微服务某些 API 第一次被调用时，响应特别慢。
因此 Pod 在提供服务前，需要提前「预热」一次这些接口，将需要用到的资源提前初始化好。

在负载很高的情况下，HPA 会自动扩容。
但是如果扩容的 Pod 需要预热，就可能会遇到「预热陷阱」。

在有大量用户访问的时候，不论使用何种负载均衡策略，只要请求被转发到新建的 Pod 上，这个请求就会「卡住」。
如果请求速度太快，Pod 启动的瞬间「卡住」的请求就越多，这将会导致新建 Pod 因为压力过大而垮掉。
然后 Pod 一重启就被压垮，进入 CrashLoopBackoff 循环。

如果是在使用多线程做负载测试时，效果更明显：50 个线程在不间断地请求，
别的 Pod 响应时间是「毫秒级」，而新建的 Pod 的首次响应是「秒级」。几乎是一瞬间，50 个线程就会全部陷在新建的 Pod 这里。
而新建的 Pod 在启动的瞬间可能特别脆弱，瞬间的 50 个并发请求就可以将它压垮。
然后 Pod 一重启就被压垮，进入 CrashLoopBackoff 循环。

**解决方法**：

1. 在就绪探针 API 的后端控制器里面，依次调用所有需要预热的接口，提前初始化好所有资源。
   1. 就绪探针的控制器中，可以通过 `localhost` 回环地址调用它自身的接口。
1. 使用「AOT 预编译」技术：预热，通常都是因为「JIT 即时编译」导致的问题，在需要用到时它才编译。而 AOT 是预先编译，在使用前完成编译，因此 AOT 能解决预热的问题。

## 参考

- [Pod 水平自动伸缩 - Kubernetes Docs](https://kubernetes.io/zh/docs/tasks/run-application/horizontal-pod-autoscale/)
- [Horizontal Pod Autoscaler演练 - Kubernetes Docs](https://kubernetes.io/zh/docs/tasks/run-application/horizontal-pod-autoscale-walkthrough/)

