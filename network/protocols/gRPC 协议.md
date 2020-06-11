# [gRPC over HTTP2](https://github.com/grpc/grpc/blob/master/doc/PROTOCOL-HTTP2.md)

>A high-performance, open source universal RPC framework

gRPC （默认情况下）使用 HTTP/2 进行数据的传输，使用 protobuf3 进行 RPC 数据的序列化以及 RPC 接口的定义。

gRPC 的 Request 只使用 HTTP 的 POST 方法；
另外 gRPC Response 的 HTTP 状态码只用于表示网络状态，固定为 200，gRPC 自己定义了一个 `grpc-status` 来表达 API 详细的调用结果。
