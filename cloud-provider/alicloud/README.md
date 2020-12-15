# 阿里云

阿里云是目前国内最成熟的云服务提供商。

## 费用优化

### ARMS Prometheus 费用优化

阿里云的 ARMS Prometheus 在采集标准 k8s 集群的日志时，是没有任何费用的，全部指标都免费。

但是自定义指标收费，如果你在集群中部署各种工具、应用，而且这些应用的 Pod 带有 ` prometheus.io/scrape: true` 相关注解，
Prometheus Agent 就会采集这些 Pod 暴露出来的自定义指标。
在部署第三方工具时要谨慎，不注意就可能产生大量的自定义指标，产生大量收费。

比如我们部署 flagger 时没注意到，它的 helm values 中有如下默认参数：

```yaml
podAnnotations:
  # 如果不希望抓取 flagger export 的灰度状态与权重相关信息，请删除如下两个 prometheus 注解
  prometheus.io/scrape: "true"
  prometheus.io/port: "8080"
```

这导致 flagger 生成了好几百条自定义指标，再乘上我们的 Pod 数量，一天下来就好几十（单位：百万）的指标，一个月下来这些自定义指标的费用有近一千块。


针对这种情况，最佳方案是直接通过 helm 的 vaules 自定义功能，修改 prometheus 注解，关闭这类指标的抓取。

第二种方法，是直接在 ARMS Prometheus 的「设置」-「指标」-「配置废弃指标」中，将不需要的指标名称全部配置进去。
这类废弃指标不会被 ARMS Prometheus，不计收费次数。

### ASM

阿里云的 ASM 本身免费，但是它会动态生成两个负载均衡 SLB，这两个 SLB 是按量收费的。


### 日志服务

阿里云日志服务的收费项有如下几个：

1. 索引流量
2. 存储空间
3. 读写次数
4. 读写流量
5. 活跃 Shards(分片)租用：单个分片的价格 0.04元/天
    - 默认情况下，每个 logstore 都有两个读写分片，也就是说每个 logstore 的固定费用是 0.08 元/天。

在几乎没什么流量写入时，几乎所有的费用都来自「活跃 Shards(分片)租用」。
一个 k8s 集群的日志 project 通常有 4 个 logstores，固定费用就是 0.32 元/天。

有很多的日志、分析、告警的数据都会往日志服务写，包括：

1. arms prometheus: 它数据是往日志服务存的
2. 成本管家(bill analysis)
3. 链路追踪
4. OSS 日志
5. 操作审计
6. 短信服务日志
7. 等等

总而言之，各种其他服务，都可能会在日志服务中创建 project 和 logstores，
这导致我们一个闲置的阿里云账号，每个月居然也要扣一笔日志服务的费用。
