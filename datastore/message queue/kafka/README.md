# Kafka

常用命令：

```shell

# 列出所有 topic 
bin/kafka-topics.sh --list --zookeeper localhost:2181

# 描述某个 toppic
## 会给出 Topic 的 PartitionCount ReplicationFactor 以及其他 Configs 信息
./bin/kafka-topics.sh --describe --zookeeper localhost:2181 --topic topic_name

# 生产者发送消息
./bin/kafka-console-producer.sh --broker-list ip1:9092,ip2:9092 --topic topic_name

# 查询 topic 内容
bin/kafka-console-consumer.sh --bootstrap-server localhost:9092 --topic topicName --from-beginning
```


## 更复杂的命令

使用 python 读取特定 partition 的消息:

```python
# 安装依赖: pip3 install kafka-python
# manually assign the partition list for the consumer
from kafka import (
    KafkaConsumer,
    TopicPartition,
)
consumer = KafkaConsumer(bootstrap_servers=[
			'localhost:9092',
])
consumer.assign([TopicPartition('foobar', 0)])

# 读取 10 条消息
[next(consumer).value for it in range(10)]
```


## 其他

1. kafka 限流（确保 kafka 性能，避免被无限制 write/read 导致集群崩溃，在线上集群是非常重要的功能）
    1. producer 限流
    2. consumer 限流
2. 重平衡限流
    1. 避免节点故障后的重平衡导致集群性能剧烈下降

## 故障处理流程

1. 故障节点的快速替换
2. kafka 节点 cpu 扩容：提升云服务器实例类型的同时，需要调整 kafka 的 threads 参数

## 进阶

- 使用 Pulsar 替换 kafka（好处是存算分离，扩容简单，云原生）

