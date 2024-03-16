# ALB 请求日志分析

这里描述的查询方法，适合每天日志量不多的场景，通过按天进行分区查询，可提升查询效率。

但是如果每天的日志量都超过 100G，那这种做法就不太可行了，用 Athena 查起来会比较费钱。

估算下的话，ALB 每 1000 个平均 QPS，每天日志量就将多大约 27Gi，这样算的话，这种查询方法适合平均 4000
QPS 以内，而且查询不频繁的 ALB 日志。

如果日志量更大，可能更适合先使用 Glue 对日志进行转换，详见
[AWS 服务日志转换](./AWS%20%E6%9C%8D%E5%8A%A1%E6%97%A5%E5%BF%97%E8%BD%AC%E6%8D%A2.md)

## 创建 Athena 查询表

这里使用了 Athena 分区投影（Partition Projection）功能自动管理分区，通过分区提升查询性能，同时自动管
理分区避免了手工维护分区的成本。

SQL 如下，注意修改表名 `xxx_alb_logs_partitioned` 及 `s3` 地址：

```sql
CREATE EXTERNAL TABLE IF NOT EXISTS xxx_alb_logs_partitioned (
  type string,
  time string,
  elb string,
  client_ip string,
  client_port int,
  target_ip string,
  target_port int,
  request_processing_time double,
  target_processing_time double,
  response_processing_time double,
  elb_status_code int,
  target_status_code string,
  received_bytes bigint,
  sent_bytes bigint,
  request_verb string,
  request_url string,
  request_proto string,
  user_agent string,
  ssl_cipher string,
  ssl_protocol string,
  target_group_arn string,
  trace_id string,
  domain_name string,
  chosen_cert_arn string,
  matched_rule_priority string,
  request_creation_time string,
  actions_executed string,
  redirect_url string,
  lambda_error_reason string,
  target_port_list string,
  target_status_code_list string,
  classification string,
  classification_reason string
  )
  PARTITIONED BY
  (
    day STRING
  )
  ROW FORMAT SERDE 'org.apache.hadoop.hive.serde2.RegexSetDe'
  WITH SERDEPROPERTIES (
  'serialization.format' = '1',
  'input.regex' =
'([^ ]*) ([^ ]*) ([^ ]*) ([^ ]*):([0-9]*) ([^ ]*)[:-]([0-9]*) ([-.0-9]*) ([-.0-9]*) ([-.0-9]*) (|[-0-9]*) (-|[-0-9]*) ([-0-9]*) ([-0-9]*) \"([^ ]*) (.*) (- |[^ ]*)\" \"([^\"]*)\" ([A-Z0-9-_]+) ([A-Za-z0-9.-]*) ([^ ]*) \"([^\"]*)\" \"([^\"]*)\" \"([^\"]*)\" ([-.0-9]*) ([^ ]*) \"([^\"]*)\" \"([^\"]*)\" \"([^ ]*)\" \"([^\s]+?)\" \"([^\s]+)\" \"([^ ]*)\" \"([^ ]*)\"')
  LOCATION 's3://your-alb-logs-directory/AWSLogs/<ACCOUNT-ID>/elasticloadbalancing/<REGION>/'
  TBLPROPERTIES
  (
    "projection.enabled" = "true",
    "projection.day.type" = "date",
    "projection.day.range" = "2022/01/01,NOW",
    "projection.day.format" = "yyyy/MM/dd",
    "projection.day.interval" = "1",
    "projection.day.interval.unit" = "DAYS",
    "storage.location.template" = "s3://your-alb-logs-directory/AWSLogs/<ACCOUNT-ID>/elasticloadbalancing/<REGION>/${day}"
  )
```

## 查询：

自己琢磨吧 emmm

## 参考

- [Querying Application Load Balancer Logs - AWS Athena](https://docs.aws.amazon.com/athena/latest/ug/application-load-balancer-logs.html)
