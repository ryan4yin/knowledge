Ubiquiti 公司的 EdgeRoute-X 是一款有线广受好评的专业路由器，稳定可靠。
它使用的 EdgeOS frok 自 vyatta 项目，底层是 Debian 系统。可玩性很高，甚至能直接使用 `apt-get` 安装 debian 包。


## 一、基础配置

### 1. 物理端口规划：网段划分

主要是要事先规划好，设置的时候挺简单的，UI 操作流程网上都能搜到。

在每个物理端口上，都可以设定一个独立的网段，`Address` 的参数格式为 `192.168.3.1/24`，即 `<网关>/掩码`。

也可以使用 `switch` 将多个物理端口桥接到一起。

待补充。

### 2. PPPoe 拨号、DHCP、DNS

DHCP 就填下 IP 段、DNS1/DNS2、默认网关就 ok 了。

DNS1 填内网 DNS 服务器地址，DNS2 可以填公网的（114.114.114.114）。
这种配置方法下如果 DNS1（内网 DNS）挂掉，用户仍然能够正常访问公网域名（DNS2），只是解析速度会变慢（因为每次都会先尝试连接 DNS1）。

PPPoe 拨号也很简单，填下账号密码就 OK 了。

## 三、配置 Dynamic DNS

如果你的 WAN 口被供应商分配了动态的公网 IP，可以通过配置 DDNS 提供一个固定的公网入口。
这样 IP 会动态变更，但是域名始终固定，就可以在内网运行公网可访问的 Web 应用了。

ER-X 自身支持的 DDNS 服务商太少，不过它使用的是基于 debian 的 OS，可以直接通过 ssh 登入 OS 内进行 DDNS 配置。
目前自带 python2.7，如果要安装 python 依赖，需要先通过 [get-pip.py](https://pip.pypa.io/en/stable/installing/#installing-with-get-pip-py) 安装好 pip.

- [阿里云 DDNS 客户端 - 非官方](https://github.com/rfancn/aliyun-ddns-client)

上面的客户端使用 python 编码，需要通过 `python-pip` 安装一些依赖。安装方法见下一小节。

## 四、EdgeOS 安装 Debian 包

EdgeOS 是基于 Debian 定制的一个路由器 OS，它可以直接通过 `apt-get` 安装各种依赖。

首先通过 SSH 协议登入 EdgeOS 控制台：

```shell
# 就和登录别的远程主机一样的操作。使用用户名和主机 IP 地址进行登录。
ssh admin@192.168.1.1
# 输入管理员密码即可成功登录。
```

接下来进行 `apt-get` 相关配置：

```shell
# 以下内容基于 EdgeOS v2.0(deiban 9 strech)，更低的版本请将 stretch 修改为 Wheezy(debian 7)

# 1. 入 config edit 模式
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

# 如果提示空间不足，先进行一下空间清理。再重新执行安装命令
sudo apt-get clean  # 清理 apt-get 缓存
# 如果你升级了固件，edgeos 默认会保留旧固件，这会占用大量空间。
delete system image  # 清理旧固件
```

需要注意的是，ER-X 的存储空间只有 256M，非常小。因此尽量不要装任何可选的组件，能省则省。。
比如如果你写个 python 脚本需要安装 `requests` 等第三方依赖，千万别装 `python-pip`，这东西一装就要 160M 的空间。。
替代的方法有：

1. 通过 `apt-get` 安装：`sudo apt-get install python-requests`。
2. 通过 `setup.py` 安装：手动下载依赖，然后通过 `setup.py` 进行安装。这个比较麻烦。


参考：

- [EdgeRouter - Add Debian Packages to EdgeOS](https://help.ui.com/hc/en-us/articles/205202560-EdgeRouter-Add-Debian-Packages-to-EdgeOS)

## 五、策略路由

- 参考文档：[EdgeRouter端口策略路由配置案例](https://bbs.ui.com.cn/t/edgerouter/42290)

源地址（Source Address）策略路由，就是让不同源 IP 的流量路由到不同的接口。主要场景有如下几种：

1. 在多 WAN(Wire Area Network) 场景下（EdgeRoute-X 支持多 WAN），我们可能会希望不同网段的流量走不同的 WAN 出去。
    - 比如一个网段用电信网，另一个网段用联通网。

另外还有目标地址策略路由，顾名思义，就是根据 Destination Address/Port 进行路由。

### 「策略路由」配置

>configure 中所有的命令，都可以通过 [tab] 补全或者查看帮助！非常方便。

这个策略配置在 Web UI 上没有展示面板，需要通过 ssh 进入 Terminal，通过如下命令查看：

```shell
configure  # 进入 config edit 模式
# 查看所有的策略路由设置
show firewall modify
# 查看所有静态路由表设置
show protocols static table

# 1. 创建一条新路由，走 pppoe0 号接口（出去）
set protocols static table 11 description "route all traffic to pppoe0"
set protocols static table 11 interface-route 0.0.0.0/0 next-hop-interface pppoe0
## 或者也可以通过 ip 地址指定路由的下一跳
set protocols static table 12 description "route all traffic to 192.168.2.1"
set protocols static table 12 route 0.0.0.0/0 next-hop 192.168.2.1
# 2. 切换到 firewall.modify 中
edit firewall modify
## 2.1 根据 source address 选择路由表
## 这里的 `traffic_out` 只是一个配置名称，只要求它是唯一的
set traffic_out description "route traffic to wan"  # 简要说明下配置的用途
set traffic_out rule 10 description "route all traffic to pppoe0"  # 其中的 10 是一个 id，只要求它是一个唯一的数字。
set traffic_out rule 10 source address 192.168.5.0/24
set traffic_out rule 40 modify table 11  # 让被匹配的流量使用 id 为 11 的路由（也就是从 pppoe0 出去）

# 3. 指定哪些接口需要使用 traffic_out 这个策略路由配置
# 这里的 `in` 匹配穿透该接口的流量，也就是说会过滤掉访问接口本身的流量（比如访问路由器主页）。
set interfaces ethernet eth1 firewall in modify traffic_out
set interfaces ethernet eth2 firewall in modify traffic_out

# 4. 保存修改
commit ; save

# 5. 查看 ip route 路由表信息，验证配置正确性
show ip route
# 查看 modify 防火墙的统计信息
show firewall modify statistics
```

## 六、防火墙与网络之间的流量限制

### 1. WAN 的 Firewall Policy

顾名思义，这就是在 WAN 端口上配置的防火墙。它可以防止外部的异常流量进入路由器/LAN，它是一个完全针对外部流量的防火墙策略。

EdgeOS 的默认配置会设置两条 WAN 防火墙策略：

1. `WAN_IN`(WAN to LAN): 匹配穿透路由器的流量，分成两种流量类型：无效流量、相关的/已建立连接的流量。
2. `WAN_LOCAL`(WAN to LOCAL): 匹配以路由器本身为目的地的流量，流量也可分成上述两种类型分别处理。

这个「相关的流量」，大概就是 `port-forwarding`/`dnat` 处理过的流量。（个人理解）
而已「建立连接的流量」就很好理解了，是状态为「Estabilished」的 TCP 流量。

参考：

- [EdgeRouter - How to Create a WAN Firewall Rule](https://help.ui.com/hc/en-us/articles/204962154-EdgeRouter-How-to-Create-a-WAN-Firewall-Rule)

### 2. LAN 的 Firewall Policy

这个策略可以针对各个 LAN 设置防火墙策略，限制各 LAN 的互访。
比如设置一个 Wireless 的 Guest 网络，只允许该网段用户使用 WAN，并访问有限的几个不重要的服务器。

参考：

- [EdgeRouter - How to Create a Guest\LAN Firewall Rule](https://help.ui.com/hc/en-us/articles/218889067-EdgeRouter-How-to-Create-a-Guest-LAN-Firewall-Rule)

## 七、SNAT 和 DNAT 设置

待续

## 参考

- [EdgeRoute 系列官方文档](https://help.ui.com/hc/en-us/sections/360008075214-EdgeRouter)
