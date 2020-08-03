# [Nginx](https://github.com/nginx/nginx)

- [nginx-admins-handbook](https://github.com/trimstray/nginx-admins-handbook)
- [nginxconfig.io](https://github.com/digitalocean/nginxconfig.io)
- [nginx-proxy](https://github.com/jwilder/nginx-proxy)
- [uwsgi-nginx-flask-docker](https://github.com/tiangolo/uwsgi-nginx-flask-docker)


## 反向代理与长连接

>HTTP/1.0 需要显式设置请求头 `Connection: keep-alive` 来启用长连接。
而 HTTP/1.1 默认就是 Keep-Alive 的，关闭连接需要显式设置 `Connection: close`.
详见 [HTTP/Headers/Connection - MDN](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Connection)

>HTTP/2 没有 keep-alive 的概念，它通过多路复用等手段复用 HTTP 连接，TCP 连接的长短不在 HTTP 层控制了（个人理解，不一定正确）。

- [ nginx反向代理时保持长连接](https://www.cnblogs.com/liuxia912/p/11075630.html)
