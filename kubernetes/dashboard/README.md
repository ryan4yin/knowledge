# Kubernetes 控制面板

Kubernetes 有很多的 Web UI 或者本地 UI 组件可供选择：

1. [官方 Dashboard](https://github.com/kubernetes/dashboard): 个人感觉不是很好用，界面也比较丑。
3. [Kuboard](https://github.com/eip-work/kuboard-press): 一个很现代化的 Web UI 界面，界面信息非常详细，很适合初学者。
2. [K9s](https://github.com/derailed/k9s): 最好用的命令行 UI 界面，没有之一！
3. [kubesphere](https://github.com/kubesphere/kubesphere): 青云推出的 k8s 集群全家桶，自带 Web UI。值得一试。
4. 其他 rancher/openshift 等 k8s 发行版自带的 UI。


客户端建议安装 k9s，集群的 Web UI 推荐使用 kuboard。

kuboard 官方给出的安装命令：

```shell
# 1. 安装 kuboard
kubectl apply -f https://kuboard.cn/install-script/kuboard.yaml

# 2. 安装 metrics-server，这是 k8s 官方的 CPU/RAM 指标收集器，主要用于给 HPA 提供监控指标。同时也可用做轻量级的监控指标源。
kubectl apply -f https://addons.kuboard.cn/metrics-server/0.3.7/metrics-server.yaml
```
