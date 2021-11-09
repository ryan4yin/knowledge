# [KEDA](https://github.com/kedacore/keda)

KEDA 是微软开源的一个 kubernetes 自动伸缩组件，KEDA 以 Metrics Server 的形式工作，允许用户通过 CRDs 定制伸缩策略。

阿里的 kubevela 底层就使用了 KEDA 做自动伸缩。


## 优势

- 支持非常多种数据源
- Kubernetes 自带的 HPA，伸缩算法是固定的 `期望副本数 = ceil[当前副本数 * ( 当前指标 / 目标指标 )]`。而 KEDA 可以自定义伸缩规则
