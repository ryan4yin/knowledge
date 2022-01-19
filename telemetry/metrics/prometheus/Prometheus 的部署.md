## 高可用 Prometheus

单节点的 Prometheus 存在如下问题：

- 抓取指标的性能不够：targets 越来越多时，单个 P8s 的压力会越来越大。
- 查询性能堪忧：数据都保存在本地，查询的数据量一大，一个是速度会很慢，二个是很容易把 P8s 搞崩（OOM）。
- 启动速度慢、甚至无法启动：万一 P8s 被查崩了需要重启，本地的 WAL 数据量太大，会导致 P8s 一启动就 OOM（读 WAL 需要大量内存）。

一个高可用的 Prometheus 方案需要能够漂亮地解决上述问题才行。目前社区的方案很多：thanos/cortex/m3db/VictoriaMetrics...

## 主流的 HA 方案

>[Comparing Thanos to VictoriaMetrics cluster](https://faun.pub/comparing-thanos-to-victoriametrics-cluster-b193bea1683)

针对前面提到的「抓取指标的性能不够」的问题，我们通常的做法是拆分成多个 P8s，分别负责采集某种类型的 targets 指标。

而对于「查询性能」以及「数据存储」两个方面，目前最流行的是如下两个方案：

- [thanos-io/thanos(灭霸)](https://github.com/thanos-io/thanos): 通过 sidecar 将 p8s 的数据直接同步到 S3（或其他对象存储），或者降采样后再同步到 S3，确保数据不丢失。本地只保留 2h 的数据。
  - S3 等对象存储的价格都很低，很经济实惠。
  -  但是 thanos 结构较复杂，维护成本可能会比较高。
- [VictoriaMetrics](https://github.com/VictoriaMetrics/VictoriaMetrics): 通过 p8s 的 Remote Write API 获取 P8s 的数据，然后保存到 vmstorage 中，再通过 vmselect 组件提供查询 API。
  - 结构简单，只有三个组件 vminsert/vmstorage/vmselect，而且这三个组件的可拓展性都很强。
  - 数据虽然是保存到本地磁盘，但是专门对 HDD 做了优化，存储成本跟 S3 没多大差距。而且 VictoriaMetrics 使用了更强悍的落盘数据压缩策略，相比 thanos 使用的存储空间会少很多。
  - 数据安全：
    - 数据冗余：为 `vminsert` 添加参数 `-replicationFactor=N`，可确保在集群有超过 $$2N - 1$$ 个节点的情况下，挂掉不超过 $$N-1$$ 个节点，都不会影响数据的可用性。
    - 数据备份：
      - 支持通过 `vmbackup` 定期将数据备份到 S3 等对象存储中，如果挂掉超过 $$2N - 1$$ 个节点，还能从 S3 备份中恢复。
      - 云上虚拟机的话，本来就支持做磁盘快照，这也是一个备份手段。


thanos 本身结构会复杂些，会有些额外的维护成本，但是除了 p8s 自身外，没有 stateful 组件。
而 VictoriaMetrics 结构很简单，但是就需要注意 `vmstorage` 的数据安全性。

个人感觉 VictoriaMetrics 可能是更好的选择？毕竟它的数据安全性其实已经做到很棒了，而且结构简单好维护。



## 部署 Prometheus

从实践的角度看，建议 P8s 只当作指标采集器使用，并且按 targets 类型拆分成多个以降低压力、也降低个别 P8s 挂掉的影响面。
再通过 Kubernetes 实现 P8s 的高可用（快速重新调度）。

## 指标抓取

### 1. Kubernetes 的指标

- Pods 的指标：社区版的 helm chart 都可以通过注解自动发现 Kubernetes 中的 targets，并抓取指标，详见其 README。
- Nodes 的指标：社区的 [node_exporter](https://github.com/prometheus/node_exporter) 就够用了，建议按需要关闭掉不需要的 `collectors` 以降低 node_exporter 对节点性能的影响。

### 2. AWS 资源、虚拟机、中间件的指标

大一统的 Metrics Agent：

- [influxdata/telegraf](https://github.com/influxdata/telegraf): 通过插件机制获取到 kafka/mysql/postgresql/redis/aws-ec2/... 的信息，转换成指标，按需要对指标进行裁剪、自定义，然后再提供给 Prometheus 等组件采集。

另外的方案，就是通过在 virtual_machine/kubernetes 上运行社区各种各样的 expoter，暴露出各种各样的指标，然后再配置 p8s 去一个个采集，这种方式很散，管理起来不太方便。
