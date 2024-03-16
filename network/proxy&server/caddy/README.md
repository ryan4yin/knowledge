# [Caddy](https://github.com/caddyserver/caddy)

Caddy 与 nginx 类似，但是配置简单非常多，而且支持自动管理证书、自动 http 重定向到 https。

对于个人用户而言，Caddy 绝对是 nginx 绝佳的替代品，非常省心。

不过它是 Go 写的，比较吃内存，性能相对比 Nginx 差一点，高性能场景一般还是选择 OpenResty。
