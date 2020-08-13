# [Jaeger](https://github.com/jaegertracing/jaeger/)

## 一、部署

docker-compose 部署：

1. 使用 casandra 做存储：https://github.com/jaegertracing/jaeger/tree/master/docker-compose
1. 使用 elasticsearch 做存储：https://github.com/jaegertracing/jaeger/tree/master/crossdock
   1. 此文件夹中包含一个 opentelemetry 版的 docker-compose.yaml，在 9411 端口监听 zipkin 协议数据。
