## Socket 状态变迁图

![](https://img2018.cnblogs.com/blog/968138/202002/968138-20200202132332451-1115949935.png)

## 命令行查看方法

查看 socket 信息可以帮我们回答下列问题：

1. 我的程序是不是真的在监听我指定的端口？
1. 我的程序是在监听 127.0.0.1（本机），还是在监听 0.0.0.0（整个网络）
1. 进程们分别在使用哪些端口？
1. 我的连接数是否达到了上限？

我们使用 ss （socket statistics）命令来查看 socket 信息（CentOS/Ubuntu 已经使用 `ss` 替换了 `netstat`，推荐使用 ss）：

```
# 查看 socket 连接的统计信息
# 主要统计处于各种状态的 tcp sockets 数量，以及其他 sockets 的统计信息
ss --summary
ss -s  # 缩写

# 查看哪个进程在监听 80 端口
# --listening 列出所有正在被监听的 socket
# --processes 显示出每个 socket 对应的 process 名称和 pid
# --numeric 直接打印数字端口号（不解析协议名称）
ss --listening --processes --numeric | grep 80
ss -nlp | grep 80  # 缩写
ss -lp | grep http  # 解析协议名称，然后通过协议名搜索监听

## 使用过时的 netstat
### -t tcp
### -u udp
netstat -tunlp | grep ":80"

# 查看 sshd 当前使用的端口号
ss --listening --processes | grep sshd
## 使用过时的 netstat
netstat -tunlp | grep <pid>  # pid 通过 ps 命令获得

# 列出所有的 tcp sockets，包括所有的 socket 状态
ss --tcp --all

# 只列出正在 listen 的 socket
ss --listening

# 列出所有 ESTABLISHED 的 socket（默认行为）
ss

# 统计 TCP 连接数
ss | grep ESTAB | wc -l

# 列出所有 ESTABLISHED 的 socket，并且给出连接的计时器
ss --options

# 查看所有来自 192.168.5 的 sockets
ss dst 192.168.1.5

# 查看本机与服务器 192.168.1.100 建立的 sockets
ss src 192.168.1.5

# 查看路由表
routel
```

TCP 连接数受 Linux 文件描述符上限控制，可以通过如下方法查看已用文件句柄的数量。

```shell
# 已用文件描述符数量
lsof | wc -l
# 文件描述符上限
ulimit -n 
```

## 查看 Docker 容器的 socket 信息

Docker 容器有自己的 namespace，直接通过宿主机的 ss 命令是查看不到容器的 socket 信息的。

比较直观的方法是直接通过 `docker exec` 在容器中通过 ss 命令。但是这要求容器中必须自带 ss 等程序，有的精简镜像可能不会自带它。

因此用的更多的方法，有两种：

### 1. 通过 nsenter 直接在目标容器的 namespace 中使用宿主机的命令。

这个适合单机 docker 的网络诊断，用法如下：

```
# 1. 查询到容器对应的 pid
PID=$(docker inspect --format {{.State.Pid}} <container_name_or_ID>)

# 2. nsenter 通过 pid 进入容器的 network namespace，执行 ss 查看 socket 信息
nsenter --target $PID --net ss -s
```

`nsenter` 这个工具貌似是 docker 自带的，只要装了 docker，ubuntu/centos 都可以直接使用这个命令。

### 2. 使用专用的网络诊断镜像进行容器网络诊断（SideCar）

这种方式一般用于容器集群的诊断，K8s 社区提供了一个工具 [kubectl-debug](https://github.com/aylei/kubectl-debug/)，以这种 SideCar 的方式进行容器诊断。详情参见它的文档。


## Windows 系统查看 socket 信息

Windows 系统没有 `ss`，但是自带 `netstat`，该命令和 Linux 下的 `netstat` 有一定差别，具体使用方法如下：

```shell
netstat -?  # 查看使用帮助，很清晰易懂

# 查看那个进程在监听 80 端口，最后一列是进程的 Pid
netstat -ano | findstr 80        # windows 命令
netstat -ano | select-string 80  # powershell 命令

# 不仅列出 Pid，还给出 Pid 对应的可执行文件名称（需要管理员权限）
netstat -ano -b | select-string 80  # powershell 命令

# 列出所有 ESTABLISHED 的 socket（默认行为）
netstat

# 列出所有正在监听的端口
netstat -ano | findstr LISTENING

# 只列出 TCP 连接
netstat -ano -p TCP


# 查看路由表
route -?  # 查看使用帮助，很清晰易懂
route print    # 查看所有路由信息
route print -4  # 仅 ipv4
```

比如我们遇到端口占用问题时，就可以通过上述命令查找到端口对应的 Pid，然后使用 `kill <Pid>` 命令（powershell `stop-process` 的别名）杀死对应的进程。

## 参考

- [如何在 Linux 中查看进程占用的端口号](https://zhuanlan.zhihu.com/p/45920111)
- [github - nsenter](https://github.com/jpetazzo/nsenter#how-do-i-use-nsenter)