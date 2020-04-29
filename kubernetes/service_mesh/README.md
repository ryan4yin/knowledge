# Service Mesh

## 一、Istio

### 1. 部署

使用 istioctl 部署 istio:
```shell
# 只部署 istiod 和 ingressgateway
istioctl manifest apply --set profile=default --set values.prometheus.enabled=false 

# 只部署 istiod 和 ingressgateway，并且使用内网的 docker hub 缓存
istioctl manifest apply --set profile=default --set values.prometheus.enabled=false --set hub=harbor.local/istio
```

使用 yaml 文件部署 istio:

>使用 yaml 进行部署的好处是可以很方便地进行自定义修改，比如修改 hpa，添加 nodeSelector 等调度策略，等等。

```shell
# 1. 生成 manifest.yaml 文件
istioctl manifest generate \
  --set profile=default --set values.prometheus.enabled=false \
  --set hub=registry.xxx.local > istio-manifest.yaml
# 2. 修改 istio-manifest.yaml，修改 HPA，添加调度策略等。
# 3. 通过 istioctl+修改过的 yaml 文件进行部署(不能直接用 kubectl apply!)
istioctl manifest apply --filename istio-manifest.yaml
```

### istioctl + prometheus-operator

部署 Istio 时可以不部署它自带的 Prometheus+Grafana，而是使用以 [kube-prometheus](https://github.com/coreos/kube-prometheus) 部署的监控系统进行监控。
但是需要手动修改 `istio-manifest.yaml`（前述生成的 yaml 配置），详见 [istioctl with prometheus-operator install](https://github.com/istio/istio/issues/21187#issuecomment-610744178)
