# [KEDA](https://github.com/kedacore/keda)

KEDA 是微软开源的一个 kubernetes 自动伸缩组件，KEDA 以 Metrics Server 的形式工作，允许用户通过 CRDs 定制伸缩策略。

它支持通过事件驱动来扩缩容，并且可以缩容至 0，因此也非常适合于 Serverless 场景。

阿里的 kubevela 底层就使用了 KEDA 做自动伸缩。


## 优势

- 支持非常多种数据源，完爆 prometheus-adapter
- CRD 定义比 HPA v2beta2 以及 prometheus-adapter 更直观，更好理解


## 使用 KEDA 实现服务扩缩容

>https://keda.sh/docs/2.5/concepts/scaling-deployments/#scaledobject-spec

这里暂时不涉及 serverless 场景，因此先不考虑缩容到 0

### 1. 使用 Istio 的 QPS 进行扩缩容

```yaml
apiVersion: keda.sh/v1alpha1
kind: ScaledObject
metadata:
  name: my-app-v3
  namespace: default
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind:  Deployment
    name: my-app-v3
  pollingInterval:  30
  minReplicaCount:  3
  maxReplicaCount:  100
  # idleReplicaCount: 0    # （必须为 0）如果设置了它，服务在空闲时会缩容到 0
  # cooldownPeriod:   300  # 从 0 扩容到 minReplicaCount 后，缩容到 0 的冷却时间
  advanced:
    restoreToOriginalReplicaCount: false
    horizontalPodAutoscalerConfig:
    # kubernetes 1.18+ 的 behavior 参数
      behavior: 
        scaleDown:
          stabilizationWindowSeconds: 300
          policies:
          - type: Percent
            value: 100
            periodSeconds: 15
  triggers:
  - type: prometheus
    metadata:
        serverAddress: http://<prometheus-host>:9090
        metricName: istio_requests_total_my_app_v3
        # istio 的 HTTP QPS 指标，排除掉只有代理层才会产生的错误状态码：502/503/504
        query: sum(irate(istio_requests_total{reporter="destination", response_code!~"502|503|504", destination_service_name="my-app", destination_service_namespace="default", destination_version="v3"}[2m]))
        # istio 的 GRPC 请求速率指标
        # query: sum(irate(istio_request_messages_total{reporter="destination", destination_service_name="my-app", destination_service_namespace="default", destination_version="v3"}[2m]))
        threshold: '180'  # （query 值 / 副本数）假设每个 Pod 能撑住 300 QPS，这里以 60% 为扩容临界值
```

## 直接获取裸指标

参见 https://keda.sh/docs/2.5/operate/metrics-server/

