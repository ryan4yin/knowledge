## APISIX 的 ETCD 高可用问题

测试发现 APISIX 2.15 与 3.2.2 都存在 ETCD 高可用问题，当 ETCD 集群中的某个节点宕机后，APISIX 会出现频繁的 etcd 连接失败问题，导致 QPS 出现持续波动。

但挂掉一个 ETCD 节点时，ETCD 集群本身工作正常，使用 etcdctl 测试能正常读写数据。

测试发现在 APISIX pod 中添加一个 etcd gateway 容器作为代理层，可以解决这个问题，因此初步判断是 APISIX 连接 ETCD 的代码存在问题。

## 代码分析

首先针对 request-id 插件的 snowflake 算法，找到如下 PR/Issue: https://github.com/apache/apisix/pull/9715

但测试关闭 request-id 插件后，问题依然存在，只是 QPS 与 P99/P95 延迟的波动幅度变小了。

APISIX 连接 etcd 的代码：

1. <https://github.com/apache/apisix/blob/3.2.2/apisix/core/etcd.lua#L135-L146>: 从这里看它貌似是使用 apisix/conf_server.lua 来连接 etcd 的，即使用 nginx 自身的 http 模块实现 etcd 连接的负载均衡。
1. <https://github.com/apache/apisix/blob/3.2.2/apisix/conf_server.lua>: 这里看它的负载均衡实现，每次请求都会重新选择一个 etcd 节点进行连接，如果连接失败就会重试，直到重试次数超过 3 次。
1. 进一步定位到 [_M.balancer()](https://github.com/apache/apisix/blob/3.2.2/apisix/conf_server.lua#L260-L288) 使用的节点选择算法有点问题： <https://github.com/apache/apisix/blob/3.2.2/apisix/conf_server.lua#L218-L229>，如果第一个节点被标记为不健康，它会直接选择第二个节点，完全假设了第二次选中的节点一定是可用的。但我不太清楚 nginx 的异步模型，不了解这个逻辑影响多大。
    1. 又因为 <https://github.com/apache/apisix/blob/3.2.2/apisix/conf_server.lua#L19>，APISIX 居然使用了 least_conn 算法来选择 ETCD 节点，那有问题的节点可能会被频繁选择到，感觉这更不合理了。


etcd gateway 能解决问题，那它是如何工作的呢？

1. <https://github.com/etcd-io/etcd/blob/v3.5.9/server/etcdmain/gateway.go>: `etcd gateway` 命令的入口代码，它实际是启动了一个 tcpproxy
1. <https://github.com/etcd-io/etcd/blob/v3.5.9/server/proxy/tcpproxy/userspace.go>: tcpproxy 的具体实现，实际看它就是每次建立 tcp 连接时，如果失败就会将 endpoint deactive，然后重新选择一个 endpoint 进行连接。连接成功后，会直接将客户端的的连接与 endpoint 的连接做 IO 同步操作。
  1. 其关键点应该是，etcd gateway 能确保客户端的每次请求都能成功，使客户端在连接层面对任意一台 etcd 节点宕机完全无感知。


测试时 etcd gateway 的日志如下（依次测试关掉三个节点中的任意一台，APISIX 通过 etcd gateway 访问时全程对问题无任何感知）：

```shell
{"level":"info","ts":"2023-12-18T08:10:10.570728Z","caller":"etcdmain/gateway.go:103","msg":"Running: ","args":["etcd","gateway","start","--endpoints=192.168.3.123:2379,192.168.3.134:2379,192.168.3.187:2379","–-listen-addr=127.0.0.1:23790"]}                                              
{"level":"info","ts":"2023-12-18T08:10:10.570905Z","caller":"etcdmain/main.go:44","msg":"notifying init daemon"}                                                                                                                                                                            
{"level":"info","ts":"2023-12-18T08:10:10.570923Z","caller":"etcdmain/main.go:50","msg":"successfully notified init daemon"}                                                                                                                                                                
{"level":"info","ts":"2023-12-18T08:10:10.570937Z","caller":"tcpproxy/userspace.go:87","msg":"ready to proxy client requests","endpoints":["192.168.3.123:2379","192.168.3.134:2379","192.168.3.187:2379"]}                                                                                    
{"level":"warn","ts":"2023-12-18T08:14:43.994181Z","caller":"tcpproxy/userspace.go:178","msg":"deactivated endpoint","address":"192.168.3.134:2379","interval":"1m0s","error":"dial tcp 192.168.3.134:2379: connect: connection refused"}                                                     
{"level":"warn","ts":"2023-12-18T08:17:21.890075Z","caller":"tcpproxy/userspace.go:210","msg":"failed to activate endpoint (stay inactive for another interval)","address":"192.168.3.134:2379","interval":"1m0s","error":"dial tcp 192.168.3.134:2379: connect: connection timed out"}       
{"level":"warn","ts":"2023-12-18T08:18:23.3301Z","caller":"tcpproxy/userspace.go:210","msg":"failed to activate endpoint (stay inactive for another interval)","address":"192.168.3.134:2379","interval":"1m0s","error":"dial tcp 192.168.3.134:2379: connect: connection timed out"}         
{"level":"warn","ts":"2023-12-18T08:19:24.780008Z","caller":"tcpproxy/userspace.go:210","msg":"failed to activate endpoint (stay inactive for another interval)","address":"192.168.3.134:2379","interval":"1m0s","error":"dial tcp 192.168.3.134:2379: connect: connection timed out"}       
{"level":"warn","ts":"2023-12-18T08:20:21.090109Z","caller":"tcpproxy/userspace.go:210","msg":"failed to activate endpoint (stay inactive for another interval)","address":"192.168.3.134:2379","interval":"1m0s","error":"dial tcp 192.168.3.134:2379: connect: connection timed out"}       
{"level":"warn","ts":"2023-12-18T08:21:22.529993Z","caller":"tcpproxy/userspace.go:210","msg":"failed to activate endpoint (stay inactive for another interval)","address":"192.168.3.134:2379","interval":"1m0s","error":"dial tcp 192.168.3.134:2379: connect: connection timed out"}       
{"level":"info","ts":"2023-12-18T08:22:10.591569Z","caller":"tcpproxy/userspace.go:214","msg":"activated","address":"192.168.3.134:2379"}                                                                                                                                                    
{"level":"info","ts":"2023-12-18T08:22:15.650159Z","caller":"tcpproxy/userspace.go:214","msg":"activated","address":"192.168.3.134:2379"}                                                                                                                                                    
{"level":"warn","ts":"2023-12-18T08:22:23.980015Z","caller":"tcpproxy/userspace.go:210","msg":"failed to activate endpoint (stay inactive for another interval)","address":"192.168.3.134:2379","interval":"1m0s","error":"dial tcp 192.168.3.134:2379: connect: connection timed out"}       
{"level":"warn","ts":"2023-12-18T08:28:42.849995Z","caller":"tcpproxy/userspace.go:178","msg":"deactivated endpoint","address":"192.168.3.187:2379","interval":"1m0s","error":"dial tcp 192.168.3.187:2379: connect: connection timed out"}                                                   
{"level":"warn","ts":"2023-12-18T08:29:54.539991Z","caller":"tcpproxy/userspace.go:178","msg":"deactivated endpoint","address":"192.168.3.187:2379","interval":"1m0s","error":"dial tcp 192.168.3.187:2379: connect: connection timed out"}                                                   
{"level":"warn","ts":"2023-12-18T08:30:45.730035Z","caller":"tcpproxy/userspace.go:178","msg":"deactivated endpoint","address":"192.168.3.187:2379","interval":"1m0s","error":"dial tcp 192.168.3.187:2379: connect: connection timed out"}                                                   
{"level":"warn","ts":"2023-12-18T08:31:21.570085Z","caller":"tcpproxy/userspace.go:210","msg":"failed to activate endpoint (stay inactive for another interval)","address":"192.168.3.187:2379","interval":"1m0s","error":"dial tcp 192.168.3.187:2379: connect: connection timed out"}       
{"level":"info","ts":"2023-12-18T08:31:42.691046Z","caller":"tcpproxy/userspace.go:214","msg":"activated","address":"192.168.3.187:2379"}                                                                                                                                                    
{"level":"warn","ts":"2023-12-18T08:32:23.017654Z","caller":"tcpproxy/userspace.go:210","msg":"failed to activate endpoint (stay inactive for another interval)","address":"192.168.3.187:2379","interval":"1m0s","error":"dial tcp 192.168.3.187:2379: connect: connection timed out"}       
{"level":"warn","ts":"2023-12-18T08:34:44.190564Z","caller":"tcpproxy/userspace.go:178","msg":"deactivated endpoint","address":"192.168.3.123:2379","interval":"1m0s","error":"dial tcp 192.168.3.132:2379: connect: connection refused"}                                                     
{"level":"warn","ts":"2023-12-18T08:37:19.970118Z","caller":"tcpproxy/userspace.go:210","msg":"failed to activate endpoint (stay inactive for another interval)","address":"192.168.3.123:2379","interval":"1m0s","error":"dial tcp 192.168.3.132:2379: connect: connection timed out"}       
{"level":"warn","ts":"2023-12-18T08:38:21.420092Z","caller":"tcpproxy/userspace.go:210","msg":"failed to activate endpoint (stay inactive for another interval)","address":"192.168.3.123:2379","interval":"1m0s","error":"dial tcp 192.168.3.132:2379: connect: connection timed out"}       
{"level":"warn","ts":"2023-12-18T08:39:22.859962Z","caller":"tcpproxy/userspace.go:210","msg":"failed to activate endpoint (stay inactive for another interval)","address":"192.168.3.123:2379","interval":"1m0s","error":"dial tcp 192.168.3.132:2379: connect: connection timed out"}       
{"level":"warn","ts":"2023-12-18T08:40:24.290091Z","caller":"tcpproxy/userspace.go:210","msg":"failed to activate endpoint (stay inactive for another interval)","address":"192.168.3.123:2379","interval":"1m0s","error":"dial tcp 192.168.3.132:2379: connect: connection timed out"}       
{"level":"warn","ts":"2023-12-18T08:41:20.620061Z","caller":"tcpproxy/userspace.go:210","msg":"failed to activate endpoint (stay inactive for another interval)","address":"192.168.3.123:2379","interval":"1m0s","error":"dial tcp 192.168.3.132:2379: connect: connection timed out"}       
{"level":"warn","ts":"2023-12-18T08:42:22.050072Z","caller":"tcpproxy/userspace.go:210","msg":"failed to activate endpoint (stay inactive for another interval)","address":"192.168.3.123:2379","interval":"1m0s","error":"dial tcp 192.168.3.132:2379: connect: connection timed out"}       
{"level":"warn","ts":"2023-12-18T08:43:23.499967Z","caller":"tcpproxy/userspace.go:210","msg":"failed to activate endpoint (stay inactive for another interval)","address":"192.168.3.123:2379","interval":"1m0s","error":"dial tcp 192.168.3.132:2379: connect: connection timed out"}       
{"level":"warn","ts":"2023-12-18T08:44:19.810035Z","caller":"tcpproxy/userspace.go:210","msg":"failed to activate endpoint (stay inactive for another interval)","address":"192.168.3.123:2379","interval":"1m0s","error":"dial tcp 192.168.3.132:2379: connect: connection timed out"}       
{"level":"warn","ts":"2023-12-18T08:45:21.250097Z","caller":"tcpproxy/userspace.go:210","msg":"failed to activate endpoint (stay inactive for another interval)","address":"192.168.3.123:2379","interval":"1m0s","error":"dial tcp 192.168.3.132:2379: connect: connection timed out"}       
{"level":"warn","ts":"2023-12-18T08:46:22.690116Z","caller":"tcpproxy/userspace.go:210","msg":"failed to activate endpoint (stay inactive for another interval)","address":"192.168.3.123:2379","interval":"1m0s","error":"dial tcp 192.168.3.132:2379: connect: connection timed out"}       
{"level":"warn","ts":"2023-12-18T08:47:24.130141Z","caller":"tcpproxy/userspace.go:210","msg":"failed to activate endpoint (stay inactive for another interval)","address":"192.168.3.123:2379","interval":"1m0s","error":"dial tcp 192.168.3.132:2379: connect: connection timed out"}       
{"level":"warn","ts":"2023-12-18T08:48:20.450015Z","caller":"tcpproxy/userspace.go:210","msg":"failed to activate endpoint (stay inactive for another interval)","address":"192.168.3.123:2379","interval":"1m0s","error":"dial tcp 192.168.3.132:2379: connect: connection timed out"}       
{"level":"warn","ts":"2023-12-18T08:49:21.890339Z","caller":"tcpproxy/userspace.go:210","msg":"failed to activate endpoint (stay inactive for another interval)","address":"192.168.3.123:2379","interval":"1m0s","error":"dial tcp 192.168.3.132:2379: connect: connection timed out"}       
{"level":"warn","ts":"2023-12-18T08:50:23.330769Z","caller":"tcpproxy/userspace.go:210","msg":"failed to activate endpoint (stay inactive for another interval)","address":"192.168.3.123:2379","interval":"1m0s","error":"dial tcp 192.168.3.132:2379: connect: connection timed out"}       
{"level":"warn","ts":"2023-12-18T08:51:24.780062Z","caller":"tcpproxy/userspace.go:210","msg":"failed to activate endpoint (stay inactive for another interval)","address":"192.168.3.123:2379","interval":"1m0s","error":"dial tcp 192.168.3.132:2379: connect: connection timed out"}       
{"level":"warn","ts":"2023-12-18T08:52:21.090378Z","caller":"tcpproxy/userspace.go:210","msg":"failed to activate endpoint (stay inactive for another interval)","address":"192.168.3.123:2379","interval":"1m0s","error":"dial tcp 192.168.3.132:2379: connect: connection timed out"}       
{"level":"warn","ts":"2023-12-18T08:53:22.530491Z","caller":"tcpproxy/userspace.go:210","msg":"failed to activate endpoint (stay inactive for another interval)","address":"192.168.3.123:2379","interval":"1m0s","error":"dial tcp 192.168.3.132:2379: connect: connection timed out"}       
{"level":"warn","ts":"2023-12-18T08:54:23.970351Z","caller":"tcpproxy/userspace.go:210","msg":"failed to activate endpoint (stay inactive for another interval)","address":"192.168.3.123:2379","interval":"1m0s","error":"dial tcp 192.168.3.132:2379: connect: connection timed out"}       
{"level":"info","ts":"2023-12-18T08:55:10.634141Z","caller":"tcpproxy/userspace.go:214","msg":"activated","address":"192.168.3.123:2379"}                                                                                                                                                    
{"level":"info","ts":"2023-12-18T08:55:15.170592Z","caller":"tcpproxy/userspace.go:214","msg":"activated","address":"192.168.3.123:2379"}                                                                                                                                                    
{"level":"warn","ts":"2023-12-18T08:55:20.2903Z","caller":"tcpproxy/userspace.go:210","msg":"failed to activate endpoint (stay inactive for another interval)","address":"192.168.3.123:2379","interval":"1m0s","error":"dial tcp 192.168.3.132:2379: connect: connection timed out"}
```

从上面的分析看，apisix 自身的 etcd 连接代码，应该是无法保证每次请求都能成功的，因此当某个 etcd 节点宕机后，APISIX 会出现频繁的 etcd 连接失败问题，从而影响到其正常工作。


进一步分析与 Bug 复现步骤待补充...


