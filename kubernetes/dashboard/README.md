# Kubernetes 控制面板

Kubernetes 有很多的 Web UI 或者本地 UI 组件可供选择：

1. [K9s](https://github.com/derailed/k9s): 本地命令行工具，最好用的命令行 UI 界面，没有之一！
2. [lens](https://github.com/lensapp/lens): 本地工具，UI 设计非常直观，信息也非常丰富，非常受欢迎。
3. [octant](https://github.com/vmware-tanzu/octant): 本地工具，UI 风格跟 Harbor 一脉相承。听说很好用，最大的特点是它的插件系统，可定制性很强。
   1. 它跟 lens 比较类似，而且从 2021 年底开始就不怎么活跃了。
4. [kuboard](https://github.com/eip-work/kuboard-press): 一个很现代化的 Web UI 界面，界面信息非常详细，很适合 Kubernetes 初学者。
5.  [官方 Dashboard](https://github.com/kubernetes/dashboard): 不是很好用，支持的认证方式也很有限，UI 设计也不太友好，直接暴露了一大堆信息。不推荐使用。
7. [scope](https://github.com/weaveworks/scope): 它感觉更多的是个集群拓扑可视化工具，听说拓扑图画得很不错，其他的功能或许有限？
    1.  但是 2020 年开始就不怎么活跃了。
8. [kubesphere](https://github.com/kubesphere/kubesphere): 青云推出的 k8s 集群全家桶，自带 Web UI。值得一试。
9.  其他 rancher/openshift 等 k8s 发行版自带的 UI


远程跳板机建议安装 k9s，本地 UI 可以考虑 k8s/lens.
至于集群的 Web UI，如果是提供给非专业用户或者初学者推荐使用 kuboard，如果希望获得强大的集群可视化能力可以考虑 scope.

kuboard 官方给出的安装命令：

```shell
# 1. 安装 kuboard
kubectl apply -f https://kuboard.cn/install-script/kuboard.yaml

# 2. 安装 metrics-server，这是 k8s 官方的 CPU/RAM 指标收集器，主要用于给 HPA 提供监控指标。同时也可用做轻量级的监控指标源。
kubectl apply -f https://addons.kuboard.cn/metrics-server/0.3.7/metrics-server.yaml
```

## 相关资料

视频:

- [A Walk Through the Kubernetes UI Landscape - Joaquim Rocha, Kinvolk & Henning Jacobs, Zalando SE](https://www.youtube.com/watch?v=lsrB21rjSok&list=PLj6h78yzYM2Pn8RxfLh2qrXBDftr6Qjut&index=136)
