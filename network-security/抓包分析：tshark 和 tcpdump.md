# 抓包分析

在进行远程网络抓包分析时，我们通常的做法是：

1. 使用 `tcpdump` 在远程主机上抓包，保存为 pcap 文件。
2. 将 pcap 文件拷贝到本地，使用 wireshark 对其进行分析。

另外 `wireshark` 也提供一个命令行的版本 `tshark`，命令行参数和 tcpdump 很相似，但是它功能更强大一些——能直接解析上百种协议。比如直接在命令行显示 http 内容：

```shell
tshark -i eth0 -x tcp port 80 -R http
```

不过我们一般都是将 pcap 文件拷到本地，所以 tcpdump 用的应该是最多的。

## tcpdump 常用命令

待续

## WireShark 远程抓包

待续

## 参考

- [Tracing network traffic using tcpdump and tshark](https://techzone.ergon.ch/tcpdump)