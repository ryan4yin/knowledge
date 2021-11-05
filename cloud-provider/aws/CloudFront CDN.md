# CloudFront


## CloudFront + Lambda@Edge

1. lambda@edge 配置失误，可能会导致 5xx 报错



## CDN 缓存策略

- [aws cloudfront - 优化缓存和可用性](https://docs.aws.amazon.com/zh_cn/AmazonCloudFront/latest/DeveloperGuide/ConfiguringCaching.html)

注意事项：

- 添加 header、params、cookie 的透传规则（即 CloudFront 的 cache key），都会导致缓存命令率下降，从而增加后端服务的压力。`cache key` 对应的 value 可选项越多，缓存命中率就越低。


