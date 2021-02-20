# K8s 网关

要想将一个集群内的应用暴露给外部使用，有如下几种方式：

1. 使用 LoadBalancer Service 暴露，但是 k8s 官方不提供实现，只有各云提供商才支持这种 Service 类型。
   1. 自建生产环境集群，可以考虑使用 [metallb](https://github.com/metallb/metallb)/[porter](https://github.com/kubesphere/porter) 这两个 bare-metal 的 LoadBalancer Service 实现。
2. 使用 NodePort Service，但是 K8s NodePort 只允许暴露 30000-32767 范围内的端口，而且每个应用必须使用不同的 NodePort.
   1. 对于内部测试集群这类可靠性要求不高的环境，可以考虑手动去除 NodePort 的端口范围限制，后面详细介绍。
3. 使用 Ingress/Istio，但是 IngressContorller/IstioGateway 本身还是需要通过 LoadBalancer 或者 NodePort 方式暴露给外部。

总结一下，推荐使用 Ingress/Istio 将应用提供给外部访问，而 Ingress/Istio 如何暴露到外部，视情况选择：

2. 云上 k8s 集群，请直接使用 LoadBalancer 暴露服务。
1. 自建的本地测试集群，建议直接使用 NodePort 暴露 80/443 端口。
3. 自建的本地生产环境集群，可以考虑使用 [metallb](https://github.com/metallb/metallb)/[porter](https://github.com/kubesphere/porter) 这两个 bare-metal 的 LoadBalancer Service 实现。
   1. metallb 和 porter 需要搭配支持 BGP 协议的路由器使用，而且路由器本身也需要做高可用，更底层还有链路层高可用要做。门槛比较高，这也是普通企业搞不起私有云的原因。


## 修改 NodePort 的端口范围限制

端口范围受 kube-apiserver 的管理，可通过 kube-apiserver 的 `--service-node-port-range` 参数配置：

```shell
$ docker run --rm registry.cn-hangzhou.aliyuncs.com/google_containers/kube-apiserver:v1.18.0  kube-apiserver --help
......
Misc flags:
......
      --service-node-port-range portRange         A port range to reserve for services with NodePort visibility. Example: '30000-32767'. Inclusive at both ends of the range. (default 30000-32767)

```

可以看到默认的端口范围是 `30000-32767`.

要去掉这个限制，就需要手动修改**所有 kube-apiserver** 的配置文件，添加参数 `--service-node-port-range=20-30000`，然后重启所有 kube-apiserver.

kube-apiserver 的配置文件位置一般为 `/etc/kubernetes/manifests/kube-apiserver.yaml`，是一个 Pod 定义文件。
