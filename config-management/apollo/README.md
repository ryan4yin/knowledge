# [Apollo](https://github.com/ctripcorp/apollo)

>此文档基于 1.7.1 版本编写

Apollo 是携程开源的一个分布式配置中心，在国内非常流行。
它功能强大，支持配置的继承，也有提供 API 方便自动化配置。缺点是权限管理比较弱，也不支持信息加密，不适合直接存储敏感信息。


## 一、部署流程

个人推荐两种部署方式：docker-compose 和 kubernetes helm.
下面是详细的部署说明。

注意事项：Apollo 是 Java 应用，启动大概需要 5-10 分钟。请耐心等待...

### 1. Docker-Compose 部署

>推荐用于本地开发测试环境

官方只提供了 Docker 命令部署，此文件夹下的 docker-compose.yml 来自同事的总结哈哈。

需要注意的有：

1. configservice 和 adminservice 及对应的 apolloconfigdb 数据库，是每个环境一套，dev/fat/uat 三个环境就需要三套
   1. 数据库可以通过后缀区分环境：ApolloConfigDB_DEV / ApolloConfigDB_FAT. 简单起见，测试环境可以使用同一个 mysql.
   2. `docker-compose.yml` 中只添加了 dev/fat/uat 三个环境。我们的 pro 是线上生产专用的环境。
2. configservice 和 adminservice 都是通过 `ServerConfig` 表 `eureka.service.url` 的属性来访问注册中心(eruka) 的。
   1. 而 Apollo 官方给的默认值是 `http://localhost:8080/eureka/`，使用 docker 网络时必须要手动修改 `localhost` 为 configservice 的名称（因为 eruka 和 configservice 在同一个容器中）。
3. 不管有多少个环境，portal 都只需要一个。
   1. portal 支持通过环境变量配置所有的环境(ENV)及对应的 META Server 地址，不需要手动修改数据库。
4. portal 的 `organizations`（部门列表）目前只能通过 `apolloportaldb.sql` 末尾的 INSERT 语句设置。不提供 API 进行修改。
5. `apolloportaldb.sql` 末尾的 `consumer.token.salt` 需要自行设置随机值！使用默认值安全性太低。
6. portal 的默认账号在 `apolloportaldb.sql` 中被插入 `Users` 表，默认账号密码`apollo/admin`。密码可在登录后修改。


### Kubernetes + Helm 部署

>推荐用于生产环境

Apollo 分布式配置中心，最简单的部署方式是使用 Kubernetes + Helm.
流程如下：

1. 创建数据库：Apollo服务端共需要两个数据库：ApolloPortalDB 和 ApolloConfigDB
   1. 详见：[Apollo 分布式部署指南-创建数据库](https://github.com/ctripcorp/apollo/wiki/%E5%88%86%E5%B8%83%E5%BC%8F%E9%83%A8%E7%BD%B2%E6%8C%87%E5%8D%97#21-%E5%88%9B%E5%BB%BA%E6%95%B0%E6%8D%AE%E5%BA%93)
2. 通过 Helm 进行部署：
   1. 部署 apollo-configservice 和 apollo-adminservice，每一个配置环境都需要独立部署这两个服务。
   2. 部署 apollo-portal，这个是 Apollo 的 UI/API 面板，所有环境公用。
   3. 详见[Apollo 分布式部署指南-kubernetes部署](https://github.com/ctripcorp/apollo/wiki/%E5%88%86%E5%B8%83%E5%BC%8F%E9%83%A8%E7%BD%B2%E6%8C%87%E5%8D%97#24-kubernetes%E9%83%A8%E7%BD%B2)

部署完成后就能直接用浏览器登入 portal 面板了，默认账号 apollo 密码 admin，helm 配置中没找到自定义密码的参数。

### 注意事项

1. 目前 Portal 貌似是使用服务端 Session，Cookie 只包含 SessionID，Session 具体的内容保存在服务端内存中。
   这导致 Portal 本身成了一个有状态应用，Session 不能在 Pod 之间共享！因此多副本情况下必须配置基于 ClientIP 的会话亲和！使用 Istio/Ingress 时还需要在 Istio/Ingress 配置中配上基于 ClientIP 的路由策略。
1. 如果 MySQL 数据库地址使用 IP，就不能使用 ExternalService 类型的 Service!，否则 Apollo 将无法访问数据库！
1. Portal 数据库中的 ENV，helm 配置中的 ENV，以及通过开发 API 访问 Portal 时需要设定的 ENV 这三个东西，必须要一致！
   1. 否则会出现报错信息：无法找到对应的 meta server.

## 二、使用 Apollo

### 1. 添加配置

Apollo 支持通过 RESTful API 自动添加修改配置，也可以通过 Portal 面板手动添加修改配置。

手动添加的流程略过，下面介绍一下通过 RESTful API 自动化添加修改配置的方法。
它很适合用于搭建与全量更新测试环境的 Apollo 配置。一套微服务体系成百上千的配置项，手动通过 Web UI 进行全量更新基本上是不可能的。

>RESTful API 的官方文档：[Apollo开放平台](https://github.com/ctripcorp/apollo/wiki/Apollo%E5%BC%80%E6%94%BE%E5%B9%B3%E5%8F%B0)

使用 Apollo Open API 需要先通过 Portal 面板创建一个 APP 并给予权限，这个流程也可以使用脚本直接调 Portal API 实现.

通过 API 重新灌入 Apollo 配置的流程：

1. 清空所有表（所有旧配置），但是 `ServerConfig`/`Users`/`Authorities` 这三个系统配置表除外。
2. 使用管理员账号模拟登录 Apollo Portal，进行如下操作
   1. 创建所有 APP
   2. 创建一个第三方应用 A（获取 token）
   3. 赋予 token 操作所有 app 的权限
3. 使用上一步获得的 token 调用 Apollo Open API，进行如下操作：
   1. 在所有 APP 中创建 namespace 并注入配置数据
   2. 如果有用到集群，创建对应的集群

### 2. 微服务读取配置 

Apollo 为微服务提供 HTTP API 来读取与更新配置，并且支持以长轮询的方式动态更新微服务的配置。

官方及社区有提供各语言的 SDK，请自行在 Apollo WiKi 上查看。
