# CloudFront

>https://docs.aws.amazon.com/zh_cn/AmazonCloudFront/latest/DeveloperGuide/Introduction.html

## CloudFront + Lambda@Edge

1. lambda@edge 配置失误，可能会导致 5xx 报错

## CloudFront Function

可以理解为更轻量的、更便宜的、环境受限的 lambda@edge.

TBD


## Origin Sheild

集中式缓存层，可以降低延迟，提高响应速度。

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


## CloudFront 成本

>https://aws.amazon.com/cloudfront/pricing/

CloudFront 成本分成这几个部分：

- 回源成本：
  - CloudFront 边缘节点回源到 AWS 服务（如 S3/EC2/ELB/API Gateway）均免费。
  - CloudFront 回源到其他源站，会收回源流量费。
- 出网成本 DTO
  - 流量流出到公网的成本 `DataTransfer-Out-Bytes`，默认按梯度收费的，而且分 Region 进行统计。
- 请求处理费
  - 对于大的静态文件而言，请求的处理费占比通常很小，DTO 是主要成本。
  - 对于使用 CloudFront 作为 API 前端的情况，情况可能会不同。
- Origin Sheild
  - 固定按量计费

### 使用 CloudFront 作为后端服务的代理

CDN 通常只用在静态站点、音视频、图片等领域，但是实际上有些时候，使用 CDN 代理后端服务也是有很多好处的。

为线上 API 也使用 CloudFront => ELB/EC2 => K8s 的结构，主要有如下好处：

- **降低后端服务的负载**：
  - CloudFront 有 origin sheild 跨 region 的集中式缓存，也有边缘节点缓存。对于请求参数完全一模一样的请求，缓存可以帮助降低后端压力
  - 测试发现在请求参数不同但是响应 body 绝大部分数据相同的情况下（比如 APK 动态打包，响应体为 APK 母包 + 少许特殊信息，母包大都是一模一样的），开启 origin sheild 能明显降低响应延迟，原因不明。
  - 但是开缓存这个，得依赖业务侧的洞察，因为不是所有的 API 都可以开 CDN 缓存！有许多接口要求实时数据。
- **提升网络性能**
  - 上述缓存层同样能提升请求的性能，降低服务延迟
  - 从边缘节点回源到 AWS 也是有性能提升的，主要手段有：边缘节点会维持回源的长连接、更宽的 TCP 初始拥塞窗口。
    - 因此即使完全禁用掉缓存，加一层 CDN 仍然能在一定程度上提升 API 的速度。
- **保护后端服务**：
  - 首先只有合法的 HTTP 请求才会被 CloudFront 转发到 ELB 进而转发到后端服务，这可以防范所有 TCP 层的攻击
  - 其次对于合法的 HTTP 请求，缓存层实际上也是为后端服务提供了一层保护，可以防范许多种 CC 攻击。
  - 还可以考虑直接为 CloudFront/ELB 购买 WAF（AWS Shield）服务，防范更多的攻击。

但是用量小的情况下这么搞成本会比较高，所以这个方案可能不太适合用量不高的情况。

而对于大客户而言（比如 CDN 每月用量接近 PB 级，其他 AWS 服务的用量也不少？）就不同了，CloudFront 的价格可以靠商业谈判获得非常大的折扣。

如果你的 CloudFront 用量非常大，AWS 给的折扣非常高，CDN 出网流量价格比 ELB/EC2 的出网流量价格低很多的话，在线服务也使用 CloudFront + ELB/EC2 提供出网服务，在成本上甚至可能有优惠：

- DTO 出网流量价格低很多
- 回源到 AWS 自身的服务是免费的（S3）
- CloudFront 会多一个按请求量的收费项

