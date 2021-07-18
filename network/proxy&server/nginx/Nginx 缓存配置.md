# Nginx 的缓存配置

Nginx 可以配置缓存，降低上游服务的压力。

通常对于静态资源，我们会根据更新频率，设定较长时间的缓存时间，比如一小时、甚至三天。
而对于某些对实时性要求不高的 api，我们也可以设定短时间的缓存，比如 60s/180s。


## 缓存的层级

流量流经的每个地方都可以设置缓存，企业常见的流量链路有：

1. 浏览器 => Nginx负载均衡 => 后端服务
2. 浏览器 => CDN服务 => Nginx负载均衡 => 服务器
1. 浏览器 => CDN服务 => 对象存储服务

上面的任何一环都可以有自己的缓存，浏览器缓存、CDN 缓存、Nginx缓存、后端服务自身的缓存...

我们称浏览器缓存，为客户端的**私有缓存**。
而中间的代理服务器如 Nginx/CDN 的缓存，则为 **共享缓存**，在缓存有效时，所有客户端都可以使用这份缓存。


## 通过 `Cache-Control` Header 来设置缓存策略

>`Cache-Control` 要求 HTTP1.1+，upstream 连接需要设置用 http1.1 协议


## Nginx 缓存配置

一个示例配置如下:

```conf
http {
    ...
    // 缓存目录：/data/nginx/cache
    // 缓存名称：one
    // 缓存占用内存空间：10m
    // 缓存目录级别为2
    // 缓存最大时间为60分钟
    // 加载器每次迭代过程最多执行300毫秒
    // 加载器每次迭代过程中最多加载200个文件
    // 缓存硬盘空间最多为 200m
    proxy_cache_path /data/nginx/cache  levels=1:2 keys_zone=one:10m inactive=60m loader_threshold=300 loader_files=200 max_size=200m;
    server {
        listen 8080;
        // 使用名称为one的缓存
        proxy_cache one;
        location / {
            // 此 location 使用默认的缓存配置
            proxy_pass http://backend1;
        }
        location /some/path {
            proxy_pass http://backend2;
            
            // 缓存有效期为1分钟
            proxy_cache_valid any 1m;
            // 被请求3次以上时才缓存
            proxy_cache_min_uses 3;

            // 请求中有下面参数时不走缓存（cookie 中包含 nocache，arg 中包含 nocache）
            proxy_cache_bypass $cookie_nocache $arg_nocache$arg_comment;

            # 只缓存 GET HEAD 两种方法的响应（默认行为）
            proxy_cache_methods GET HEAD;

            # 使用自定义的 key 来存储和检索缓存
            proxy_cache_key $scheme$proxy_host$request
        }
    }
}
```


## 参考文档

- [Nginx缓存配置](https://www.cnblogs.com/itzgr/p/13321980.html)
- [HTTP Headers - Cache-Control](https://developer.mozilla.org/zh-CN/docs/Web/HTTP/Headers/Cache-Control)
