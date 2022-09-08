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



