# [Jaeger](https://github.com/jaegertracing/jaeger/)

## 一、部署

docker-compose 部署：

1. 使用 casandra 做存储：https://github.com/jaegertracing/jaeger/tree/master/docker-compose
1. 使用 elasticsearch 做存储：https://github.com/jaegertracing/jaeger/tree/master/crossdock
   1. 此文件夹中包含一个 opentelemetry 版的 docker-compose.yaml，在 9411 端口监听 zipkin 协议数据。


## 二、API

参见: https://www.jaegertracing.io/docs/1.18/apis/

常用的两个数据上报 API：

1. ZipKin 格式协议: `http://<jaeger-collector>:9411/api/v2/spans`
1. Jaeger 原生协议(Thrift over HTTP): `http://<jaeger-collector>:14268/api/traces`

UI 查询界面：`http://<jaeger-agent>:16686`
