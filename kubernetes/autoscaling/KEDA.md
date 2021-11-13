# [KEDA](https://github.com/kedacore/keda)

KEDA 是微软开源的一个 kubernetes 自动伸缩组件，KEDA 以 Metrics Server 的形式工作，允许用户通过 CRDs 定制伸缩策略。

阿里的 kubevela 底层就使用了 KEDA 做自动伸缩。


## 优势

- 支持非常多种数据源
- CRD 定义比 HPA v2beta2 更直观，更好理解。
