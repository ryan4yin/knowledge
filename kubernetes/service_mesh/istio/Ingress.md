# Istio IngressGateway

>https://istio.io/latest/docs/setup/additional-setup/gateway/

Istio IngressGateway 跟 APISIX-Ingress-Conroller 等类似，都是 EKS 集群的入口网关。
区别在于它跟服务网格的结合比较紧密。

但是根据我的使用体验看，原生的 Istio 网关的 access_log、metrics、direct_reponse、rate_limit 等功能还是有很多缺陷的，需要自己写很多的 EnvoyFilter 才能达成我们的需求：

- 负载均衡相关能力：负载均衡、流量切分、流量镜像、限流限并发
  - 其中 Istio 目前对限流限并发的支持不太行
- 请求与响应的 rewrite
  - Istio IngressGateway 提供了一定程度的支持，但是不太够
- 基于一些第三方机制的访问控制
  - Istio 对 JWT 提供一定支持
- 监控：按 Host/Path 等纬度划分的状态码、延时指标监控
  - Istio 支持此功能，但是默认不开 host/path 标签，直接打开还会导致指标数量暴增，需要自定义 EnvoyFilter
  - Istio 提供 Path 分类的能力，比如按前缀分类，但是都需要自己写 EnvoyFilter 实现
- 访问日志：统一收集好访问日志后，可使用 SQL 对全局流量的 Host/Path/Headers/Params 等进行深度分析
  - Istio 支持，也可以通过 EnvoyFilter/Telemetry API 自定义访问日志格式
  - 不过将日志直接上传到 S3/Kafka 的功能，就需要自己写插件或者加 Sidecar 来实现了
- direct_reponse 只能通过 envoyfilter 搞
  - 这个已经有对应的 PR 了：https://github.com/istio/istio/pull/39776
- API 生命周期管理
  - Istio 没这功能，不过好消息是绝大部分网关都没这功能

根据官方文档，我们最好将 ingressGateway 部署在独立的名字空间：

```shell
kubectl create ns istio-ingress
kubectl apply -f common-ingressgateway.yaml
```

然后直接创建 Gateway 对象，通过 label 选择 ingressgateway 即可，示例：

```yaml
apiVersion: networking.istio.io/v1beta1
kind: Gateway
metadata:
  name: common-gateway
  namespace: prod
spec:
  selector:
    app: commmon-ingressgateway
  servers:
  - port:
      number: 8080
      name: http
      protocol: HTTP
    hosts:
    - '*.k8s.local'
```

之后就能通过 virtaulservice/destinationrule 等，来使用这个 ingressgateway 了，示例：

```yaml
apiVersion: networking.istio.io/v1alpha3
kind: VirtualService
metadata:
  name: product
spec:
  hosts:
  - product.k8s.local
  gateways:
  - common-gateway
  http:
  - route:
    - destination:
        host: product
        port:
          number: 8080
---
apiVersion: v1
kind: Service
metadata:
  labels:
    app: product
  name: product
  namespace: prod
spec:
  ports:
  - name: grpc
    port: 9090
    protocol: TCP
    targetPort: 9090
  - name: http
    port: 8080
    protocol: TCP
    targetPort: 8080
  selector:
    app: product
  sessionAffinity: None
  type: ClusterIP
---
apiVersion: networking.istio.io/v1alpha3
kind: DestinationRule
metadata:
  name: product
spec:
  host: product
  # 定义了两个 subset
  subsets:
  - labels:
      version: v1
    name: v1
  - labels:
      version: v2
    name: v2
```
