# EgressGateway

Istio 有 IngressGateway 作为集中式的流量入口，方便统一管理入网流量。
而 EgressGateway 自然就是统一管理出网流量。

通过设置 EgressGateway，Istio 的所有出网流量，都将通过 EgressGateway 的 Pod 出网。好处有：

1. 可以要求所有的出网流量都通过某个专用节点出去，只有这个节点可以访问外部网络，并且受到严密监控。
2. 可以限制只允许访问某些需要的域名，禁止所有其他的域名。
3. 可以监控外外部域名的请求，统计 HTTP/HTTPS 请求的 2xx/4xx/5xx 数据，甚至对请求做某些修改。

我基本没用过这个功能，不过感觉它跟 Network Policy 有点类似？只是它可以在 L7 层生效。

## 一、部署 EgressGateway

在通过 istioctl 部署 istio 时，设置 egressgateway 相关的参数：

1. `spec.meshConfig.outboundTrafficPolicy.mode`: 安全起见，这个应该改为 `REGISTRY_ONLY`
   1. `REGISTRY_ONLY`: 只允许访问已注册的外部服务(external services)，即外部域名
2. `spec.components.egressGateways`: 这里设置 egress 部署相关的参数。
3. `spec.values.gateways.istio-egressgateway`: 要在这里打开 egressgateway 的 autoscalar.

可以参见我的自定义配置 [./istio-operator-values.yaml](./istio-operator-values.yaml)

### 只允许通过 Egress Gateway 访问外部网络

部署完成后，还有个问题：Istio 只能管控经过 sidecar 的流量。如果未注入 sidecar，那 Pod 的流量就不受 istio 管控了！
为此需要设置 Kubernetes 的网络策略（NetworkPolicy），禁止掉所有不是源自 EgressGateway 的出集群流量。

具体的配置内容待续。。

## 二、使用外部服务限制 Pod 访问外部网络

>注意：**这种方法不依赖 EgressGateway 流量出口，流量是直接从 Istio-Proxy 出去的！**

按前面的方法部署好带 EgressGateway 的 Istio 后，集群内带 Sidecar 的容器应该就只能访问已注册的外部服务了。
但是现在没有任何已注册的外部服务，所以应该无法访问任何外部域名。

以知乎 `zhihu.com` 为例，使用 curl/wget 进行测试，流程如下：

1. 首先确认 Pod 中无法访问知乎。
2. 将知乎 `zhihu.com` 注册为外部服务。
3. 确认现在可以在 Pod 中访问知乎了。

使用 ServiceEntry 在 Istio 中将知乎注册外部服务：

```yaml
apiVersion: networking.istio.io/v1alpha3
kind: ServiceEntry
metadata:
  name: zhihu-ext
spec:
  hosts:
  - zhihu.com
  - www.zhihu.com
  ports:
  - number: 80
    name: http
    protocol: HTTP
  - number: 443
    name: https
    protocol: HTTPS
  resolution: DNS  # 要求源 ip 必须包含在 DNS 记录中，避免中间人攻击。 
  location: MESH_EXTERNAL
```

也可以将泛域名注册为外部服务，但是这种方式只支持 `resolution: None`，不够安全：

```yaml
apiVersion: networking.istio.io/v1alpha3
kind: ServiceEntry
metadata:
  name: zhihu-ext
spec:
  hosts:
  - "*.zhihu.com"
  ports:
  - number: 80
    name: http
    protocol: HTTP
  - number: 443
    name: https
    protocol: HTTPS
  resolution: None  # 只检查 Host 请求头，不检查源 IP 地址
  location: MESH_EXTERNAL
```

## 三、只允许外部流量从 EgressGateway 出网

要让流量从 EgressGateway 出网，除了上一步配置的 ServiceEntry 外，还需要：

1. Gateway: 匹配 EgressGateway Pod，hosts 为 `*.zhihu.com`
1. DestinationRule: 对 EgressGateway Pod 进行分类，暂且统一使用 `default-egress`
1. VirtualService: 具体的路由规则


```yaml
apiVersion: networking.istio.io/v1alpha3
kind: Gateway
metadata:
  name: egress-zhihu
spec:
  selector:
    istio: egressgateway
  servers:
  - port:
      number: 443
      name: tls
      protocol: TLS
    hosts:
    - "*.zhihu.com"
    tls:
      mode: PASSTHROUGH
---
apiVersion: networking.istio.io/v1alpha3
kind: DestinationRule
metadata:
  name: egress-default
spec:
  host: istio-egressgateway.istio-system.svc.cluster.local
  subsets:
  - name: default
---
apiVersion: networking.istio.io/v1alpha3
kind: VirtualService
metadata:
  name: direct-zhihu-through-egress-gateway
spec:
  hosts:
  - zhihu.com
  - www.zhihu.com
  gateways:
  - mesh
  - egress-zhihu
  tls:
  - match:  # Pod -> EgressGateway
    - gateways:
      - mesh
      port: 443
      sniHosts:
      - zhihu.com
    route:
    - destination:
        host: istio-egressgateway.istio-system.svc.cluster.local
        subset: default
        port:
          number: 443
  - match:  # egress-gateway -> ServiceEntry
    - gateways:
      - egress-zhihu
      port: 443
      sniHosts:
      - zhihu.com
    route:
    - destination:
        host: zhihu.com
        port:
          number: 443
      weight: 100
```

现在可以直接在 Pod 中请求知乎，观察 EgressGateway 的信息。
