# Linux 服务器配置

## 镜像源

请选择对应 OS 的镜像源设置命令：
```shell
# alpine
cp /etc/apk/repositories /etc/apk/repositories.bak
sed -i "s@dl-cdn.alpinelinux.org@mirrors.aliyun.com@g" /etc/apk/repositories
# debian
cp /etc/apt/sources.list /etc/apt/sources.list.bak
sed -i "s@\(deb\|security\).debian.org@mirrors.aliyun.com@g" /etc/apt/sources.list
# ubuntu
cp /etc/apt/sources.list /etc/apt/sources.list.bak
sudo sed -i 's@\(archive\|security\).ubuntu.com@mirrors.aliyun.com@g' /etc/apt/sources.list

# ubuntu/debian 切换 https 源
apt-get install -y --no-install-recommends ca-certificates apt-transport-https
sed -i "s@http://@https://@g" /etc/apt/sources.list
```


## 网络设置

对物理机，可以编写通用脚本设置静态 IP、DNS 等。
不同发行版的网络配置方法也不同，要注意区分：

1. Ubuntu: 新版现在已经使用 netplan 进行配置了，配置文件是 `/etc/netplan/xxx.yaml`
1. CentOS7: 配置文件是 `/etc/sysconfig/network-scripts/ifcfg-<interface-name>`

Ubuntu netplan 配置，修改后通过命令 `sudo netplan apply` 使配置生效：
```yaml
# cat /etc/netplan/50-cloud-init.yaml
network:
    ethernets:
        ens33:  # 网卡名称
            addresses:  # 静态 IP 和网段
            - 192.168.1.111/24
            gateway4: 192.168.1.1  # ipv4 默认网关
            nameservers:  # DNS 服务器
                addresses:
                - 114.114.114.114
    version: 2
```

CentOS7 网络配置，修改后通过命令 `systemctl restart network` 使配置生效：
```conf
#  cat /etc/sysconfig/network-scripts/ifcfg-ens33
TYPE=Ethernet
PROXY_METHOD=none
BROWSER_ONLY=no
BOOTPROTO=static  # 使用静态 IP
DEFROUTE=yes
IPV4_FAILURE_FATAL=no
IPV6INIT=yes
IPV6_AUTOCONF=yes
IPV6_DEFROUTE=yes
IPV6_FAILURE_FATAL=no
IPV6_ADDR_GEN_MODE=stable-privacy
NAME=ens33
UUID=1bfd36ad-a80b-48c0-9cdb-b28bcf281e27
DEVICE=ens33
ONBOOT=yes
IPADDR=192.168.1.111  # 静态 IP
PREFIX=24             # 网段
GATEWAY=192.168.1.1   # 默认网关
DNS1=114.114.114.114  # DNS 服务器
# DNS2=
```

对虚拟机，可以在打包 ova 前首先使用 `apt`/`yum` 安装好 open-vm-tools，
然后直接使用 terraform 的 vsphere 等插件从 ova 模板新建虚拟机。
新建虚拟机时可以直接通过 terraform 的配置文件设置好虚拟机的硬件和网络参数。
这种方式对 ubuntu/centos 都有效，运维不需要自己去处理各 linux 发行版网络配置的差异。

## Swap 分区设置

- [Linux Server Swap 分区设置](https://www.cnblogs.com/kirito-c/p/12058159.html)

## 查看文件句柄数

已用文件句柄数：

```shell
lsof | wc -l
```

可用文件句柄数：

```shell
ulimit -n
```

## Linux 系统参数设置（ulimit/sysctl）


为了让应用程序能发挥出最高的效率，我们经常需要调整一部分 Linux 系统参数。
或者是通过提高内存使用率来提升性能，或者是提升 TCP 连接数以提升网络性能，等等。

Linux 系统参数的修改主要包含两个部分：

1. `ulimit`：linux shell 的内建命令，它具有一套参数集，用于对 shell进程 及其 子进程 进行 资源限制。（退出 shell 后失效）
    - 例如用户同时运行了两个shell终端进程，只在其中一个环境中执行了ulimit – s 100，则该 shell 进程里创建文件的大小会有相应的限制，而另一个 shell 终端包括其上运行的子程序都不会受其影响。
      因此 docker-compose.yml 中可以直接设定 ulimit 参数。因为这个参数是 per-process 的。
    - `docker-compose.yaml` 中有一套完整的参数用于控制 ulimit 限制。
2. `sysctl`：临时修改整个系统的内核参数（重启后失效）
    - 另外 linux 还有一个 /proc 文件系统，也是 Linux 内核提供的，用于临时查看/修改内核参数的机制，可通过修改文件内容临时修改内核参数。它和 sysctl 功能基本一致。
    - docker 和宿主机共用内核，因此直接修改宿主机的 sysctl 参数，在容器内也会生效。
    - docker-compose 只支持设置一部分 sysctl 参数。所有支持的参数见 [Docker - Configure namespaced kernel parameters (sysctls) at runtime](https://docs.docker.com/engine/reference/commandline/run/#configure-namespaced-kernel-parameters-sysctls-at-runtime) 和 [docker-compose - sysctls](https://docs.docker.com/compose/compose-file/#sysctls)

上述两个命令都是临时修改，系统重启后又需要重新设置。要想做到永久修改，需要修改它们对应的默认配置文件：

1. `/etc/security/limits.conf`: ulimit 的默认配置
2. `/etc/sysctl.conf`: sysctl 的默认配置

关于这两个配置的详细说明，参见 [ulimit、limits.conf、sysctl和proc文件系统](https://www.jianshu.com/p/20a2dd80cbad)

对系统参数最敏感的，应该是 数据库/缓存/搜索引擎 这些应用。
具体而言，不同的服务器/应用对系统参数的要求也不尽相同，需要具体环境具体分析。


### 通用配置：增加 TCP 连接数

虽说具体的参数配置需要具体情况具体分析，但是有一项配置是肯定要设的，那就是 TCP 连接数。

几乎所有的服务器都是依赖网络提供服务的，绝大多数程序又是使用 TCP 协议。而 Linux 目前默认的配置（打开的文件描述符上限才 1024），完全不够用。

因此我们修改下基础镜像的这个参数，修改 `/etc/security/limits.conf` 文件末尾的这几个参数：

```conf
# 打开文件描述符的最大数目（linux 中一切皆文件，连接也是一个被打开的文件）
# 对应 ulimit -n 655350
root  soft  nofile  655350
root  hard  nofile  655350  
```

以及 `/etc/sysctl.conf` 中的如下参数（或者直接在末尾添加也行）：

```
# 增大最大连接数
net.core.somaxconn = 50000
# 只要还有内存的情况下，就不使用 swap 交换空间
vm.swappiness = 0
```


## OS 特定的配置

### Ubuntu：修改 /etc/cloud/cloud.cfg

ubuntu 1804 开始自带 cloud-init，这个工具默认情况下会使我们修改 `/etc/hostname` 失效，也就是无法修改主机名称！

但是 kubernetes 的节点必须具有不同的主机名，而且用主机名表示该机器的用途也能方便管理。

我们需要修改 cloud-init 的配置文件 /etc/cloud/cloud.cfg 文件，将里面的 `preserve_hostname` 改成 false，这样才能修改主机名称。


## 参考

- [Linux 系统参数调整：ulimit 与 sysctl](https://www.cnblogs.com/kirito-c/p/12254664.html)
- [ulimit、limits.conf、sysctl和proc文件系统](https://www.jianshu.com/p/20a2dd80cbad)
- [Rancher - 基础环境配置](https://docs.rancher.cn/rancher2x/install-prepare/basic-environment-configuration.html)
- [最佳实践 - 主机 OS 调优](https://docs.rancher.cn/rancher2x/install-prepare/best-practices/os.html)

- [一台机器最多能撑多少个TCP连接? 今天掰扯清楚！](https://zhuanlan.zhihu.com/p/290651392)
