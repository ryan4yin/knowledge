# AWS 服务日志转换

>https://github.com/awslabs/athena-glue-service-logs

AWS 输出的服务日志格式、文件夹结构各异，直接通过 Athena 查询很可能会遇到各种性能、成本问题，
最佳实践是首先使用 Glue 脚本将 AWS 服务的日志转换为 athena 友好的格式，然后再使用 Athena 查询。

支持处理 ALB/ELB/CloudTrail/CloudFront/S3/VPC 等日志。

待续...

