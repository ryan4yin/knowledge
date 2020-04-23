# Network-Proxy & Web Server

## 网络代理

有两种类型的网络代理：

1. 反向代理(Reverse Proxy): 可理解成**服务端代理**，是服务端配置的一个中间代理服务器，负责将客户端的请求转发给后端服务器。 
   - 常被用于流量负载均衡(Load Balancer)、API网关、实现缓存/https/安全等功能。
   - ![reverse-proxy](_imgs/reverse-proxy-flow.svg)
2. 前向代理(Forward Proxy)/转发代理: 可理解成**客户端代理**，是客户端配置的一个中间代理服务器，负责将客户端的请求转发给后端服务器。 
   - 常被用于突破某些服务端的访问限制（比如地域限制-翻墙），或者在网络上隐藏自己的真实身份（Tor 洋葱代理）。
   - 也可用于添加某些访问限制：比如学校/企业可以通过前向代理禁止用户访问 Zhihu/Bilibili 等娱乐网站。
   - ![forward-proxy](_imgs/forward-proxy-flow.svg)


下面介绍几种当下比较流行的代理软件：

全能选手，既可用做代理，又可用做 Web 服务器：

1. Nginx: 使用最广泛，最年长，但是配置稍显复杂。
2. Caddy: 新兴的 Web Server & Network-Proxy。配置比 Nginx 简单，支持自动配置 SSL 证书，默认启用 HTTP2/HTTPS。

专用代理软件：

1. Traefik: 一个纯粹的代理软件，支持自动配置 SSL 证书，配置很简单，功能相当丰富，还有好看的 Web UI。
1. Envoy: Istio 钦定代理，在服务网格中专门负责流量转发
2. Linkerd: 用 rust 写的轻量高效的代理，值得一看。


## 参考

- [What is a reverse proxy? - cloudflare](https://www.cloudflare.com/learning/cdn/glossary/reverse-proxy/)
