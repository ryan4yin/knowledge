# Logstash 数据管道

## Logstash API 记录

> 参考官方文档：https://www.elastic.co/guide/en/logstash/current/node-info-api.html

管道信息：

```shell
curl -XGET 'http://localhost:9600/_node/pipelines?pretty'
```

管道状态：

```shell
curl -XGET 'http://localhost:9600/_node/stats/pipelines?pretty'
```

详细的还是看官方文档吧，或者启动 kibana 的监控功能，那个更方便。（注意监控索引会占用大量存储空间）

## Logstash 启动慢的问题

我这边测试，启动单个 pipeline 的 logstash，在服务器上需要大概一分钟。然后现在公司有近 40 个
pipelines，logstash 7.4.2 启动后，编译这 40 个 pipelines 需要 27 分钟...

我一度怀疑 logstash 根本就不是这么用的，不应该使用太多的 pipelines...

在 logstash issues 里搜 `slow`，可以看到一堆的
[相关 issues](https://github.com/elastic/logstash/issues?q=slow)，报告的编译时间最长的一个小时都没编
译完成...

issues 中有人提交了 PR 实现了相当程度的启动速度优化，其中最牛批的是
[JEE: nix global compiler lock by normalizing to Dataset interface #12047](https://github.com/elastic/logstash/pull/12060)，
直接把一小时多的编译时间优化到了几十秒。

但是貌似要升级到 7.9.0+ 才能用上这个优化。
