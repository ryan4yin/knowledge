
# [安装 Argo Workflow](https://argoproj.github.io/argo/installation/)

安装一个集群版(cluster wide)的 Argo Workflow，使用 MinIO 做 artifacts 存储：

```shell
kubectl apply -f https://raw.githubusercontent.com/argoproj/argo/stable/manifests/install.yaml
```

部署 MinIO:

```shell
helm repo add minio https://helm.min.io/ # official minio Helm charts
# 查看历史版本
helm search repo minio/minio -l | head
# 下载并解压 chart
helm pull minio/minio --untar --version 8.0.9

# 编写 custom-values.yaml，然后部署 minio
kubectl create namespace minio
helm install minio ./minio -n argo -f custom-values.yaml
```

minio 部署好后，它会将默认的 `accesskey` 和 `secretkey` 保存在名为 `minio` 的 secret 中。
我们需要修改 argo 的配置，将 minio 作为它的默认 artifact 仓库。

在 configmap `workflow-controller-configmap` 的 data 中添加如下字段：

```shell
  artifactRepository: |
    archiveLogs: true
    s3:
      bucket: argo-bucket   # bucket 名称，这个 bucket 需要先手动创建好！
      endpoint: minio:9000  # minio 地址
      insecure: true
      # 从 minio 这个 secret 中获取 key/secret
      accessKeySecret:
        name: minio
        key: accesskey
      secretKeySecret:
        name: minio
        key: secretkey
```

现在还差最后一步：手动进入 minio 的 Web UI，创建好 `argo-bucket` 这个 bucket.
直接访问 minio 的 9000 端口（需要使用 nodeport/ingress 等方式暴露此端口）就能进入 Web UI，使用前面提到的 secret `minio` 中的 key/secret 登录，就能创建 bucket.


## [ServiceAccount 配置](https://argoproj.github.io/argo/service-accounts/)

Argo Workflow 依赖于 ServiceAccount 进行验证与授权，而且默认情况下，它使用所在 namespace 的 `default` ServiceAccount 运行 workflow.

可 `default` 这个 ServiceAccount 默认根本没有任何权限！所以 Argo 的 artifacts, outputs, access to secrets 等功能全都会因为权限不足而无法使用！

为此，Argo 的官方文档提供了两个解决方法。

方法一，直接给 default 绑定 `cluster-admin` ClusterRole，给它集群管理员的权限，只要一行命令（但是显然安全性堪忧）： 

```shell
kubectl create rolebinding default-admin --clusterrole=admin --serviceaccount=<namespace>:default -n <namespace>
```

方法二，官方给出了[Argo Workflow 需要的最小权限的 Role 定义](https://argoproj.github.io/argo/workflow-rbac/)，方便起见我将它改成一个 ClusterRole:

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: argo-workflow-role
rules:
# pod get/watch is used to identify the container IDs of the current pod
# pod patch is used to annotate the step's outputs back to controller (e.g. artifact location)
- apiGroups:
  - ""
  resources:
  - pods
  verbs:
  - get
  - watch
  - patch
# logs get/watch are used to get the pods logs for script outputs, and for log archival
- apiGroups:
  - ""
  resources:
  - pods/log
  verbs:
  - get
  - watch
```

创建好上面这个最小的 ClusterRole，然后为每个名字空间，跑一下如下命令，给 default 账号绑定这个 clusterrole:

```shell
kubectl create rolebinding default-argo-workflow --clusterrole=argo-workflow-role  --serviceaccount=<namespace>:default -n <namespace>
```

这样就能给 default 账号提供最小的 workflow 运行权限。

或者如果你希望使用别的 ServiceAccount 来运行 workflow，也可以自行创建 ServiceAccount，然后再走上面方法二的流程，但是最后，要记得在 workflow 的 `spec.serviceAccountName` 中设定好 ServiceAccount 名称。


## [Workflow Executors](https://argoproj.github.io/argo/workflow-executors/)

Workflow Executor 是符合特定接口的一个进程(Process)，Argo 可以通过它执行一些动作，如监控 Pod 日志、收集 Artifacts、管理容器生命周期等等...

Workflow Executor 有多种实现，可以通过前面提到的 configmap `workflow-controller-configmap` 的 `containerRuntimeExecutor` 这个参数来选择。

可选项如下：

1. docker(默认): 目前使用范围最广，但是安全性最差。它要求一定要挂载访问 `docker.sock`，因此一定要 root 权限！
2. kubelet: 应用非常少，目前功能也有些欠缺，目前也必须提供 root 权限
3. Kubernetes API (k8sapi): 直接通过调用 k8sapi 实现日志监控、Artifacts 手机等功能，非常安全，但是性能欠佳。
4. Process Namespace Sharing (pns): 安全性比 k8sapi 差一点，因为 Process 对其他所有容器都可见了。但是相对的性能好很多。

在 docker 被 kubernetes 抛弃的当下，如果你已经改用 containerd 做为 kubernetes 运行时，那 argo 将会无法工作，因为它默认使用 docker 作为运行时！

我们建议将 workflow executore 改为 `pns`，兼顾安全性与性能。
