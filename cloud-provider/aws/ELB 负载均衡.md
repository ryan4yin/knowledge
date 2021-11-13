# Elastic Load Balancing

AWS ELB 提供了请求的负载均衡服务，我们目前用到的主要有如下几种：

- Application Load Balancing: 基于 openresty 的七层负载均衡，支持 http 层的流量切分，推荐使用。
- Network Load Balancing: 高性能的四层负载均衡，价格比 ALB 更贵。
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

但是需要注意跨区流量问题，使用 `ip` 模式的 NLB targetgroup，否则可能会产生大量的跨区流量费
