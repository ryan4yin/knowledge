# CloudFront


## CloudFront + Lambda@Edge

1. lambda@edge 配置失误，可能会导致 5xx 报错

## CloudFront Function

可以理解为更轻量的、更便宜的、环境受限的 lambda@edge.

TBD


## 如何看 CloudFront 的监控

CloudFront 的请求数、上传下载字节数等指标有个特点是：它的采样间隔我们是不确定的，所以绝对不能直接使用 `Average`!!!

正确的查询方法是：

- 将监控的查询方法设置为 `Sum`
- 时长设置为 `1min` 或者 `5mins`
- 查询出数据后，每个数据都除以 `60s` 或者 `300s`，这样就得到了最终的每秒请求数/字节数。


## CDN 缓存策略

- [aws cloudfront - 优化缓存和可用性](https://docs.aws.amazon.com/zh_cn/AmazonCloudFront/latest/DeveloperGuide/ConfiguringCaching.html)

注意事项：

- 添加 header、params、cookie 的透传规则（即 CloudFront 的 cache key），都会导致缓存命令率下降，从而增加后端服务的压力。`cache key` 对应的 value 可选项越多，缓存命中率就越低。


## CDN 如何处理与缓存 3xx/4xx/5xx 响应

>https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/HTTPStatusCodes.html

TBD


## CloudFront 回源成本

根据 [S3 定价文档](https://aws.amazon.com/s3/pricing/)，CloudFront 回源到 S3 是没有流量成本的，只收请求成本与其他成本。

TBD
