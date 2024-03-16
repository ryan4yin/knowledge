# APISIX API 介绍

APISIX 抽象出了几个简单的资源来控制流量的处理和转发，其中最重要的是如下三个：

```mermaid
graph LR
    Route --> Service --> Upstream
```

上图描述了请求在这三个资源之间的流动关系，按请求经过的顺序描述如下：

- Route
  - 通过一系列规则（hosts/uris 等）来匹配一个请求，匹配成功的请求交由 Service 进行后续处理
- Service
  - 加载并执行一系列插件（监控、限流限并发、rewrite 等），然后将请求交给指定的 Upstream
- Upstream
  - 将流量转发给一组具体的后端实例。Upstream 提供流量切分、负载均衡、服务发现、健康检查、请求重试等
    功能。

## 配置结构及使用规范介绍

### Route

Route 本身可以设置很多参数，不过我们只使用 Route 处理 host 和 URI 的 match，匹配成功的请求将会由指定
的 Service 进行后续处理，这样维护起来结构会清晰很多。

> 多个 Route 可以绑定同一个 Service，Service 实际上是为了复用 Route 的 plugins 配置而被设计出来的

Route 的完整配置结构：

```yaml
{
  "id": "1", # id
  "uris": ["/a", "/b"], # 一组 URL 路径
  "methods": ["GET", "POST"], # 可以填多个方法
  "hosts": ["a.com", "b.com"], # 一组 host 域名
  "priority": 0, # apisix 支持多种匹配方式，可能会在一次匹配中同时匹配到多条路由，此时优先级高的优先匹配中
  "desc": "hello world",
  "remote_addrs": ["127.0.0.1", "192.0.0.0/8"], # 一组客户端请求 IP 地址
  "vars": [["http_user", "==", "ios"]], # 由一个或多个 [var, operator, val] 元素组成的列表
  "service_id": "hello", # upstream 对象在 etcd 中的 id ，建议使用此值
  "filter_func": "", # 用户自定义的过滤函数，非必填
}
```

比如，将 `aa.hello.com` 和 `bb.hello.com` 的请求都交给 `hello` 这个 service 进行后续处理的命令如下：

```shell
# 请将 X-API-KEY: xxx 替换为你的 API-KEY
curl -X PUT http://localhost:9180/apisix/admin/routes/aa-hello -H 'X-API-KEY: xxx' --data-raw \
'{
  "hosts": [" aa.hello.com", " bb.hello.com"],
  "uris": ["/*"],
  "service_id": "hello"
}'
```

注意这里的 `uris` 的值，目前有两种格式：

- 完全匹配: `/a` `/b` 这种不以 `*` 结尾的，都是完全匹配！别搞错了
- 前缀匹配: `/*` `/a*` 这种，才是前缀匹配，也应该是我们用的最多的

### Service

Service 包含两部分配置：`plugins` + `upstream_id`

一个添加了 prometheus 监控、限流限并发插件的 Service 配置如下：

```yaml
{
  "id": "hello",
  "upstream_id": "hello-v1", # 引用了一个 Upstream
  "plugins":
    {
      "prometheus": {},
      "limit-conn":
        {
          "key": "server_addr",
          "default_conn_delay": 0.1,
          "burst": 0,
          "rejected_code": 529,
          "conn": 2000,
        },
      "limit-req": { "key": "server_addr", "rate": 3000, "burst": 6000, "rejected_code": 529 },
    },
}
```

它对应的控制面 API 是 `http://localhost:9180/apisix/admin/services/<id>`，可通过 PUT 方法进行修改，
通过 GET 方法进行查询。

### Upstream

Service 将请求提供给 Upstream 后，Upstream 按照自己的配置规则，在多个后端实例 `node` 之间进行请求的
负载均衡

> 如果是在 Kubernetes 中，直接使用 Kubernetes Service 做为 node，就不需要用到 APISIX Upstream 中的健
> 康检查逻辑，但代价是多走了一层 kube-proxy 逻辑。因此 APISIX-Ingress-Controller 默认的策略是自己去
> Watch Kubernetes Service 的 Endpoints 变动，将所有 Endpoints 注册到 APISIX 的 Nodes 中。

一个示例配置如下（使用 weight 做了流量切分）

```yaml
{
  "id": "hello-v1", # id
  "retries": 1, # 请求重试次数
  "timeout": { "connect": 1, "send": 1, "read": 1 }, # 设置连接、发送消息、接收消息的超时时间
  "type": "roundrobin",
  "nodes": [
      {
        "priority": 0,
        "port": 80,
        "weight": 99,
        # host 这里也可以写域名，会根据 TTL 刷新 DNS，但是只会选择 DNS 解析出的第一个 IP，无法实现负载均衡！
        "host": "11.22.33.10", # 实例 1
      },
      {
        "priority": 0,
        "port": 80,
        "weight": 1,
        "host": "11.22.33.37", # 实例 2
      },
    ],
  "desc": "hello world", # upstream 描述
  "scheme": "http", # 跟上游通信时使用的 scheme，默认是 `http`
}
```

它对应的控制面 API 是 `http://localhost:9180/apisix/admin/upstreams/<id>`，可通过 PUT 方法进行修改，
通过 GET 方法进行查询。

另一个选择是使用 APISIX 的 DNS 服务发现功能，此功能依次按 `SRV -> A -> AAAA -> CNAME` 的顺序进行 DNS
查询，并将查到的所有结果注册为 upstream 的 nodes. 因为 Kubernetes Service 是提供 SRV 记录的，所以基
于 DNS 的服务发现也适用于 Kubernetes.

> 基于 DNS 的服务发现是基于 TTL 去定期更新，而 APISIX-Ingress-Controller 是通过 Watch Kubernetes API
> 即时动态更新，Watch 机制更新会更及时些，因此更适合 Kubernetes 场景。

> 详见 [基于 DNS 的服务发现 - APISIX](https://apisix.apache.org/zh/docs/apisix/discovery/dns/)

```yaml
{
  "id": "1", # id
  "retries": 1, # 请求重试次数
  "timeout": { "connect": 5, "send": 5, "read": 5 }, # 设置连接、发送消息、接收消息的超时时间
  "discovery_type": "dns", # 使用 DNS 做服务发现
  "service_name": "hello-v1:8080", # DNS 域名+端口号
  "type": "roundrobin", # 负载均衡算法
  "checks":
    {
      "active":
        {
          "http_path": "/status",
          "healthy": { "interval": 1, "successes": 1 },
          "unhealthy": { "interval": 1, "http_failures": 1 },
        },
    },
  "hash_on": "",
  "key": "",
  "desc": "hello world", # upstream 描述
  "scheme": "http", # 跟上游通信时使用的 scheme，['http', 'https', 'grpc', 'grpcs'] , 默认是 `http`
}
```

### 插件的热加载

APISIX 的插件是热加载的，不管你是新增、删除还是修改插件，都不需要重启服务。

只需要通过 admin API 发送一个 HTTP 请求即可：

```shell
curl -X PUT http://127.0.0.1:9080/apisix/admin/plugins/reload -H 'X-API-KEY: xxx'
```

## 其他资源介绍

### GlobalRule - 全局生效的插件配置

> https://apisix.apache.org/zh/docs/apisix/terminology/global-rule/

设置全局运行的插件。这一类插件在所有路由级别的插件之前优先运行。

### Script - 自定义 lua 脚本

> https://apisix.apache.org/zh/docs/apisix/terminology/script/

可以在 Route 中使用 Script 直接提供自定义 lua 脚本，替代掉 Plugin 配置。

需要注意的是 Route 跟 Plugin 互斥，如果启用了 Script，Route/Service 中配置的所有 Plugin 都将被忽略。

示例：

```json
{
    ...
    "script": "local _M = {} \n function _M.access(api_ctx) \n ngx.log(ngx.INFO,\"hit access phase\") \n end \nreturn _M"
}
```
