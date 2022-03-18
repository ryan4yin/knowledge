# Athena 成本分析

## Athena 分析 CUR 成本报表

AWS CUR，即 AWS Cost and Usage Reports

详见官方文档：https://docs.aws.amazon.com/cur/latest/userguide/cur-data-view.html

查询所有产品代码:

```sql
SELECT DISTINCT line_item_product_code FROM "my_cur";
```

查询 S3 成本:

```sql
SELECT
  regexp_extract(line_item_usage_start_date, '^..........') as usage_start_date,
  line_item_operation,
  sum(line_item_blended_cost) as blended_cost,
FROM "my_cur"
where regexp_extract(line_item_usage_start_date, '^..........') >= '2021-11-28'
  and line_item_product_code  = 'AmazonS3'
  and line_item_resource_id = 'bucket_name'
group by
  line_item_operation,
  regexp_extract(line_item_usage_start_date, '^..........')
order by regexp_extract(line_item_usage_start_date, '^..........'),line_item_operation
```

查询 EC2 成本：

```sql
SELECT
  regexp_extract(line_item_usage_start_date, '^..........') as usage_start_date,
  line_item_operation,
  --line_item_usage_type,
  sum(line_item_blended_cost) as blended_cost,
FROM "my_cur"
where regexp_extract(line_item_usage_start_date, '^..........') >= '2021-12-27'
  and line_item_product_code  = 'AmazonEC2'
  and line_item_resource_id = 'ec2_id'  -- 或者使用 tag 查一批 ec2 的成本
  -- and line_item_usage_type = 'DataTransfer-Regional-Bytes' -- 跨区/跨域流量成本
  and line_item_usage_type != 'DataTransfer-Regional-Bytes' -- 去掉流量成本，就是计算+存储的成本
group by
  regexp_extract(line_item_usage_start_date, '^..........'),
  --line_item_usage_type,
  line_item_operation
order by regexp_extract(line_item_usage_start_date, '^..........'), line_item_operation
```

## Athena 自身的成本分析

- 把 workspace 拆得更细致，可以单独分析每个 workspace 的成本
- 对同一 workspace 内的成本，可以通过脚本把所有 SQL 的查询记录导出来分析


## 参考

- [增强Amazon Athena对历史查询记录的统计分析功能](https://aws.amazon.com/cn/blogs/china/enhance-amazon-athenas-statistical-analysis-function-for-historical-query-records/)
