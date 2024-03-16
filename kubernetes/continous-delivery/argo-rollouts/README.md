# Argo-Rollouts

Argo-Rollouts 也是一个 K8s 上的渐进式交付工具，支持的服务网格/Ingress 不如 Flagger 丰富，但是个人觉
得它对 Istio 的支持，封装程度更合适。

argo-rollouts 不直接生成 istio 配置，istio 配置由用户通过其他手段提前部署好，argo-rollouts 仅在该配
置上进行切量配置的动态更新。这在 Istio 配置上给了我们更大的自定义空间。
