# Kubernetes 安全


## [Pod 安全策略](https://kubernetes.io/docs/tasks/configure-pod-container/security-context/)

通过设置 Pod 的 SecurityContext，可以为每个 Pod 设置特定的安全策略。

此外，在集群层面，Kubernetes 还提供了 [Pod Security Policy](https://kubernetes.io/docs/concepts/policy/pod-security-policy/) 控制集群中 Pod 安全相关的限制。

### 1. SecurityContext

我们比较常遇到的一些**提升权限**的安全策略：

1. 特权容器：spec.containers[*].securityContext.privileged
2. 添加（Capabilities）可选的系统级能力: spec.containers[*].securityContext.capabilities.add
   1. 只有 ntp 同步服务等少数容器，可以开启这项功能。请注意这非常危险。
3. Sysctls: 系统参数: spec.securityContext.sysctls

**权限限制**相关的安全策略有（**强烈建议在所有 Pod 上按需配置如下安全策略！**）：

1. `spec.volumes`: 所有的数据卷都可以设定读写权限
3. `spec.securityContext.runAsNonRoot: true` Pod 必须以非 root 用户运行
4. `spec.securityContext.readOnlyRootFileSystem:true` **将容器层设为只读，防止容器文件被篡改。**
   1. 如果微服务需要读写文件，建议额外挂载 `emptydir` 类型的数据卷。
5. `spec.securityContext.allowPrivilegeEscalation: false` 不允许 Pod 做任何权限提升！
6. `spec.containers[*].securityContext.capabilities.drop`: 移除（Capabilities）可选的系统级能力

还有其他诸如指定容器的运行用户(user)/用户组(group)等功能未列出，请自行查阅 Kubernetes 相关文档。

一个无状态的微服务 Pod 配置举例：

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: <Pod name>
  annotations:
    # 设置 secure computing mode 为 `runtime/default`，这个我还没搞明白
    seccomp.security.alpha.kubernetes.io/pod: "runtime/default"
spec:
  containers:
  - name: <container name>
    image: <image>
    imagePullPolicy: IfNotPresent 
    # ......此处省略 500 字
  securityContext:
    runAsNonRoot: true  # Pod 必须以非 root 用户运行
    readOnlyRootFilesystem: true  # 将容器层设为只读，防止容器文件被篡改。
    allowPrivilegeEscalation: false  # 禁止 Pod 做任何权限提升
```

## 参考

- [Kubernetes Security](https://kubernetes.io/docs/concepts/security/)
