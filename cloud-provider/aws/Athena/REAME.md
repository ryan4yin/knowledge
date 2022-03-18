# Athena - 使用 SQL 查询 S3 数据

Athena 提供使用标准 SQL 分析 Amazon S3 中的数据的能力，主要的用途：

- 分析 S3 中的各种 AWS 服务日志
  - ALB 请求日志
  - [CloudFront 请求日志](https://docs.aws.amazon.com/athena/latest/ug/cloudfront-logs.html)
  - 等等
- 查询用户保存的具有一定格式的数据

类似的产品有：

- Google BigQuery: 支持查询 Google CloudStorage 中的格式化数据
