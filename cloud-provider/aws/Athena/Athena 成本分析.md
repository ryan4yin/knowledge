# Athena 成本分析

## Athena 分析 CUR 成本报表

AWS CUR，即 AWS Cost and Usage Reports, 这里主要给出几个查询细节成本的 SQL 模板。

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
  sum(line_item_blended_cost) as blended_cost
FROM "my_cur"
where regexp_extract(line_item_usage_start_date, '^..........') >= '2021-11-28'
  and line_item_product_code  = 'AmazonS3'
  and line_item_resource_id = 'bucket_name'
group by 1, 2
order by 1, 2
```

查询 S3 的流量成本:

```sql
SELECT
  regexp_extract(line_item_usage_start_date, '^..........') as usage_start_date,
  sum(line_item_blended_cost) as blended_cost,
  line_item_operation,
  line_item_usage_type,
  line_item_usage_amount,
  line_item_line_item_description,
  product_from_location,
  product_from_location_type,
  product_to_location,        -- S3 只收传出到 internet/其他 region 的流量成本
  product_to_location_type
FROM "my_cur"
where regexp_extract(line_item_usage_start_date, '^..........') = '2022-04-05'
  and line_item_product_code  = 'AmazonS3'
  and line_item_resource_id = 'bucket_name'
  and line_item_usage_type like 'DataTransfer-Out-Bytes'  --  只查询 S3 传出的流量成本
group by
  1,3,4,5,6,7,8,9,10
order by 1, 3, 2
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
group by 1, 2
order by 1, 2
```


CloudFront 成本分析：

```sql
SELECT
  regexp_extract(line_item_usage_start_date, '^..........') as usage_start_date,
  sum(line_item_blended_cost) as blended_cost,
  line_item_usage_amount,
  line_item_usage_type,
  line_item_line_item_description
FROM "my_cur"
where regexp_extract(line_item_usage_start_date, '^..........') = '2022-03-25'
  and line_item_product_code  = 'AmazonCloudFront'
  and line_item_resource_id like '%xxx'
  -- and line_item_usage_type like '%DataTransfer-Out-OBytes'  -- 只查询回源流量的成本
  and line_item_usage_type like '%DataTransfer-Out-Bytes'  -- 只查询 CDN 出网流量的成本
group by 1,3,4,5
```

NAT 网关成本分析：

```sql
SELECT * from (

SELECT
    regexp_extract(line_item_usage_start_date, '^..........') as start_date,
    line_item_usage_type,
    sum(line_item_blended_cost) as blended_cost
  FROM "my_cur"
  where regexp_extract(line_item_usage_start_date, '^..........') > '2021-11-23'
    and line_item_product_code  = 'AmazonEC2'
    and line_item_resource_id like '%nat-%'  -- NAT 网关
  group by 1,2

) where cost > 10
order by 2, 1
```

## SavingPlans/ReservedInstances 对 CUR 成本的影响

SP/RI 会导致部分被 cover 的实例成本下降，而其他实例的成本没变化，而且它是根据一些难以预测的手段去选择 cover 哪些实例的。这会导致基于 CUR 的成本分析手段失效。

解决方法是以 `pricing_public_on_demand_cost` 这个字段进行成本分析，这个给出的是按标准价格计算的实例成本。可以将总的 `blended_cost` 也就是真实成本，以上述 OD 成本为权重进行拆分，得到的就是一个比较准确的成本了。

## Athena 自身的成本分析

- 把 workspace 拆得更细致，可以单独分析每个 workspace 的成本
- 对同一 workspace 内的成本，可以通过脚本把所有 SQL 的查询记录导出来分析


## 参考

- [增强Amazon Athena对历史查询记录的统计分析功能](https://aws.amazon.com/cn/blogs/china/enhance-amazon-athenas-statistical-analysis-function-for-historical-query-records/)
