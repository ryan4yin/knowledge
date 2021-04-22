## 前言

如果要在Linux 上设置一个开机自启，出现问题自动重启，并且有良好日志的程序，比较流行的方法有 supervisord、systemd，除此之外，还有 upstart、runit 等类似的工具。
但是自从 systemd 被 ubuntu、centos 等主流 Linux 发行版应用以来，systemd 渐渐成为主流方案。

### 配置说明

要自定义一个服务，需要在 `/usr/lib/systemd/system/` 下添加一个配置文件：`<software-name>.service`

> 如果 `/usr/lib/systemd/system/` 不存在，可考虑使用 `/lib/systemd/system/` 或 `/etc/systemd/system/`

> `ExecXXX` 中的命令，均可以正常使用转义字符以及环境变量插值语法，比如用 `\` 结尾表示换行，用 $Xxx 获取环境变量。

配置文件的内容说明：
```conf
[Unit]: 服务的启动顺序与依赖关系
Description: 当前服务的简单描述
After: 当前服务（<software-name>.service）需要在这些服务启动后，才启动
Before: 和 After 相反，当前服务需要在这些服务启动前，先启动
Wants：表示当前服务"弱依赖"于这些服务。即当前服务依赖于它们，但是没有它们，当前服务也能正常运行。
Requires: 表示"强依赖"关系，即如果该服务启动失败或异常退出，那么当前服务也必须退出。


[Service] 服务运行参数的设置
Type=forking  后台运行的形式
PIDFile=/software-name/pid   pid文件路径
EnvironmentFile=/xxx/prod.env  通过文件设定环境变量，注意这东西不支持环境变量的插值语法 ${xxx}
WorkingDirectory=/xxx/xxx    工作目录
ExecStartPre  为启动做准备的命令
ExecStart  服务的具体运行命令（对非 workingdirectory 的文件，必须用绝对路径！
ExecReload  重载命令，如果程序支持 HUP 信号的话，通常将此项设为 `/bin/kill -HUP $MAINPID`
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

Type 感觉是整个配置文件里面最不好理解的一个配置项，它的实际作用就是：**告诉 systemd 你的 Service 是如何启动的**

1. `Type=simple`（默认值）：`ExecStart` 命令会立即启动你的服务，并且持续运行，不会退出。

2. `Type=forking`：`ExecStart` 命令会 fork 出你的服务主进程，然后正常退出。使用此 Type 时应同时指定 `PIDFile=`，systemd 使用它跟踪服务的主进程。

3. `Type=oneshot`：`ExecStart` 命令。可能需要同时设置 `RemainAfterExit=yes` 使得 `systemd` 在服务进程退出之后仍然认为服务处于激活状态

4. `Type=notify`：与 `Type=simple` 相同，但约定服务会在就绪后向 systemd 发送一个信号，以表明自己已经启动成功。
   - 细节：systemd 会创建一个 unix socket，并将地址通过 $NOTIFY_SOCKET 环境变量提供给服务，同时监听该 socket 上的信号。服务可以使用 systemd 提供的 C 函数 `sd_notify()` 或者命令行工具 `systemd-notify` 发送信号给 systemd.
   - 因为多了个 notify 信号，所以这一 Type 要比 simple 更精确一点。但是需要服务的配合，

5. `Type=dbus`：若以此方式启动，当指定的 BusName 出现在 DBus 系统总线上时，systemd 认为服务就绪。

6. `Type=idle`：没搞明白，不过通常也用不到。

更详细的见 [Systemd 入门教程：命令篇 - 阮一峰](http://www.ruanyifeng.com/blog/2016/03/systemd-tutorial-commands.html)。

### 配置举例

比如 shadowsocks Server Service，的配置文件 `ss-server.service` 的内容为：
```conf

[Unit]
Description=shadowsocks server
After=network.target auditd.service

[Service]
Type=forking
ExecStart=/usr/local/bin/ssserver -c /etc/shadowsocks.json --user shadowsocks --pid-file /var/run/shadowsocks.pid -d start
ExecStop=/usr/local/bin/ssserver -c /etc/shadowsocks.json --user shadowsocks --pid-file /var/run/shadowsocks.pid -d stop
PIDFile=/var/run/shadowsocks.pid
Restart=always
RestartSec=4

[Install]
WantedBy=multi-user.target
```

而 enginx 的配置文件 `nginx.service` 的内容是：
```conf
[Description=The NGINX HTTP and reverse proxy server
After=syslog.target network-online.target remote-fs.target nss-lookup.target
Wants=network-online.target

[Service]
Type=forking
PIDFile=/run/nginx.pid
ExecStartPre=/usr/sbin/nginx -t
ExecStart=/usr/sbin/nginx
ExecReload=/usr/sbin/nginx -s reload
ExecStop=/bin/kill -s QUIT $MAINPID
PrivateTmp=true

[Install]
WantedBy=multi-user.target
```

为了使用环境变量插值，而使用 sh 启动的 etcd 服务，它的 `etcd.service` 配置如下:

```conf
[Unit]
Description=etcd key-value store
Documentation=https://github.com/etcd-io/etcd
After=network.target

[Service]
Type=simple
# EnvironmentFile 不支持使用 ${xxx} 变量插值，这里不适合使用
# EnvironmentFile=/data/etcd.env
# -a 表示传递环境变量
ExecStart=/bin/bash -ac '. /data/etcd.env; /data/bin/etcd'
Restart=always
RestartSec=5s
LimitNOFILE=40000

[Install]
WantedBy=multi-user.target
```

或者你把需要插值的内容移到 `ExecStart` 命令中，此命令能正常使用插值语法:

```conf
[Unit]
Description=etcd key-value store
Documentation=https://github.com/etcd-io/etcd
After=network.target

[Service]
Type=notify
EnvironmentFile=/data/etcd.env
# ExecXXX 的命令中是可以使用 ${Xxx} 插值语法的
ExecStart=/data/bin/etcd \
    --initial-advertise-peer-urls http://${THIS_IP}:2380 \
    --listen-peer-urls http://${THIS_IP}:2380 \
    --advertise-client-urls http://${THIS_IP}:2379 \
    --listen-client-urls http://${THIS_IP}:2379 \
    --initial-cluster "${NAME_1}=http://${HOST_1}:2380,${NAME_2}=http://${HOST_2}:2380,${NAME_3}=http://${HOST_3}:2380"
Restart=always
RestartSec=5s
LimitNOFILE=40000

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

- [Systemd 入门教程：命令篇 - 阮一峰](http://www.ruanyifeng.com/blog/2016/03/systemd-tutorial-commands.html)
- [systemd.exec 中文手册](http://www.jinbuguo.com/systemd/systemd.exec.html)
- [第十七章、認識系統服務 (daemons) - 鸟哥的 Linux 私房菜](https://linux.vbird.org/linux_basic/centos7/0560daemons.php)