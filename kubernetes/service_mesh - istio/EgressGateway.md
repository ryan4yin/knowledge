# EgressGateway

Istio 有 IngressGateway 作为集中式的流量入口，方便统一管理入网流量。
而 EgressGateway 自然就是统一管理出网流量。

通过设置 EgressGateway，Istio 的所有出网流量，都将通过 EgressGateway 的 Pod 出网。好处有：

1. 可以要求所有的出网流量都通过某个专用节点出去，只有这个节点可以访问外部网络，并且受到严密监控。
2. 可以限制只允许访问某些需要的域名，禁止所有其他的域名。


## 一、部署 EgressGateway

在通过 istioctl 部署 istio 时，设置 egressgateway 相关的参数：

1. `spec.meshConfig.outboundTrafficPolicy.mode`: 安全起见，这个应该改为 `REGISTRY_ONLY`
1. `spec.components.egressGateways`: 这里设置 egress 部署相关的参数。
2. `spec.values.gateways.istio-egressgateway`: 要在这里打开 egressgateway 的 autoscalar.

可以参见我的自定义配置 [./istio-operator-values.yaml](./istio-operator-values.yaml)

### 只允许通过 Egress Gateway 访问外部网络

部署完成后，还有个问题：Istio 只能管控经过 sidecar 的流量。如果未注入 sidecar，那 Pod 的流量就不受 istio 管控了！
为此需要设置 Kubernetes 的网络策略（NetworkPolicy），禁止掉所有不是源自 EgressGateway 的出集群流量。

具体的配置内容待续。。

## 二、使用 EgressGateway

按前面的方法部署好带 EgressGateway 的 Istio 后，集群内带 Sidecar 的容器应该就无法访问外部网络了。

我们设了只允许已注册的 host 出网（outboundTrafficPolicy），但是现在没有任何已注册的 host，所以无法访问外部网络。

以知乎 `zhihu.com` 为例，使用 curl/wget 进行测试，流程如下：

1. 首先确认 Pod 中无法访问知乎。
1. 将知乎 `zhihu.com` 注册为外部 host
2. 确认现在可以在 Pod 中访问知乎了。


