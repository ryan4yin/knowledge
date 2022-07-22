# Elastic Load Balancing

AWS ELB 提供了请求的负载均衡服务，我们目前用到的主要有如下几种：

- Application Load Balancing: 基于 openresty 的七层负载均衡，支持 http 层的流量切分，推荐使用。
  - 和阿里云不一样，它只按流量计费，而且可以扩容，理论上可以无限并发，但是扩容慢。如果预判流量要升高，需要提前调 API 扩容。
- Network Load Balancing: 高性能的四层负载均衡，价格比 ALB 更低。
  - 性能高，但是流量费太贵，一般游戏行业用的多。
- Classic Load Balancing: 旧版本的七层负载均衡（基于 Apache），已经不建议使用了


## 一、ALB 功能与使用方法

>https://docs.aws.amazon.com/zh_cn/elasticloadbalancing/latest/application/introduction.html

ALB 是七层负载均衡，主要由两部分组成：

- ALB 实例及监听规则
- ALB TargetGroup: 每个组包含若干个 targets, 在 EKS 场景下，建议选用 `TargetType=ip`

ALB 支持一个七层负载均衡应有的绝大多数功能：TLS、基于 HTTP 的 Path/Host 的路由策略，流量切分，X-Forwarded 属性转发，等等。

ALB 可以与 AWS Web Application Firewall (WAF) 集成，WAF 提供各种限流限并发的规则，帮助保护 Web 程序免受攻击。

ALB 域名解析出的 IP 地址是不固定的，可能会随负载变化与后台维护而变化。

### ALB TargetGroup 的参数说明

其中比较有用的参数之一，应该是 `slow_start`，该参数使用户能设定一个时间段如 30s.

当有新的 target 加入到 TargetGroup 时，ALB 会慢慢地将线上请求一点点切到该 target 上，起到一个 warm up 的作用。
此功能主要针对「推荐服务」等对本地缓存依赖比较重的程序，使其首先在较低 QPS 下完成缓存预热，实现平滑扩容。

### ALB 取消注册 targets

ALB 取消注册（Deregistering）一个 target，ALB 会立即停止向该 targets 转发请求。
在未处理完的请求结束前，该 target 会处于 `draining` 状态，所有请求处理完毕后它会被直接从 targetgroup 中移除。

## 二、NLB 功能与使用方法

>https://docs.aws.amazon.com/zh_cn/elasticloadbalancing/latest/network/introduction.html

NLB 是四层负载均衡，主要由两部分组成：

- NLB 实例及监听规则
- NLB TargetGroup: 每个组包含若干个 targets, 在 EKS 场景下，建议选用 `TargetType=ip`

它的优势：

- 极高的性能与动态拓展速度、超低延迟
  - ALB 的拓展速度可能不够块，不适合流量剧烈波动的场景。在 ALB 之间切量时也要考虑到这点，提工单让 AWS 提前扩容 ALB
- 每个 NLB 在每个可用区中提供单个静态 IP 地址
- 客户端的流量到达 NLB 在某个可用区提供的静态 IP 后，NLB 会向相同可用区内的后端实例分发流量。
  - 也即默认情况下仅在同可用区内进行负载均衡。性能更好。
  - 如果手动启用了跨区流量负载均衡，性能会更差，而且还会收跨区流量费！
- 利用 Route53 的健康检查，NLB 支持在一个区域内及跨区域和本地站点实现故障切换。

其他 FAQ：

- TCP 连接的 NLB 空闲超时为 350 秒。UDP 流的空闲超时为 120 秒。
- 每个可用区目前最多支持 200 个 Targets

从 ALB 切换到 NLB 可能会遇到的问题：

- ALB 上可以直接绑定安全组，而 NLB 不提供此功能！
  - NLB 设置了源 IP 透传后，基于源 IP 的安全组，就得加在后端的所有实例上了！
- ALB 会在 L7 上启用 TCP 连接复用，而 NLB 是 L4 负载均衡不存在此功能，因此从 ALB 切换到 NLB 后，后端实例的 TCP 连接数很可能会上升。
- ALB 会通过 HTTP 的 `X-Forwarded-For` `X-Forwarded-Proto` Headers 将 IP/协议透传到后端实例，而 NLB 仅工作在 L4 层，使用这些 headers 的逻辑将会失效。
  - 对于客户端 IP，NLB 可以设置直接在 L3 层透传该源 IP
  - 对于 HTTP/HTTPS 协议的判断。最好的处理办法是 TLS/TCP 分别使用不同的 targetgroup，转发到后端实例的不同端口，通过端口来区分前端协议。

其他问题参见官方文档 [排查您的 Network Load Balancer 问题](https://docs.aws.amazon.com/zh_cn/elasticloadbalancing/latest/network/load-balancer-troubleshooting.html)

### Health Check

NLB 有两种健康检查功能：

- 主动健康检查：这个是用户可以配置的健康检查功能，NLB 基于用户提供的参数进行主动健康检查。
- 被动健康检查：用户无法控制此行为，NLB 通过监控流量的情况，来判断 targets 是否存在异常，并决定是否要把它设置为 unhealthy.

如果 targets 进入 unhealthy 状态，NLB 不会再将流量转发给它，对于已存在的连接，NLB 会向客户端发送 TCP RST 数据包。

而如果所有 targets 都不处于 healthy 状态，NLB 进入 fail open 状态，此状态下 NLB 将所有流量随机的转发给所有的 targets，而不管它们的状态如何。

### 跨区负载均衡

NLB 在 DNS 解析中，为每个 Zone 提供一个 IP 地址，如果某可用区的 targets 全部被取消注册， NLB 会从 DNS 中删除对应的 IP 地址。但是我们都知道 DNS 是有 TTL 的，所以这可能会造成部分请求失败。

所以最好的办法是：一定要确保使用到的每个 Zone，都始终有足够的 Targets 可用！

### NLB 取消注册 targets

NLB 取消注册（Deregistering）target 的逻辑跟 ALB 不太一样。
在一个 targets 被取消注册后，它会进入 `draining` 状态，在此状态的停留时间由 `deregistration_delay` 参数设定，默认为 300s。
在 `draining` 状态中，NLB 不会向 targets 建立新的连接，但是仍然会保持已有的连接。（这是因为 NLB 只清楚 L4 层的信息，它无法判定在什么时间点中断连接不会造成问题）。

**而最坑的一点是，如果被取消注册的 targets 仍然维持在 healthy 状态，并且已存在的连接持续被使用，未进入 idle 状态，NLB 就会持续将流量转发到这个 targets 上**！
**这导致如果被取消注册的 target 已经终止了，在 health_check 将它的状态变更为 unhealthy 之前的这段时间，请求仍然有机会被转发到这个已经终止的 target，导致请求无响应而超时**！

官方对这个问题给出的建议是：

- 启用 targetgroup 的 `connection termination` 功能
  - 此功能将在超过 `deregistration_delay` 时间后，强制关闭所有 LB 与 targets 之间的连接
- 确保在取消注册 target 前，它已经进入了 unhealthy 状态

其他资料：

- 官方文档：[Deregistration delay - AWS NLB](https://docs.aws.amazon.com/elasticloadbalancing/latest/network/load-balancer-target-groups.html#deregistration-delay)
- 相关 issue: 
  - <https://github.com/kubernetes-sigs/aws-load-balancer-controller/issues/2131>
  - <https://github.com/kubernetes-sigs/aws-load-balancer-controller/issues/2366>

根据上述资料，NLB target 被取消注册后，大概需要 60s-180s 的时间进行 drain 操作，这之前都持续会有请求被转发到该 targets！
因此对 k8s 而言，建议在 pod 上设置 180s - 240s 的 preStop 以及对应的 terminationGracePeriodSeconds，确保所有请求都能被正常处理！

## 三、结合 Kubernetes 的应用

aws 为 Kubernetes 提供的 [AWS Load Balancer Controller](https://github.com/kubernetes-sigs/aws-load-balancer-controller)，支持两种 ELB:

- 七层代理 ALB：通过 ingress 定义，可以将 service 绑定到一个 7 层负载均衡
  - 也可以通过 TargetGroupBinding 绑定一个 TargetGroup，再将 TargetGroup 绑定到自行创建的 ALB 上
- 四层代理 NLB：AWS Load Balancer Controller 会自动为 LoadBalancer 类型的 K8s Service 创建并绑定一个 NLB

## 四、成本分析

>https://aws.amazon.com/cn/elasticloadbalancing/pricing/

### 1. ALB 定价

ALB 按实例费用以及 LCU 计费，每个 ALB 实例的固定费用为 $0.54/day，几乎可忽略不计。

而 LCU 实际是一个综合收费项，单价为 **$0.008/hour**，每个 LCU 包括：

- **新连接数**：每秒 **25** 个新连接。
- **活跃连接数**：每分钟 **3000** 个活跃连接。
- **已处理字节数**：ALB 处理的请求/响应的总字节数。EC2 实例、ECS 容器和 IP 地址作为目标时为每小时 **1 GB**，Lambda 函数作为目标时为每小时 **0.4 GB**。
- **规则评估数**：`规则评估数 = 请求速率 * (处理的规则数量 – 10 个免费规则)`，每秒 **1000** 个规则评估。
- ALB 貌似不区分 HTTP/HTTPS 数据，价格都是一致的。

可以通过 CloudWatch 查看上述所有三个指标的使用情况，**AWS 按上述三个指标分别计算 LCU 数量，并使用最高的值来计费**。不足一个 LCU 的按一个 LCU 计费，不足一小时的也按一小时计费。

>**注意事项**：四个 LCU 指标的统计时间跨度并不一致！
CloudWatch 默认显示的 LCU 是 `1 Min` 统计的，并不准。
要看到实际 LCU 的成本，需要把统计时长改成 `1 Hour`！

自行验证 LCU 数量，首先打开 ALB 监控页（默认的统计间隔为 1mins）：

- 将 `Active Connection Count` 显示的数值除个 3000，就得到此指标对应的 LCU
  - 假设值为 `1,500,000`，则对应的 LCU 数量为 500
- 将 `New Connection Count` 显示的数值除个 60 得到每秒新建连接数，再除个 25 得到对应的 LCU
  - 假设值为 `2,500,000`，则对应的 LCU 为 1667
- 将 `Processed Bytes` 的指标求和间隔改为 `1 Hour`，将显示的数值除个 1024 的 3 次方，得到每小时处理的 GB 数据量，即 LCU
  - 假设值为 `400,000,000,000`，则对应的 LCU 为 372
- 取三个值中最大的那个，得到 LCU 值为 1667
- 将 `Consumed Load Balancer Capacity Units` 的指标求和间隔改为 `1 Hour`，应该能看到该时间点的 LCU 跟我们算出的 1667 很接近。
- 每天的费用为 $0.008/hour * 24h * 1667 = $320/d
- 考虑到 toC 业务的流量波动，按峰值计算的成本可能得 * 0.7 才是比较正确的最终费用，得到 $224/d


### 2. NLB 定价

NLB 同样按实例费用以及 NLCU 计费，每个 NLB 实例的固定费用也是 $0.54/day，几乎可忽略不计。

而 NLCU 实际是一个综合收费项，单价为 **$0.006/day**，每个 NLCU 都使用如下三个指标衡量：

- 新连接或流数：每秒新建 TCP 连接/ UDP 流的数量。许多技术（HTTP、WebSockets 等）会重用传输控制协议 (TCP) 连接以提升效率。新连接数通常会少于请求数或消息数。
- 活跃连接或流数：并行 TCP 连接/ UDP 流的峰值，每分钟取样。
- 已处理的字节数：负载均衡器处理的字节数（以 GB 为单位）。

可以通过 CloudWatch 查看上述所有三个指标的使用情况，**按上述三个指标分别计算 NLCU 数量，并使用最高的值来计费**。不足一个 NLCU 的按一个 NLCU 计费，不足一小时的也按一小时计费。

对于 TCP 流量，一个 NLCU 包含：
- 每秒 800 个新 TCP 连接。
- 100000 个活跃 TCP 连接（每分钟取样）。
- 对于 EC2 实例、ECS 容器、IP 地址和 ALB 作为目标，每小时 1GB。

对于 UDP 流量，一个 NLCU 包含：
- 每秒 400 个新 UDP 流。
- 50000 个活跃 UDP 流（每分钟取样）。
- 对于EC2 实例、ECS 容器、IP 地址和 ALB 作为目标，每小时 1GB。

对于 TLS 流量，一个 NLCU 包含：
- 每秒 50 个新 TLS 连接或流。
- 3000 个活跃 TLS 连接或流（每分钟取样）。
- 对于 EC2 实例、ECS 容器、IP 地址和 ALB 作为目标，每小时 1GB。

TCP 和 UDP 流量是指去往网络负载均衡器上的所有 TCP/UDP 侦听器的流量，而 TLS 流量则是指去往网络负载均衡器上的所有 TLS 侦听器的流量。

>**注意事项**：四个 LCU 指标的统计时间跨度并不一致！
CloudWatch 默认显示的 LCU 是 `1 Min` 统计的，并不准。
要看到实际 LCU 的成本，需要把统计时长改成 `1 Hour`！

单纯从成本方面考虑，能看到 ALB 跟 NLB 的 LCU 收费单位区别如下：

- NLB 的单价要低 25%
- 对 HTTP 协议而言，NLB 的每个 NLCU 支持的连接数要比 ALB 高了大概 32 倍。
- 数据量的衡量指标是一致的
- 只有 NLB 才支持非 HTTP 协议
- 如果要在 NLB 上处理 TLS 协议，三个衡量指标跟 ALB 的区别就差别不大了。

总的看，如果你的内部链路还有其他负载均衡器（比如 Istio IngressGateway / K8s Ingress Controller），
在外部使用 NLB 要比 ALB **至少低 25% 的 LCU 费用**，但是如果考虑到跨区流量成本，那就不一定了。

实际使用发现，在单可用区场景下（即无跨区流量费），NLB 的费用要比 ALB 低 60%。

自行验证 LCU 数量，首先打开 ALB 监控页（默认的统计间隔为 1mins）：

- TCP
  - 将 `New flow count` 的数值除 60 得到每秒流数，再除个 800 得到对应的 NLCU 值
    - 假设值为 `2,000,000`，则 NLCU 为 42
  - 将 `Active flow count` 的数值除个 100000，得到对应的 NLCU 值
    - 假设值为 `10,000,000`，则 NLCU 为 100
  - 将 `Processed Bytes` 的指标求和间隔改为 `1 Hour`，将显示的数值除个 1024 的 3 次方，得到每小时处理的 GB 数据量，即 LCU
    - 假设值为 `500,000,000,000`，则对应的 LCU 为 466
- TLS
  - 将 `New flow count TLS` 的数值除个 60s 再除个 50 得到 NLCU 值
    - 假设值为 `2,000,000`，则 NLCU 为 666
  - 将 `Active flow count TLS` 的数值除个 3000，得到对应的 NLCU 值
    - 假设值为 `8,000,000`，则 NLCU 为 2667
  - 将 `Processed Bytes` 的指标求和间隔改为 `1 Hour`，将显示的数值除个 1024 的 3 次方，得到每小时处理的 GB 数据量，即 LCU
    - 假设值为 `500,000,000,000`，则对应的 LCU 为 466
- 将 TCP 跟 TLS 的最高 NLCU 相加，得到 466 + 2667 = 3133
- - 将 `Consumed Load Balancer Capacity Units` 的指标求和间隔改为 `1 Hour`，应该能看到该时间点的 LCU 跟我们算出的 3133 很接近。
- 每天的费用为 $0.006/hour * 24h * 3133 = $451/d
- 考虑到 toC 业务的流量波动，按峰值计算的成本可能得 * 0.7 才是比较正确的最终费用，得到 $315/d

可以看到，这样的计算下，TLS 的活跃连接数会导致 LCU 剧烈增长，TLS NLCU 的 3000 个活跃连接，是 TCP 100000 的接近三十四分之一！
貌似将 TLS 加密放在自己的 L7 负载均衡上做，可以省很多的钱？？仅猜测，还不是很确定。

### 跨区流量成本

#### 1. 只有 NLB 启用「跨区负载均衡」后才会收取跨区流量成本

官方文档 [data transferred "in" to and "out" of Amazon EC2](https://aws.amazon.com/ec2/pricing/on-demand/#Data_Transfer) 中有这么一句话：

    Data transferred "in" to and "out" from Amazon Classic and Application Elastic Load Balancers using private IP addresses, between EC2 instances and the load balancer in the same AWS VPC is free.

这说明 CLB/ALB 是免跨区流量费的。

而 ELB 的 [FAQ](https://aws.amazon.com/cn/elasticloadbalancing/faqs/)  中提到，当 NLB 中启用「跨区域负载均衡」时，将对可用区之间的区域数据传输进行计费。

「[跨区域负载均衡](https://docs.aws.amazon.com/zh_cn/elasticloadbalancing/latest/userguide/how-elastic-load-balancing-works.html#cross-zone-load-balancing)」是一个在所有可用区上进行负载均衡的功能，在未启用它时（默认情况），ALB/NLB 将只会在每个可用区内进行负载均衡。
比如说你有三个可用区 A B C 的实例数分别为 10 20 30，那 ALB/NLB 会尽量保证每个可用区处理 1/3 的流量，这实际上会导致可用区之间的流量不均。
而启用了「跨区域负载均衡」后，流量就均衡了。

所以总的来说如果使用 NLB，就尽量不要开启「跨可用区负载均衡」，跨区流量费可能会变得难以承受。

而对于 Application Load Balancer，跨区域负载均衡始终处于启用状态，而且这个功能是完全免费的。

#### 2. ALB/CLB 也可能非直接地导致跨区流量成本

在 Kubernetes 集群中，如果使用 instance 模式的 ALB，或者使用了 CLB，那么 LB 其实会在所有 nodes 上进行负载均衡。

但是实际处理请求的 Pod 不一定在该 Node 上，这会导致 k8s 集群在 nodes 间进行不必要的流量转发，造成 ec2 之间跨区流量成本的上升！

因此对于任何用于 K8s 的 ALB/NLB，都建议使用 ip 模式进行负载均衡。

### 跨域流量成本

如果 ELB 被跨域访问，那此 ELB 还将被收取跨域流量成本。

如果 ELB 类型为 `internet-facing`，那它还将被收取公网传输成本。


## 五、Gateway Load Balancer

>https://aws.amazon.com/cn/blogs/networking-and-content-delivery/category/networking-content-delivery/elastic-load-balancing/gateway-load-balancer/

Gateway Load Balancer 是一个 L3 + L4 负载均衡。

GWLB 的结构如下：

- GWLB 的前端仅提供 L3 的 Endpoint，叫做 GWLBe，这个 GWLBe 可被配置为路由的下一跳。
  - 类似路由器的 IP，可以被配置在路由表中
- GWLB 在 TargetGroup 中的实例上进行负载均衡，但是要求后端必须支持 GENEVE 隧道协议！在所有实例的 GENEVE 6081/UDP 端口上进行负载均衡。
  - 后端实例可以使用 TCP/HTTP 等协议进行健康检查。

>[GENEVE](https://thiscute.world/posts/linux-virtual-network-interfaces/#vxlan-geneve) 是新一代 overlay 网络协议，可取代 2014 年标准化的 vxlan 协议。目前 cilium 容器网络就支持通过 geneve 创建 overlay 容器集群网络。

我理解它的主要用途：

- 在一个 Security VPC 中对流量进行安全合规检测，比如说只允许合规的流量出网。
- 深度流量检测，可用于防火墙、DDoS 防护等功能

主要是提供给第三方的防火墙、DDoS、深度流量检测等服务提供商，它们可以通过 GWLBe 与 GWLB，为其他 AWS 云用户提供相关云服务。
