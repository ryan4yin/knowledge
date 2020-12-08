# 超时与重试

在使用 python `requests` 请求某些 API 时，偶尔会发现它报错：

```
urllib3.exceptions.MaxRetryError: HTTPConnectionPool(host='xxx.com', port=80): Max retries exceeded with url: /swagger/v1/swagger.json (Caused by NewConnectionError('<urllib3.connection.HTTPConnection object at 0x7f09b265b3d0>: Failed to establish a new connection: [Errno 111] Connection refused'))
```

提示 `MaxRetryError`，查看 requests 文档，相关描述如下：

```
max_retries: Note, this applies only to failed DNS lookups, socket connections and connection timeouts, never to requests where data has made it to the server. By default, Requests does not retry failed connections.
```

**只有在 DNS 解析失败、socket 连接失败以及连接超时三种情况下，requests 才会重试一个请求。**
如果数据已经被发送到服务端，requests 绝对不会重试。默认情况下，requests 也不会重试一个失败的连接。

## 幂等性

requests 为何不重试失败的连接？主要是因为，requests 不知道服务端是否已经收到了数据。
如果服务端收到了数据，而请求又不是幂等的，requests 擅自重试这个请求，就很可能导致严重的后果，比如付一次款得到两份肯德基。

说一个请求幂等，是指这个请求不论是发生一次，还是发生多次，对结果都没有任何影响。

假设一个请求是幂等的，那这个请求就能设置很灵活的重试策略。

灵活的重试策略，可以提高应用的容错能力。尤其是对于复杂的微服务间调用而言。

### 什么情况下可以重试一个「非幂等请求」

**对于非幂等请求，只有在 DNS 解析失败、socket 连接失败（第四层连接失败）以及连接超时（第四层连接超时）三种情况下，才可以重试。**

要注意的是「连接超时」!=「请求超时」！「连接超时」是 TCP 连接超时无法建立，而请求超时是 TCP 连接已经建立成功了，数据发送到服务器了但是没得到响应。

总而言之，对非幂等请求，只有在确定服务端没有收到数据的情况下，才允许重试。

## Istio/Envoy 重试机制

Istio/Envoy 提供功能非常丰富的 http/grpc 重试机制，可以设置各种各样的重试触发条件。
但是在 API 非幂等的情况下，贸然使用 Istio/Envoy 的重试功能，会导致非常严重的问题！！！

所以一定要搞清楚 Istio/Envoy 的各类重试条件的具体意义，再去使用！

就比如 Istio 官方提供的 [HTTPRetry 示例](https://istio.io/latest/docs/reference/config/networking/virtual-service/#HTTPRetry)：

```yaml
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: ratings-route
spec:
  hosts:
  - ratings.prod.svc.cluster.local
  http:
  - route:
    - destination:
        host: ratings.prod.svc.cluster.local
        subset: v1
    retries:
      attempts: 3  # 重试次数
      perTryTimeout: 2s  # 重试间隔
      # 触发重试的条件
      retryOn: gateway-error,connect-failure,refused-stream
    timeout: 10s
```

一旦 retry 机制被触发，Envoy 就会以两秒的间隔进行重试，直到请求成功，或者达到重试上限 3 次。

yaml 中的三个重试触发条件，详细说明如下：

1. gateway-error: only retry requests that result in a 502, 503, or 504.
   1. 502 Bad Gateway，上游返回给网关无效的信息。
   1. 503 服务目前不可用
   2. 504 网关超时，后端无响应或者后端 IP 不存在，会导致报这个错。
2. connect-failure: 连接失败
3. refused-stream: 上游服务器重置了连接

但是实际测试发现，**任一请求的超时时间 = min(`http[0].retries.perTryTimeout`, `http[0].timeout`)**！（测试版本: 1.6.8）
Istio 文档里没有找到相关描述信息！


因为请求超时，网关报错 504，触发了 gateway-error 这个重试条件。

Istio 貌似没有能力区分是四层连接超时或失败，还是四层连接成功了但七层请求超时或失败。也没有「只重试 GET 请求」这种功能。

### 画外

不论是客户端 requests，还是网关 Envoy，又或者手机APP/Web前端，任何重试操作都应该遵循这里讨论出来的原则：

1. 只有幂等接口，可以随意重试。
2. 对于非幂等请求，只有在 DNS 解析失败、socket 连接失败（第四层连接失败）以及连接超时（第四层连接超时）三种情况下，才可以重试。

比如 APP 提交订单失败时，就不应该弹出「重试」的按钮。
如果非要「重试」，则必须将订单提交接口设计成幂等的。否则就可能导致生成多个订单的问题。
