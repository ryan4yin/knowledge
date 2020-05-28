# 抓包分析

抓包分析工具主要有两种：

1. http/https 抓包工具：mitmproxy/fiddler 都属于这一类，用于分析 http 非常方便。但是只支持 http/https，有局限性。
2. tcp/udp/icmp 等网络层的数据嗅探：tcpdump/tshark 都属于这一类，网络故障分析等场景常用。

这里主要介绍如何使用 tcpdump + wireshark 进行远程实时抓包分析。
而 mitmproxy 抓包和 wireshark 本地抓包都相当简单，就不介绍了。

>P.S. tshark 是 wireshark 的命令行版本，用法 tcpdump 非常相似。

## tcpdump + ssh + wireshark 远程实时抓包

在进行远程网络抓包分析时，我们通常的做法是：

1. 使用 `tcpdump` 在远程主机上抓包，保存为 pcap 文件。
2. 将 pcap 文件拷贝到本地，使用 wireshark 对其进行分析。

但是这样做没有时效性，而且数据拷贝来去也比较麻烦。

考虑使用流的方式，在远程主机上使用 `tcpdump` 抓包，本地使用 `wireshark` 进行实时分析。

使用 ssh 协议进行流式传输的示例如下：

```shell
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
# 1. 在 adb shell 里使用 tcpdump 抓包
tcpdump -i wlan0 -s0 -w - | nc -l -p 11111

# 2. 在本机使用 adb forward 将本机的 11111 端口和手机的 11111 端口绑定
adb forward tcp:11233 tcp:11233

# 3. 直接从本机的 11111 端口读取数据，提供给 wireshark
nc localhost 11111 | wireshark -k -S -i -
```

如果需要对 Kubernetes 集群中的容器进行抓包，推荐直接使用 [ksniff](https://github.com/eldadru/ksniff)!

## Windows 系统

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


## 参考

- [Tracing network traffic using tcpdump and tshark](https://techzone.ergon.ch/tcpdump)
- [Android remote sniffing using Tcpdump, nc and Wireshark](https://blog.dornea.nu/2015/02/20/android-remote-sniffing-using-tcpdump-nc-and-wireshark/)
- [聊聊tcpdump与Wireshark抓包分析](https://www.jianshu.com/p/a62ed1bb5b20)