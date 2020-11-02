## 「重打标签」配置 - relabel_config/metric_relabel_config

>[relabel_config - prometheus docs](https://prometheus.io/docs/prometheus/latest/configuration/configuration/#relabel_config)

「重打标签」是 Prometheus 处理指标标签的主要手段。在 serviceMonitor/podMonitor 及 prometheus.yml 中都可以看到它的存在。
虽然名为「重打标签」，但实际上对「target」及「标签(label)」的增删改，都是可以通过它来进行的。

relabel_config: 在指标被采集前进行处理，假入某个标签被 drop，那么它根本不会被采集。
metric_relabel_config: 在指标被采集完成，还没有入库前，对指标进行处理。

根据「及早处理」的原则，应该尽量使用 relabel_config，不得已时才使用 metric_relabel_config。

### 详细语法



## PromQL

待续

