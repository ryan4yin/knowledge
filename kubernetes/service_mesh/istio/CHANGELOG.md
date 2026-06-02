# CHANGELOG - 一些值得一提的变更

注意，这里一般不记录实验性特性、alpha 特性等不推荐上生产环境的变更，除非它非常有用。

- istio 1.5
  - 回归单体结构 - istiod
  - PeerAuthentication/RequestAuthentication 与 authorization 进入 beta
  - 使用数据面的 Telemetry v2 插件替代中心化的 Mixer，istio 的指标因此发生较大变化
- istio 1.8
  - 添加全局与 Pod 级别的 holdApplicationUntilProxyStarts 参数，使应用程序在 proxy 就续后再启动，避
    免无法访问网络导致应用报错
  - 支持通过 `X-Forwarded-For` (XFF) and `X-Forwarded-Client-Cert` (XFCC) 请求头转发客户端 IP/证
    书：[Configuring Gateway Network Topology](https://istio.io/latest/docs/ops/configuration/traffic-management/network-topologies/)
- istio 1.9
  - 虚拟机支持进入 beta
  - Request Classification 进入 beta（监控指标相关的优化，可用于按 path/header 等信息进行指标分类，
    分类的目的是为了在指标精细度与指标数据量之间取得一个平衡）
  - 添加镜像仓库 `gcr.io/istio-release` 以避免 Dockerhub 的镜像拉取速率限制
- istio 1.10
  - 服务发现方面的性能优化
  - 支持多个版本的控制面共存，通过 namespace 的 label 来切换版本
  - 旧版本中，sidecar 从 eth0 截获数据后，会通过 lo 转发给应用容器，现在改成了同样通过 eth0 发送给应
    用容器
    - 如果应用容器原来只监听 `127.0.0.1` 等 lo 地址，就会出问题！需要改成 `0.0.0.0`
- istio 1.11
  - CNI 插件进入 beta，它能缩减 sidecar 的权限
  - External control plane 进入 beta
  - Gateway injection: 新的 Gateway 部署方式，并给出了简单易懂的文档。
- istio 1.12
  - [alpha] 为 Telemetry 添加专用 API:
    [Telemetry API](https://istio.io/latest/docs/reference/config/telemetr)，可以非常方便地自定义
    Tracing/Metrics/Logging 配置
  - [alpha] 为 WASM 插件添加 API: `WasmPlugin`
  - 优化 helm chart
  - [alpha] Gateway API 升级到 v1alpha2
- istio 1.13
  - 在 k8s 1.21+ 集群上，通过 EndpointSlice 资源获取所有 workloads，而不是 Endpoint
  - fix: 有部分连接被 reset:
    [Drop packets in INVALID state to avoid intermittent connection reset from sidecar](https://github.com/istio/istio/pull/36566)，
    感觉这个可能就是造成 0 状态码的罪魁祸首？
  - fix:
    [HTTP/1.0 requests to be rejected (with a 426 Upgrade Required error) in some cases](https://github.com/istio/istio/issues/36707)
- istio 1.14
  - 默认负载均衡算法从 ROUND_ROBIN 切换到 LEAST_REQUEST。
    - 官方通过一系列测试发现，LEAST_REQUEST 在几乎所有虚拟场景中，效果都优于 ROUND_ROBIN，因此决定做
      这一修改。
  - [DestinationRule](https://istio.io/latest/docs/reference/config/networking/destination-rule/#LoadBalancerSettings)
    添加参数 `warmupDurationSecs`
    - fix [支持 Pod 扩容时，新 Pod 的 slow start](https://github.com/istio/istio/issues/21228)
    - 但也存在一些 bug: [slow start in istio](https://github.com/istio/istio/issues?q=slow+start)
- istio 1.15
  - **支持越来越流行的 arm64 架构**
    - 要知道 AWS 的 arm64 实例比 amd64 性价比高 40%！升级后 Istio 网关层将能立即取得到这项收益
    - 测试发现如果采用了 mtls 加密，arm64 的性价比就低很多了，因为它的加密性能不如 amd64
  - [取消总权重为 `100` 的限制，可以设为任意整数](https://github.com/istio/istio/issues/36069)
- istio 1.16 - 2022-11-15
  - **Kubernetes Gateway API 进入 Beta**
  - 添加对 MAGLEV 负载均衡算法的支持
  - 支持 OpenTelemetry Provider 用于 Tracing
    - 同时 Telemetry API 改用新的 native 插件替换旧的 wasm 插件，降低了其 CPU/MEM 消耗
  - 其他小变更
    - Host 的匹配，默认忽略端口号，可通过环境变量 `SIDECAR_IGNORE_PORT_IN_HOST_MATCH` 控制这一行为
- istio 1.17 - 2023-02-14
  - 金丝雀升级功能进入 beta
  - helm 安装方式进入 beta
  - Kubernetes Gateway API 升级到最新版本（0.6.1）
  - IPv6 双栈支持改进
- istio 1.18 - 2023-06-07
  - 实验性的 ambient mesh 功能 - 使用节点级别的 proxy，大大降低 sidecar proxy 的资源占用
- istio 1.19 - 2023-09-05
  - Gateway API 升级到 v0.8.0，**首次加入 Service Mesh 支持**
- [istio 1.20](https://istio.io/latest/news/releases/1.20.x/announcing-1.20/) - 2023-11-14
  - Gateway API GA，升级到 1.0.0
  - StartupProbe in Sidecar Containers, 大概能缩短 1s 的启动时间
- [istio 1.21](https://istio.io/latest/news/releases/1.21.x/announcing-1.21/) - 2024-03-13
  - 优化配置兼容性，支持设置兼容版本，这样在升级到新版本后，仍然可以使用旧版本的配置，兼容其行为。
- **[istio 1.22](https://istio.io/latest/news/releases/1.22.x/announcing-1.22/)** - 2024-05-13
  - **Ambient Mesh 功能进入 beta**
    - Compared to sidecar mode, ambient mode reduces memory overhead and CPU usage by over 90% in
      many cases.
  - **VirtualService/DestinationRule/Gateway/Sidecar/... 这套 APIs 终
    于[从 v1beta1 升级到了 v1](https://istio.io/latest/blog/2024/v1-apis/)**.
  - **Gateway API 对 service mesh 的支持进入 stable**，也就是说可以考虑从
    virtualservice/DestinationRule 这一套 API 彻底迁移到 Gateway API 了.
  - **Delta xDS 成为默认方式，这极大地提高了控制面与 sidecar proxy 的性能**
- **[istio 1.23](https://istio.io/latest/news/releases/1.23.x/announcing-1.23/)** - 2024-08-14
  - 对 Ambient Mesh 做了大量改进
- **[istio 1.24](https://istio.io/latest/news/releases/1.24.x/announcing-1.24/)** - 2024-11-07

  - [Ambient Mode 进入 GA](https://istio.io/latest/blog/2024/ambient-reaches-ga/)
    - 一系列 Ambient mode 的改进，以及 troubleshooting 文档:
      <https://github.com/istio/istio/wiki/Troubleshooting-Istio-Ambient>

- **[istio 1.25](https://istio.io/latest/news/releases/1.25.x/announcing-1.25/)** - 2025-03-03
  - 跨区流量治理 - 支持 Kubernetes 原生的
    [Traffic Distribution](https://kubernetes.io/docs/concepts/services-networking/service/#traffic-distribution)
    参数
  - istio-cni 支持了热更新，不会造成节点上的流量中断。
- **[istio 1.26](https://istio.io/latest/news/releases/1.26.x/announcing-1.26/)** - 2025-05-08

  - 支持通过 Configmap 自定义 Gateway API 的 Gateway 资源自动创建的 Deployment/Service/HPA/PDB 等资
    源参数
  - 新增了对 Gateway API 的 TCPRoute 的支持

  - 重要升级变化
    - 默认使用 Kubernetes Gateway API v1.3，升级前需确认集群中 Gateway API CRD 版本
    - `istioctl manifest` 相关命令继续弱化，推荐迁移到 Helm 或 `istioctl install`

- **[istio 1.27](https://istio.io/latest/news/releases/1.27.x/announcing-1.27/)** - 2025-08-11
  - **Waypoint proxy 成熟度提升**，Ambient mode 下 L7 策略、遥测与流量治理能力继续补齐
  - **Gateway API 支持增强**，继续减少对 VirtualService/Gateway 旧 API 组合的依赖
  - 重要升级变化
    - 继续推进 Gateway API/ambient 方向，升级前应检查 waypoint、ztunnel、CNI 与控制面版本一致性
    - 使用 EnvoyFilter 的场景仍需逐项回归，因为 EnvoyFilter 依赖底层 Envoy 细节，跨版本风险最高
- **[istio 1.28](https://istio.io/latest/news/releases/1.28.x/announcing-1.28/)** - 2025-11-06
  - Ambient mode 继续增强，包括 waypoint、ztunnel、故障排查与可观测性能力
  - Gateway API 集成继续增强，适合作为新流量入口/服务网格 API 的默认方向
  - 重要升级变化
    - 关注 Gateway API CRD 版本与 Kubernetes 版本兼容性，避免控制面升级后 CRD 仍停留在旧版本
    - 自定义安装参数建议迁移到 Helm values，减少对旧 manifest 生成流程的依赖
- **[istio 1.29](https://istio.io/latest/news/releases/1.29.x/announcing-1.29/)** - 2026-02-12
  - **Gateway API Inference Extension 支持进入 alpha**，支持面向 LLM/AI 服务的 EPP (Endpoint Picker
    Provider) 流量选择
  - **零停机金丝雀升级体验优化**，减少 sidecar 升级时短暂流量中断的概率
  - **Telemetry API 的访问日志配置能力增强**，可更细粒度地控制 access log
  - **支持多集群 Harbor Gateway**，多集群入口/网关拓扑能力增强
  - 重要升级变化
    - 升级前建议先用 `istioctl analyze` 检查弃用配置与 analyzer 告警
    - 如果使用 Inference Extension，需要同步检查 Gateway API 扩展 CRD 与 EPP 实现版本
- **[istio 1.30](https://istio.io/latest/news/releases/1.30.x/announcing-1.30/)** - 2026-05-07
  - **Gateway API Inference Extension 进入 beta**，推理服务流量选择能力更接近生产可用
  - **Ambient mode 支持 multicluster**，并发布新的 ambient multicluster 安装文档
  - **支持对 `istioctl waypoint apply` 创建的 waypoint 做定制化配置**
  - **新增 alpha 级别的 sidecar 高可用模式**，可通过同一 Pod 内多个 Envoy proxy 提升可用性
  - 新增 `istioctl experimental describe`，辅助分析 `VirtualService`/`DestinationRule`/服务的配置关
    系
  - 重要升级变化
    - 升级 Kubernetes 到 1.36 前，需同步关注 Istio CNI、ztunnel、waypoint 与 Gateway API CRD 版本
    - Ingress NGINX 已退休，使用 Istio Gateway/Gateway API 作为入口时应优先规划 Gateway API 化
    - 使用旧版 Telemetry、EnvoyFilter、非默认 meshConfig 的集群，应在灰度控制面中先验证行为变化
