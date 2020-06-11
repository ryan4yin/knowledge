# [gRPC](https://github.com/grpc)

>A high-performance, open source universal RPC framework

gRPC （默认情况下）使用 HTTP/2 进行数据的传输，使用 protobuf3 进行 RPC 数据的序列化以及 RPC 接口的定义。


## gRPC 状态码

- [Status codes and their use in gRPC](https://github.com/grpc/grpc/blob/master/doc/statuscodes.md)

## [gRPC over HTTP2](https://github.com/grpc/grpc/blob/master/doc/PROTOCOL-HTTP2.md)

gRPC 的 Request 只使用 HTTP 的 POST 方法；
另外 gRPC Response 的 HTTP 状态码只用于表示网络状态，标准的 gRPC 服务端应该永远返回 200，gRPC 自己定义了一个 `grpc-status` 来表达 API 详细的调用结果。

如果 HTTP 响应中包含 `grpc-status`，客户端一定会以它为 gRPC 请求的结果，HTTP 状态码会被客户端忽略。

如果响应中不包含 `grpc-status`（比如请求了一个 HTTP REST API），gRPC 客户端会通过如下映射关系，通过 HTTP 状态码得到 gRPC 的结果：

| HTTP Status Code           | gRPC Status Code   |
|----------------------------|--------------------|
| 400 Bad Request            | INTERNAL           |
| 401 Unauthorized           | UNAUTHENTICATED    |
| 403 Forbidden              | PERMISSION\_DENIED |
| 404 Not Found              | UNIMPLEMENTED      |
| 429 Too Many Requests      | UNAVAILABLE        |
| 502 Bad Gateway            | UNAVAILABLE        |
| 503 Service Unavailable    | UNAVAILABLE        |
| 504 Gateway Timeout        | UNAVAILABLE        |
| _All other codes_          | UNKNOWN            |


## 参考

- [HTTP to gRPC Status Code Mapping](https://github.com/grpc/grpc/blob/master/doc/http-grpc-status-mapping.md)
