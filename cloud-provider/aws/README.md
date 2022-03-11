# AWS

目前全球最大的云服务提供商，也是云服务的先驱。

Github 上最流行的 AWS 实践手册：

- [Amazon Web Services — a practical guide](https://github.com/open-guides/og-aws)

## EC2

cloudinit: https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/user-data.html#user-data-cloud-init

## 存储

我们最常用的，是 S3 对象存储。它价格便宜，而且使用灵活，支持在 s3 控制台直接查看数据内容、直接通过 CDN 提供给用户访问、配置生命周期策略等。
不常用的数据还可以归档或者转为长期存储，更省钱。

第二类是 EBS 块存储，常用在 EC2 及 EKS 上：

1. SSD - 特点是随机读写很快，绝大部分场景都应该选择使用 SSD.
   1. gp2 - 普通 SSD，快，是最常用的 EBS 类型。
   2. io1 - 更快，更贵
2. HDD - 机械硬盘，随机 IO 慢但是顺序 IO 快，适合用于存储大文件，如视频、大数据存储等。

EBS 的缺点是：

- 必须要挂载到实例上，才能看到里面的文件目录及内容。
- 存储价格差不多是 S3 标准存储的两倍。

第三类是 EFS 弹性文件系统，支持同时多人读写。EFS 性能不太行，价格也贵，是 EBS 的三倍以上。用得比较少。


## EC2 实例类型

1. 按需实例 - 临时测试用
2. 预留实例 - 固定的工作，使用预留实例
3. 竞价 Spot 实例，随时可能被终止 - 爬虫、map reduce 的 task 实例

在任一 ec2 实例中调用固定的 http api，就能获取到它自身相关的 user-data/meta-data 以及资源绑定的 Role 相关的 Ak/SK 信息，
这两个文件其实和 cloud-init 很类似，甚至就是用 cloud-init 实现的。

## Aurora 数据库

窟窿原理 - 三可用区，每个可用区两副本，同时写入 4 个实例，读取任意三个实例，保证性能和一致性。

比 MySQL 强，但是比 TiDB 差。

### RDS  serverless

AutoScaling 太慢，改一个不太大的表要几个小时，线上不要用，也就 staging 可以用用。

## DynamoDB - DDB

文档数据库，类似 MongoDB.

我们每个业务线都有在用 DynamoDB，它读写分离、支持事务、可横向扩展，而且不需要我们维护，给钱就行。

DDB 甚至可以替代部分 RDS
利用好 DDB 的索引可以做关系映射
有全局 / 本地 索引，官方提供 SQL 迁移到 DDB 的方案

所以我们基本上正在用 DynamoDB 替换我们的 MongoDB.


## VPC 网络

1. 每个 VPC 可以添加一个唯一的 IGW，相当于提供公网路由器
1. NAT 网关：和 IGW 的区别？


### 路由表

每个 VPC 里面都可以创建很多个路由表，每个路由表可以关联 VPC 中的多个 subnet，只有关联上 subnet，路由表中的规则才会生效。

但是每个 subnet 只能绑定一个路由表，也就是说 route table 和 subnet 是一对多的关系。

如果我们创建了一个路由表，里面添加了指向 IGW 的路由规则（dst=0.0.0.0/0, target=IGW），那它就是一个**公网路由表**。

如果路由表没有添加和公网相关的东西，那就是它就是一个**私网路由表**。


### 子网 - Subnet

首先，一开始创建的所有 subnet 都是私网的，无法访问外网的。

1. 子网是否可连接公网，是只能主动往外访问，还是也允许外部主动来连接我？这些都是由绑定的路由表决定的。
   1. 绑定的路由表有 IGW 路由规则，那你服务器就能直连外网，外网也能直接访问你。
2. 可以启用自动分配公网 IP，但是如果和 IGW 之间没有路由，那公网 IP 就是废的。
3. 只有公网 subnet 的实例，绑定一个弹性公网 IP 才有意义。
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

AWS 资源之间的访问，默认可以认为是走外网的，要计费。

要走内网，需要创建 VPC endpoints，有两种类型：

- Interface endpoints
- Gateway endpoints - 这东西以后要淘汰

它不像阿里云，所有资源默认都是不提供内网 endpoints 的，需要你额外创建 VPC endpoints 来实现走内网的功能。

比如 System Manager（SSM, 贼难用），默认只能管理外网资源，要管理内网资源，得添加 VPC endpoints


### ELB

ALB: 和阿里云不一样，它只按流量计费，而且可以扩容，理论上可以无限并发，但是扩容慢。如果预判流量要升高，需要提前调 API 扩容。

NLB: 性能高，但是流量费太贵，一般游戏行业用的多。


### Route53 DNS 服务


没啥好解释的？就 DNS 服务嘛。

## IAM 账号与权限管理

1. Policy 编写测试工具：有一个权限测试模拟器

Policy <- Role <- Person/Resources

Role 具有信任策略，表示谁可以使用这个 Role

Asume Role - STS 临时凭证

### OIDC 身份验证

OIDC 身份验证：客户端会先查看 jwt body 内容，从中获取到 provider URL，通过它来认证身份获取到 APIKey SecretKey，然后再用 AK SK 来调用 aws api


- boto3 就封装了这些行为，它们对用户都是透明的
- 适用场景：AWS EKS 的 IAM ServiceAccount

### InstanceProfile - 实例配置文件

AWS EC2 的 InstanceProfile 是一个 IAM Role 的容器，EC2 不能直接关联 IAM Role，必须使用 InstanceProfile 作为中介。

当用户直接在 EC2 控制台上创建一个关联了 IAM Role 的 EC2 时，实际上 AWS 会自动为该 IAM Role 创建一个同名的 InstanceProfile，然后将这个 IntanceProfile 关联到 EC2 上。

AWS EKS 的 NodeGroup 也是使用 InstanceProfile 来创建 EC2 实例的，它首先创建一个 InstanceProfile 并绑定上 EKS 集群的基础 Role，然后使用这个 InstanceProfile 来创建 EC2 实例，这样所有的 EC2 实例默认都具有连接上 EKS 集群的必要权限，才可以正常加入到集群中。
用户也可以自定义 EKS 集群的默认 InstanceProfile，使集群的 Pod 默认就具有某些 AWS 权限。

## 监控

### 成本监控

通过 Tag 来查看成本


### [CloudWatch](https://console.aws.amazon.com/cloudwatch/home) - 指标监控、事件监控与触发

cloudwatch 推送指标 + log 功能 - 像是 20 世纪初的设计，SRE 和 BE 都不太喜欢


### [Amazon EventBridge](https://console.aws.amazon.com/events/home)

可译为 Amazon 事件中继服务，能够监控 aws 上的各种事件，并触发某种操作：

- 调用某个 aws lambda 函数处理该事件
- 将事件丢到 SQS 里
- ...

比如用于监控「Spot 中断通知」及「EC2 再平衡建议」等事件。

### [CloudTrail](https://console.aws.amazon.com/cloudtrail/home) - 操作审计

监控账号中的所有 API 调用，不过只保留 90 天内的数据，不清楚这个能不能调。

比如查询 90 天内所有的 Spot 中断事件。


### [AWS Config](https://console.aws.amazon.com/config/home)

AWS Config 提供了账户中所有历史 AWS 资源配置的详细信息，包括资源之间的关联方式以及资源的历史配置。

简单点说，它就是一个 AWS 资源配置的历史版本管理系统，而且支持通过 SQL 查询数据。

利用 AWS Config，您可以：

- 检索一个或多个资源的历史配置
  - 如果做了误操作，可以通过 AWS Config 找回该资源正确的配置。
- 检索一个或多个资源的历史事件
  - 比如什么时候创建、什么时候启动、修改、终止或者删除。
- 在资源被创建、修改或删除时接收通知，审计这些操作是否符合规范，对有问题的进行某些操作，比如直接通知到对应责任人。
- 查看不同资源之间的关系。例如，您可能想要找到使用特定安全组的所有资源。

定价：主要成本是 ConfigurationRecord 的单价—— $0.003，对资源的 Tag 修改、配置变更、启动关闭，都会产生配置记录。

如果使用了按需创建、销毁的 OnDemand/Spot 实例，就会造成大量的 ConfigurationRecord 记录成本。

### VPC 流日志

待续

## Auto Scaling 实例数量的自动伸缩

1. 按计划（预测时间）进行伸缩
2. 动态拓展 - 按 CPU 等资源使用率进行伸缩

## 会话亲和性

缺点：可能造成流量负载不均衡，新扩容的实例全程围观
解决方法：使用中心化的、分布式的缓存，比如 Redis


## 解耦合架构


使用消息队列解耦合 APP 与 Web 端，功能就类似水库，削峰填谷。

消息队列的知识：
- 死信队列，多次处理未果
- 消息可能重复，MQTT 也有这样的问题。
  - 使用可见性超时，在用户 1 读取到消息 A 时，暂时把该消息 A 锁定。
- watch


发布订阅服务：功能为扇出，即一次发布，多人订阅。


### SNS

可以制定消息订阅条件，只接收特定内容的消息

================================================

kvm vs hvm
IGW vs NAT
