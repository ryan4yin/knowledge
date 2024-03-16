# Pulsar

- [次时代Kafka与Pulsar该如何选择？](https://developer.aliyun.com/article/1220133)

开源领域中有诸多优秀开源消息队列，例如 RabbitMQ、Apache RocketMQ、Apache ActiveMQ 和 Apache Kafka。
在前人的基础上，Pulsar 实现了很多上一代消息系统或者上一代流数据系统没有实现的功能和特性，比如云原
生、多租户、存储与计算分离、分层存储这些特性。针对之前消息队列系统的痛点，Pulsar 做了很多针对化的解
决措施。

## 架构

Pulsar 的核心组建有如下三部分：

- Zookeeper: 负责存储元数据。
  - 目前 Pulsar 正在做改造降低对 zookeeper 的强依赖，但目前仍然推荐使用 zookeeper。
- Broker：也即 Pulsar 本身，它负责计算。
- BookKeeper：负责消息的持久化存储。

这三个部分可以分别单独部署。

### 1. BookKeeper

BookKeeper 是 Pulsar 的存储层，它是一个分布式的日志存储系统，其每一个节点被称作 Bookie.

BookKeeper 最简单的使用方法，是以 Daemonset 的方式部署在 Kubernetes 集群中，每新扩容一个节点，就会自
动在新节点上部署一个 Bookie。Bookie 会直接使用节点的本地磁盘存储数据，BookKeeper 负责将数据复制到多
个 Bookie 上，以保证数据的高可用性。

这样做的好处是不需要走 K8s 的存储卷机制，部署维护更简单，而且性能更好延迟更低（因为通常 K8s 的 PVC
本身也可能做了数据的复制容错）。

> 当然也会有缺点，使用 PVC 的情况下，直接替换掉一个旧节点，新节点可以很快挂载上同一个 PVC，不需要从
> 其他节点恢复数据。而使用本地磁盘的方式，新节点需要从其他节点恢复数据，这个过程可能会比较慢，也影响
> 集群性能。
