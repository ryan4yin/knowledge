## 错误配置集锦

### `proxy_set_header` 和 `add_header` 不生效的问题

最近在写 nginx 配置时遇到个问题：如下配置中，`server` 块中定义的所有 `proxy_set_header` 属性都不会生
效：

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

查看官方文档
[proxy_set_header - nginx docs](http://nginx.org/en/docs/http/ngx_http_proxy_module.html#proxy_set_header)，
发现它明确提到，只有在当前 block 中不存在 `proxy_set_header` 的情况下，才会继承上层的
`proxy_set_header` 配置。

上面的 `location ^~ /ws` 块包含了 `proxy_set_header`，导致 `server` 块中的 `proxy_set_header` 失效！

因此正确的写法是，应该把外部的 `proxy_set_header` 配置拷贝到 `location ^~ /ws` 块中

这里还有更详细的论
述：[Set the HTTP headers with `add_header` and `proxy_*_header` directives properly](https://github.com/trimstray/nginx-admins-handbook/blob/master/doc/RULES.md#beginner-set-the-http-headers-with-add_header-and-proxy__header-directives-properly)

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

查阅官方文档
[ngx_http_rewrite_module](http://nginx.org/en/docs/http/ngx_http_rewrite_module.html#rewrite) 发现，
rewrite 的 `last` 和 `break` 两个都会停止处理当前上下文中 `ngx_http_rewrite_module` 模块的所有指令，
而 `return` 指令就是由 `ngx_http_rewrite_module` 模块提供的，因此它被直接忽略了。由于请求未得到处
理，导致 nginx 直接返回了 `404`.

### proxy_pass 的 upstream DNS 缓存问题

Nginx 的 upstream 地址只会在启动时被解析一次，后续如果 upstream DNS 存在变更，就会导致错误。

参考文章：

- [运维遇坑记录(3)-Nginx缓存了DNS解析造成后端不通](https://segmentfault.com/a/1190000022365954)
- [How to force nginx to resolve DNS (of a dynamic hostname) everytime when doing proxy_pass?](https://serverfault.com/questions/240476/how-to-force-nginx-to-resolve-dns-of-a-dynamic-hostname-everytime-when-doing-p)

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

### 带 path 的 proxy_pass 语句

通常我们的 `proxy_pass` 是只传一个 upstream 名称，或者一个不带 Path 的 URI，举例：

```conf
location /xxx {
    # requests_uri 会被原封不动地传递给 upstream
    proxy_pass http://xxx.example.com:8080;
}
```

但是有时候我们会看到带 Path 的 proxy_pass 配置：

```conf
location /xxx {
    # requests_uri 会被替换掉 location 匹配的前缀后，再传递给 upstream.
    # 比如请求 /xxx/yyy.html，实际上代理到 upstream 的地址会是 /yyy.html
    proxy_pass http://xxx.example.com:8080/;
}

location /xxx {
    # 比如请求 /xxx/yyy.html，实际上代理到 upstream 的地址会是 /aaayyy.html
    proxy_pass http://xxx.example.com:8080/aaa;
}

location /xxx {
    # 比如请求 /xxx/yyy.html，实际上代理到 upstream 的地址会是 /aaa/yyy.html
    proxy_pass http://xxx.example.com:8080/aaa/;
}
```

### 使用 Nginx 的 Mirror 流量镜像时未单独设置连接 timeout 参数

> http://nginx.org/en/docs/http/ngx_http_mirror_module.html

Nginx 的源请求，会一直等待到默认 Upstream 与 Mirror Upstream 全部处理完成后，才会把响应发送给客户
端！

所以如果 Mirror 镜像的 Upstream 出了问题，比如完全宕机了，就会导致所有请求全部会在等待超过 TCP 连接
超时时间后，才被返回给客户端！

为了避免 mirror upstream 问题影响源请求，建议按如下方式给 mirror upstream 单独设置超时参数：

```conf
location / {
    mirror /mirror;
    proxy_pass http://backend;
}

location = /mirror {
    internal;

    # mirror upstream 单独设置 timeout 超时，避免影响到源请求
    proxy_connect_timeout 350ms;
    proxy_read_timeout 350ms;
    proxy_send_timeout 350ms;

    proxy_http_version 1.1;
    proxy_set_header Host $upstream_host;

    # proxy_set_header     X-Forwarded-For $proxy_add_x_forwarded_for;
    # proxy_set_header   X-Forwarded-Host     $xxx;

    proxy_pass http://test_backend$request_uri;
}
```
