# Horizontal Pod Autoscaler - Pod 自动扩缩容

Kubernetes 的 HPA 可以通过 CPU/RAM 进行 Pod 伸缩，另外也支持自定义指标（如每秒请求数等）。

注意事项：

1. HPA 需要从 metrics-server 获取监控指标，因此 kubernetes 集群一定要部署好 [metrics-server](../metrics/metrics-server.md).
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


## HPA 的期望值设成多少合适

这个具体情况具体分析，以最常用的 CPU 值为例：

- 通常情况下，HPA 期望值建议设为 60% 到 65% 可能是比较合适的。最小副本数建议设为 3/4/5
  - 同时建议为服务添加 `PodDisruptionBudget`，将最小可用副本数设为 2/3/4，保证正常的节点伸缩场景下，同时被干掉的 pod 数量至多只有 1 个。
- 如果服务性能不太行，QPS 稍微一变化，CPU 就可能飙升，那也只好调低服务的 HPA 期望值，比如调整到 50%


## 问题

### 1. Pod 扩容 - 预热陷阱

>预热：Java/C# 这类运行在虚拟机上的语言，第一次使用到某些功能时，往往需要初始化一些资源，例如「JIT 即时编译」。
如果代码里还应用了动态类加载之类的功能，就很可能导致微服务某些 API 第一次被调用时，响应特别慢（要动态编译 class）。
因此 Pod 在提供服务前，需要提前「预热（slow_start）」一次这些接口，将需要用到的资源提前初始化好。

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

可以在「应用层面」解决：
1. 在就绪探针 API 的后端控制器里面，依次调用所有需要预热的接口，提前初始化好所有资源。
   1. 就绪探针的控制器中，可以通过 `localhost` 回环地址调用它自身的接口。
2. 使用「AOT 预编译」技术：预热，通常都是因为「JIT 即时编译」导致的问题，在需要用到时它才编译。而 AOT 是预先编译，在使用前完成编译，因此 AOT 能解决预热的问题。
也可以在「基础设施层面」解决：
1. 像 AWS ALB TargetGroup 以及其他云服务商的 ALB 服务，通常都可以设置 `slow_start` 时长，即对新加入的实例，使用一定时间慢慢地把流量切过去，最终达到预期的负载均衡状态。这个可以解决服务预热问题。


### 2. HPA 扩缩容过于敏感，导致 Pod 数量震荡

通常来讲，EKS 上绝大部分负载都应该选择使用 CPU 进行扩缩容。因为 CPU 通常能很好的反映服务的负载情况，对大部分服务而言，也就是 QPS.

但是有些服务会存在其他影响 CPU 使用率的因素，导致使用 CPU 扩缩容变得不那么可靠，比如：
- 有些 Java 服务堆内存设得很大，GC pause 也设得比较长，因此内存 GC 会造成 CPU 间歇性飙升，CPU 监控会有大量的尖峰。

因为上述问题存在，使用 CPU 扩缩容，就可能会造成服务频繁的扩容然后缩容。
而有些服务（如我们的「推荐服务」），对「扩容」和「缩容」都是比较敏感的，每次扩缩都会造成服务可用率抖动。

对这类服务而言，HPA 有这几种调整策略：
- 选择使用 **QPS** 等相对比较平滑，没有 GC 这类干扰的指标来进行扩缩容
- 对 kubernetes 1.18+，可以直接使用 HPA 的 `behavior.scaleDown` 和 `behavior.scaleUp` 两个参数，控制每次扩缩容的最多 pod 数量或者比例。 示例如下：

```yaml
---
apiVersion: autoscaling/v2beta2
kind: HorizontalPodAutoscaler
metadata:
  annotations:
    # 这个 behavior 注解，功能与下面的 behavior 字段等同，二选一即可
    # 只在 kubernetes 1.18+ 生效，低版本可以 apply 此注解，但是实际上无效
    autoscaling.alpha.kubernetes.io/behavior: |
      {"ScaleDown":{
        "StabilizationWindowSeconds":600,
        "SelectPolicy":"Min",
        "Policies":[
          {"Type":"Percent","Value":5,"PeriodSeconds":1200},
          {"Type":"Pods","Value":3,"PeriodSeconds":1200}
        ]
      }}'
  name: podinfo
  namespace: default
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: podinfo
  minReplicas: 3
  maxReplicas: 50
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 50  # 期望的 CPU 平均值
  behavior:
    # 以下的一切配置，都是为了更平滑地缩容
    scaleDown:
      stabilizationWindowSeconds: 600  # 使用过去 10 mins 的最大 cpu 值进行缩容计算
      policies:
      - type: Percent  # 每 20 mins 最多缩容 `ceil[当前副本数 * 5%]` 个 pod（20 个 pod 以内，一次只缩容 1 个 pod）
        value: 5
        periodSeconds: 1200
      - type: Pods  # 每 20 mins 最多缩容 3 个 pod（即 >= 60 个 pods 时，每次缩容的 pod 数就不会涨了）
        value: 3
        periodSeconds: 1200
      selectPolicy: Min  # 上面的 policies 列表，只生效其中最小的值作为缩容限制（保证平滑缩容）
```


而对于扩容不够平滑这个问题，可以考虑提供类似 AWS ALB TargetGroup `slow_start` 的功能，在扩容时缓慢将流量切到新 Pod 上，以实现预热服务（JVM 预热以及本地缓存预热），这样就能达到比较好的平滑扩容效果。

## 参考

- [Pod 水平自动伸缩 - Kubernetes Docs](https://kubernetes.io/zh/docs/tasks/run-application/horizontal-pod-autoscale/)
- [Horizontal Pod Autoscaler演练 - Kubernetes Docs](https://kubernetes.io/zh/docs/tasks/run-application/horizontal-pod-autoscale-walkthrough/)

