# Proxy 协议

[The PROXY protocol - Versions 1 & 2](http://www.haproxy.org/download/1.8/doc/proxy-protocol.txt) 是
HAProxy 提出的一个专用代理协议。这样上游的代理程序如 Nginx，就能获得客户端的真实 IP 地址和端口，这样
Nginx 就能将这个源 IP 地址通过 HTTP 的 `X-Forwarded-For` 将源 IP 发送给对应的业务程序，业务程序就能
使用这个 IP 进行一些操作。

以 AWS NLB 为例，假设我们启用了 PROXY 协议，nginx 中各变量对应的内容如下：

- `$proxy_protocol_addr` 和 `$proxy_protocol_port` 分别表示的是原始客户端的 IP 地址和端口号。
- `$remote_addr` 和 `$remote_port` 表示的是下游代理程序的 IP 地址和端口。
