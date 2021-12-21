# Kubernetes 最佳实践

首先，最基本的配置：

- 将容器的资源请求与限制设置成一样的，避免出现资源竞争


## 零、示例

首先给出一个 Deployment+HPA+ PodDisruptionBudget 的 demo：

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-app-v3
  namespace: prod
  labels:
    app: my-app
spec:
  replicas: 3
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 10%  # 滚动更新时，每次最多更新 10% 的 Pods
      maxUnavailable: 0  # 滚动更新时，不允许出现不可用的 Pods，也就是说始终要维持 3 个可用副本
  selector:
    matchLabels:
      app: my-app
      version: v3
  template:
    metadata:
      labels:
        app: my-app
        version: v3
    spec:
      affinity:
        podAffinity:
          preferredDuringSchedulingIgnoredDuringExecution: # 非强制性条件
          - weight: 100  # weight 用于为节点评分，会优先选择评分最高的节点（只有一条规则的情况下，这个值没啥意义）
            podAffinityTerm:
              labelSelector:
                matchExpressions:
                - key: app
                  operator: In
                  values:
                  - my-app
                - key: version
                  operator: In
                  values:
                  - v3
              # pod 尽量使用同一种节点类型，也就是尽量保证节点的性能一致
              topologyKey: node.kubernetes.io/instance-type
        podAntiAffinity:
          preferredDuringSchedulingIgnoredDuringExecution: # 非强制性条件
          - weight: 100  # weight 用于为节点评分，会优先选择评分最高的节点（只有一条规则的情况下，这个值没啥意义）
            podAffinityTerm:
              labelSelector:
                matchExpressions:
                - key: app
                  operator: In
                  values:
                  - my-app
                - key: version
                  operator: In
                  values:
                  - v3
              # 将 pod 尽量打散在多个可用区
              topologyKey: topology.kubernetes.io/zone
          requiredDuringSchedulingIgnoredDuringExecution:  # 强制性要求（这个建议按需添加）
          # 注意这个没有 weights，必须满足列表中的所有条件
          - labelSelector:
              matchExpressions:
              - key: app
                operator: In
                values:
                - my-app
              - key: version
                operator: In
                values:
                - v3
            # Pod 必须运行在不同的节点上
            topologyKey: kubernetes.io/hostname
      securityContext:
        # runAsUser: 1000  # 设定用户
        # runAsGroup: 1000  # 设定用户组
        runAsNonRoot: true  # Pod 必须以非 root 用户运行
        seccompProfile:  # security compute mode
          type: RuntimeDefault
      nodeSelector:
        eks.amazonaws.com/nodegroup: common  # 使用专用节点组，如果希望使用多个节点组，可改用节点亲和性
      volumes:
      - name: tmp-dir
        emptyDir: {}
      containers:
      - name: my-app-v3
        image: my-app:v3  # 建议使用私有镜像仓库，规避 docker.io 的镜像拉取限制
        imagePullPolicy: IfNotPresent
        volumeMounts:
        - mountPath: /tmp
          name: tmp-dir
        lifecycle:
          preStop:
            exec:
              command:
              - /bin/sh
              - -c
              - "while [ $(netstat -plunt | grep tcp | wc -l | xargs) -ne 0 ]; do sleep 1; done"
        resources:  # 资源请求与限制
          # 对于核心服务，建议设置 requests = limits，避免资源竞争
          requests:
            # HPA 会使用 requests 计算资源利用率
            # 建议将 requests 设为服务正常状态下的 CPU 使用率，HPA 的目前指标设为 80%
            # 所有容器的 requests 总量不建议为 2c/4G 4c/8G 等常见值，因为节点通常也是这个配置，这会导致 Pod 只能调度到更大的节点上，适当调小 requests 等扩充可用的节点类型，从而扩充节点池。 
            cpu: 1000m
            memory: 1Gi
          limits:
            # limits - requests 为允许超卖的资源量，建议为 requests 的 1 到 2 倍，酌情配置。
            cpu: 1000m
            memory: 1Gi
        securityContext:
          # 将容器层设为只读，防止容器文件被篡改
          ## 如果需要写入临时文件，建议额外挂载 emptyDir 来提供可读写的数据卷
          readOnlyRootFilesystem: true
          # 禁止 Pod 做任何权限提升
          allowPrivilegeEscalation: false
          capabilities:
            # drop ALL 的权限比较严格，可按需修改
            drop:
            - ALL
        startupProbe:  # 要求 kubernetes 1.18+
          httpGet:
            path: /actuator/health  # 直接使用健康检查接口即可
            port: 8080
          periodSeconds: 5
          timeoutSeconds: 1
          failureThreshold: 20  # 最多提供给服务 5s * 20 的启动时间
          successThreshold: 1
        livenessProbe:
          httpGet:
            path: /actuator/health  # spring 的通用健康检查路径
            port: 8080
          periodSeconds: 5
          timeoutSeconds: 1
          failureThreshold: 5
          successThreshold: 1
        # Readiness probes are very important for a RollingUpdate to work properly,
        readinessProbe:
          httpGet:
            path: /actuator/health  # 简单起见可直接使用 livenessProbe 相同的接口，当然也可额外定义
            port: 8080
          periodSeconds: 5
          timeoutSeconds: 1
          failureThreshold: 5
          successThreshold: 1
---
apiVersion: autoscaling/v2beta2
kind: HorizontalPodAutoscaler
metadata:
  labels:
    app: my-app
  name: my-app-v3
  namespace: prod
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: my-app-v3
  maxReplicas: 50
  minReplicas: 3
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
---
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: my-app-v3
  namespace: prod
  labels:
    app: my-app
spec:
  minAvailable: 75%
  selector:
    matchLabels:
      app: my-app
      version: v3
```

## 一、优雅停止（Gracful Shutdown）与 502/504 报错

如果 Pod 正在处理大量请求（比如 1000 QPS+）时，因为节点故障或「竞价节点」被回收等原因被重新调度，
你可能会观察到在容器被 terminate 的一段时间内出现少量 502/504。

为了搞清楚这个问题，需要先理解清楚 terminate 一个 Pod 的流程：

1. Pod 的状态被设为「Terminating」，（几乎）同时该 Pod 被从所有关联的 Service Endpoints 中移除
2. `preStop` 钩子被执行，它可以是一个命令，或者一个对 Pod 中容器的 http 调用
   1. 如果你的程序在收到 SIGTERM 信号时，无法优雅退出，就可以考虑使用 `preStop`
   2. 如果让程序本身支持优雅退出比较麻烦的话，用 `preStop` 实现优雅退出是一个非常好的方式
3. 将 SIGTERM 发送给 Pod 中的所有容器
4. 继续等待，直到超过 `spec.terminationGracePeriodSeconds` 设定好的时间，这个值默认为 30s
   1. 需要注意的是，这个优雅退出的等待计时是与 `preStop` 同步开始的！而且它也不会等待 `preStop` 结束！
5. 如果超过了 `spec.terminationGracePeriodSeconds` 容器仍然没有停止，k8s 将会发送 SIGKILL 信号给容器
6. 进程全部终止后，整个 Pod 完全被清理掉

**注意**：1 和 2 两个工作是异步发生的，所以可能会出现「Pod 还在 Service Endpoints 中，但是 `preStop` 已经执行了」的情况，我们需要考虑到这种状况的发生。

了解了上面的流程后，我们就能分析出两种错误码出现的原因：

- 502：应用程序在收到 SIGTERM 信号后直接终止了运行，导致部分还没有被处理完的请求直接中断，代理层返回 502 表示这种情况
- 504：Service Endpoints 移除不够及时，在 Pod 已经被终止后，仍然有个别请求被路由到了该 Pod，得不到响应导致 504

通常的解决方案是，在 Pod 的 `preStop` 步骤加一个 15s 的等待时间。
其原理是：在 Pod 处理 terminating 状态的时候，就会被从 Service Endpoints 中移除，也就不会再有新的请求过来了。
在 `preStop` 等待 15s，基本就能保证所有的请求都在容器死掉之前被处理完成（一般来说，绝大部分请求的处理时间都在 300ms 以内吧）。

一个简单的示例如下，它使 Pod 被终止时，总是先等待 15s，再发送 SIGTERM 信号给容器：

```yaml
    containers:
    - name: my-app
      # 添加下面这部分
      lifecycle:
        preStop:
          exec:
            command:
            - /bin/sleep
            - "15"
```

更好的解决办法，是直接等待所有 tcp 连接都关闭（需要镜像中有 netstat）：

```yaml
    containers:
    - name: my-app
      # 添加下面这部分
      lifecycle:
      preStop:
          exec:
            command:
            - /bin/sh
            - -c
            - "while [ $(netstat -plunt | grep tcp | wc -l | xargs) -ne 0 ]; do sleep 1; done"
```


### 参考

- [Kubernetes best practices: terminating with grace](https://cloud.google.com/blog/products/containers-kubernetes/kubernetes-best-practices-terminating-with-grace)
- [Graceful shutdown in Kubernetes is not always trivial](https://medium.com/flant-com/kubernetes-graceful-shutdown-nginx-php-fpm-d5ab266963c2)


## 二、[节点维护与Pod干扰预算](https://kubernetes.io/zh/docs/tasks/run-application/configure-pdb/)

在我们通过 `kubectl drain` 将某个节点上的容器驱逐走的时候，
kubernetes 会依据 Pod 的「PodDistruptionBuget」来进行 Pod 的驱逐。

如果不设置任何明确的 PodDistruptionBuget，Pod 将会被直接杀死，然后在别的节点重新调度，**这可能导致服务中断！**

PDB 是一个单独的 CR 自定义资源，示例如下：

```yaml
apiVersion: policy/v1beta1
kind: PodDisruptionBudget
metadata:
  name: podinfo-pdb
spec:
  # 如果不满足 PDB，Pod 驱逐将会失败！
  minAvailable: 1      # 最少也要维持一个 Pod 可用
#   maxUnavailable: 1  # 最大不可用的 Pod 数，与 minAvailable 不能同时配置！二选一
  selector:
    matchLabels:
      app: podinfo
```

如果在进行节点维护时(kubectl drain)，Pod 不满足 PDB，drain 将会失败，示例：

```shell
> kubectl drain node-205 --ignore-daemonsets --delete-local-data
node/node-205 cordoned
WARNING: ignoring DaemonSet-managed Pods: kube-system/calico-node-nfhj7, kube-system/kube-proxy-94dz5
evicting pod default/podinfo-7c84d8c94d-h9brq
evicting pod default/podinfo-7c84d8c94d-gw6qf
error when evicting pod "podinfo-7c84d8c94d-h9brq" (will retry after 5s): Cannot evict pod as it would violate the pod's disruption budget.
evicting pod default/podinfo-7c84d8c94d-h9brq
error when evicting pod "podinfo-7c84d8c94d-h9brq" (will retry after 5s): Cannot evict pod as it would violate the pod's disruption budget.
evicting pod default/podinfo-7c84d8c94d-h9brq
error when evicting pod "podinfo-7c84d8c94d-h9brq" (will retry after 5s): Cannot evict pod as it would violate the pod's disruption budget.
evicting pod default/podinfo-7c84d8c94d-h9brq
pod/podinfo-7c84d8c94d-gw6qf evicted
pod/podinfo-7c84d8c94d-h9brq evicted
node/node-205 evicted
```

上面的示例中，podinfo 一共有两个副本，都运行在 node-205 上面。我给它设置了干扰预算 PDB `minAvailable: 1`。

然后使用 `kubectl drain` 驱逐 Pod 时，其中一个 Pod 被立即驱逐走了，而另一个 Pod 大概在 15 秒内一直驱逐失败。
因为第一个 Pod 还没有在新的节点上启动完成，它不满足干扰预算 PDB `minAvailable: 1` 这个条件。

大约 15 秒后，最先被驱逐走的 Pod 在新节点上启动完成了，另一个 Pod 满足了 PDB 所以终于也被驱逐了。这才完成了一个节点的 drain 操作。

>ClusterAutoscaler 等集群节点伸缩组件，在缩容节点时也会考虑 PodDisruptionBudget. 如果你的集群使用了 ClusterAutoscaler 等动态扩缩容节点的组件，强烈建议设置为所有服务设置 PodDisruptionBudget.


#### 在 PDB 中使用百分比的注意事项

在使用百分比时，计算出的实例数都会被向上取整，这会造成两个现象：

- 如果使用 `minAvailable`，实例数较少的情况下，可能会导致 ALLOWED DISRUPTIONS 为 0
- 如果使用 `maxUnavailable`，因为是向上取整，ALLOWED DISRUPTIONS 的值一定不会低于 1

因此从便于驱逐的角度看，如果你的服务至少有 2-3 个实例，建议在 PDB 中使用百分比配置 `maxUnavailable`，而不是 `minAvailable`.

### 最佳实践 Deployment + HPA + PodDisruptionBudget

一般而言，一个服务的每个版本，都应该包含如下三个资源：

- Deployment: 管理服务自身的 Pods 嘛
- HPA: 负责 Pods 的扩缩容，通常使用 CPU 指标进行扩缩容
- PodDisruptionBudget(PDB): 建议按照 HPA 的目标值，来设置 PDB. 
  - 比如 HPA CPU 目标值为 60%，就可以考虑设置 PDB `minAvailable=65%`，保证至少有 65% 的 Pod 可用。这样理论上极限情况下 QPS 均摊到剩下 65% 的 Pods 上也不会造成雪崩（这里假设 QPS 和 CPU 是完全的线性关系） 

## 三、节点亲和性与节点组

我们一个集群，通常会使用不同的标签为节点组进行分类，比如 kubernetes 自动生成的一些节点标签：

- `kubernetes.io/os`: 通常都用 `linux`
- `kubernetes.io/arch`: `amd64`, `arm64`
- `topology.kubernetes.io/region` 和 `topology.kubernetes.io/zone`: 云服务的区域及可用区

我们使用得比较多的，是「节点亲和性」以及「Pod 反亲和性」，另外两个策略视情况使用。

### 1. 节点亲和性

如果你使用的是 aws，那 aws 有一些自定义的节点标签：

- `eks.amazonaws.com/nodegroup`: aws eks 节点组的名称，同一个节点组使用同样的 aws ec2 实例模板
  - 比如 arm64 节点组、amd64/x64 节点组
  - 内存比例高的节点组如 m 系实例，计算性能高的节点组如 c 系列
  - 竞价实例节点组：这个省钱啊，但是动态性很高，随时可能被回收
  - 按量付费节点组：这类实例贵，但是稳定。

假设你希望优先选择竞价实例跑你的 Pod，如果竞价实例暂时跑满了，就选择按量付费实例。
那 `nodeSelector` 就满足不了你的需求了，你需要使用 `nodeAffinity`，示例如下:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: xxx
  namespace: xxx
spec:
  # ...
  template:
    # ...
    spec:
      affinity:
        nodeAffinity:
          # 优先选择 spot-group-c 的节点
          preferredDuringSchedulingIgnoredDuringExecution:
          - preference:
              matchExpressions:
              - key: eks.amazonaws.com/nodegroup
                operator: In
                values:
                - spot-group-c
            weight: 80  # weight 用于为节点评分，会优先选择评分最高的节点
          - preference:
              matchExpressions:
              # 优先选择 aws c6i 的机器
              - key: node.kubernetes.io/instance-type
                operator: In
                values:
                - "c6i.xlarge"
                - "c6i.2xlarge"
                - "c6i.4xlarge"
                - "c6i.8xlarge"
            weight: 70
          - preference:
              matchExpressions:
              # 其次选择 aws c5 的机器
              - key: node.kubernetes.io/instance-type
                operator: In
                values:
                - "c5.xlarge"
                - "c5.2xlarge"
                - "c5.4xlarge"
                - "c5.9xlarge"
            weight: 60
         # 如果没 spot-group-c 可用，也可选择 ondemand-group-c 的节点跑
          requiredDuringSchedulingIgnoredDuringExecution:
            nodeSelectorTerms:
            - matchExpressions:
              - key: eks.amazonaws.com/nodegroup
                operator: In
                values:
                - spot-group-c
                - ondemand-group-c
      containers:
        # ...
```


### 2. Pod 反亲和性

通常建议为每个 Deployment 的 template 配置 Pod 反亲和性，把 Pods 打散在所有节点上：

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: xxx
  namespace: xxx
spec:
  # ...
  template:
    # ...
    spec:
      replicas: 3
      affinity:
        podAntiAffinity:
          preferredDuringSchedulingIgnoredDuringExecution: # 非强制性条件
          - weight: 100  # weight 用于为节点评分，会优先选择评分最高的节点
            podAffinityTerm:
              labelSelector:
                matchExpressions:
                - key: app
                  operator: In
                  values:
                  - xxx
                - key: version
                  operator: In
                  values:
                  - v12
              # 将 pod 尽量打散在多个可用区
              topologyKey: topology.kubernetes.io/zone
          requiredDuringSchedulingIgnoredDuringExecution:  # 强制性要求
          # 注意这个没有 weights，必须满足列表中的所有条件
          - labelSelector:
              matchExpressions:
              - key: app
                operator: In
                values:
                - xxx
              - key: version
                operator: In
                values:
                - v12
            # Pod 必须运行在不同的节点上
            topologyKey: kubernetes.io/hostname
```


## 四、Pod 的就绪探针、存活探针与启动探针

Pod 提供如下三种探针，均支持使用 Command、HTTP API、TCP Socket 这三种手段来进行服务可用性探测。

- `startupProbe` 启动探针（Kubernetes v1.18 [beta]）: 此探针通过后，「就绪探针」与「存活探针」才会进行存活性与就绪检查
  - 用于对慢启动容器进行存活性检测，避免它们在启动运行之前就被杀掉
    - startupProbe 显然比 livenessProbe 的 initialDelaySeconds 参数更灵活。
    - 同时它也能延迟 readinessProbe 的生效时间，这主要是为了避免无意义的探测。容器都还没 startUp，显然是不可能就绪的。
  - 程序将最多有 `failureThreshold * periodSeconds` 的时间用于启动，比如设置 `failureThreshold=20`、`periodSeconds=5`，程序启动时间最长就为 100s，如果超过 100s 仍然未通过「启动探测」，容器会被杀死。
- `readinessProbe` 就绪探针:
  - 就绪探针失败次数超过 `failureThreshold` 限制（默认三次），服务将被暂时从 Service 的 Endpoints 中踢出，直到服务再次满足 `successThreshold`.
- `livenessProbe` 存活探针: 检测服务是否存活，它可以捕捉到死锁等情况，及时杀死这种容器。
  - 存活探针失败可能的原因：
    - 服务发生死锁，对所有请求均无响应
    - 服务线程全部卡在对外部 redis/mysql 等外部依赖的等待中，导致请求无响应
  - 存活探针失败次数超过 `failureThreshold` 限制（默认三次），容器将被杀死，随后根据重启策略执行重启。
    - `kubectl describe pod` 会显示重启原因为 `State.Last State.Reason = Error, Exit Code=137`，同时 Events 中会有 `Liveness probe failed: ...` 这样的描述。


上述三类探测器的参数都是通用的，五个时间相关的参数列举如下：

```yaml
# 下面的值就是 k8s 的默认值
initialDelaySeconds: 0  # 默认没有 delay 时间
periodSeconds: 10
timeoutSeconds: 1
failureThreshold: 3
successThreshold: 1
```

示例：

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-app-v3
spec:
  # ...
  template:
    #  ...
    spec:
      containers:
      - name: my-app-v3
        image: xxx.com/app/my-app:v3
        imagePullPolicy: IfNotPresent 
        # ... 省略若干配置
        startupProbe:
          httpGet:
            path: /actuator/health  # 直接使用健康检查接口即可
            port: 8080
          periodSeconds: 5
          timeoutSeconds: 1
          failureThreshold: 20  # 最多提供给服务 5s * 20 的启动时间
          successThreshold: 1
        livenessProbe:
          httpGet:
            path: /actuator/health  # spring 的通用健康检查路径
            port: 8080
          periodSeconds: 5
          timeoutSeconds: 1
          failureThreshold: 5
          successThreshold: 1
        # Readiness probes are very important for a RollingUpdate to work properly,
        readinessProbe:
          httpGet:
            path: /actuator/health  # 简单起见可直接使用 livenessProbe 相同的接口，当然也可额外定义
            port: 8080
          periodSeconds: 5
          timeoutSeconds: 1
          failureThreshold: 5
          successThreshold: 1
```

在 Kubernetes 1.18 之前，通用的手段是为「就绪探针」添加较长的 `initialDelaySeconds` 来实现类似「启动探针」的功能动，避免容器因为启动太慢，存活探针失败导致容器被重启。示例如下：

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-app-v3
spec:
  # ...
  template:
    #  ...
    spec:
      containers:
      - name: my-app-v3
        image: xxx.com/app/my-app:v3
        imagePullPolicy: IfNotPresent 
        # ... 省略若干配置
        livenessProbe:
          httpGet:
            path: /actuator/health  # spring 的通用健康检查路径
            port: 8080
          initialDelaySeconds: 120  # 前两分钟，都假设服务健康，避免 livenessProbe 失败导致服务重启
          periodSeconds: 5
          timeoutSeconds: 1
          failureThreshold: 5
          successThreshold: 1
        # 容器一启动，Readiness probes 就会不断进行检测
        readinessProbe:
          httpGet:
            path: /actuator/health
            port: 8080
          initialDelaySeconds: 3  # readiness probe 不需要设太长时间，使 Pod 尽快加入到 Endpoints.
          periodSeconds: 5
          timeoutSeconds: 1
          failureThreshold: 5
          successThreshold: 1
```

## 五、Pod 安全 {#security}

这里只介绍 Pod 中安全相关的参数，其他诸如集群全局的安全策略，不在这里讨论。

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


## 其他问题

- 不同节点类型的性能有差距，导致 QPS 均衡的情况下，CPU 负载不均衡
  - 解决办法：
    - 尽量使用性能相同的实例类型：通过 `podAffinity` 及 `nodeAffinity` 添加节点类型的亲和性
