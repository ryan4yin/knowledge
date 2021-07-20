## 「重打标签」配置 - relabel_config/metric_relabel_config

>[relabel_config - prometheus docs](https://prometheus.io/docs/prometheus/latest/configuration/configuration/#relabel_config)

「重打标签」是 Prometheus 处理指标标签的主要手段。在 serviceMonitor/podMonitor 及 prometheus.yml 中都可以看到它的存在。
虽然名为「重打标签」，但实际上对「target」及「标签(label)」的增删改，都是可以通过它来进行的。

relabel_config: 在指标被采集前进行处理，假入某个标签被 drop，那么它根本不会被采集。
metric_relabel_config: 在指标被采集完成，还没有入库前，对指标进行处理。

根据「及早处理」的原则，应该尽量使用 relabel_config，不得已时才使用 metric_relabel_config。

### 详细语法



## PromQL



### 个人常用 PromQL 集锦

#### 1. Nginx(by [nginx-lua-prometheus](https://github.com/knyar/nginx-lua-prometheus))

请求速率，按 host/uri/status 分类:

```promql
# full match uri
sum by(host,uri,status)  (rate(nginx_http_requests_total{host="xxx.xxx", uri="/xxx"}[3m]))

# uri prefix
sum by(host,uri,status)  (rate(nginx_http_requests_total{host="xxx.xxx", uri=~"/prefix.+"}[3m]))
```

请求用时：

```promql
# 延时低于 0.2s 的请求数
nginx_http_request_duration_seconds_bucket{host="xxx.xxx",le="00.200"}
# 总的请求数
nginx_http_request_duration_seconds_count{host="xxx.xxx"}

# 延时超过 0.2s 的请求数占比

```

#### 2. APISIX

请求速率，按 host/uri/k8s_namespace/apisix_service 分类:

```promql
sum by(matched_host,code,matched_uri,kubernetes_namespace,service)  (rate(apisix_http_status{matched_host="xxx.xxx", matched_uri=~"/prefix.+"}[3m]))
```

请求延迟(apisix 2.6+):
```promql
# apisix 自身的处理延迟，低于 200ms 的请求数
apisix_http_latency_bucket{type="request",service="<service_id>",kubernetes_namespace="prod", le="200"}
# 总数
apisix_http_latency_count{type="request",service="<service_id>", kubernetes_namespace="prod"}

# upstream 的延迟，低于 200ms 的请求数
apisix_http_latency_bucket{type="upstream",service="<service_id>", le="200"}
# 总数
apisix_http_latency_count{type="upstream",service="<service_id>", kubernetes_namespace="prod"}
```


#### 3. Istio


```promql
# istio http 状态指标查询
sum by (destination_version, destination_service_name, namespace, response_code) (rate(istio_requests_total{destination_service_name="xxx", namespace="default"}[1m]))
```


#### 4. Kubernetes

```promql
# CPU 使用率
sum(irate(container_cpu_usage_seconds_total{namespace="istio-system", pod=~"<deployment_name>.+"}[3m])) by (namespace, pod) / (sum(container_spec_cpu_shares{namespace="istio-system", pod=~"<deployment_name>.+"}) by(namespace, pod) / 1024)
```




