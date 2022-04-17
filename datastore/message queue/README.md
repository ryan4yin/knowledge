# 消息队列

消息队列是分布式系统常用的中间件之一。流行的开源消息队列有很多——kafka/rabbitmq/redis/activemq 等等，它们都各有优劣。

此外，还有专用于物联网(Iot)/实时通讯(IM)的 mqtt 协议相关实现(emqx/emmiter)，它也是一种消息队列。

以及 ZeroMQ——一个消息通讯库，它直接连接客户端和服务端，不需要中间件（Message Broker 代理），因此吞吐量和延时都很低。但是不支持持久化，也不保证消息的送达。

## 主要指标：吞吐量、延时、可靠性、持久化

不同的使用场景对各项指标的要求也不尽相同，也就适合使用不同的消息队列。

比如有的时候，我们追求吞吐量，为此可以接受一部分的消息丢失。
而有的场景下，我们追求的是消息完整送达，对吞吐量和延时的要求则不高。

## 各 MQ 对比

待续

1. Kafka
2. rabbitmq
3. pulsar: 读写分离，不依赖 zookeeper（自己实现了 raft 共识算法），兼容 kafka 协议

## 参考

- [新手也能看懂，消息队列其实很简单 - 知乎](https://zhuanlan.zhihu.com/p/52773169)
- [Dissecting Message Queues(剖析消息队列)](https://bravenewgeek.com/dissecting-message-queues/)

