# Kubernetes 安全


## [Pod 安全策略](https://kubernetes.io/docs/tasks/configure-pod-container/security-context/)

通过设置 Pod 的 SecurityContext，可以为每个 Pod 设置特定的安全策略。

此外，在集群层面，Kubernetes 还提供了 [Pod Security Policy](https://kubernetes.io/docs/concepts/policy/pod-security-policy/) 控制集群中 Pod 安全相关的限制。

### 1. SecurityContext

我们比较常遇到的一些**提升权限**的安全策略：

1. 特权容器：spec.containers[*].securityContext.privileged
2. Capabilities 可选的系统级能力: spec.containers[*].securityContext.capabilities.add
   1. 只有 ntp 同步服务等少数容器，可以开启这项功能。请注意这非常危险。
3. Sysctls: 系统参数: spec.securityContext.sysctls

**权限限制**相关的安全策略有：

1. spec.volumes: 所有的数据卷都可以设定读写权限
2. spec.securityContext.runAsNonRoot: Pod 必须以非 root 用户运行
3. spec.securityContext.readOnlyRootFileSystem: **将容器层设为只读，防止容器文件被篡改。**

还有其他诸如指定容器的运行用户(user)/用户组(group)等功能未列出，请自行查阅 Kubernetes 相关文档。

## 参考

- [Kubernetes Security](https://kubernetes.io/docs/concepts/security/)
