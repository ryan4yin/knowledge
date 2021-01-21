# Kubernetes 安全

CNCF Landscape 中的 Security&Compliance 中的项目真的一大把。

这里主要介绍 Kubernetes 自身的安全策略， 像 open policy agent、falco、还有 notray(貌似主要用做镜像签名校验) 等项目的介绍，请参考此文件夹下的其他文章。


## 一、Key Management

密钥管理方面，目前最流行的第三方工具显然是 hashicorp vault，另外还有个专门管 tls 证书的 cert-manager.

kubernetes 自带的 secrets 用的也必要多。

## 二、容器权限策略

### 1. [Pod SecurityContext](https://kubernetes.io/docs/tasks/configure-pod-container/security-context/)

通过设置 Pod 的 SecurityContext，可以为每个 Pod 设置特定的安全策略。

SecurityContext 有两种类型：

1. `spec.securityContext`: 这是一个 [PodSecurityContext](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.20/#podsecuritycontext-v1-core) 对象
    - 顾名思义，它对 Pod 中的所有 contaienrs 都有效。
2. `spec.containers[*].securityContext`: 这是一个 [SecurityContext](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.20/#securitycontext-v1-core) 对象
    - container 私有的 SecurityContext

这两个 SecurityContext 的参数只有部分重叠，重叠的部分 `spec.containers[*].securityContext` 优先级更高。


我们比较常遇到的一些**提升权限**的安全策略：

1. 特权容器：`spec.containers[*].securityContext.privileged`
2. 添加（Capabilities）可选的系统级能力: `spec.containers[*].securityContext.capabilities.add`
   1. 只有 ntp 同步服务等少数容器，可以开启这项功能。请注意这非常危险。
3. Sysctls: 系统参数: `spec.securityContext.sysctls`

**权限限制**相关的安全策略有（**强烈建议在所有 Pod 上按需配置如下安全策略！**）：

1. `spec.volumes`: 所有的数据卷都可以设定读写权限
3. `spec.securityContext.runAsNonRoot: true` Pod 必须以非 root 用户运行
4. `spec.containers[*].securityContext.readOnlyRootFileSystem:true` **将容器层设为只读，防止容器文件被篡改。**
   1. 如果微服务需要读写文件，建议额外挂载 `emptydir` 类型的数据卷。
5. `spec.containers[*].securityContext.allowPrivilegeEscalation: false` 不允许 Pod 做任何权限提升！
6. `spec.containers[*].securityContext.capabilities.drop`: 移除（Capabilities）可选的系统级能力

还有其他诸如指定容器的运行用户(user)/用户组(group)等功能未列出，请自行查阅 Kubernetes 相关文档。

一个无状态的微服务 Pod 配置举例：

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: <Pod name>
spec:
  containers:
  - name: <container name>
    image: <image>
    imagePullPolicy: IfNotPresent 
    # ......此处省略 500 字
    securityContext:
      readOnlyRootFilesystem: true  # 将容器层设为只读，防止容器文件被篡改。
      allowPrivilegeEscalation: false  # 禁止 Pod 做任何权限提升
      capabilities:
        drop:
        # 禁止容器使用 raw 套接字，通常只有 hacker 才会用到 raw 套接字。
        # raw_socket 可自定义网络层数据，避开 tcp/udp 协议栈，直接操作底层的 ip/icmp 数据包。可实现 ip 伪装、自定义协议等功能。
        # 去掉 net_raw 会导致 tcpdump 无法使用，无法进行容器内抓包。需要抓包时可临时去除这项配置
        - NET_RAW
        # 更好的选择：直接禁用所有 capabilities
        # - ALL
  securityContext:
    # runAsUser: 1000  # 设定用户
    # runAsGroup: 1000  # 设定用户组
    runAsNonRoot: true  # Pod 必须以非 root 用户运行
    seccompProfile:  # security compute mode
      type: RuntimeDefault
```

### 2. seccomp: security compute mode

seccomp 和 seccomp-bpf 允许对系统调用进行过滤，可以防止用户的二进制文对主机操作系统件执行通常情况下并不需要的危险操作。它和 Falco 有些类似，不过 Seccomp 没有为容器提供特别的支持。

视频:

- [Seccomp: What Can It Do For You? - Justin Cormack, Docker](https://www.youtube.com/watch?v=Ro4QRx7VPsY&list=PLj6h78yzYM2Pn8RxfLh2qrXBDftr6Qjut$index=22)


### 3. 集群全局的 Pod 安全策略

Pod SecurityContext 只能为每个 Pod 单独配置安全策略。为了保证安全性，我们显然还希望为整个集群定制一个最小安全策略，禁止所有不符合此策略的 Pod 被提交运行。

Kubernetes 还提供了 [Pod Security Policy](https://kubernetes.io/docs/concepts/policy/pod-security-policy/) 控制集群中 Pod 安全相关的限制。但是[ PSP 已在 kubernetes 1.21 被标记为废弃，并将在 1.25 中被彻底删除](https://github.com/kubernetes/kubernetes/pull/97171)。

目前 PSP 的替代品有 [open-policy-agent/gatekeeper](https://github.com/open-policy-agent/gatekeeper)
以及 [kyverno](https://github.com/kyverno/kyverno)

其中基于 OpenPolicyAgent 的 gatekeeper，需要使用 OPA 的 DSL rego 来编写配置，
而 kyverno 提供了更易用的 CRD，[kyverno smaples](https://github.com/kyverno/kyverno/tree/main/samples) 中提供的 yaml 配置很方便理解。

fluxcd/flux2 使用了 kyverno 做策略控制，它的配置非常直观，个人挺喜欢的。


## 二、容器运行时安全检测

### 1. [falco](https://github.com/falcosecurity/falco)

利用 Sysdig 的 Linux 内核指令和系统调用分析，Falco 能够深入理解系统行为。它的运行时规则引擎能够检测应用、容器、主机以及 Kubernetes 的反常行为。

凭借 Falco，在每个 Kubernetes 节点部署一个代理，无需修改或者注入第三方代码或者加入 Sidecar 容器，就能够得到完整的运行时可见性以及威胁检测。

但是也有人认为 Falco 不靠谱，因为它自身就是使用不安全的容器来运行的。


## 三、安全审计/扫描

- [kube-bench](https://github.com/aquasecurity/kube-bench): 使用 CIS Kubernetes 基准测试扫描集群组件，衡量 Kubernetes 集群的安全程度
- [kube-hunter](https://github.com/aquasecurity/kube-hunter): Kube-Hunter 在 Kubernetes 集群中查找安全弱点（例如远程代码执行或者信息泄露）。可以把 Kube-Hunter 作为一个远程扫描器，来从外部攻击者的视角来观察你的集群；也可以用 Pod 的方式来运行。
  - Kube-Hunter 有个特别之处就是“active hunting”，它不仅会报告问题，而且还会尝试利用在 Kubernetes 集群中发现的问题，这种操作可能对集群有害，应小心使用。
- [sonobuoy](https://github.com/vmware-tanzu/sonobuoy): 以无损害的方式运行一组插件（包括Kubernetes一致性测试）来评估 Kubernetes 集群的安全状态。


## 四、镜像安全

漏洞扫描：

- [trivy](https://github.com/aquasecurity/trivy): 容器镜像的漏洞扫描工具，harbor 可集成此工具为默认扫描器

安全分发（镜像签名与验证）：

- [theupdateframework/notray](https://github.com/theupdateframework/notary): harbor 仓库有集成此项目
- [theupdateframework/tuf](https://github.com/theupdateframework/tuf)


### 参考

- [Kubernetes Security](https://kubernetes.io/docs/concepts/security/)
- [9 Kubernetes security best practices everyone must follow](https://www.cncf.io/blog/2019/01/14/9-kubernetes-security-best-practices-everyone-must-follow/)
- [Kyverno: The Swiss Army Knife of Kubernetes](https://neonmirrors.net/post/2021-01/kyverno-the-swiss-army-knife-of-kubernetes/)