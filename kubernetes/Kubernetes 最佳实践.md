
>文档已迁移至：https://thiscute.world/posts/kubernetes-best-practices/

## 会话亲和性

缺点：可能造成流量负载不均衡，新扩容的实例全程围观
解决方法：使用中心化的、分布式的缓存，比如 Redis
