# Elastic Load Balancing

AWS ELB 提供了请求的负载均衡服务，我们目前用到的主要有如下几种：

- Application Load Balancing: 基于 openresty 的七层负载均衡
- Network Load Balancing: 高性能的四层负载均衡
- Classic Load Balancing: 旧版本的七层负载均衡（基于 Apache），已经不建议使用了


## 结合 EKS 的应用

aws 为 EKS 提供的 AWS Load Balancer Controller 控制器，支持两种 ELB:

- 七层代理：通过 ingress 定义，可以将 service 绑定到一个 7 层负载均衡
  - 也可以通过 TargetGroupBinding 绑定一个 TargetGroup，再将 TargetGroup 绑定到自行创建的 ALB 上
- 四层代理：AWS Load Balancer Controller 会自动为 LoadBalancer 类型的 K8s Service 创建并绑定一个 NLB


## NLB 的坑

NLB 按标准的计算算法，是比 ALB 更便宜的，而且性能更高，还可以设置静态 IP，看起来是好处多多。

但是它有一个坑（待确认）：**NLB 所有的流量全部是跨 AZ 的，这会导致大量的跨区流量费用。**

这个问题导致在很多场景下，它没啥性价比。

