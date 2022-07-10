# Istio IngressGateway

>https://istio.io/latest/docs/setup/additional-setup/gateway/

Istio IngressGateway 跟官方的 nginx-ingressgateway、APISIX-Ingress-Conroller 等类似，都是 EKS 集群的入口网关。

区别在于它跟服务网格的结合比较紧密。但是根据我的使用体验看，直接将它当作核心网关用，存在诸多问题。
相比 APISIX 等网关，它仍然缺失一些我们比较重要的功能，详见 [/kubernetes/ingress-egress](/kubernetes/ingress-egress/README.md)。

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

之后就能通过 virtaulservice/destinationrule 等，来使用这个 ingressgateway 了。
