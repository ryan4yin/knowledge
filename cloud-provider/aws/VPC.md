# VPC 网络

1. 每个 VPC 可以添加一个唯一的 IGW，相当于一个公网路由器
1. NAT 网关：为私有子网提供访问公网的能力，需要收 NAT 费用


### 路由表

每个 VPC 里面都可以创建很多个路由表，每个路由表可以关联 VPC 中的多个 subnet，只有关联上 subnet，路由表中的规则才会生效。

但是每个 subnet 只能绑定一个路由表，也就是说 route table 和 subnet 是一对多的关系。

如果我们创建了一个路由表，里面添加了指向 IGW 的路由规则（dst=0.0.0.0/0, target=IGW），那它就是一个**公网路由表**。

如果路由表没有添加和公网相关的东西，那就是它就是一个**私网路由表**。


### 子网 - Subnet

首先，一开始创建的所有 subnet 都是私网的，无法访问外网的。

1. **公有子网**：如果子网绑定的路由表的默认路由规则是到 IGW ，那它就是一个**公有子网**，服务器就能直连外网，外网也能直接通过服务器的公网 IP 访问你。
2. 私有子网： 如果子网的默认路由规则不是到 IGW，那它就是一个私有子网，其中的设备无法直接被外部访问。
   2. 私有子网的默认路由规则 `0.0.0.0/0`，可以设置为到公有子网的 NAT 网关，这样就它就能通过 NAT 访问公网。
   1. 私有子网也可以启用自动分配公网 IP，但是因为和 IGW 之间没有路由，公网 IP 实际上是没用的。
4. 推荐 VPC 使用 16 位掩码，公网 subnet 设为 24 位，私有 subnet 通常服务更多，可以设为 23 位，比公网刚好大一倍。


### ENI 和 EIP

弹性 IP 和 ENI 弹性网卡，都可以做高可用：

- 弹性 IP: 收费，IP 固定（不用要收钱，但是在使用状态时，EC2 的费用已经包含了 IP 费用，所以反而不收 EIP 的费用），而且可以跨可用区使用
- ENI 弹性网卡：只要买了，不管用不用，都会一直收钱。IP/mac 地址都固定，但是不能跨可用区使用。


这里其实还有些疑问。

### 安全组 SG 和 ACL

#### 1. 安全组(VPC 级别的)

有记忆能力，被允许进入的流量，也是允许出去的。

使用方法：安全组是很灵活的，在创建 EC2 等资源时，可以按需绑定安全组，只有你绑定的 SG，它的规则才会生效。


安全组的建议设计方案，建议分成三类：
- web 层安全组，直接对外
- 应用程序安全组，仅 web 层可以访问它
- 数据库安全组，仅应用程序层可以访问它


#### 2. ACL 访问控制列表（subnet 级别的）

无记忆能力，说拒绝就一定会拒绝！

使用方法：ACL 是 subnet 全局一定会生效的，所有此 subnet 中的流量都必须遵守这个 ACL 规则。

ACL 和安全组的配合方式：建议外松内紧，就是 ACL 设松一点，里面的安全组设紧一点。


### 对等连接 Peer Connection

1. 在两个 VPC 之间创建对等连接
   1. 创建阶段分为 requester 和 accepter，表示你创建一个连接请求给 accepter，只要它同意，你们就能创建对等连接
   2. 实际创建完成后，这个连接是对等的，不是单向的！只有在创建阶段才有角色区分
2. 分别配置两个 VPC 的路由表，让它们的流量能正确互通。


### AWS Transit Gateway

中心化的 VPC 互联网关，形成一个星型网络，在 VPC 比较多的情况下，比「对等连接」要方便很多。

### AWS 网络拓展到私有云

1. 使用 VPN 连接私有云和 AWS VPC，走 Internet，最大 1.25G
2. 建立物理专线 AWS Direct Connect，带宽有 1G 到 10G，也可以聚合四条专线达到 40G 的速率。


### VPC endpoints

AWS 资源之间的访问，默认都是走外网的，从 VPC 内请求会走 NAT 网关，速度会更慢，而且还会收 NAT 费用与流量传输费用。

可以通过 VPC endpoints 让这些请求都直接走 VPC 内部，避免 NAT 费用与流量传输费用。

>作为对比我们看下阿里云，它所有资源都直接提供内网与公网两个 endpoints，使用内网 endpoints 请求就会走内网，不需要额外创建 VPC endpoints.

VPC endpoints 有两种类型：

- Interface endpoints
  - 一个绑定了一个私网 IP 的弹性网卡，它可将流量转发到 AWS 服务（如 S3）、AWS 用户或合作伙伴的服务
  - 有独立的域名，客户端必须使用这个独立域名来请求服务！比如 `vpce-1a2b3c4d-5e6f.s3.us-east-1.vpce.amazonaws.com`
  - 会收取数据处理费用，另外每个实例还会单独按小时计费
- [Gateway endpoints](https://docs.aws.amazon.com/vpc/latest/privatelink/gateway-endpoints.html)
  - 它是一个路由网关，可将流量经由内部网络转发到 S3 或者 DynamoDB，无需经过 IGW 或者 NAT.
  - 目前只支持 DynamoDB 与 S3 这两个服务
  - 目前免费
  - 配置方式：必须在 endpoints 页面上选择要绑定的 route_tables！（无法在 route_tables 页面绑定 gateway endpoints）

常见的比如 S3/DynamoDB/SQS/ECR 等等，都需要添加 VPC endpoints 才能走内网访问。

比如 System Manager（SSM, 贼难用），默认只能管理外网资源，要管理内网资源，得添加 VPC endpoints

应该为 DynamoDB/S3 配置 Gateway endpoint.

**存疑：如果不给 ECR 配 Interface Endpoints，是否会造成比较大的 NAT 成本**？

### VPC Flow Log 流日志




