# [Nginx(Engine X)](https://github.com/nginx/nginx)

毫无疑问，nginx 是目前最流行的网页服务器（WebServer）、负载均衡器（LoadBalancer）和反向代理（ReverseProxy）.


## 相关文档

入门文档与查询手册：

- [nginx-admins-handbook](https://github.com/trimstray/nginx-admins-handbook): 通俗易懂，快速入门

自动生成配置：

- [nginxconfig.io](https://github.com/digitalocean/nginxconfig.io)： 快速生成 nginx 配置文件
- [nginx 配置模板](https://github.com/h5bp/server-configs-nginx)


开箱即用的容器镜像：

- [nginx-proxy](https://github.com/jwilder/nginx-proxy)
- [uwsgi-nginx-flask-docker](https://github.com/tiangolo/uwsgi-nginx-flask-docker)
- [docker-letsencrypt-nginx-proxy-companion](https://github.com/JrCs/docker-letsencrypt-nginx-proxy-companion): 使用 docker 快速部署一个启用了 https 的 nginx 代理。

源码阅读：

- [nginx-1.9.2源码通读分析注释](https://github.com/y123456yz/reading-code-of-nginx-1.9.2)

openresty:

- [openresty-best-practices](https://github.com/moonbingbing/openresty-best-practices)

## 反向代理与长连接

>HTTP/1.0 需要显式设置请求头 `Connection: keep-alive` 来启用长连接。
而 HTTP/1.1 默认就是 Keep-Alive 的，关闭连接需要显式设置 `Connection: close`.
详见 [HTTP/Headers/Connection - MDN](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Connection)

>HTTP/2 没有 keep-alive 的概念，它通过多路复用等手段复用 TCP 连接，TCP 连接的长短不在 HTTP 层控制了（个人理解，不一定正确）。

- [keepalive in upstream layer - nginx admin's handbook](https://github.com/trimstray/nginx-admins-handbook/blob/master/doc/NGINX_BASICS.md#upstream-layer)
- [ nginx反向代理时保持长连接](https://www.cnblogs.com/liuxia912/p/11075630.html)
- [与上游服务器之间，保持长连接](https://nginx.org/en/docs/http/ngx_http_upstream_module.html)：在该页面搜索 `keepalive connections` 即可找到相关信息
    1. nginx 默认使用 http1.0 与上游服务器通信，而 `keep-alive` 是 http1.1 的特性，因此要修改配置。详见上面给出的文档页。
    1. [关于 Nginx upstream keepalive 的说明](https://www.cnblogs.com/kabi/p/7123354.html)


## HTTPS 比 HTTP 多用多少资源？

答案：

1. 不使用专用的硬件加速的情况下，HTTPS 新建连接的 CPU 消耗是 HTTP 的接近 100 倍。
1. 运行连接复用跟连接池的情况下，HTTPS 的资源消耗会缩小到 HTTP 的 5-6 倍左右。

相关资料：

- [HTTPS 要比 HTTP 多用多少服务器资源？](https://www.zhihu.com/question/21518760/answer/32384258)
- [Testing the Performance of NGINX and NGINX Plus Web Servers](https://www.nginx.com/blog/testing-the-performance-of-nginx-and-nginx-plus-web-servers/)

