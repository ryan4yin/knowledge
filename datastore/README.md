# Datastore - 数据存储

Datastore 意即数据存储，这里用来指代所有数据存储相关的软件，目前有如下三类：

- Database: 关系数据库、文档数据库、等等
- Artifactory: 制品库，即 apt/yum/pypi/nuget/maven 等仓库
- 文件存储与分享: 云盘、NAS

## 数据库相关

1. ElasticSearch
2. Redis
3. Mongodb
4. MySQL
5. PostgreSQL

主要提供开发/测试环境的 docker-compose 部署配置。

生产环境通常都要求部署高可用、高性能的数据库集群，比如 ElasticSearch 集群、MySQL 集群等等，
目前在 Kubernetes 上通过 Operator 部署这类数据库集群，应该是最简单的方法。

## [在 Kubernetes 上部署有状态应用（主要是数据库）](/kubernetes/crd+operator%20-%20stateful%20app/README.md)

首先声明一点，**对于技术力不高的团队而言，购买各大云厂商的云上数据库，是最安全可靠、物美价廉的解决方案！**

进入正题，目前各类数据库集群在 Kubernetes 上的部署，有已经有了大量的落地案例。比如京东在 2017 年就已经使用 Vitess 搭建了他们的弹性数据库。
但是记住一点，使用 Kubernetes 部署数据库集群的前提，是你的分布式存储够快够稳定！

在硬件层面，这要求：

1. 网络：带宽高、延迟低。（家庭千兆网可以用来学习，生产环境就洗洗睡吧）
1. 硬盘：SSD 企业硬盘。

软件方案，分布式存储方案如 Ceph/GlusterFS 的部署方式，目前都还是以虚拟机部署为主。
虽然说目前已经有 Rook 这类分布式存储编排工具，但是还不够成熟，不够稳定，落地案例比较少。
数据就是生命，不得不慎重！

>关于使用 Kubernetes 部署分布式存储，可以参考我的笔记 [distributed storage](/kubernetes/distributed-storage/README.md)

好，现在假设我们软硬件条件齐全（或者开发/测试环境，数据无所谓），就可以考虑通过 Kubernetes 部署数据库了。
部署方法参见各子文件夹中的文档。。。


## 自建数据库的各种常见问题

自建数据库，不论是 ES/Mongo/Redis 还是 MySQL/PostgreSQL，最常见的问题，也是我到现在都没搞清楚的问题，有两个：

1. 连接拒绝(Connection Refused): Redis 容器方式启动，在连接数达到 1000 左右时，就开始出现大量连接拒绝，排查不到问题。
2. 响应速度慢，连接超时: ES/Redis 开机时间一长（短则一天，长则两三个月），速度就越来越慢。

因为我的主要工作并不是维护数据库，所以上述问题到现在都没找到好的解决方法。

个人猜测，首先和本地测试环境，服务器负载超量分配过多，负载过重有很大关系。
其中最大的瓶颈估计是磁盘，本来就是垃圾硬盘，还做了一层虚拟化+LVM。
其次是 Linux 虚拟机的 ulimit/sysctl 参数设置可能不太对，但是这两个是专门拷贝的 rancher 文档提供的内核调优配置，不应该会导致问题。。。

待解决
