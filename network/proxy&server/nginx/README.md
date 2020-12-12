# [Nginx(Engine X)](https://github.com/nginx/nginx)

毫无疑问，nginx 是目前最流行的网页服务器（WebServer）、负载均衡器（LoadBalancer）和反向代理（ReverseProxy）.

- [nginx-admins-handbook](https://github.com/trimstray/nginx-admins-handbook): 通俗易懂，快速入门
- [nginxconfig.io](https://github.com/digitalocean/nginxconfig.io)： 快速生成 nginx 配置文件
- [nginx-proxy](https://github.com/jwilder/nginx-proxy)
- [uwsgi-nginx-flask-docker](https://github.com/tiangolo/uwsgi-nginx-flask-docker)
- [docker-letsencrypt-nginx-proxy-companion](https://github.com/JrCs/docker-letsencrypt-nginx-proxy-companion): 使用 docker 快速部署一个启用了 https 的 nginx 代理。
- [nginx 配置模板](https://github.com/h5bp/server-configs-nginx)



## 反向代理与长连接

>HTTP/1.0 需要显式设置请求头 `Connection: keep-alive` 来启用长连接。
而 HTTP/1.1 默认就是 Keep-Alive 的，关闭连接需要显式设置 `Connection: close`.
详见 [HTTP/Headers/Connection - MDN](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Connection)

>HTTP/2 没有 keep-alive 的概念，它通过多路复用等手段复用 TCP 连接，TCP 连接的长短不在 HTTP 层控制了（个人理解，不一定正确）。

- [ nginx反向代理时保持长连接](https://www.cnblogs.com/liuxia912/p/11075630.html)

