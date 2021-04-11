# Linux 中的 `ip` 命令及 `ss` 命令

现在较新版本的 Ubuntu 和 CentOS 都已经使用 `iproute2` 替换掉了 `net-tools`，
如果你还需要使用陈旧的 `route` `netstat` `ifconfig` 等命令，需要手动安装 `net-tools`。

但是我们显然应该改用新的 `iproute2` 了，它提供了 `ip addr` `ip link` `ip route` `ss` 等命令来替换掉曾经由 `net-tools` 提供的一堆繁杂的命令。 

待续。。建议直接看参考文档

## 参考

- [iproute2 对决 net-tools](https://linux.cn/article-4326-1.html)
