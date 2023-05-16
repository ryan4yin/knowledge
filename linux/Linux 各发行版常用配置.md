
## 镜像源

请选择对应 OS 的镜像源设置命令：
```shell
# alpine
cp /etc/apk/repositories /etc/apk/repositories.bak
sed -i "s@dl-cdn.alpinelinux.org@mirrors.bfsu.edu.cn@g" /etc/apk/repositories
# debian
cp /etc/apt/sources.list /etc/apt/sources.list.bak
sed -i "s@\(deb\|security\).debian.org@mirrors.bfsu.edu.cn@g" /etc/apt/sources.list
# ubuntu
cp /etc/apt/sources.list /etc/apt/sources.list.bak
sudo sed -i 's@\(archive\|security\).ubuntu.com@mirrors.bfsu.edu.cn@g' /etc/apt/sources.list

# ubuntu/debian 切换 https 源
apt-get install -y --no-install-recommends ca-certificates apt-transport-https
sed -i "s@http://@https://@g" /etc/apt/sources.list
```

Linux 各发行版及相关配置
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


## 其他常用设置

```
# 改时区
ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime

# 改语言环境
sudo echo 'LANG="en_US.UTF-8"' >> /etc/profile;source /etc/profile
```

## OS 特定的配置

### Ubuntu：修改 /etc/cloud/cloud.cfg

ubuntu 1804 开始自带 cloud-init，这个工具默认情况下会使我们修改 `/etc/hostname` 失效，也就是无法修改主机名称！

但是 kubernetes 的节点必须具有不同的主机名，而且用主机名表示该机器的用途也能方便管理。

我们需要修改 cloud-init 的配置文件 /etc/cloud/cloud.cfg 文件，将里面的 `preserve_hostname` 改成 false，这样才能修改主机名称。


