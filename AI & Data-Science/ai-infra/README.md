# AI 基础设施

## 负载均衡

AI Gateway，或者 LLM Gateway，是专为 AI 服务优化的网关，总体看是在 2024 年底才开始逐渐变热的一个赛
道。目前 Kong, Envoy, Traefik, APISIX 等各大流行网关都有在做类似功能的插件。

其主要特点：

- 针对 LLM 而言，AI Gateway 内置了对众多 LLM API 供应商的支持，而且对客户端屏蔽了底层 API 的差异，使
  得用户可以很便捷得在各种模型与供应商之间切换。
- 根据成本与请求延迟来综合考虑负载均衡策略，达到可用性与成本的平衡。
- 提供 AI/LLM 层面的细粒度监控指标，并基于这些指标动态调整负载均衡策略。
- 其他可能提供的功能：AI 日志、输入输出的安全检查、提示词模板、AI 缓存（相同的提示词可以直接返回结
  果）等等。

相关开源项目：

- LLM Gateway
  - https://github.com/Portkey-AI/gateway: 支持众多 LLM API 提供商
  - https://github.com/envoyproxy/ai-gateway: 与 portkey-ai 的 gateway 目标一致，它虽然部署在 k8s
    内，但主要目标也是将 LLM 请求负载均衡到其他外补 LLM API 提供商，而不是 k8s 内的其他 pods.
  - https://docs.konghq.com/hub/kong-inc/ai-proxy/: kong ai proxy 的开源版本，功能比 envoy 的要成熟
    许多，它还有个功能更强大的企业版。

以及国内相关的项目：

- https://github.com/QuantumNous/new-api: 支持了众多国内 LLM API 提供商的开源项目，貌似目标用户是不
  会编程的普通人，而且还做了充值收费功能，适合个人或私有化部署使用。

## 编排调度与扩缩容

这又分成两个部分：

- AI 训练：训练工作是一个批处理任务式的工作负载，目前貌似 kubeflow + volcano 比较适用这个场景。
- AI 推理：推理请求更类似传统的 API 服务，但是它的容器环境相当笨重，提升扩容速度是一大难题，此外一个
  LLM 请求也常常要花几秒甚至几十秒，因此也常用 websocket 流式响应。
  - 这个部分我目前搜到高策的
    [在 Kubernetes 中 部署 LLM 的实践](https://zhuanlan.zhihu.com/p/1607895216698) 最有参考价值，其
    中挺多跟我的使用经验也能对应上。
  - 推理主要就是分成**模型下载、镜像拉取以及负载均衡**这三个部分，负载均衡这部分前面已经有介绍了一些
    开源项目，虽然不太能开箱即用，但参考思路是没问题的。模型跟镜像这部分则是综合利用高效压缩、内网缓
    存、节点缓存、流式传输、lazy pulling 等各种手段提速。
