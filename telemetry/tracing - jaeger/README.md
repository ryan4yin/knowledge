# [Jaeger](https://github.com/jaegertracing/jaeger/)

Jaeger 是云原生社区最流行的开源链路追踪工具。

> 开源链路追踪工具中，目前只有 Jaeger 和 OpenZipkin。商业化方案还有 Lightstep/Datadog/NewRelic 可
> 选。

## 一、部署

### 1. docker-compose 部署（单机）

1. 使用 casandra 做存储：https://github.com/jaegertracing/jaeger/tree/master/docker-compose
1. 使用 elasticsearch 做存储：https://github.com/jaegertracing/jaeger/tree/master/crossdock
   1. 此文件夹中包含一个 opentelemetry 版的 docker-compose.yaml，在 9411 端口监听 zipkin 协议数据。

### 2. kubernetes operator 部署（推荐）

使用 helm 安装 jaeger operator:

```shell
# 添加　chart 仓库
helm repo add jaegertracing https://jaegertracing.github.io/helm-charts
# 查看历史版本
helm search repo jaegertracing/jaeger-operator -l | head
# 下载并解压 chart，目的是方便 gitops 版本管理
helm pull jaegertracing/jaeger-operator  --untar --version 2.15.1

# 查看生成出的 kubernetes yaml 内容
helm template ./jaeger-operator --namespace tracing \
  -f jaeger-operator-values.yaml > jaeger-operator-all.yaml

# 安装或更新
kubectl create namespace tracing
helm upgrade --install jaeger-operator --namespace tracing \
  -f jaeger-operator-values.yaml ./jaeger-operator
```

jaeger-operator 自身的部署参数很少，基本没什么可定制的。这是因为它只是一个 jager 管理器，真正的
jaeger 还需要在后面创建，请看下一节。

#### 通过 jaeger operator 部署 jaeger

[jaeger operator](https://github.com/jaegertracing/jaeger-operator) 只是一个单纯的 jaeger 管理器。我
们还需要部署 operator 定义的资源，operator 才会去部署真正的 jaeger。

可以使用如下 yaml 配置进行测试，它告诉 operator 部署一个 all in one 的 jaeger:

```yaml
apiVersion: jaegertracing.io/v1
kind: Jaeger
metadata:
  name: jaeger-allinone
```

所有的 jaeger 属性，都可以通过 `Jaeger.jaegertracing.io/v1` 这个 CR (自定义资源)进行配置。

完整的 yaml 配置：

```yaml
apiVersion: jaegertracing.io/v1
kind: Jaeger
metadata:
  name: my-jaeger
spec:
  strategy: allInOne # 生产环境请改成 production/streaming
  allInOne:
    image: jaegertracing/all-in-one:latest
    options: # 所有与存储无关的命令行参数
      log-level: debug # 将被转换成 --log-level=debug
  storage:
    type: memory # 后端存储，生产环境需要改成 Cassandra, Elasticsearch, Kafka
    options: # 所有存储相关的命令行参数
      memory:
        max-traces: 100000
  ingress: # 网关
    enabled: false
  agent:
    strategy: DaemonSet
  annotations: # 所有 jaeger deployment 统一添加这个注解
    scheduler.alpha.kubernetes.io/critical-pod: ""
```

其他参数请自行参阅文档。建议使用 ingress/nodeport 暴露出 jaeger-query 的 Web UI。

部署命令：

```shell
# 注意要部署在 tracing 名字空间，默认情况下 jaeger-operator 只在它自己的名字空间里工作
kubectl apply -f jaeger-cr.yaml --namespace tracing
```

## 二、API

参见: https://www.jaegertracing.io/docs/1.18/apis/

常用的两个 HTTP 数据上报 API（直接上报给 `jaeger-collector`）：

1. ZipKin 格式协议: `http://<jaeger-collector>:9411/api/v2/spans`
1. Jaeger 原生协议(Thrift over HTTP): `http://<jaeger-collector>:14268/api/traces`
1. grpc 协议(Protobuf via gRPC)：14250 端口，这是 jaeger-agent 上报数据到 `jaeger-collector` 的推荐
   方式

两个 UDP 数据上报 API（上报给 `jaeger-agent`）:

1. 5775 端口： UDP agent accept zipkin.thrift over compact thrift protocol
   1. zipkin 协议
2. 6831 端口： UDP agent accept jaeger.thrift over compact thrift protocol
   1. 大多数 jaeger 客户端都使用这种协议上报数据，比如 python
3. 6832 端口： UDP agent accept jaeger.thrift over binary thrift protocol
   1. 少量不支持 compact 编码的客户端，会使用这个协议上报数据。

UI 查询界面：`http://<jaeger-query>:16686`

# 三、架构

参见：https://www.jaegertracing.io/docs/1.18/architecture/

简单介绍：

1. jaeger-agent: 监听通过 UDP 上报的 spans，然后批量提交给 jaeger-collector.
   1. 建议每台主机上安装一个 jaeger-agent，最简单的方式是使用 kubernetes daemonset。
2. jaeger-collector: 接收 jaeger-agent 上报的 spans，然后通过一个 pipeline 对 spans 进行验证、索引、
   转换，最后保存它们。
   1. 客户端也可以直接通过 http 协议将 span 上报给 jaeger-collector.
   2. 后端存储目前支持 cassandra、elasticsearch 和 kafka
3. jaeger-query: 提供前端查询页面及 API，可以使用它方便地查询浏览链路追踪信息。
