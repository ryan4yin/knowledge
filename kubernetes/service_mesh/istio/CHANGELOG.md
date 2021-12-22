# CHANGELOG - 一些值得一提的变更

注意，这里一般不记录实验性特性、alpha 特性等不推荐上生产环境的变更，除非它非常有用。

- istio 1.5
  - 回归单体结构 - istiod
  - PeerAuthentication/RequestAuthentication 与 authorization 进入 beta
  - 使用数据面的 Telemetry v2 插件替代中心化的 Mixer，istio 的指标因此发生较大变化
- istio 1.8
  - 添加全局与 Pod 级别的 holdApplicationUntilProxyStarts 参数，使应用程序在 proxy 就续后再启动，避免无法访问网络导致应用报错
  - 支持通过 `X-Forwarded-For` (XFF) and `X-Forwarded-Client-Cert` (XFCC) 请求头转发客户端 IP/证书：[Configuring Gateway Network Topology](https://istio.io/latest/docs/ops/configuration/traffic-management/network-topologies/)
- istio 1.9
  - 虚拟机支持进入 beta
  - Request Classification 进入 beta（监控指标相关的优化，还没搞懂具体的用处）
  - 添加镜像仓库 `gcr.io/istio-release` 以避免 Dockerhub 的镜像拉取速率限制
- istio 1.10
  - 服务发现方面的性能优化
  - 支持多个版本的控制面共存，通过 namespace 的 label 来切换版本
  - 旧版本中，sidecar 从 eth0 截获数据后，会通过 lo 转发给应用容器，现在改成了同样通过 eth0 发送给应用容器
    - 如果应用容器原来只监听 `127.0.0.1` 等 lo 地址，就会出问题！需要改成 `0.0.0.0`
- istio 1.11
  - CNI 插件进入 beta，它能缩减 sidecar 的权限
  - External control plane 进入 beta
  - Gateway injection: 新的 Gateway 部署方式，并给出了简单易懂的文档。
- istio 1.12
  - [alpha] 为 Telemetry 添加专用 API: [Telemetry API](https://istio.io/latest/docs/reference/config/telemetr)，可以非常方便地自定义 Tracing/Metrics/Logging 配置
  - [alpha] 为 WASM 插件添加 API: `WasmPlugin`
  - 优化 helm chart
  - [alpha] Gateway API 升级到 v1alpha2
- upcomming istio 1.1x
  - [取消总权重为 `100` 的限制，可以设为任意整数](https://github.com/istio/istio/issues/36069)
  - [支持 Pod 扩容时，新 Pod 的 warm up](https://github.com/istio/istio/issues/21228)

