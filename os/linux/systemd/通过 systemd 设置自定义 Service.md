如果要在Linux 上设置一个开机自启，出现问题自动重启，并且有良好日志的程序，比较流行的方法有 supervisord、systemd，除此之外，还有 upstart、runit 等类似的工具。
但是自从 systemd 被 ubuntu、centos 等主流 Linux 发行版应用以来，systemd 渐渐成为主流方案。

### 配置说明

要自定义一个服务，需要在 `/usr/lib/systemd/system/` 下添加一个配置文件：`<software-name>.service`

> 如果 `/usr/lib/systemd/system/` 不存在，可考虑使用 `/lib/systemd/system/` 或 `/etc/systemd/system/`

配置文件的内容说明：
```config
[Unit]: 服务的启动顺序与依赖关系
Description: 当前服务的简单描述
After: 当前服务（<software-name>.service）需要在这些服务启动后，才启动
Before: 和 After 相反，当前服务需要在这些服务启动前，先启动
Wants：表示当前服务"弱依赖"于这些服务。即当前服务依赖于它们，但是没有它们，当前服务也能正常运行。
Requires: 表示"强依赖"关系，即如果该服务启动失败或异常退出，那么当前服务也必须退出。


[Service] 服务运行参数的设置
Type=forking  后台运行的形式
PIDFile=/software-name/pid   pid文件路径
EnvironmentFile=/xxx/prod.env  通过文件设定环境变量
WorkingDirectory=/xxx/xxx    工作目录
ExecStartPre  启动前要做什么（为启动做准备）
ExecStart  服务的具体运行命令（对非 workingdirectory 的文件，必须用绝对路径！因为 systemd 不使用 shell，也就不查找 PATH）
ExecReload  重载命令
ExecStop  停止命令
ExecStartPre：启动服务之前执行的命令
ExecStartPost：启动服务之后执行的命令
ExecStopPost：停止服务之后执行的命令
RuntimeDirectory=xxxx
RuntimeDirectoryMode=0775
PrivateTmp=True  表示给服务分配独立的临时空间
RestartSec  自动重启当前服务间隔的秒数
Restart  定义何种情况 Systemd 会自动重启当前服务，可能的值包括always（总是重启）、on-success、on-failure 等
# 程序的 user 和 group
User=ryan
Group=ryan


注意：启动、重载、停止命令全部要求使用绝对路径

[Install] 定义如何安装这个配置文件，即怎样做到开机启动。
# Target的含义是服务组，表示一组服务。
WantedBy=multi-user.target
```

**注意，service 文件不支持行内注释！！！注释必须单独一行**

### Type 说明
1. `Type=simple`（默认值）：systemd认为该服务将立即启动。服务进程不会fork。如果该服务要启动其他服务，不要使用此类型启动，除非该服务是socket激活型。

1. `Type=forking`：systemd认为当该服务进程fork，且父进程退出后服务启动成功。对于常规的守护进程（daemon），除非你确定此启动方式无法满足需求，使用此类型启动即可。使用此启动类型应同时指定 PIDFile=，以便systemd能够跟踪服务的主进程。

1. `Type=oneshot`：这一选项适用于只执行一项任务、随后立即退出的服务。可能需要同时设置 RemainAfterExit=yes使得systemd在服务进程退出之后仍然认为服务处于激活状态

1. `Type=notify`：与 Type=simple相同，但约定服务会在就绪后向systemd发送一个信号。这一通知的实现由 libsystemd-daemon.so提供。

1. `Type=dbus`：若以此方式启动，当指定的 BusName 出现在DBus系统总线上时，systemd认为服务就绪。

更详细的见 [Systemd 入门教程：命令篇 - 阮一峰](http://www.ruanyifeng.com/blog/2016/03/systemd-tutorial-commands.html)。

### 配置举例

比如 shadows*ks Server Service，的配置文件 `ss-server.service` 的内容为：
```config
[Unit]
Description=ss Server Service
After=network.target

[Service]
Type=simple
User=nobody
ExecStart=/usr/bin/ssserver -c /etc/ss/ss.json -d start
ExecStop=/usr/bin/ssserver -c /etc/ss/ss.json -d stop

[Install]
WantedBy=multi-user.target
```

而 enginx 的配置文件 `nginx.service` 的内容是：
```config
[Unit]
Description=nginx - high performance web server
After=network.target remote-fs.target nss-lookup.target

[Service]
Type=forking
ExecStart=/usr/local/nginx/sbin/nginx -c /usr/local/nginx/conf/nginx.conf
ExecReload=/usr/local/nginx/sbin/nginx -s reload
ExecStop=/usr/local/nginx/sbin/nginx -s stop

[Install]
WantedBy=multi-user.target
```

### 服务的启动、关闭

```
systemctl enable ss-server.service  # 启用服务，即开机自动启动
systemctl disable ss-server.service  # 取消服务，取消开机启动

systemctl start ss-server.service   # 启动服务
systemctl stop ss-server.service   # 停止服务

systemctl restart ss-server.service   # 重启服务(stop + start)
systemctl reload ss-server.service   # 服务不 stop，直接加载配置更新等（对应 ExecReload）

# 检查状态
systemctl status ss-server.service -l

systemctl list-units --type=service  # 查看所有服务
```

### 参考

- [systemd.exec 中文手册](http://www.jinbuguo.com/systemd/systemd.exec.html)
- [Systemd 入门教程：命令篇 - 阮一峰](http://www.ruanyifeng.com/blog/2016/03/systemd-tutorial-commands.html)
- [Systemd(Service文件)详解](https://blog.csdn.net/Mr_Yang__/article/details/84133783)
- [ss - aur](https://www.archlinux.org/packages/community/any/ss/)
- [systemctl 设置自定义服务管理（以nginx为例）](https://segmentfault.com/a/1190000009723940)