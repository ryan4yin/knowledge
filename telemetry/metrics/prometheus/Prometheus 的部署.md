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
  - 但是 thanos 结构较复杂，维护成本可能会比较高。
- [VictoriaMetrics](https://github.com/VictoriaMetrics/VictoriaMetrics): 通过 p8s 的 Remote Write API 获取 P8s 的数据，然后保存到 vmstorage 中，再通过 vmselect 组件提供查询 API。
  - 官方宣称在存储数百万不同的时间序列时，它比 InfluxDB 少用 10 倍的 RAM，比 Prometheus, Thanos 或 Cortex 少用 7 倍的 RAM。其他第三方的测试也显示它比 prometheus/mimir 要更省 CPU/RAM 或者存储空间。
  - 结构简单，只有三个组件 vminsert/vmstorage/vmselect，而且这三个组件的可拓展性都很强。
  - 数据虽然是保存到本地磁盘，但是专门对 HDD 做了优化，存储成本跟 S3 没多大差距。而且 VictoriaMetrics 使用了更强悍的落盘数据压缩策略，相比 thanos 使用的存储空间会少很多。
  - 数据安全：
    - 数据冗余：为 `vminsert` 添加参数 `-replicationFactor=N`，可确保在集群有超过 $2N - 1$ 个节点的情况下，挂掉不超过 $N-1$ 个节点，都不会影响数据的可用性。
    - 数据备份：
      - 支持通过 `vmbackup` 定期将数据备份到 S3 等对象存储中，如果挂掉超过 $2N - 1$ 个节点，还能从 S3 备份中恢复。
      - 云上虚拟机的话，本来就支持做磁盘快照，这也是一个备份手段。


thanos 本身结构会复杂些，会有些额外的维护成本，但是除了 p8s 自身外，没有 stateful 组件。
而 VictoriaMetrics 结构很简单，但是就需要注意 `vmstorage` 的数据安全性。

个人感觉 VictoriaMetrics 可能是更好的选择？毕竟它的数据安全性其实已经做到很棒了，而且结构简单好维护。



## 部署 Prometheus

从实践的角度看，建议 P8s 只当作指标采集器使用，并且按 targets 类型拆分成多个以降低压力、也降低个别 P8s 挂掉的影响面，再通过 Kubernetes 实现 P8s 的高可用（快速重新调度），这是迁移难度最小的方案。

当然 VicotiaMetrics 本身也有提供 agnet 用于指标采集，它也是可用的，对于没有历史配置且很信任 VicotiaMetrics 的公司而言，使用这种方法会更简单。

## 指标抓取

### 1. Kubernetes 的指标

- Pods 的指标：社区版的 helm chart 都可以通过注解自动发现 Kubernetes 中的 targets，并抓取指标，详见其 README。
- Nodes 的指标：社区的 [node_exporter](https://github.com/prometheus/node_exporter) 就够用了，建议按需要关闭掉不需要的 `collectors` 以降低 node_exporter 对节点性能的影响。

### 2. AWS 资源、虚拟机、中间件的指标

大一统的 Metrics Agent：

- [influxdata/telegraf](https://github.com/influxdata/telegraf): 通过插件机制获取到 kafka/mysql/postgresql/redis/aws-ec2/... 的信息，转换成指标，按需要对指标进行裁剪、自定义，然后再提供给 Prometheus 等组件采集。

另外的方案，就是通过在 virtual_machine/kubernetes 上运行社区各种各样的 expoter，暴露出各种各样的指标，然后再配置 p8s 去一个个采集，这种方式很散，管理起来不太方便。


## Prometheus 常见问题

- PV 卷满了没告警导致数据丢失
  - 负面影响：p8s 也没挂，就是单纯直接不存数据了，这导致我们一次丢了 9 个小时的数据，我自己上班查数据时才发现没指标了
  - 解决方法：prometheus 有提供 API 检查 PV 卷的使用情况，添加一个基于该 API 的 PV 卷监控
- 没有做 prometheus 交叉验证，p8s 自身挂了，完全感知不到
  - 负面影响：因为一些变更导致高峰期 prometheus 内存不够挂掉，然后每次一读 WAL 就内存用尽，一直重启。直到第二天上班业务侧查不到指标反馈，我们才感知到问题...也是丢了大概 10 小时数据
  - 解决方案：建两个 prometheus 做交叉验证，出问题就告警
- 查询的数据量太多时容易把 promethus 查崩
  - 负面影响：一是看不到数据，二是 prometheus 重启完成前的数据会丢，甚至有时候 WAL 数据太多，重启都可能启动不起来...
  - 解决方案：victoria metrics 存算分离，查询组件能单独扩缩容，而且不影响存储跟指标采集功能
