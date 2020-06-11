## socat(socket cat) 和 netcat(network cat)

netcat 是一个历史悠久的网络工具包，被称作 TCP/IP 的瑞士军刀，各大 Linux 发行版中都被默认安装。但是已经很久没更新了。(最新的是 2004 年。。)

而 socat，官方文档描述它是 `"netcat++" (extended design, new implementation)`，项目比较活跃，kubernetes-client(kubectl) 底层就是使用的它做各种流量转发。

## 参考

- [用好你的瑞士军刀/netcat - 韦易笑 - 知乎](https://zhuanlan.zhihu.com/p/83959309)
- [socat - Multipurpose relay](http://www.dest-unreach.org/socat/)
