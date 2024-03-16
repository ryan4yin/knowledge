# Kiali 流量观测

## 一、安装

> 以下部署方案还未完善，待修改

从 Istio 1.7 开始，Istioctl 不再安装 kiali，推荐使用 helm 部署最新稳定版的 kiali.

首先安装 helm-operator:

```shell
# 下载 flux 的 charts，我们需要修改其中一些配置
helm repo add kiali https://kiali.org/helm-charts
# 查看历史版本
helm search repo kiali/kiali-operator -l | head
# 下载并解压 chart，目的是方便 gitops 版本管理
helm pull kiali/kiali-operator --untar --version 1.23.0

# 安装或更新
kubectl create namespace kiali-operator
helm upgrade --install kiali-operator --namespace kiali-operator -f kiali-operator-values.yaml ./kiali-operator

# 卸载
helm uninstall kiali-operator --namespace kiali-operator
```

> 和 jaeger-operator 一样，kiali-operator 自身也没几个参数可配置。

operator 有了，现在手动下载并修改
[kiali_cr.yaml](https://github.com/kiali/kiali-operator/blob/master/deploy/kiali/kiali_cr.yaml) 并部
署。kiali-operator 会根据 `kiali_cr.yaml` 的内容，创建/更新/修改 kiali 服务。

需要修改的配置有：

1. prometheus+grafana: kiali 需要从 prometheus 中查询 istio 网格的各项指标。
   1. 我们使用 prometheus operator，需要自定义 prometheus 的 url 为
      `http://prometheus-operator-prometheus.monitoring:9090`
   2. kiali 需要使用 grafana 中定义好的 istio 相关 PromQL，因此得自定义 grafana 的 url 为
      `http://prometheus-operator-grafana.monitoring:80`
1. jaeger: kiali 还需要查询链路追踪的数据，因此还得配置 jaeger-query　的　api url:
   `http://jaeger.tracing:80`
1. Web UI 相关：kiali 通过 Web UI 展示网格数据。
   1. `auth`: 测试环境可设置为 `anonymous`，方便测试。
   2. 本地测试环境使用 NodePort 暴露出 Web UI 端口

```shell
kubectl apply -f my-kiali-cr.yaml -n istio-system
```

### 基于流量拓扑图的流量观测

待续
