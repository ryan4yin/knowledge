# 抓包分析

抓包分析工具主要有两种：

1. http/https 网络代理工具：[mitmproxy](https://github.com/mitmproxy/mitmproxy)/fiddler 都属于这一类，用于分析 http 非常方便。但是只支持 http/https，有局限性。
2. tcp/udp/icmp 等网络嗅探工具：tcpdump/tshark 都属于这一类，网络故障分析等场景常用。

这里主要介绍如何使用 tcpdump + wireshark 进行远程实时抓包分析。
而 mitmproxy 抓包和 wireshark 本地抓包都相当简单，就不介绍了。

>P.S. tshark 是 wireshark 的命令行版本，用法 tcpdump 非常相似。

## 一、wireshark 的基本用法

WireShark 的 UI 界面如何使用，网上能搜得到各种类型的 wireshark 演示，多看几篇博客就会了。
搜索 [xxx 协议 wireshark 抓包分析] 就能找到各种各样的演示，比如

1. 「gRPC 协议 wireshark 抓包分析」
2. 「WebSocket 协议 wireshark 抓包分析」
3. 「TCP 协议 wireshark 抓包分析」
4. 等等

主要需要介绍的，应该是 wireshark 的数据包过滤器。
wireshark 中有两种包过滤器：

1. 捕获过滤器：在抓包的时候使用它对数据包进行过滤。
1. 显示过滤器：对抓到的所有数据包进行过滤。

显示过滤器是最有用的，下面简要介绍下显示过滤器的语法。

可以直接通过「**协议名称**」进行过滤：

```
# 只看 tcp 流量
tcp
# 只看 http 流量
http

# 使用感叹号（或 not）进行反向过滤
!arp  # 过滤掉所有 arp 数据包
```

也可以通过「**协议名称.协议属性**」和「比较操作符（比如 `==`）」进行更精确的过滤：

```
# 通过 ip 的源地址 src 或 dst 进行过滤
ip.src==192.168.1.33

# 通过 IP 地址（ip.addr）进行过滤（匹配 ip.src 或 ip.dst）
ip.addr==192.168.0.5
# 上一条过滤表达式等价于：
ip.src==192.168.0.5 or ip.dst==192.168.0.5

# 通过 tcp 端口号进行过滤
tcp.port==80
tcp.port>4000

# 通过 http 的 host 属性进行过滤
http.host != "xxx.baidu.com"
# 通过 http.referer 属性进行过滤
http.referer == "xxx.baidu.com"

# 多个过滤器之间用 and、or 进行组合
http.host != "xxx.baidu.com" and http.referer == "xxx.baidu.com"
```

## 二、tcpdump + ssh + wireshark 远程实时抓包

在进行远程网络抓包分析时，我们通常的做法是：

1. 使用 `tcpdump` 在远程主机上抓包，保存为 pcap 文件。
2. 将 pcap 文件拷贝到本地，使用 wireshark 对其进行分析。

但是这样做没有时效性，而且数据拷贝来去也比较麻烦。

考虑使用流的方式，在远程主机上使用 `tcpdump` 抓包，本地使用 `wireshark` 进行实时分析。

使用 ssh 协议进行流式传输的示例如下：

```shell
# eth0 更换成你的机器 interface 名称，虚拟机可能是 ens33
ssh root@some.host "tcpdump -i eth0 -l -w -" | wireshark -k -i -
```

在不方便使用 ssh 协议的情况下（比如容器抓包、Android 抓包），可以考虑使用 `nc`(netcat) 进行数据流的转发：

```shell
# 1. 远程主机抓包：将数据流通过 11111 端口暴露出去
tcpdump -i wlan0 -s0 -w - | nc -l -p 11111

# 2. 本地主机从远程主机的 11111 端口读取数据，提供给 wireshark
nc <remote-host> 11111 | wireshark -k -S -i -
```

如果是抓取 Android 手机的数据，方便起见，可以通过 adb 多进行一次数据转发：

```shell
# 方案一：root 手机后，将 arm 版的 tcpdump 拷贝到手机内进行抓包
# 1. 在 adb shell 里使用 tcpdump 抓 WiFi 的数据包，转发到 11111 端口
## 需要先获取到 root 权限，将 tcpdump 拷贝到 /system/bin/ 目录下
tcpdump -i wlan0 -s0 -w - | nc -l -p 11111

# 2. 在本机使用 adb forward 将手机的 11111 端口绑定到本机(PC)的 11111 端口
adb forward tcp:11111 tcp:11111

# 3. 直接从本机(PC)的 11111 端口读取数据，提供给 wireshark
nc localhost 11111 | wireshark -k -S -i -
## 通过数据转发，本机 11111 端口的数据，就是安卓手机内 tcmpdump 的 stdout 内容。

# 方案二：
# 如果手机不方便 root，推荐 PC 开启 WiFi 热点，手机连上这个热点访问网络。
# 这样手机的数据就一定会走 PC，直接在 PC 上通过 wireshark 抓包就行。
# 如果你只需要简单地抓 http/https 包，请使用 fiddler/mitmproxy
```

如果需要对 Kubernetes 集群中的容器进行抓包，推荐直接使用 [ksniff](https://github.com/eldadru/ksniff)!

## 

### Windows 系统

另外如果你本机是 Windows 系统，要分 shell 讨论：

1. `cmd`: 可以直接使用上述命令。
2. `powershell`: **PowerShell 管道对 `native commands` 的支持不是很好，管道两边的命令貌似是串行执行的，这会导致 wireshark 无法启动！**目前没有找到好的解决方法。。


另外如果你使用 `wsl`，那么可以通过如下命令使 `wsl` 调用 windows 中的 wireshark 进行抓包分析：

```shell
# 添加软链接
sudo ln -s "$(which wireshark.exe)" /usr/local/bin/wireshark
```

添加了上述软链接后，就可以正常地在 `wsl` 中使用前面介绍的所有抓包指令了（包括 [ksniff](https://github.com/eldadru/ksniff)）。
它能正常调用 windows 中的 wireshark，数据流也能正常地通过 shell 管道传输。


## 2. [termshark](https://github.com/gcla/termshark): 直接通过命令行 UI 进行实时抓包分析

有的时候，远程实时抓包因为某些原因无法实现，而把 pcap 数据拷贝到本地分析又比较麻烦。
这时你可以考虑直接使用命令行版本的 `wireshark` UI: [termshark](https://github.com/gcla/termshark)，直接在命令行进行实时的抓包分析。

[kubectl-debug](https://github.com/aylei/kubectl-debug) 默认的调试镜像中，就自带 `termshark`.

## 参考

- [WireShark使用教程](https://zhuanlan.zhihu.com/p/92993778)
- [Tracing network traffic using tcpdump and tshark](https://techzone.ergon.ch/tcpdump)
- [Android remote sniffing using Tcpdump, nc and Wireshark](https://blog.dornea.nu/2015/02/20/android-remote-sniffing-using-tcpdump-nc-and-wireshark/)
- [聊聊tcpdump与Wireshark抓包分析](https://www.jianshu.com/p/a62ed1bb5b20)