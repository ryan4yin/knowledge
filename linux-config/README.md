# Linux 服务器配置

为了让应用程序能发挥出最高的效率，我们经常需要调整一部分 Linux 系统参数。

或者是通过提高内存使用率来提升性能，或者是提升 TCP 连接数以提升网络性能，等等。

其中主要涉及的系统参数有两个：

1. ulimit：linux shell 的内建命令，它具有一套参数集，用于对进程及子进程进行资源限制。（退出 shell 后失效）
    - `/etc/security/limits.conf`: ulimit 的默认配置。修改它的值，重启后就永久有效了。
    - `docker-compose.yaml` 中有一套完整的参数用于控制 ulimit 限制。
1. sysctl：临时修改整个系统的内核参数（重启后失效）
    - `/etc/security/limits.conf`: ulimit 的默认配置。修改它同样是重启后永久有效。
    - `docker-compose.yaml` 中也可以修改有限的几个 sysctl 参数。大部分 sysctl 参数需要直接修改宿主机配置。

具体的参数配置，因服务器配置而异，也因应用程序的功能与特性而异。

## 查看文件句柄数

已用文件句柄数：

```shell
lsof | wc -l
```

可用文件句柄数：

```shell
ulimit -n
```

## 通用配置：增加 TCP 连接数

虽说具体的参数配置需要具体情况具体分析，但是有一项配置是肯定要设的，那就是 TCP 连接数。

几乎所有的服务器都是依赖网络提供服务的，绝大多数程序又是使用 TCP 协议。而 Linux 目前默认的配置（打开的文件描述符上限才 1024），完全不够用。


## 参考

- [ulimit、limits.conf、sysctl和proc文件系统](https://www.jianshu.com/p/20a2dd80cbad)