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


## 错误配置集锦

### `proxy_set_header` 和 `add_header` 不生效的问题

最近在写 nginx 配置时遇到个问题：如下配置中，`server` 块中定义的所有 `proxy_set_header` 属性都不会生效：

```
server{
    server_name 192.168.31.123:80;
    proxy_set_header   Host             $host;
    proxy_set_header   X-Real-IP        $remote_addr;
    proxy_set_header   X-Forwarded-For  $proxy_add_x_forwarded_for;

    location / {
            proxy_pass http://xxx;
    }

    # ^~ 开头对 URL 路径进行前缀匹配，并优先于正则匹配。
    location ^~ /ws
    {
        proxy_set_header Connection "upgrade";
        proxy_set_header Upgrade $http_upgrade;

        proxy_pass http://xxx;
    }
}
```

查看官方文档 [proxy_set_header - nginx docs](http://nginx.org/en/docs/http/ngx_http_proxy_module.html#proxy_set_header)，发现它明确提到，只有在当前 block 中不存在 `proxy_set_header` 的情况下，才会继承上层的 `proxy_set_header` 配置。

上面的 `location ^~ /ws` 块包含了 `proxy_set_header`，导致 `server` 块中的 `proxy_set_header` 失效！

因此正确的写法是，应该把外部的 `proxy_set_header` 配置拷贝到 `location ^~ /ws` 块中

这里还有更详细的论述：[Set the HTTP headers with `add_header` and `proxy_*_header` directives properly](https://github.com/trimstray/nginx-admins-handbook/blob/master/doc/RULES.md#beginner-set-the-http-headers-with-add_header-and-proxy__header-directives-properly)


### `rewrite xxx xxx break` 后面的 return 语句不生效

如下配置中，`rewrite` 后面的 `return` 语句不会生效，请求会返回 `404`：

```nginx
# ......
http {
    # ......
    server {
        # ......

        location /xxx/ {
            rewrite ^/xxx/(.*)$ /yyy/$1 break;
            return 200 "hhh";
        }
    }

...
}
```

查阅官方文档 [ngx_http_rewrite_module](http://nginx.org/en/docs/http/ngx_http_rewrite_module.html#rewrite) 发现，
rewrite 的 `last` 和 `break` 两个都会停止处理当然的所有 `ngx_http_rewrite_module` 模块的所有指令，而 `return` 指令就是由 `ngx_http_rewrite_module` 模块提供的，因此它被直接忽略了。
由于请求未得到处理，导致 nginx 直接返回了 `404`.


###  proxy_pass 的 upstream DNS 缓存问题

Nginx 的 upstream 地址只会在启动时被解析一次，后续如果 upstream DNS 存在变更，就会导致错误。

参考文章：

- [运维遇坑记录(3)-Nginx缓存了DNS解析造成后端不通](https://segmentfault.com/a/1190000022365954)

解决方案：

- 方案一：每次 DNS 变更都 reload nginx，比如写个脚本监控 DNS 变更，有变更就跑下 nginx reload
- 方案二：通过 set+resolver 的方式动态更新 DNS
  - 但是这个方案不适合 QPS 高的情况，因为它不支持 keepalive
    ```conf
    location / {
        resolver 8.8.8.8;
        set $backend https://demo-app.com$uri$is_args$args;
        proxy_pass $backend;
        include proxy_params;
    }
    ```
- 方案三：使用第三方模块


