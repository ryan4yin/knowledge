如何升级一个 Kubernetes 集群
---



## 热升级

Kubernetes 作为一个复杂的集群系统，在其中正运行着重要应用的情况下，热升级需要考虑的东西非常多。

最简单也是最常见的升级方式，是直接搭建一个新集群并测试好，然后直接将流量切到新集群。
这个方法一是简单，二是出了问题可以立即回滚到旧集群。


那么如果非热升级不可（这种情况应该很少见），该如何处理呢？云上环境建议直接和云服务提供商（阿里/腾讯/华为/AWS）沟通，设计方案。


## 参考

- [Upgrading kubeadm clusters](https://kubernetes.io/docs/tasks/administer-cluster/kubeadm/kubeadm-upgrade/)
