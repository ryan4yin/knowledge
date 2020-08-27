# [Jaeger](https://github.com/jaegertracing/jaeger/)

## 一、部署

docker-compose 部署：

1. 使用 casandra 做存储：https://github.com/jaegertracing/jaeger/tree/master/docker-compose
1. 使用 elasticsearch 做存储：https://github.com/jaegertracing/jaeger/tree/master/crossdock
   1. 此文件夹中包含一个 opentelemetry 版的 docker-compose.yaml，在 9411 端口监听 zipkin 协议数据。


## 二、API

参见: https://www.jaegertracing.io/docs/1.18/apis/

常用的两个 HTTP 数据上报 API（直接上报给 `jaeger-collector`）：

1. ZipKin 格式协议: `http://<jaeger-collector>:9411/api/v2/spans`
1. Jaeger 原生协议(Thrift over HTTP): `http://<jaeger-collector>:14268/api/traces`
2. grpc 协议(Protobuf via gRPC)：14250 端口，这是 jaeger-agent 上报数据到 `jaeger-collector` 的推荐方式

两个 UDP 数据上报 API（上报给 `jaeger-agent`）: 

1. 6831 端口	UDP	agent	accept jaeger.thrift over compact thrift protocol
   1. 大多数 jaeger 客户端都使用这种协议上报数据，比如 python
2. 6832 端口	UDP	agent	accept jaeger.thrift over binary thrift protocol
   1. 少量不支持 compact 编码的客户端，会使用这个协议上报数据。

UI 查询界面：`http://<jaeger-query>:16686`


# 三、架构

参见：https://www.jaegertracing.io/docs/1.18/architecture/

简单介绍：

1. jaeger-agent: 监听通过 UDP 上报的 spans，然后批量提交给 jaeger-collector.
   1. 建议每台主机上安装一个 jaeger-agent，最简单的方式是使用 kubernetes daemonset。
2. jaeger-collector: 接收 jaeger-agent 上报的 spans，然后通过一个 pipeline 对 spans 进行验证、索引、转换，最后保存它们。
   1. 客户端也可以直接通过 http 协议将 span 上报给 jaeger-collector.
   2. 后端存储目前支持 cassandra、elasticsearch 和 kafka
3. jaeger-query: 提供前端查询页面及 API，可以使用它方便地查询浏览链路追踪信息。
