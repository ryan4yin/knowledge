# Elastic Load Balancing

AWS ELB 提供了请求的负载均衡服务，我们目前用到的主要有如下几种：

- Application Load Balancing: 基于 openresty 的七层负载均衡，支持 http 层的流量切分，推荐使用。
  - 和阿里云不一样，它只按流量计费，而且可以扩容，理论上可以无限并发，但是扩容慢。如果预判流量要升高，需要提前调 API 扩容。
- Network Load Balancing: 高性能的四层负载均衡，价格比 ALB 更贵。
  - 性能高，但是流量费太贵，一般游戏行业用的多。
- Classic Load Balancing: 旧版本的七层负载均衡（基于 Apache），已经不建议使用了


## 结合 Kubernetes 的应用

aws 为 Kubernetes 提供的 [AWS Load Balancer Controller](https://github.com/kubernetes-sigs/aws-load-balancer-controller)，支持两种 ELB:

- 七层代理 ALB：通过 ingress 定义，可以将 service 绑定到一个 7 层负载均衡
  - 也可以通过 TargetGroupBinding 绑定一个 TargetGroup，再将 TargetGroup 绑定到自行创建的 ALB 上
- 四层代理 NLB：AWS Load Balancer Controller 会自动为 LoadBalancer 类型的 K8s Service 创建并绑定一个 NLB


## ALB

ALB 的主要由两部分组成：

- ALB 自身
- TargetGroup: 每个组包含若干个 targets, 在 EKS 场景下，建议选用 `TargetType=ip`

### ALB TargetGroup 的参数说明

其中比较有用的参数之一，应该是 `slow_start`，该参数使用户能设定一个时间段如 30s.

当有新的 target 加入到 TargetGroup 时，ALB 会慢慢地将线上请求一点点切到该 target 上，起到一个 warm up 的作用。
此功能主要针对「推荐服务」等对本地缓存依赖比较重的程序，使其首先在较低 QPS 下完成缓存预热，实现平滑扩容。

## NLB

NLB 按标准的计算算法，是比 ALB 更便宜的，而且性能更高，还可以设置静态 IP，看起来是好处多多。

但是需要注意跨区流量问题，使用 `ip` 模式的 NLB targetgroup，否则可能会产生大量的跨区流量费。后面会详细介绍。

## 成本分析

### 跨区流量成本

#### 1. 只有 NLB 才会收取跨区流量成本

官方文档 [data transferred "in" to and "out" of Amazon EC2](https://aws.amazon.com/ec2/pricing/on-demand/#Data_Transfer) 中有这么一句话：

    Data transferred "in" to and "out" from Amazon Classic and Application Elastic Load Balancers using private IP addresses, between EC2 instances and the load balancer in the same AWS VPC is free.

这说明 CLB/ALB 是免跨区流量费的，而 NLB 虽然更便宜，但是不免除跨区流量费！

因此 NLB 需要注意使用 `ip` 模式的 NLB targetgroup，否则可能会产生大量的跨区流量费。后面会详细介绍。

另外还不清楚 NLB 自身的地址是否是区分 zone 的，否则下游的流量也可能会产生跨区流量费...

#### 2. ALB/CLB 也可能非直接地导致跨区流量成本

在 Kubernetes 集群中，如果使用 instance 模式的 ALB，或者使用了 CLB，那么 LB 其实会在所有 nodes 上进行负载均衡。

但是实际处理请求的 Pod 不一定在该 Node 上，这会导致 k8s 集群在 nodes 间进行不必要的流量转发，造成 ec2 之间跨区流量成本的上升！

### 跨域流量成本

如果 ELB 被跨域访问，那此 ELB 还将被收取跨域流量成本。

如果 ELB 类型为 `internet-facing`，那它还将被收取公网传输成本。

