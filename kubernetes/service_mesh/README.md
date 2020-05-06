# Service Mesh

## 一、Istio

### 1. 部署

使用 istioctl 部署 istio:
```shell
# 示例1：只部署 istiod 和 ingressgateway
istioctl manifest apply --set profile=default --set values.prometheus.enabled=false 

# 示例2：只部署 istiod 和 ingressgateway，并且使用内网的 docker hub 缓存
istioctl manifest apply \
  --set profile=default \
  --set values.prometheus.enabled=false \
  --set hub=registry.xxx.local > istio-manifest.yaml
```

这种方式适合自定义参数比较少，而且只是临时测试的情形。

#### 1.1 自定义部署（推荐方式）

可以通过 `istioctl manifest apply -f custom-operator.yml` 进行自定义部署，[custom-operator.yml](./custom-operator.yml) 就在当前文件夹内。

通过 [custom-operator.yml](./custom-operator.yml)，可以自定义 k8s 资源定义（节点选择器、HPA、资源预留与限制等等）、istio 组件本身的设置等等。而且可以直接保存在 git 仓库里，方便迭代、自动化部署。

可以通过 `istioctl profile dump` 查看完整的 IstioOperator 配置，作为编写 [custom-operator.yml](./custom-operator.yml) 的参考。

更多自定义部署的信息，参见官方文档 [istioctl: configure-component-settings](https://istio.io/docs/setup/install/istioctl/#configure-component-settings)


#### 1.2 升级与删除

滚动升级 istio:

```shell
# TODO 我使用此命令从 1.5.0 升级到 1.5.2 时一直卡住，没升级成功。
# 最后只好先删除掉 1.5.0 然后重新安装 1.5.2
istioctl upgrade -f custom-operator.yml
```

删除 istio：

```shell
# 格式如下：
istioctl manifest generate <your original installation options> | kubectl delete -f -
# 使用 --set 指定自定义参数
istioctl manifest generate --set profile=default --set values.prometheus.enabled=false | kubectl delete -f -
# 使用 istiooperator 配置指定自定义参数
istioctl manifest generate -f custom-operator.yml | kubectl delete -f -
```

### 2. 监控：istioctl + prometheus-operator

部署 Istio 时可以不部署它自带的 Prometheus+Grafana，而是使用以 [kube-prometheus](https://github.com/coreos/kube-prometheus) 部署的监控系统进行监控。
但是需要通过 [custom-operator.yml](./custom-operator.yml) 设定额外的配置，详见 [istioctl with prometheus-operator install](https://github.com/istio/istio/issues/21187#issuecomment-610744178)


### 4. 链路追踪（Istio + Jaeger + OpenTelemetry）

>OpenTracing 只支持跟踪 HTTP/GRPC 调用，而 Opencensus 提供了自定义指标的功能，使我们能跟踪任意自定义指标（比如 mysql 调用、redis 调用，甚至任意本地方法调用）。
现在上述两个开放标准已经合二为一：[OpenTelemetry](https://github.com/open-telemetry).

待续


### 5. Kiali 网络拓扑

待续
