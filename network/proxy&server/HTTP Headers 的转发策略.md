# HTTP Headers 的转发策略


在使用 nginx/traefik/caddy 做代理服务器时，我们需要考虑到 Headers 转发相关的问题：

## 默认情况下，Proxy 会如何处理请求 Headers？

### 1. Proxy 会修改哪些 Headers？

- Nginx:
  - 默认情况下，Nginx 会将 `Host` 修改为 `$proxy_host` 的值， 将 `Connection` 设为 `close`.
  - 可以通过 `proxy_set_header` 修改这项行为。
  - 参考 [Nginx Reverse Proxy - Passing Request Headers](https://docs.nginx.com/nginx/admin-guide/web-server/reverse-proxy/#headers)
- Envoy:
  - TODO

### 2. Proxy 会删除哪些 Headers？

- Nginx:
  - 默认情况下有 `proxy_pass_request_headers on;`，也即会转发几乎所有 headers，但有如下介绍的这些例外。
    - Nginx 会删除掉所有带有下划线的 Headers，可通过设置 `underscores_in_headers on;` 禁用这一默认行为。（这是完全符合 HTTP 标准的行为）
    - 前面提到了 `Host` 跟 `Connection` 会被 proxy_pass 重写。
    - 如果启用了缓存，与缓存相关的请求头不会被传递到 upstream（`If-Modified-Since`, `If-Unmodified-Since`, `If-None-Match`, `If-Match`, `Range`, and `If-Range`）.
  - 参考
    - [Nginx - Missing (disappearing) HTTP Headers](https://www.nginx.com/resources/wiki/start/topics/tutorials/config_pitfalls/#missing-disappearing-http-headers)
    - [ngx_http_proxy_module - docs](http://nginx.org/en/docs/http/ngx_http_proxy_module.html#proxy_pass_request_headers)

### 3. Proxy 会添加哪些 Headers？

- `X-Forward-X`...

## Request Headers 的转发策略

1. 反向代理：
   2. traefik: 通过 `headers` 中间件，修改请求头
   3. caddy: 通过 `reverse_proxy/header_up` 修改请求头
   1. nginx: 通过 `proxy_set_header` 修改 Request Headers
      - 默认情况下: nginx 会修改请求头中的 host 和 Connection -> close
   4. envoy: 待续

## Response Headers 的转发策略

默认情况下，反向代理貌似不会修改响应头？？？

1. 反向代理: 
   1. traefik: 通过 `headers` 中间件，修改响应头 Response Headers
      1. 可以修改 CORS 同源策略等响应头内容
   2. caddy: 通过 `reverse_proxy/header_down` 修改响应头
   3. nginx: 通过 `add_header` 添加响应头
      1. 更复杂的操作需要安装插件: [openresty/headers-more-nginx-module](https://github.com/openresty/headers-more-nginx-module)
   4. envoy: 待续


## 参考

