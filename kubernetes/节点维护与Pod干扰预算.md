# [节点维护与Pod干扰预算](https://kubernetes.io/zh/docs/tasks/run-application/configure-pdb/)

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
#   maxUnavailable: 1  # 最大不可用的 Pod 数
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


## 创业初期使用单副本微服务时的节点维护方案

如果你的团队没钱，撑不起双副本，那么在节点维护时就会遇到问题：

1. 不设 PDB 的情况下，一旦驱逐 Pod，就一定会导致服务短暂中断。
2. 设了 PDB 的情况下，Pod 将无法被驱逐——满足不了 PDB 预算。

唯一的解决方法，就是设置了 PDB 后，先扩容到双副本，再进行节点维护。

但是因为钱不够，所以只能：

1. `kubectl drain node-xxx`
2. 扩容微服务 A 到双副本，等待它完成驱逐。
3. 将微服务 A 再缩容为单副本。
4. 扩容微服务 B 到双副本，等待它完成驱逐。
5. 将微服务 B 再缩容为单副本
6. 以此类推，直到所有微服务都被调度到其他节点上。

不知道有没有谁做过类似的自动化功能。。。
