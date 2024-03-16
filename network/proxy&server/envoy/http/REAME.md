# Envoy HTTP 连接管理器(HCM)

HTTP 在现代网络中是如此重要，网络中无数的应用程序都依赖 HTTP。因此 Envoy 专门为 HTTP 协议提供了大量
的功能。HTTP 连接管理器是 HTTP 内置的一个网络层过滤器，它将 L3/L4 层的数据翻译为 HTTP 层的信息与事件
（比如收到 HTTP 响应头，接收到 body 数据等），另外一些 HTTP 连接的通用能力也由它提供，比如访问日志、
链路追踪、headers 修改、HTTP 路由、记录统计指标等...

从协议的角度来看，HCM 原生支持 HTTP/1.1、WebSockets、HTTP/2 和 HTTP/3（Alpha 阶段）。

无论流来自哪种 HTTP 协议的连接（HTTP/1.1、HTTP/2 或 HTTP/3），Envoy 都使用其内部的**编解码
API**（codec API） 将流中的数据翻译成**流、请求、响应**等协议无关的格式，有了这一层抽象，上层的大多
数代码就都可以在多种协议上通用了。

Envoy 官方提供了许多有用的内置过滤器，列表参见
[Envoy HTTP filters](https://www.envoyproxy.io/docs/envoy/v1.21.1/configuration/http/http_filters/http_filters#config-http-filters)

## HTTP 过滤器

HCM 支持配置一个 HTTP 过滤器栈，HTTP 过滤器只需要关注 Envoy 提供的协议无关 HTTP 模型。HCM 提供如下三
种类型的 HTTP 过滤器：

- Decoder: Decoder 将在 HCM 解码请求流的某一部分（比如 Headers/Body）时被调用
- Encoder: Encoder 将在 HCM 编码响应流的某一部分（比如 Headers/Body）时被调用
- Decoder/Encoder: 这类过滤器在编码解码某部分数据时都会被调用

### 过滤器顺序

假设过滤器的配置如下，三个都是编解码器：

```yaml
http_filters:
  - A
  - B
  # 最后一个过滤器必须为「终端过滤器」，比如「路由过滤器」、「直接响应过滤器」及「重定向过滤器」
  - C
```

Decoder 按列表**顺序**调用这些过滤器：A => B => C 而 Encoder 则按列表**逆序**调用这些过滤器：C => B
=> A

## HTTP 路由

详见
[HTTP 路由 - Envoy](https://www.envoyproxy.io/docs/envoy/v1.21.1/intro/arch_overview/http/http_routing)

Envoy 提供一个 HTTP 路由过滤器，它主要有两个应用场景：

- 边缘网关：类似 Nginx 反向代理
  - 这是 HTTP 过滤器的各种特性的最大用武之地，常用功能包括：
    - 根据 Host/Path 转发
    - 负载均衡（加权轮询、一致性哈希等）
    - [流量的加权切分](https://www.envoyproxy.io/docs/envoy/v1.21.1/configuration/http/http_conn_man/traffic_splitting#config-http-conn-man-route-table-traffic-splitting)
    - 监控指标
    - [Path prefix/regex rewrite](https://www.envoyproxy.io/docs/envoy/v1.21.1/api-v3/config/route/v3/route_components.proto#envoy-v3-api-field-config-route-v3-redirectaction-prefix-rewrite)
    - 限流限并发
    - [直接 HTTP 响应](https://www.envoyproxy.io/docs/envoy/v1.21.1/intro/arch_overview/http/http_routing#arch-overview-http-routing-direct-response)
    - TLS 加密
  - 「直接 HTTP 响应」应用场景：
    - 下线某些曾经存在的 API 后，让边缘网关直接返回 200，避免客户端报错 5XX/4XX
  - 「Path rewrite」应用场景：
    - 随着应用的迭代，应用的外部 API 与内部 API 的 Path/Headers 可能会变得不一致，这个功能主要用于解
      决这类兼容问题
- 服务网格中的服务间代理
  - 在这个场景下主要使用的 HTTP 过滤器功能有：
    - 根据 Host 转发
    - 负载均衡（加权轮询、一致性哈希等）
    - 流量的加权切分
    - 监控指标
    - 限流限并发
    - 请求重试（注意流量放大问题）
    - mTLS: 零信任场景下可开启，有一定性能消耗
  - 服务间代理基本不需要这些功能：根据 Path 转发、Path rewrite、直接 HTTP 响应

每个 HCM 过滤器都会有一个关联的
[HTTP 路由表 `route_config`](https://www.envoyproxy.io/docs/envoy/v1.21.1/intro/arch_overview/http/http_routing#arch-overview-http-routing)，HTTP
转发表有两种配置方式：

- 静态配置
- 通过 RDS API 动态配置

### Match 路由匹配

```yaml
route_config:
  name: my_route_config # 用于指标统计的名称，与路由无关
  virtual_hosts:
    - name: bar_vhost
      domains: ["bar.io"]
      routes:
        - match:
            prefix: "/" # path 前缀匹配，默认大小写敏感
            # path: "/aaa"  # path 精确匹配，默认大小写敏感
            # safe_regex: "/a.+/b"  # path 正则匹配，大小写敏感性通过正则语法控制（猜的哈）？
            headers: # headers 匹配
              - name: xxx-header
                string_match:
                  safe_regex_match:
                    google_re2: {}
                    regex: "^v\\d+$" # 正则匹配 header 的值
              - name: yyy-header
                string_match:
                  exact: "hello" # 精确匹配
              - name: env
                contains_match: "test" # 部分匹配
                ignore_case: true # 忽略值的大小写
                invert_match: true # 翻墙匹配（即不包括 test）
          route:
            cluster: bar_io # 转发给这个 cluster
    - name: foo_vhost
      domains: ["foo.io"]
      routes: # 默认按列表顺序设定优先级，除非手动设定了 priority: HIGH
        - match:
            prefix: "/"
          route:
            cluster: foo_io # 转发到这个 cluster
        - match:
            prefix: "/api"
            priority: HIGH # 优先级高，
          route:
            cluster: foo_io_api
```

### 流量加权切分

```yaml
route_config:
  virtual_hosts:
    - name: hello_vhost
      domains: ["hello.io"]
      routes:
        - match:
            prefix: "/"
          route:
            weighted_clusters:
              total_weight: 1000 # 定义总的权重值，默认为 100
              clusters:
                - name: hello_v1
                  weight: 1
                - name: hello_v2
                  weight: 99
                - name: hello_v3
                  weight: 900
```

## HTTP Headers 操作

Envoy 按照以下顺序对请求/响应应用 Headers 配置：

- 加权的集群级头信息
- 路由级 Header
- 虚拟主机级 Header
- 全局级 Header

这个顺序意味着 Envoy 可能会用更高层次（路由、虚拟主机或全局）配置的 Headers 来覆盖更低层次设置的
Headers.

在每一级，我们可以设置以下字段来添加 / 删除请求 / 响应头。

- `response_headers_to_add`：要添加到响应中的 Header 数组
- `response_headers_to_remove`：要从响应中移除的 Header 数组
- `request_headers_to_add`：要添加到请求中的 Header 数组
- `request_headers_to_remove`：要从请求中删除的 Header 数组

Envoy 还支持使用变量动态生成 header 的值。变量名称以百分号 % 为分隔符。支持的变量名称包括：

- `%DOWNSTREAM_REMOTE_ADDRESS%`
- `%UPSTREAM_REMOTE_ADDRESS%`
- `%START_TIME%`
- `%RESPONSE_FLAGS%`
- 等等，完整列表参见
  [自定义请求/响应的 headers - Envoy](https://www.envoyproxy.io/docs/envoy/v1.21.1/configuration/http/http_conn_man/headers#custom-request-response-headers)

另外 Envoy 的 HTTP 抽象基于 HTTP/2 语义，因此注意 `Host` 属性对应的 header 名称为 `:authority`.

```yaml
route_config:
  # 全局的 headers 配置，应用在所有 virtual_hosts 上
  response_headers_to_add:
    - header:
        key: "header_1"
        value: "some_value"
      append: false # true 表示将 value 附加到当前值的末尾，false 表示直接替换
  response_headers_to_remove: "header_we_dont_need" # 移除 header
  virtual_hosts:
    - name: hello_vhost
      # virtual_host 级别的配置，应用在此虚拟主机的所有路由表上
      request_headers_to_add:
        - header:
            key: "v_host_header"
            value: "from_v_host"
      domains: ["hello.io"]
      routes:
        - match:
            prefix: "/"
          route:
            cluster: hello
          response_headers_to_add: # 路由级别的 Headers 配置
            - header:
                key: "route_header"
                value: "%DOWNSTREAM_REMOTE_ADDRESS%"
        - match:
            prefix: "/api"
          route:
            cluster: hello_api
          response_headers_to_add:
            - header:
                key: "api_route_header"
                value: "api-value"
            - header:
                key: "header_1"
                value: "this_will_be_overwritten"
```

### X-Forward-For

Envoy 支持转发源 IP 地址及协议，配置方法如下：

```yaml
...
- filters:
  - name: envoy.filters.network.http_connection_manager
    typed_config:
      "@type": type.googleapis.com/envoy.extensions.filters.network.http_connection_manager.v3.HttpConnectionManager
      use_remote_address: true  # 转发源 ip 地址
      skip_xff_append: false    # 不跳过 xff headers 的添加
      ...
```

## 限流限并发

限流限并发是一种服务保护策略，在边缘网关上主要用于防护 CC 攻击或者避免过大的峰值流量把服务打垮。而在
服务网格内部，则主要用于避免配置不当导致服务雪崩。

Envoy 支持全局（分布式）和局部（非分布式）的速率限制。对服务保护而言，我们通常只需要局部速率限制，它
配置简单，性能高，而且也同样有效。

对于服务保护而言，我们实际并不需要非常精确的速率限制能力，因此没必要使用分布式的速率限制。

示例配置：

```yaml
filter_chains:
  - filters:
      - name: envoy.filters.network.http_connection_manager
        typed_config:
          "@type": type.googleapis.com/envoy.extensions.filters.network.http_connection_manager.v3.HttpConnectionManager
          stat_prefix: ingress_http
          route_config:
            name: local_route
            virtual_hosts:
              - name: instance_1
                domains: ["*"]
                routes:
                  - match:
                      prefix: /status
                    route:
                      cluster: instance_1
                  - match:
                      prefix: /headers
                    route:
                      cluster: instance_1
                    typed_per_filter_config:
                      envoy.filters.http.local_ratelimit:
                        "@type": type.googleapis.com/envoy.extensions.filters.http.local_ratelimit.v3.LocalRateLimit
                        stat_prefix: headers_route
                        token_bucket:
                          max_tokens: 8000 # 令牌的最大总数
                          tokens_per_fill: 8000 # 每次补充的令牌个数
                          fill_interval: 1s # 多久补充一次令牌
                        filter_enabled:
                          default_value:
                            numerator: 100
                            denominator: HUNDRED
                        filter_enforced:
                          default_value:
                            numerator: 100
                            denominator: HUNDRED
                        response_headers_to_add:
                          - append: false
                            header:
                              key: x-rate-limited
                              value: OH_NO
          http_filters:
            - name: envoy.filters.http.local_ratelimit
              typed_config:
                "@type": type.googleapis.com/envoy.extensions.filters.http.local_ratelimit.v3.LocalRateLimit
                stat_prefix: httpbin_rate_limiter
            - name: envoy.filters.http.router
```

## HCM 的超时参数

详见
[Envoy 如何配置超时？](https://www.envoyproxy.io/docs/envoy/v1.21.1/faq/configuration/timeouts#faq-configuration-timeouts)

HTTP/gRPC 的超时主要有如下几个配置项：

- `common_http_protocol_options.idle_timeout`
  - http 连接没有存活请求的持续时间，超过这个时间的 HTTP 连接会被自动关闭。这是一个请求级别的超
    时，HTTP/2 PING （非请求）并不能使连接一直存活。
  - 默认 1h
  - 如果这是一个下游 HTTP/2 连接，在连接关闭前会先 drain 掉相关的连接，相关参数为
    `common_http_protocol_options.drain_timeout`
  - 禁用此超时可能会因为丢失 TCP FIN 而导致连接泄漏
- `common_http_protocol_options.max_connection_duration`
  - 连接的最大存活时间，超过此时间的 HTTP 连接会被自动关闭。
  - 如果连接空闲，将被立即关闭。如果连接存在活动请求，将会自动进入 drain 流程

举例：

```yaml
---
filters:
  - name: envoy.filters.network.http_connection_manager
    typed_config:
      "@type": type.googleapis.com/envoy.extensions.filters.network.http_connection_manager.v3.HttpConnectionManager
      stat_prefix: ingress_http
      common_http_protocol_options:
        # 设置空闲超时为 10 分钟
        idle_timeout: 600s
```

Envoy 中 HTTP 还有一个「流超时」，「流」是一个 HTTP/2 与 HTTP/3 的概念，但是在 Envoy 中 HTTP/1 的请
求也会被映射到这个抽象里，因此对 HTTP/1 而言「流」就等于「请求」。

- `request_timeout`
  - 接收请求流的超时时间，超过这个时间的请求会被断开
  - **默认不启用**这个参数，因为 HTTP/2 支持永远不会中断的流
  - 如果使用了 buffer filter 来缓存请求，则建议配置这个参数
- `request_headers_timeout`
- `stream_idle_timeout`
- `max_stream_duration`

「路由超时」是一个层级更高的超时设置，它的参数跟前面的一致，但是优先级更高。

TCP 超时：

- `connect_timeout`
  - 与上游建立连接的超时时间，默认 5s
- `idle_timeout`
  - TCP 连接的空闲时间，默认 1h

## Cluster

### 异常点检测（outlier_detection）

这是一种被动的异常检测机制，被检测到异常的 endpoints 会在一定时间内被踢出负载均衡池。

连续的 5XX:

```yaml
  clusters:
  - name: my_cluster_name
    outlier_detection:
      interval: 5s
      base_ejection_time: 15s
      max_ejection_time: 50s
      max_ejection_percent: 30
      consecutive_5xx: 10
      ...
```

### 断路器（circuit_breakers）

断路器跟前面介绍的速率限制其实功能类似，但是它是直接作用在 endpoints 层面的，比速率限制要更粗粒度
些。不过就服务保护而言，这个其实也够了（代价是某个 api 出问题，会导致所有 API 都被限速）。

```yaml
...
  clusters:
  - name: my_cluster_name
  ...
    circuit_breakers:
      thresholds:
        - priority: DEFAULT
          max_connections: 1000
        - priority: HIGH
          max_requests: 2000
...
```

## 访问日志

详见
[Envoy 访问日志](https://www.envoyproxy.io/docs/envoy/v1.21.1/configuration/observability/access_log/usage)

## Slow start 模式

[Slow start 模式](https://www.envoyproxy.io/docs/envoy/v1.21.1/intro/arch_overview/upstream/load_balancing/slow_start)
