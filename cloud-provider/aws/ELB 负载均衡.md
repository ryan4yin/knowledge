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

## 二、NLB 功能与使用方法

>https://docs.aws.amazon.com/zh_cn/elasticloadbalancing/latest/network/introduction.html

NLB 是四层负载均衡，主要由两部分组成：

- NLB 实例及监听规则
- NLB TargetGroup: 每个组包含若干个 targets, 在 EKS 场景下，建议选用 `TargetType=ip`

它的优势：

- 极高的性能与动态拓展速度、超低延迟
  - ALB 的拓展速度可能不够块，不适合流量剧烈波动的场景。在 ALB 之间切量时也要考虑到这点，提工单让 AWS 提前扩容 ALB
- 支持将静态 IP 地址用于负载均衡器。还可以针对为负载均衡器启用的每个子网分配一个弹性 IP 地址。
  - ALB 不具有这项工具

其他 FAQ：

- TCP 连接的 NLB 空闲超时为 350 秒。UDP 流的空闲超时为 120 秒。
- 每个可用区目前最多支持 200 个 Targets


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

可以通过 CloudWatch 查看上述所有三个指标的使用情况，**AWS 按上述三个指标分别计算 LCU 数量，并使用最高的值来计费**。不足一个 LCU 的按一个 LCU 计费，不足一小时的也按一小时计费。


LCU 收费规则与 QPS/延迟/连接数的大致关系如下：

TBD

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


单纯从成本方面考虑，能看到 ALB 跟 NLB 的 LCU 收费单位区别如下：

- NLB 的单价要低 25%
- 对 HTTP 协议而言，NLB 的每个 NLCU 支持的连接数要比 ALB 高了大概 32 倍。
- 数据量的衡量指标是一致的
- 只有 NLB 才支持非 HTTP 协议
- 如果要在 NLB 上处理 TLS 协议，三个衡量指标跟 ALB 的区别就差别不大了。

总的看，如果你的内部链路还有其他负载均衡器（比如 Istio IngressGateway / K8s Ingress Controller），
在外部使用 NLB 要比 ALB **至少低 25% 的 LCU 费用**，但是如果考虑到跨区流量成本，那就不一定了。

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

