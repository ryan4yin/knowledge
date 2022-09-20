
## 一、Nginx 的 DNS 缓存以及配置 Reload 代价过高的问题

>参考官方文档：https://www.nginx.com/blog/dns-service-discovery-nginx-plus/

一个非常常见的 nginx 反向代理的配置方式如下：

```conf
server {
    listen 80;
    server_name www.test.com;

    location /a {
        proxy_set_header Host proxy.test.com;
        proxy_pass http://proxy.test.com;
    }

    location /b {
        proxy_set_header Host proxy.test.com;
        proxy_pass http://service-b;
    }
}

upstream service-b {
  # 使用加权轮询（WRR）算法进行负载均衡
  server service-b.cluster-1.test.com fail_timeout=1s max_fails=3 weight=90;
  server service-b.cluster-2.test.com fail_timeout=1s max_fails=3 weight=10;
  keep_alive 30;
}
```

根据官方介绍，`proxy_pass http://proxy.test.com;` 这种直接在 `proxy_pass` 语句中写 DNS 地址的用法有如下问题：

- 如果域名无法解析，Nginx 将无法 start 或者 reload
- 开源的 Nginx 仅在 start/reload 时才会获取该域名的 DNS 记录，然后就一直缓存起来了，记录的 TTL 完全无效！
- 无法指定其他负载均衡算法，仅能使用默认的 RoundRobin 算法
- 无法保持长连接，所有请求结束后连接都被立即关闭

而上述配置中的 `proxy_pass http://service-b;` 加上 `upstream service-b {...}`。
这种配置方式相比前一种，有这几个好处：

- 可以设定在多个 server 上进行负载均衡，使用加权轮询算法调整各 server 的权重
- 可以调整负载均衡算法、超时时间、重试次数等其他参数。
- 可以保持长连接，通过 `keepavlie` 设定长连接的超时时长

但是它仍然存在 DNS 解析会在 start/reload 时被缓存、以及 DNS 无法解析时会 start/reload 失败的问题！

### 解决方法一

这种方法是 `proxy_pass http://proxy.test.com;` 的一个变体，它可以避免 DNS 被 nginx 缓存，TTL 被忽略的问题。

>注意：此方法对**对使用了 `upstream` 中的域名无效**！

```conf
resolver 10.0.0.2 valid=10s;

server {
    location / {
        set $backend_servers backends.example.com;
        proxy_pass http://$backend_servers:8080;
    }
}
```

这种方法通过在 nginx 配置中明确设定 resolver 以及 `valid=10s`，使 nginx 每 10s 检查下 TTL 是否过期，过期则重新进行解析。

### 解决方法二

在 DNS 出现变更时，手动或自动地 reload 下 nginx 配置。

### 解决方法三 - tengine

阿里巴巴对 Nginx 的修改版——Tengine，提供了 [ngx_http_upstream_dynamic_module](https://github.com/alibaba/tengine/blob/master/docs/modules/ngx_http_upstream_dynamic.md) 模块，可以动态解析 upstream 的 DNS 记录。

### 解决方法四 - 第三方模块

[ngx_upstream_jdomain](https://github.com/nicholaschiasson/ngx_upstream_jdomain) 这个第三方模块支持动态解析 upstream 的 DNS 记录。

### 解决方法五 - Nginx Pluse

Nginx Plus 支持在 `upstream` 中进行动态 DNS 解析.

## 二、热重启 Nginx Master

如果 lua 代码存在隐患，长期运行的 Nginx Master 可能会遇到内存溢出，为此需要定期重启（比如两三个星期一次）：

```
ps aux | grep nginx

export OLD_MASTER=

# 启动一个新的 master 进程，平滑地启动新的 worker，和旧 worker 一起处理请求
sudo kill -USR2 $OLD_MASTER

# 等待 60s

# 让旧 master 进程优雅关闭所有旧的 worker，然后退出
sudo kill -QUIT $OLD_MASTER

# 再等待 3m，并且注意观察 QPS、错误状态码（499/5xx）、可用率的监控
```


## 三、Nginx 反向代理的排查思路

### P99 延迟上升的排查思路

排查状态码：

- 大量 499: 客户端不想等了，直接断开连接。
- 出现 502/504:
  - 后端被打垮了，无响应或者只给了部分响应
  - DNS 更新不及时，请求到了已经被回收的 ip 地址，导致响应超时

排查系统层面的性能问题：

- 首先确认 CPU/MEM/Network IO/Disk IO 是否达到瓶颈
- 其次，检查 TCP 连接数量监控，是否有异常

再次，排查客户端的问题：

- 客户端网络状况如何？是否存在部分请求上传 body 过大、网络较差，导致延迟高或者 499/408 状态码
- 客户端代码逻辑是否存在问题？比如说出现 TCP 连接泄漏，这些泄漏连接超时触发 Nginx 返回 408

相关案例：

- [APISIX - bug: P99 latency is too high](https://github.com/apache/apisix/issues/7919)

### 504 超时请求上升的排查思路

- 确认是否存在 CPU 性能问题
- 如果 CPU 利用率正常，再检查 upstream 的 `keepalive` 配置，如果配的连接数不够也会导致请求超时。
- 再检查 nginx 的 `worker_rlimit_nofile` `worker_connections` 以及 Linux 内核的 `ulimit -n` `sysctl: fs.file-max` 等参数
- 检查实例当前的连接数状况：`while true; do  netstat -an | awk '{print $6}' | sort | uniq -c | sort -nr; sleep 5; echo =====; done`
  - 若当前连接数状况已经接近 Linux 内核或者 nginx 的 rlimit/connections 设置，则可确定是这些参数的问题
  - 检查 error_log 里有没有 `worker_connections are not enough, reusing connections` 类似的日志。
- 检查服务器的网络带宽是否跑满了

如果上述参数都正常，那很可能是其他 TCP/IP 协议栈的问题导致的丢包，最终造成 504 超时，丢包通常会有些连带的现象：

- 504 状态码上升
- Pod 健康检查超时无响应
- 对许多其他服务的请求都失败，但是其他服务各种指标一切正常

这类问题最常出现在边缘网关这类需要承接大量客户端请求的位置。其排查解决方法参见 [Linux 504 超时丢包问题解决思路](/linux/Linux%20504%20%E8%B6%85%E6%97%B6%E4%B8%A2%E5%8C%85%E9%97%AE%E9%A2%98%E8%A7%A3%E5%86%B3%E6%80%9D%E8%B7%AF.md)
