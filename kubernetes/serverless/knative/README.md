# [Knative - Serverless 应用的构建、部署与管理平台](https://github.com/knative)

## 架构

Knative 由两大组件组成：

1. Servering（工作负载管理）: 负责处理容器部署、网络、扩缩容和版本追踪。
2. Eventing（事件管理）: 统一的事件管理，

Knative 本身只提供容器级别的 Serverless 能力，而从源码到容器的流程，它建议你使用 Tekton:

1. [Tekton](/CI-CD/tekton/README.md): 一个云原生的 CI/CD 流水线。


结合上述三个组件，就得到了 Knative: 应用从源码到生产环境的全生命周期管理平台。

此外，Knative 还可以与服务网格 Istio 结合，提供服务路由管理、灰度发布等功能。


## 部署

首先，请先安装好 Istio 服务网格，Knative 依赖于它进行流量管控和指标监控。

接下来跟着官方文档安装 Knative:

```shell
export KNATIVE_VER=v0.19.0
# 1. 下载 servering 配置
## crds
wget https://github.com/knative/serving/releases/download/$KNATIVE_VER/serving-crds.yaml
# core
wget https://github.com/knative/serving/releases/download/$KNATIVE_VER/serving-core.yaml
# istio 集成
wget -O net-istio.yaml https://github.com/knative/net-istio/releases/download/$KNATIVE_VER/release.yaml
# hpa
wget https://github.com/knative/serving/releases/download/$KNATIVE_VER/serving-hpa.yaml

# 2. 下载 eventing 配置
## crds
wget https://github.com/knative/eventing/releases/download/$KNATIVE_VER/eventing-crds.yaml
# core
wget https://github.com/knative/eventing/releases/download/$KNATIVE_VER/eventing-core.yaml
# default Channel (messaging) layer - 也可选用 NATS
wget https://github.com/knative/eventing/releases/download/$KNATIVE_VER/in-memory-channel.yaml
# Broker (eventing) layer
wget https://github.com/knative/eventing/releases/download/$KNATIVE_VER/mt-channel-broker.yaml

# 下载可选的事件源配置，支持 Github Source 等
# 待续

# 一次部署所有
kubectl apply -f .
```



## 参考


- [《Knative 云原生应用开发指南》开启云原生时代 Serverless 之门 - 阿里云社区](https://developer.aliyun.com/article/739122)
- [实现Serverless面临的五大挑战](https://zhuanlan.zhihu.com/p/143389610)
