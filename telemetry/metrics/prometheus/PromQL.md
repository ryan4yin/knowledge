
# PromQL

### 1. 语法

#### 通过 label 进行指标过滤

- `=` 匹配值相同的标签
- `!=` 匹配值不相同的标签
- `=~` 值与正则表达式匹配的标签
- `!~` 值与正则表达式不匹配的标签

举例：
```promql
# 完全相等
http_requests_total{host="xxx.xxx", uri="/xxx"}

# 正则匹配 uri
http_requests_total{host="xxx.xxx", uri=~"/prefix.+"}
```

#### 常用函数

```
# 计算每秒的速率（使用前 5m 内的所有值计算平均值，作为该时间点的速率）
rate(http_requests_total{job="api-server"}[5m])

# 计算每秒的速率（使用前 5m 时间段末尾最新的两个数据来计算每秒速率，能避免因为平均而导致曲线被「削峰填谷」）
irate(http_requests_total{job="api-server"}[5m])
```

时间范围可使用的单位有：`5s` `5m` `5h` `5d` 等.

其他函数参见 [Prometheus Functions](https://prometheus.io/docs/prometheus/latest/querying/functions/)

#### 指标的聚合操作符（Aggregation Operators）

可用于聚合 label 相同的指标:

```promql
# 将所有 status 标签相同的指标加到一起，聚合成一个指标，并且去掉其他所有标签
sum by(status)  (rate(nginx_http_requests_total{host="xxx.xxx", uri="/xxx"}[3m]))

# 和 by 相反，去掉 host, uri 两个标签，按剩余的指标进行 sum 聚合。
sum without(host, uri)  (rate(nginx_http_requests_total{host="xxx.xxx", uri="/xxx"}[3m]))

# 计算 p95
quantile(0.95, rate(nginx_http_requests_total{host="xxx.xxx", uri="/xxx"}[3m])) by(host, uri, status)
```

其他的聚合操作符参见 [Prometheus Aggregation operators](https://prometheus.io/docs/prometheus/latest/querying/operators/#aggregation-operators)

#### 指标之间的运算

指标之间可以进行运算，默认情况下，运算以左边的指标为主，在右边的指标中寻找所有标签完全一致的指标，进行运算（也就是说右侧的指标不一定会全部都用上！这和 SQL 的 left_join 类似）：

```promql
# 4xx 占比（注意我先用 sum 聚合了数据，这样两边的标签才能够一致）
sum by(matched_host,matched_uri)  (rate(apisix_http_status{matched_host="xxx", code=~"4.."}[1m]))
/ 
sum by(matched_host,matched_uri)  (rate(apisix_http_status{matched_host="xxx"}[1m]))
```

也可以通过 `on` 来指定使用哪几个标签去右侧查找对应的值，或者通过 `ignore` 忽略某些特定的标签：

```
# 各状态码的占比，这里使用了 ignoring 忽略左侧的 code 标签。
# 同时左侧对右侧是「多对一」的关系，因此需要使用 group_left
sum by(matched_host,matched_uri, code)  (rate(apisix_http_status{matched_host="xxx"}[1m])) 
/ ignoring(code) group_left 
sum by(matched_host,matched_uri)  (rate(apisix_http_status{matched_host="xxx"}[1m]))

# 下面这个是使用 on 的语法，与上面的 promql 等价
sum by(matched_host,matched_uri, code)  (rate(apisix_http_status{matched_host="xxx"}[1m])) 
/ on(matched_host,matched_uri) group_left 
sum by(matched_host,matched_uri)  (rate(apisix_http_status{matched_host="xxx"}[1m]))
```

注意在非「一对一」的指标运算中，需要使用 `group_left` 或者 `group_right` 来指定哪一方为**多**的一方。

### 2. 个人常用 PromQL 集锦

#### 2.1 Nginx(by [nginx-lua-prometheus](https://github.com/knyar/nginx-lua-prometheus))

请求速率，按 host/uri/status 分类:

```promql
# full match uri
sum by(host,uri,status)  (rate(nginx_http_requests_total{host="xxx.xxx", uri="/xxx"}[3m])) > 0

# uri prefix
sum by(host,uri,status)  (rate(nginx_http_requests_total{host="xxx.xxx", uri=~"/prefix.+"}[3m])) > 0
```

请求用时：

```promql
# 每秒，延时低于 0.2s 的请求数
rate(nginx_http_request_duration_seconds_bucket{host="xxx.xxx",le="00.200"}[1m])
# 每秒，总的请求数
rate(nginx_http_request_duration_seconds_count{host="xxx.xxx"}[1m])

# 延时低于 0.2s 的请求数占比（多对一）
nginx_http_request_duration_seconds_bucket{host="xxx.xxx",le="00.200"}
/
nginx_http_request_duration_seconds_count{host="xxx.xxx"}

# 计算 p95（histogram_quantile 会使用 le 标签计算分位值，该标签必须存在），单位和 le 相同
histogram_quantile(0.95, sum by (le) (rate(nginx_http_request_duration_seconds_bucket{host="xxx.xxx"}[1m])))
```

#### 2.2 APISIX

请求速率，按 host/uri/k8s_namespace/apisix_service 分类:

```promql
sum by(matched_host,code,matched_uri,kubernetes_namespace,service)  (rate(apisix_http_status{matched_host="xxx.xxx", matched_uri=~"/prefix.+"}[3m])) > 0
```

请求延迟(apisix 2.6+):
```promql
# 每秒，apisix 自身的处理延迟，低于 200ms 的请求数
sum by(matched_host,code,matched_uri,kubernetes_namespace,service)  (rate(apisix_http_latency_bucket{type="request",service="<service_id>",kubernetes_namespace="staging", le="200"}[1m]))
# 每秒，请求的总数
sum by(matched_host,code,matched_uri,kubernetes_namespace,service,le)  (rate(apisix_http_latency_bucket{type="request",service="<service_id>",kubernetes_namespace="staging"}[1m]))

# 延时低于 0.2s 的请求数占比（注意 / 两边指标的 tag 必须完全一致，否则需要使用 on）
sum by(matched_host,code,matched_uri,kubernetes_namespace,service)  (rate(apisix_http_latency_bucket{type="request",service="<service_id>",kubernetes_namespace="staging", le="200"}[1m]))
/
sum by(matched_host,code,matched_uri,kubernetes_namespace,service)  (rate(apisix_http_latency_bucket{type="request",service="<service_id>",kubernetes_namespace="staging", le="+Inf"}[1m]))

# 计算 p95（histogram_quantile 会使用 le 标签计算分位值，该标签必须存在），单位和 le 相同
histogram_quantile(0.95, sum by (le, code) (rate(apisix_http_latency_bucket{type="request",service="<service_id>",kubernetes_namespace="staging"}[1m])))

# upstream 的延迟，低于 200ms 的请求数
sum by(matched_host,code,matched_uri,kubernetes_namespace,service,le)  (rate(apisix_http_latency_bucket{type="upstream",service="<service_id>", le="200"}[1m]))
# 总数
sum by(matched_host,code,matched_uri,kubernetes_namespace,service,le)  (rate(apisix_http_latency_count{type="upstream",service="<service_id>", kubernetes_namespace="prod"}[1m]))
# 计算 p95（histogram_quantile 会使用 le 标签计算分位值，该标签必须存在），单位和 le 相同
histogram_quantile(0.95, sum by (le, code) (rate(apisix_http_latency_bucket{type="upstream",service="<service_id>",kubernetes_namespace="staging"}[1m])))
```


#### 2.3 Istio


```promql
# istio http 状态指标查询
sum by (destination_version, destination_service_name, namespace, response_code) (rate(istio_requests_total{repoter="source", destination_service_name="xxx", namespace="default"}[1m]))
```


#### 2.4 Kubernetes

```promql
# CPU 使用率
sum(irate(container_cpu_usage_seconds_total{namespace="istio-system", pod=~"<deployment_name>.+"}[3m])) by (namespace, pod) / (sum(container_spec_cpu_shares{namespace="istio-system", pod=~"<deployment_name>.+"}) by(namespace, pod) / 1024)
```




