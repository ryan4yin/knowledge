# Istio 监控指标


## 自定义监控指标

### 1. 为 HTTP/gRPC 指标添加 host/method/path 信息

HTTP/gRPC 的指标都可以通过 `istio_requests_total` 查到，但是有一些重要的相关信息，Istio 默认不会放到指标里面：

- request.method
- request.host
- request.url_path - 去掉 query_string 后的 path
  - 添加这个 path 可能会导致指标数据量激增！注意谨慎处理，最好是加个截断，比如只保留 60 个字符。
  - 也可以通过 AttributeGen 根据 url_path 对请求进行分类，但是要硬编码很多内容，感觉很不方便。

那么它默认包含的信息里，哪些是有价值的呢？先看下 HTTP 协议：

- request_protocol="http"
- response_code - HTTP 状态码
- response_flags - 出现异常时，此参数会提供更多异常信息

对于 gRPC 协议呢：

- request_protocol="grpc"
- response_code - HTTP 状态码对 gRPC 而言没有任何意义，一般是写死的 200
- response_flags - 出现异常时，此参数会提供更多异常信息
- grpc_response_status - gRPC 自定义的状态码

>需要注意到，gRPC 的请求跟响应可能不是一一对应的，这个时候通过 `istio_requests_total` 得到的信息会如何处理，我还不太清楚。可能需要用到专用指标 `istio_request_messages_total` 跟 `istio_response_messages_total`？


可通过如下配置全局添加上述三个指标标签：

```yaml
apiVersion: install.istio.io/v1alpha1
kind: IstioOperator
spec:
  meshConfig:
    # `defaultConfig`: sidecar 和 gateway 的默认配置(envoy)，Pod 上的 `proxy.istio.io/config` 注解可以覆盖此默认值
    # https://istio.io/latest/docs/reference/config/istio.mesh.v1alpha1/#ProxyConfig
    defaultConfig:
      extraStatTags:  # 如果要在 metrics 中使用非默认的 stat 标签，就需要先补充到这
      - request_host
      - request_method
      - request_url_path
  components:
    telemetry:
      enabled: true
      v2:
        enabled: true
        prometheus:
          # istio 通过 EnvoyFilter 来配置 proxy 生成 prometheus 指标，这里可以实现自定义指标、增减指标的维度
          enabled: true
          wasmEnabled: false
          configOverride:
            inboundSidecar:  # 服务端 sidecar 的指标
              disable_host_header_fallback: false
              metrics:
                - name: requests_total
                  dimensions:
                    request_method: request.method
                    request_url_path: request.url_path
            outboundSidecar:  # 客户端 sidecar 的指标
              disable_host_header_fallback: false
              metrics:
                - name: requests_total
                  dimensions:
                    request_method: request.method
                    request_url_path: request.url_path
            gateway:  # 网关层的指标
              disable_host_header_fallback: true
              metrics:
                - name: requests_total
                  dimensions:  # 网关层的 requests_total 添加 request_host 标签
                    request_host: request.host
                    request_method: request.method
                    request_url_path: request.url_path
```

或许也可以通过 Telemetry API 局部添加这些标签，不全局生效，待研究

