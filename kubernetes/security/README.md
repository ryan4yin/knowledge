# Kubernetes 安全

CNCF Landscape 中的 Security&Compliance 中的项目真的一大把。

这里主要介绍 Kubernetes 自身的安全策略， 像 open policy agent、falco、还有 notray(貌似主要用做镜像签
名校验) 等项目的介绍，请参考此文件夹下的其他文章。

## 一、Key Management

密钥管理方面，目前最流行的第三方工具显然是 hashicorp vault，另外还有个专门管 tls 证书的
cert-manager.

kubernetes 自带的 secrets 用的也必要多。

## 二、容器权限策略

如下两点的内容参见 [Kubernetes 最佳实践 - Pod 安全](../Kubernetes%20最佳实践.md#security)

1. [Pod SecurityContext](https://kubernetes.io/docs/tasks/configure-pod-container/security-context/)
1. seccomp: security compute mode

### 3. 集群全局的 Pod 安全策略

Pod SecurityContext 只能为每个 Pod 单独配置安全策略。为了保证安全性，我们显然还希望为整个集群定制一
个最小安全策略，禁止所有不符合此策略的 Pod 被提交运行。

Kubernetes 还提供了
[Pod Security Policy](https://kubernetes.io/docs/concepts/policy/pod-security-policy/) 控制集群中
Pod 安全相关的限制。但
是[ PSP 已在 kubernetes 1.21 被标记为废弃，并将在 1.25 中被彻底删除](https://github.com/kubernetes/kubernetes/pull/97171)。

目前 PSP 的替代品有 [open-policy-agent/gatekeeper](https://github.com/open-policy-agent/gatekeeper)
以及 [kyverno](https://github.com/kyverno/kyverno)

其中基于 OpenPolicyAgent 的 gatekeeper，需要使用 OPA 的 DSL rego 来编写配置，而 kyverno 提供了更易用
的 CRD，[kyverno samples](https://github.com/kyverno/kyverno/tree/main/samples) 中提供的 yaml 配置很
方便理解。

fluxcd/flux2 使用了 kyverno 做策略控制，它的配置非常直观，个人挺喜欢的。

## 二、容器运行时安全检测

### 1. [falco](https://github.com/falcosecurity/falco)

利用 Sysdig 的 Linux 内核指令和系统调用分析，Falco 能够深入理解系统行为。它的运行时规则引擎能够检测
应用、容器、主机以及 Kubernetes 的反常行为。

凭借 Falco，在每个 Kubernetes 节点部署一个代理，无需修改或者注入第三方代码或者加入 Sidecar 容器，就
能够得到完整的运行时可见性以及威胁检测。

但是也有人认为 Falco 不靠谱，因为它自身就是使用不安全的容器来运行的。

## 三、安全审计/扫描

- [kube-bench](https://github.com/aquasecurity/kube-bench): 使用 CIS Kubernetes 基准测试扫描集群组
  件，衡量 Kubernetes 集群的安全程度
- [kube-hunter](https://github.com/aquasecurity/kube-hunter): Kube-Hunter 在 Kubernetes 集群中查找安
  全弱点（例如远程代码执行或者信息泄露）。可以把 Kube-Hunter 作为一个远程扫描器，来从外部攻击者的视
  角来观察你的集群；也可以用 Pod 的方式来运行。
  - Kube-Hunter 有个特别之处就是“active hunting”，它不仅会报告问题，而且还会尝试利用在 Kubernetes 集
    群中发现的问题，这种操作可能对集群有害，应小心使用。
- [sonobuoy](https://github.com/vmware-tanzu/sonobuoy): 以无损害的方式运行一组插件（包括Kubernetes一
  致性测试）来评估 Kubernetes 集群的安全状态。

## 四、镜像安全

漏洞扫描：

- [trivy](https://github.com/aquasecurity/trivy): 容器镜像的漏洞扫描工具，harbor 可集成此工具为默认
  扫描器

安全分发（镜像签名与验证）：

- [theupdateframework/notray](https://github.com/theupdateframework/notary): harbor 仓库有集成此项目
- [theupdateframework/tuf](https://github.com/theupdateframework/tuf)

### 参考

- [Kubernetes Security](https://kubernetes.io/docs/concepts/security/)
- [9 Kubernetes security best practices everyone must follow](https://www.cncf.io/blog/2019/01/14/9-kubernetes-security-best-practices-everyone-must-follow/)
