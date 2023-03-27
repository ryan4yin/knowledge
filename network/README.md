# 计算机网络


## 我的网络笔记

- [HTTP 知新](https://www.cnblogs.com/kirito-c/p/10357364.html)

## 网络层次中的哪些是操作系统控制，哪些是我们自己能控制的？

- DNS 解析: 所有的编程语言默认都是使用的 c 标准库 `nslookup` 等接口进行解析。
  - 因为传统的 DNS 协议不加密，而且有可能遇到 DNS 污染，因此目前也有些程序会绕过操作系统的 DNS resolver，使用 HTTPDNS 等新的协议进行 DNS 解析。
- 网络层(IP+路由): 默认都是由操作系统处理的，编程语言通常使用的 TCP/UDP socket 只能在传输层进行处理
  - 要获得更底层协议的控制能力，可以使用 raw socket.
  - raw socket 很强大也很危险，因此通常应该禁用掉容器的 raw socket 能力

## 我的学习资料

学习网络，最重要的是使用 Chrome/Firefox 及 Wireshark 的抓包去实践。

- [计算机网络 - 自顶向下方法](https://book.douban.com/subject/26176870/)
- [优化网络传输性能](https://www.zhihu.com/column/c_1539243008150597632): 目前在字节的网络大佬，包含巨多 TCP 干货内容

## 网络模拟

- [shadow](https://github.com/shadow/shadow): 离散事件网络模拟器，可以直接执行真实的应用。让你可以使用你的笔记本或者服务器，就可以模拟大型分布式网络系统。
- [GNS3](https://github.com/GNS3/gns3-server): 据说是最知名的网络模拟器
