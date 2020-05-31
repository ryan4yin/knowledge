
## 基础配置

### 端口规划：网段划分、PPPoe 拨号

这个比较简单，有空写。

### 动态 IP DHCP、DNS

DHCP 就填下 IP 段、DNS1/DNS2、默认网关就 ok 了。

DNS1 填内网 DNS 服务器地址，DNS2 可以填公网的（114.114.114.114）。
这种配置方法下如果 DNS1（内网 DNS）挂掉，用户仍然能够正常访问公网域名（DNS2），只是解析速度会变慢（因为每次都会先尝试连接 DNS1）。


## 配置 Dynamic DNS

如果你的 WAN 口被供应商分配了动态的公网 IP，可以通过配置 DDNS 提供一个固定的公网入口。
这样 IP 会动态变更，但是域名始终固定，就可以在内网运行公网可访问的 Web 应用了。

ER-X 自身支持的 DDNS 服务商太少，不过它使用的是基于 debian 的 OS，可以直接通过 ssh 登入 OS 内进行 DDNS 配置。
目前自带 python2.7，如果要安装 python 依赖，需要先通过 [get-pip.py](https://pip.pypa.io/en/stable/installing/#installing-with-get-pip-py) 安装好 pip.

- [阿里云 DDNS 客户端 - 非官方](https://github.com/rfancn/aliyun-ddns-client)

上面的客户端使用 python 编码，需要通过 `python-pip` 安装一些依赖。安装方法见下一小节。

## EdgeOS 安装 Debian 包

EdgeOS 是基于 Debian 定制的一个路由器 OS，它可以直接通过 `apt-get` 安装各种依赖。
方法如下：

```shell
# 以下内容基于 EdgeOS v2.0(deiban 9 strech)，更低的版本请将 stretch 修改为 Wheezy(debian 7)

# 1. 进入设置
configure
# 2. 使用 debian 阿里云镜像源
set system package repository stretch components 'main contrib non-free' 
set system package repository stretch distribution stretch
set system package repository stretch url http://mirrors.aliyun.com/debian
# 3. 保存修改
commit ; save
# 4. 拉取镜像源的索引（这里不能使用 apt-get upgrade!!! 该命令可能会破坏 edgeos 的定制依赖）
sudo apt-get update

# 现在可以正常使用 apt-get 了
sudo apt-cache search dnsutils  # 通过索引搜索依赖
sudo apt-get install dnsutils   # 安装依赖
```

参考：

- [EdgeRouter - Add Debian Packages to EdgeOS](https://help.ui.com/hc/en-us/articles/205202560-EdgeRouter-Add-Debian-Packages-to-EdgeOS)

## 源地址策略路由配置

- 参考文档：[EdgeRouter端口策略路由配置案例](https://bbs.ui.com.cn/t/edgerouter/42290)

源地址策略路由，就是让不同源 IP 的流量路由到不同的端口。主要场景有如下几种：

1. 在多 WAN(Wire Area Network) 场景下（EdgeRoute-X 支持多 WAN），我们可能会希望不同网段的流量走不同的 WAN 出去。
    - 比如一个网段用电信网，另一个网段用联通网。

### 查看与修改「源地址策略路由」配置

这个策略配置在 Web UI 上没有展示面板，需要通过 ssh 进入 Terminal，通过如下命令查看：

```shell
configure  # 进入 config edit 模式
show firewall modify  # 查看所有的源地址策略路由设置
edit firewall         # 切换到 firewall 内部进行策略修改
set modify out rule <rule-id> ...  # 修改策略，每一个子命令都可以通过 [tab] 键补全
```

## 通过 Firewall Policy 限制各网段互访

待续


## 参考

- [EdgeRoute 系列文档](https://help.ui.com/hc/en-us/sections/360008075214-EdgeRouter)