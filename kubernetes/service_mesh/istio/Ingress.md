# Istio IngressGateway

>https://istio.io/latest/docs/setup/additional-setup/gateway/

Gateways 的使用方法，视各公司环境的不同而不同。

以我司为例，我们为了方便区分各业务的成本、同时隔离业务场景，避免互相干扰。我们为每个产品线都单独创建了一个 IngressGateway.

同时我们的 HTTPS 证书都添加在了外层的 AWS ALB 上，并由 AWS 负责自动更新。
因此我们的 Istio 是使用的纯 HTTP/WebSocket，集群内都不需要考虑 HTTPS 的问题。

这种场景下，我们当然希望能够更动态地添加、删除、更新 IngressGateways.

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
  name: my-gateway
  namespace: prod
spec:
  selector:
    app: commmon-ingressgateway
  servers:
  - port:
      number: 80
      name: http
      protocol: HTTP
    hosts:
    - uk.bookinfo.com
    - eu.bookinfo.com
```

之后就能通过 virtaulservice/destinationrule 等，来使用这个 ingressgateway 了。