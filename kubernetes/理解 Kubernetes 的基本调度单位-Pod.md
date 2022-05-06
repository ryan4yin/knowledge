# 理解 Kubernetes 的基本调度单位-Pod

我们已经知道，容器是通过 Cgroups/Namespace+rootfs 实现的，它的核心就是 pid=1 的进程，可以说容器的本质就是被隔离的进程。

而 Kubernetes 的 Pod，就是进程组，也是 Kubernetes 的基本调度单位。把多个进程组合成一个进程组 Pod 进行调度，有非常多的好处：

- istio 在 pod 中注入辅助容器（也称 sidecar）实现服务网格
- 在不方便修改应用代码使日志输出到 stdout/stderr 的情况下，可以通过 sidecar 实现容器的日志收集
- argo-workflows 使用 sidecar 来管理 workflow 每个 step 的生命周期
- 可通过 init-containers 来在主容器启动前进行一些必要的环境配置
- ...

Pod 的实现：

- 通过一个 Infra 容器来 hold 容器的名字空间，默认只 hold network namespace
  - Infra 镜像为 `k8s.gcr.io/pause`，它使用汇编语言编写，解压后也只有 100k - 200k，非常轻量，基本不消耗性能
- 其他容器在 Infra 容器之后被创建启动，并加入到 Infra 的 network namespace 中

因此一个 Pod 中的所有容器是共享 network namespace 的，可以通过 `localhost` 互相访问。

那么 Pod 中的容器还可以共享哪些名字空间呢？Pod 有如下可选参数：

```yaml
apiVersion: v1
kind: Pod
...
spec:
  # 共享 pid 名字空间，这样容器就可以看到其他容器的进程
  # 可通过 ps aux 验证，会发现 1 号进程变成了 pause，并且可以看到 Pod 中的所有进程
  # 在某些场景中需要用到它，比如 argo-workflows 就使用它来监测任务容器的执行状态
  shareProcessNamespace: true
  # 直接使用宿主机网络，不新建 network namespace
  hostNetwork: true
  # 直接使用宿主机的 IPC namespace
  hostIPC: true
  # 直接使用宿主机的 pid namespace，这样容器就能看到宿主机的所有进程了
  hostPID: true
```

凡是调度、网络、存储，以及安全相关的属性，基本上是 Pod 级别的

