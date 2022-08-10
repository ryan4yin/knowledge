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



