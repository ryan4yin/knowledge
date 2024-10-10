# AWS CloudWatch

AWS 的日志、监控、事件等服务都是通过 CloudWatch 来实现的。

## CloudWatch Logs

CloudWatch Logs 是 AWS 提供的日志服务，可以将日志数据存储在 CloudWatch Logs 中，然后通过 CloudWatch
Logs Insights 来查询日志数据。

> 注意：Log Groups 中仅能做简单的数据查询过滤，如果需要更复杂的查询，必须使用 CloudWatch Logs
> Insights。

日志查询举例：

> https://docs.aws.amazon.com/AmazonCloudWatch/latest/logs/AnalyzingLogData.html

```
# 查询 kube-apiserver-audit 日志中所有删除 xxx 名字空间中 service 的记录
filter @logStream like 'kube-apiserver-audit-'
| filter @message like /"requestURI":"\/api\/v1\/namespaces\/xxx\/services\// and @message like /"verb":"delete"/
| fields @timestamp, @message
```
