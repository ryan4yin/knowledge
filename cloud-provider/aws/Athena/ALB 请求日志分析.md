# ALB 请求日志分析

## 创建 Athena 查询表

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
  elb_status_code string,  
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
  error_reason string
)
PARTITIONED BY(year string, month string, day string)
ROW FORMAT SERDE 'org.apache.hadoop.hive.serde2.RegexSerDe'
WITH SERDEPROPERTIES (
'serialization.format' = '1',
'input.regex' =
'([^ ]*) ([^ ]*) ([^ ]*) ([^ ]*):([0-9]*) ([^ ]*)[:-]([0-9]*) ([-.0-9]*) ([-.0-9]*) ([-.0-9]*) (|[-0-9]*) (-|[-0-9]*) ([-0-9]*) ([-0-9]*) \"([^ ]*) ([^ ]*) (- |[^ ]*)\" \"([^\"]*)\" ([A-Z0-9-]+) ([A-Za-z0-9.-]*) ([^ ]*) \"([^\"]*)\" \"([^\"]*)\" \"([^\"]*)\" ([-.0-9]*) ([^ ]*) \"([^\"]*)\" \"([^ ]*)\" \"([^ ]*)\"' )
LOCATION 's3://your_log_bucket/prefix/AWSLogs/AWS_account_ID/elasticloadbalancing/region/';
```

然后为每一天单独添加分区：

```sql
ALTER TABLE xxx_alb_logs_partitioned ADD
  PARTITION (year = '2022', month ='01', day= '15') LOCATION 's3://your_log_bucket/prefix/AWSLogs/AWS_account_ID/elasticloadbalancing/region/2022/01/15/'
```

生成 SQL 批量添加分区：

```python
import datetime as dt
from pathlib import Path

HEADER = """
ALTER TABLE xxx_alb_logs_partitioned ADD
"""

PARTITION_TPL = """  PARTITION (year = '{year:04}', month ='{month:02}', day= '{day:02}') LOCATION 's3://your_log_bucket/prefix/AWSLogs/AWS_account_ID/elasticloadbalancing/region/{year:04}/{month:02}/{day:02}/'
"""

# 起止日期（ALB 日志量大，不宜一次导入过多）
start_date = dt.date(year=2022, month=1, day=15)
end_date = dt.date(year=2022, month=2, day=16)

current_date = start_date
one_day = dt.timedelta(days=1)
sql_parts = [HEADER]
while current_date <= end_date:
    sql_parts.append(
        PARTITION_TPL.format(
            year=current_date.year, month=current_date.month, day=current_date.day
        ))
    current_date += one_day

sql_path = Path(__file__).parent / "xxx-alb-logs-add-partition.sql"
sql_path.write_text("".join(sql_parts))
```

## 查询：

自己琢磨吧 emmm

## 参考

- [如何使用 Athena 分析 ALB 访问日志？](https://aws.amazon.com/cn/premiumsupport/knowledge-center/athena-analyze-access-logs/)

