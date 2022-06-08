# 持续交付

在这个领域，目前社区主要就是 flagger 跟 argo-rollouts 两个工具。

但是这两个工具对 CD 的支持，感觉都还比较初级，实际应用上，可能仅适合初创公司。对于复杂场景的支持是不够的。

比如说支持多版本共存、金丝雀发布的暂停/继续/取消逻辑、自定义 Istio 的 VirtualService/DestinationRule 配置、自定义 Deployment 配置等等。


