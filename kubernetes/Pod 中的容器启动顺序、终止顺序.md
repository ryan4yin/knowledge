# Pod 中的容器启动顺序、终止顺序


## PostStart

这实际上是利用了 kubernetes 的 postStart 功能，详见 [Delaying application start until sidecar is ready](https://medium.com/@marko.luksa/delaying-application-start-until-sidecar-is-ready-2ec2d21a7b74)，文中给出的 Pod 示例如下：

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: sidecar-starts-first
spec:
  containers:
  - name: sidecar
    image: my-sidecar
    lifecycle:
      postStart:
        exec:
          command:
          - /bin/wait-until-ready.sh
  - name: application
    image: my-application
```

这个 triky 在官方支持 Sidecar 容器前，是个不错的临时解决方案。其他 Sidecar 软件也可以参考。

但是注意它只解决了启动顺序的问题，容器的终止顺序它处理不了。另外 postStart 脚本报错也会导致主容器立即启动。



## Kubernetes 对 Sidecar 的支持

Kubernetes 有一个添加 Sidecar 支持的 KEP(k8s 优化提案): [Sidecar Containers - KEPS](https://github.com/kubernetes/enhancements/tree/master/keps/sig-node/753-sidecar-containers#implementation-history)

年初的时候曾经传出信息说在 1.18 中就会实现这个 KEP，但是实际上是个大乌龙。现在这个 KEP 已经退回到「provisional」状态，不知道什么时候会被拒绝或重新实现。

