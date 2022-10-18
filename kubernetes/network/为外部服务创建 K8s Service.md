# 为外部服务创建 Kubernetes Service

有时候我们希望在集群中直接访问外部服务，有两种方法：

1. 直接使用 [ExternalName](https://kubernetes.io/docs/concepts/services-networking/service/#externalname) 类型的 Kubernetes Service
   1. 它相当于增加了一个 CNAME 记录，视情况可能会导致负载不均衡。
2. 自定义 Service + Endpoints
   1. 这种方式能使用上 kube-proxy 提供的 L4 层负载均衡功能，对于纯 IP 且无额外 DNS 记录的服务，是一个很好的选择。

自定义 Service + Endpoints 这个功能，官方给了一个示例：[Kubernetes - Services without selectors](https://kubernetes.io/docs/concepts/services-networking/service/#services-without-selectors)，摘抄如下：

```yaml
---
apiVersion: v1
kind: Service
metadata:
  name: my-service
  namespace: xxx
spec:
  ports:
    - protocol: TCP
      port: 80
      targetPort: 9376
---
apiVersion: v1
kind: Endpoints
metadata:
  # 这里的 name 跟 Service 的 name 必须一致！
  name: my-service
  namespace: xxx
subsets:
  - addresses:
      - ip: 192.0.2.42
    ports:
      - port: 9376
```

这样就能实现使用 kube-proxy 为外部服务启动 L4 负载均衡功能。
