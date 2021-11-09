

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

