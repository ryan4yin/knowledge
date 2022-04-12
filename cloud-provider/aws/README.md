# Amazon Web Services - AWS

AWS 是目前全球最大的云服务提供商，也是云计算领域的先驱及引领者。
但是其地位正在受到其他云服务商的挑战，其中势头最猛的是微软家的 Azure.

Github 上最流行的 AWS 实践手册：

- [Amazon Web Services — a practical guide](https://github.com/open-guides/og-aws)


## 杂项服务

比较重要的服务都单独列文档了，这里就简单介绍下一些不重要的杂项服务

- Route53 DNS 服务: 顾名思义，管理 DNS 解析的
- SNS: 可以制定消息订阅条件，只接收特定内容的消息


## 其他杂项内容

### 解耦合架构


使用消息队列解耦合 APP 与 Web 端，功能就类似水库，削峰填谷。

消息队列的知识：
- 死信队列，多次处理未果
- 消息可能重复，MQTT 也有这样的问题。
  - 使用可见性超时，在用户 1 读取到消息 A 时，暂时把该消息 A 锁定。
- watch


发布订阅服务：功能为扇出，即一次发布，多人订阅。


