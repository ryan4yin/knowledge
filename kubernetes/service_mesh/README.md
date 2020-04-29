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

#### 自定义部署

可以通过 `istioctl manifest apply -f custom-operator.yml` 进行自定义部署，`custom-oprator.yml` 的示例内容如下：

```yaml
apiVersion: install.istio.io/v1alpha1
kind: IstioOperator
spec:
  profile: default  # 选择 profile
  components:
    pilot:
      k8s:
        resources:
          requests:
            cpu: 1000m # override from default 500m
            memory: 4096Mi # ... default 2048Mi
        hpaSpec:
          maxReplicas: 10 # ... default 5
          minReplicas: 2  # ... default 1
        nodeSelector:
          master: "true"
        tolerations:
        - key: dedicated
          operator: Exists
          effect: NoSchedule
        - key: CriticalAddonsOnly
          operator: Exists
```

通过 `custom-operator.yml`，可以自定义 k8s 资源定义（节点选择器、HPA、资源预留与限制等等）、istio 组件本身的设置等等。

可以通过 `istioctl profile dump` 查看完整的 `operator.yml` 配置。

更多信息参见 [https://istio.io/docs/setup/install/istioctl/#configure-component-settings](https://istio.io/docs/setup/install/istioctl/#configure-component-settings)


### istioctl + prometheus-operator

部署 Istio 时可以不部署它自带的 Prometheus+Grafana，而是使用以 [kube-prometheus](https://github.com/coreos/kube-prometheus) 部署的监控系统进行监控。
但是需要手动修改 `istio-manifest.yaml`（前述生成的 yaml 配置），详见 [istioctl with prometheus-operator install](https://github.com/istio/istio/issues/21187#issuecomment-610744178)
