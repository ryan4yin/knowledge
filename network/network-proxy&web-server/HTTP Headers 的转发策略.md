# HTTP Headers 的转发策略


在使用 nginx/traefik/caddy 做代理服务器时，我们需要考虑到 Headers 转发相关的问题：

1. 默认情况下，proxy 会转发哪些 headers？会修改哪些 headers？又会添加/删除哪些 headers?
1. 如何自定义 headers 的转发策略？

## Request Headers 的转发策略

1. 反向代理：
   2. traefik: 通过 `headers` 中间件，修改请求头
   3. caddy: 通过 `reverse_proxy/header_up` 修改请求头
   1. nginx: 通过 `proxy_set_header` 修改 Request Headers
      - 默认情况下: nginx 会修改请求头中的 host 和 Connection
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

- [Nginx Reverse Proxy - Passing Request Headers](https://docs.nginx.com/nginx/admin-guide/web-server/reverse-proxy/#headers)
