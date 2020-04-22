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

使用 yaml 文件部署 istio（目前尚未找到正确方法）:

>使用 yaml 进行部署的好处是可以很方便地进行自定义修改，比如修改 hpa，添加 nodeSelector 等调度策略，等等。

```shell
# 生成 manifest.yaml 文件
istioctl manifest generate --set profile=default --set values.prometheus.enabled=false > istio-manifest.yaml
# 直接通过 kubectl 进行部署（有 Bug，无法成功！！！）
kubectl apply -f istio-manifest.yaml
```
