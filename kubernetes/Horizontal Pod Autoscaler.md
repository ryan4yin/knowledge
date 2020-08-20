# Horizontal Pod Autoscaler - Pod 自动扩缩容

Kubernetes 的 HPA 可以通过 CPU/RAM 进行 Pod 伸缩，另外也支持自定义指标（如每秒请求数等）。

注意事项：

1. HPA 的「目标指标」可以使用两种形式：绝对度量指标和资源利用率。
    - 绝对度量指标：比如 CPU，就是设定绝对核数。
    - 资源利用率（资源使用量/资源请求 * 100%）：在 Pod 设置了资源请求时，可以使用资源利用率进行 Pod 伸缩。


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


为了防止 HPA 过于敏感，

## 参考

- [Pod 水平自动伸缩 - Kubernetes Docs](https://kubernetes.io/zh/docs/tasks/run-application/horizontal-pod-autoscale/)
- [Horizontal Pod Autoscaler演练 - Kubernetes Docs](https://kubernetes.io/zh/docs/tasks/run-application/horizontal-pod-autoscale-walkthrough/)

