

## 热重启 Nginx Master

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


## Nginx 反向代理的排查思路

### 延迟上升的排查思路

排查状态码：

- 大量 499: 客户端不想等了，直接断开连接。
- 出现 502/504:
  - 后端被打垮了，无响应或者只给了部分响应
  - DNS 更新不及时，请求到了已经被回收的 ip 地址，导致响应超时

排查系统层面的性能问题：

- 首先确认 CPU/MEM/Network IO/Disk IO 是否达到瓶颈
- 其次，检查 TCP 连接数量监控，是否有异常

### 长尾请求延迟升高的排查思路



