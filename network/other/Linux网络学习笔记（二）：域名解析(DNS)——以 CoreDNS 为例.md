# Linux网络学习笔记（二）：域名解析(DNS)——以 CoreDNS 为例

>个人笔记，观点不一定正确. 适合对 Kubernetes 有一定了解的同学。

## 前言

最近一直在学习 Kubernetes，但是手头没有个自有域名，要测试 ingress 就比较麻烦，每次都是手动改 hosts 文件。。

今天突然想到——K8s 内部就是用 DNS 做的服务发现，我为啥不自己弄一个 DNS 服务器呢？然后所有节点的 DNS 都配成它，这样有需要时直接改这个 DNS 服务器的配置就行， 一劳永逸。

我首先想到的是 群晖/Windows Server 自带的那种自带图形化界面的 DNS 服务器，但是这俩都是平台特定的。

网上搜一圈没找到类似带 UI 的 DNS 工具，搜到的 powerdns/bind 相比 coredns 也没看出啥优势来，所以决定就用 CoreDNS，刚好熟悉一下它的具体使用。

不过讲 CoreDNS 前，我们还是先来熟悉一下 DNS 吧。

## 一、DNS 是个啥？

>没有写得很清楚，不适合初学。建议先通过别的资料熟悉下 DNS。

DNS，即域名系统（Domain Name System），是一项负责将一个 human readable 的所谓域名，转换成一个 ip 地址的协议。

而域名的好处，有如下几项：

1. 域名对人类更友好，可读的字符串总比一串 ip 数字好记。
1. 一个域名可以对应多个 ip，可实现所谓的负载均衡。
1. 多个域名可以对应同一个 ip，以不同的域名访问该 ip，能访问不同的应用。（通过 nginx 做代理实现）

DNS 协议是一个基于 UDP 的应用层协议，它默认使用 53 端口进行通信。
应用程序通常将 DNS 解析委派给操作系统的 DNS Resolver 来执行，程序员对它几乎无感知。

DNS 虽然说一般只用来查个 ip 地址，但是它提供的记录类型还蛮多的，主要有如下几种：

1. `A` 记录：它记录域名与 IPv4 地址的对应关系。目前用的最多的 DNS 记录就是这个。
1. `AAAA` 记录：它对应的是 IPv6，可以理解成新一代的 `A` 记录。以后会用的越来越多的。
1. `NS` 记录：记录 DNS 域对应的权威服务器**域名**，权威服务器域名必须要有对应的 `A` 记录。
    - 通过这个记录，可以将子域名的解析分配给别的 DNS 服务器。
1. `CNAME` 记录: 记录域名与另一个域名的对应关系，用于给域名起别名。这个用得也挺多的。
1. `MX` 记录：记录域名对应的邮件服务器域名，邮件服务器的域名必须要有对应的 `A` 记录。
1. `SRV` 记录：SRV 记录用于提供服务发现，看名字也能知道它和 SERVICE 有关。
    - SRV 记录的内容有固定格式：`优先级 权重 端口 目标地址`，例如 `0 5 5060 sipserver.example.com`
    - 主要用于企业域控(AD)、微服务发现（Kubernetes）

上述的所有 DNS 记录，都是属于将域名解析为 IP 地址，或者另一个域名，这被称做** DNS 正向解析**。
除了这个正向解析外，还有个非常冷门的**反向解析**，基本上只在设置邮件服务器时才会用到。（Kubernetes 可能也有用到）

反向解析主要的记录类型是：**`PTR` 记录**，它提供将 IP 地址反向解析为域名的功能。
而且因为域名是从右往左读的（最右侧是根, `www.baidu.com.`），而 IP 的网段（如 `192.168.0.0/16`）刚好相反，是左边优先。
因此 PTR 记录的“域名”必须将 IP 地址反着写，末尾再加上 `.in-addr.arpa.` 表示这是一个反向解析的域名。（ipv6 使用 `ip6.arpa.`）
拿 baidu.com 的邮件服务器测试一下：
![](https://img2018.cnblogs.com/blog/968138/202002/968138-20200207101308247-1165339332.png)


其他还有些 `TXT`、`CAA` 等奇奇怪怪的记录，就用到的时候自己再查了。

## 二、域名的分层结构

国际域名系统被分成四层：

1. **根域（Root Zone）**：所有域名的根。
    - 根域名服务器负责解析`顶级域名`，给出顶级域名的 DNS 服务器地址。
    - 全世界仅有十三组根域名服务器，这些服务器的 ip 地址基本不会变动。
    - 它的域名是 ""，空字符串。而它的**全限定域名（FQDN）**是 `.`，因为 FQDN 总是以 `.` 结尾。（FQDN 在后面解释，可暂时忽略）
1. **顶级域（Top Level Domains, TLD）**：`.com` `.cn` 等国际、国家级的域名
    - 顶级域名服务器负责解析`次级域名`，给出次级域名的 DNS 服务器地址。
    - 每个顶级域名都对应各自的服务器，它们之间是完全独立的。`.cn` 的域名解析仅由 `.cn` 顶级域名服务器提供。
    - 目前国际 DNS 系统中已有上千个 TLD，包括中文「.我爱你」甚至藏文域名，详细列表参见 [IANA TLD u数据库](http://www.iana.org/domains/root/db)
    - 除了国际可用的 TLD，还有一类类似「内网 IP 地址」的“私有 TLD”，最常见的比如  xxx.local xxx.lan，被广泛用在集群通信中。后面详细介绍
1. **次级域（Second Level Domains）**：这个才是个人/企业能够买到的域名，比如 `baidu.com`
    - 每个次级域名都有一到多个权威 DNS 服务器，这些 DNS 服务器会以 NS 记录的形式保存在对应的顶级域名（TLD）服务器中。 
    - 权威域名服务器则负责给出最终的解析结果：ip 地址(A 记录 )，另一个域名（CNAME 记录）、另一个 DNS 服务器（NS 记录）等。
1. **子域（Sub Domians）**：`*.baidu.com` 统统都是 `baidu.com` 的子域。
    - 每一个子域都可以有自己独立的权威 DNS 服务器，这通过在子域中添加 NS 记录实现。

普通用户通常是通过域名提供商如阿里云购买的次级域名，接下来我们以 `rea.ink` 为例介绍域名的购买到可用的整个流程。

这时阿里云会向该中插入几条 NS 记录，指向阿里云的次级 DNS 服务器（`vip1.alidns.com`）。

1. 你在某域名提供商处购买了一个域名 `rea.ink`
1. 域名提供商向 `.ink` 对应的顶级域名服务器中插入一条以上的 NS 记录，指向它自己的次级 DNS 服务器，如 `dns25.hichina.com.`
1. 你在该域名提供商的 DNS 管理界面中添加 `A` 记录，值为你的服务器 IP。
1. OK 现在 ping 一下 `rea.ink`，就会发现它已经解析到你自己的服务器了。

上述流程中忽略了我大天朝的特殊国情——备案，勿介意。

## 三、DNS 递归解析器：在浏览器中输入域名后发生了什么？

下面的图片拷贝自 Amazon Aws 文档，它展示了在不考虑任何 DNS 缓存的情况下，一次 Web 请求的经过，详细描绘了 DNS 解析的部分。

![](https://img2018.cnblogs.com/blog/968138/202002/968138-20200205165225054-57338322.png)

其中的第 3 4 5 步按顺序向前面讲过的根域名服务器、顶级域名服务器、权威域名服务器发起请求，以获得下一个 DNS 服务器的信息。这很清晰。

图中当前还没介绍的部分，是紫色的 `DNS Resolver`(域名解析器)，也叫 `Recursive DNS resolver`（**DNS 递归解析器**）。 
它本身只负责递归地请求 3 4 5 步中的上游服务器，然后把获取的最终结果返回给客户端，同时将记录缓存到本地以加快解析速度。

这个 DNS 解析器，其实就是所谓的**公共 DNS 服务器**：Google 的 `8.8.8.8`，国内著名的 `114.114.114.114`。

这些公共 DNS 用户量大，缓存了大量的 DNS 记录，有效地降低了上游 DNS 服务器的压力，也加快了网络上的 DNS 查询速度。

接下来使用 `dig +trace baidu.com` 复现一下上述的查询流程（这种情况下 dig 自己就是一个 DNS 递归解析器）：

![](https://img2018.cnblogs.com/blog/968138/202002/968138-20200207101817456-1276700345.png)

另外前面有讲过 DNS 的反向解析，也是同样的层级结构，是从根服务器开始往下查询的，下面拿 baidu 的一个邮件服务器进行测试：

![](https://img2018.cnblogs.com/blog/968138/202002/968138-20200207102331250-71048478.png)

>dig 工具未来可能会被 drill 取代。

### DNS 泛解析通配符 `*`

DNS 记录允许使用通配符 `*`，并且该通配符可匹配任意级数的子域！！！比如 `*.example.com` 就可以匹配所有的一二三四级域名等等，**但是无法匹配 `example.com` 本身！**

### TTL（Time To Live）

上面讲了**公共 DNS 服务器**通过缓存技术，降低了上游 DNS 服务器的压力，也加快了网络上的 DNS 查询速度。

可缓存总得有个过期时间吧！为了精确地控制 DNS 记录的过期时间，每条 DNS 记录都要求设置一个时间属性——TTL，单位为秒。这个时间可以自定义。

任何一条 DNS 缓存，在超过过期时间后都必须丢弃！

## 四、本地 DNS 服务器与私有 DNS 域

这类服务器只在当前局域网内有效，是一个私有的 DNS 服务器，企业常用。一般通过 DHCP 或者手动配置的方式，使内网的服务器都默认使用局域网 DNS 服务器进行解析。该服务器可以只解析自己的私有 DNS 域，而将其他 DNS 域的解析 forward 到公网 DNS 解析器去。

这个私有 DNS 域，会覆盖掉公网的同名域(如果公网上有这个域的话)。
私有 dns 域也可使用公网不存在的 TLD，比如 xxx.local xxx.lan 等。vmware vcenter 就默认使用 vsphere.local 作为它的 sso (单点登录)系统的域名。

私有 DNS 域的选择，参见 [DNS 私有域的选择：internal.xxx.com xxx.local 还是 xxx.zone？](https://www.cnblogs.com/kirito-c/p/12624815.html)

局域网 DNS 服务器的规模与层级，视局域网的大小而定。一般小公司一个就行，要容灾设三个副本也够了。

以 CoreDNS 为例，局域网 DNS 服务器也可以被设置成一个 DNS Resolver，可以设置只转发特定域名的 DNS 解析。这叫将某个域设为转发区域。

著名的 Kubernetes 容器集群系统（它内部使用的是自己的虚拟局域网），就是使用的 CoreDNS 进行局域网的域名解析，以实现服务发现功能。

## 五、操作系统的 DNS 解析器

应用程序实际上都是调用的操作系统的 DNS Resolver 进行域名解析的。在 Linux 中 DNS Resolver 由 glibc/musl 提供，配置文件为 `/etc/resolv.conf`。

比如 Python 的 DNS 解析，就来自于标准库的 socket 包，这个包只是对底层 c 语言库的一个简单封装。

基本上只有专门用于网络诊断的 DNS 工具包，才会自己实现 DNS 协议。

### 1. hosts 文件

操作系统中还有一个特殊文件：Linux 中的 `/etc/hosts` 和 Windows 中的 `C:\Windows\System32\drivers\etc\hosts`

系统中的 DNS resolver 会首先查看这个 `hosts` 文件中有没有该域名的记录，如果有就直接返回了。没找到才会去查找本地 DNS 缓存、别的 DNS 服务器。

只有部分专门用于网络诊断的应用程序（e.g. dig）不会依赖 OS 的 DNS 解析器，因此这个 `hosts` 会失效。`hosts` 对于绝大部分程序都有效。

>移动设备上 hosts 可能会失效，部分 app 会绕过系统，使用新兴的 HTTPDNS 协议进行 DNS 解析。


### 2. HTTPDNS

传统的 DNS 协议因为使用了明文的 UDP 协议，很容易被劫持。顺应移动互联网的兴起，目前一种新型的 DNS 协议——HTTPDNS 应用越来越广泛，国内的阿里云腾讯云都提供了这项功能。

HTTPDNS 通过 HTTP 协议直接向权威 DNS 服务器发起请求，绕过了一堆中间的 DNS 递归解析器。好处有二：

1. 权威 DNS 服务器能直接获取到客户端的真实 IP（而不是某个中间 DNS 递归解析器的 IP），能实现就近调度。
1. 因为是直接与权威 DNS 服务器连接，避免了 DNS 缓存污染的问题。

HTTPDNS 协议需要程序自己引入 SDK，或者直接请求 HTTP API。

### 3. 默认 DNS 服务器

操作系统的 DNS 解析器通常会允许我们配置多个上游 Name Servers，比如 Linux 就是通过 `/etc/resolv.conf` 配置 DNS 服务器的。

```conf
$ cat /etc/resolv.conf 
nameserver 8.8.8.8
nameserver 8.8.4.4
search lan
```

>不过现在这个文件基本不会手动修改了，各 Linux 发行版都推出了自己的网络配置工具，由这些工具自动生成 Linux 的各种网络配置，更方便。
比如 Ubuntu 就推荐使用 netplan 工具进行网络设置。

>Kubernetes 就是通过使用容器卷映射的功能，修改 /etc/resolv.conf，使集群的所有容器都使用集群 DNS 服务器（CoreDNS）进行 DNS 解析。

通过重复使用 `nameserver` 字段，可以指定多个 DNS 服务器（Linux 最多三个）。DNS 查询会按配置中的顺序选用 DNS 服务器。
**仅在靠前的 DNS 服务器没有响应（timeout）时，才会使用后续的 DNS 服务器！所以指定的服务器中的 DNS 记录最好完全一致！！！**不要把第一个配内网 DNS，第二个配外网！！！

### 4. DNS 搜索域

上一小节给出的 `/etc/resolv.conf` 文件内容的末尾，有这样一行: `search lan`，它指定的，是所谓的 DNS 搜索域。

讲到 `DNS 搜索域`，就不得不提到一个名词：全限定域名（Full Qulified Domain Name, FQDN），即一个域名的完整名称，`www.baidu.com`。

一个普通的域名，有下列四种可能：

1. `www.baidu.com.`: 末尾的 `.` 表示根域，说明 `www.baidu.com` 是一个 FQDN，因此不会使用搜索域！
1. `www.baidu.com`: 末尾没 `.`，但是域名包含不止一个 `.`。首先当作 FQDN 进行查询，没查找再按顺序在各搜索域中查询。
    - `/etc/resolv.conf` 的 `options` 参数中，可以指定域名中包含 `.` 的临界个数，默认是 1.
1. `local`: 不包含 `.`，被当作 `host` 名称，非 FQDN。首先在 `/etc/hosts` 中查找，没找到的话，再按顺序在各搜索域中查找。

>上述搜索顺序可以通过 `host -v <domain-name>` 进行测试，该命令会输出它尝试过的所有 FQDN。
修改 `/etc/resolv.conf` 中的 `search` 属性并测试，然后查看输出。

就如上面说例举的，在没有 `DNS 搜索域` 这个东西的条件下，我们访问任何域名，都必须输入一个全限定域名 FQDN。
有了搜索域我们就可以稍微偷点懒，省略掉域名的一部分后缀，让 DNS Resolver 自己去在各搜索域中搜索。

在 Kubernetes 中就使用到了搜索域，k8s 中默认的域名 FQDN 是 `service.namespace.svc.cluster.local`，
但是对于 default namespace 中的 service，我们可以直接通过 `service` 名称查询到它的 IP。
对于其他名字空间中的 service，也可以通过 `service.namespace` 查询到它们的 IP，不需要给出 FQDN。

Kubernetes 中 `/etc/resolv.conf` 的示例如下：

```conf
nameserver 10.43.0.10
search default.svc.cluster.local svc.cluster.local cluster.local
options ndots:5
```

可以看到 k8s 设置了一系列的搜索域，并且将 `.` 的临界值设为了 5。
也就是少于 5 个 dots 的域名，都首先当作非 FQDN 看待，优先在搜索域里面查找。

该配置文件的详细描述参见 [manpage - resolv.conf](http://man7.org/linux/man-pages/man5/resolv.conf.5.html)，或者在 Linux 中使用 `man resolv.conf` 命令查看。

## 六、DNS 诊断的命令行工具


```shell
dig +trace baidu.com  # 诊断 dns 的主要工具，非常强大
host -a baidu.com  # host 基本就是 dig 的弱化版，不过 host 有个有点就是能打印出它测试过的所有 FQDN


nslookup baidu.com # 和 host 没啥大差别，多个交互式查询不过一般用不到
whois baidu.com # 查询域名注册信息，内网诊断用不到
```

详细的使用请 `man dig`

## 七、CoreDNS 的使用

主流的本地 DNS 服务器中，提供 UI 界面的有 Windows DNS Server 和群晖 DNS Server，很方便，不过这两个都是操作系统绑定的。

开源的 DNS 服务器里边儿，BIND 好像是最有名的，各大 Linux 发行版自带的 `dig/host/nslookup`，最初都是 Bind 提供的命令行工具。
不过为了一举两得（DNS+K8s），咱还是直接学习 CoreDNS 的使用。

CoreDNS 最大的特点是灵活，可以很方便地给它编写插件以提供新功能。功能非常强大，相比传统 DNS 服务器，它非常“现代化”。在 K8s 中它被用于提供服务发现功能。

接下来以 CoreDNS 为例，讲述如何配置一个 DNS 服务器，添加私有的 DNS 记录，并设置转发规则以解析公网域名。

### 1. 配置文件：Corefile

CoreDNS 因为是 Go 语言写的，编译结果是单个可执行文件，它默认以当前文件夹下的 Corefile 为配置文件。以 kubernetes 中的 Corefile 为例：

```corefile
.:53 {
    errors  # 启用错误日志
    health  # 启用健康检查 api
    ready  # 启用 readiness 就绪 api

    # 启用 kubernetes 集群支持，详见 https://coredns.io/plugins/kubernetes/
    # 此插件只处理 cluster.local 域，以及 PTR 解析
    kubernetes cluster.local in-addr.arpa ip6.arpa {
      pods insecure
      upstream  # 
      fallthrough in-addr.arpa ip6.arpa  # 向下传递 DNS 反向查询
      ttl 30  # 过期时间
    }
    prometheus :9153  # 启用 prometheus metrics 支持
    forward . 114.114.114.114 19.29.29.29 # 将非集群域名的 DNS 请求，转发给公网 DNS 服务器。
    cache 30  # 启用前端缓存，缓存的 TTL 设为 30
    loop    # 检测并停止死循环解析
    reload  # 支持动态更新 Corefile

    # 随机化 A/AAAA/MX 记录的顺序以实现负载均衡。
    #   因为 DNS resolver 通常使用第一条记录，而第一条记录是随机的。这样客户端的请求就能被随机分配到多个后端。
    loadbalance
}
```

Corefile 首先定义 DNS 域，域后的代码块内定义需要使用的各种插件。**注意这里的插件顺序是没有任何意义的！**插件的调用链是在 CoreDNS 编译时就定义好的，不能在运行时更改。

通过上述配置启动的 CoreDNS 是无状态的，它以 Kubernetes ApiServer 为数据源，CoreDNS 本身只相当于一个查询器/缓存，因此它可以很方便地扩缩容。

### 2. 将 CoreDNS 设置成一个私有 DNS 服务器

现在清楚了 Corefile 的结构，让我们来设计一个通过文件配置 DNS 条目的 Corefile 配置：

```corefile
# 定义可复用 Block
(common) {
    log
    errors
    cache
    loop    # 检测并停止死循环解析
}

# 本地开发环境的 DNS 解析
dev-env.local:53 {
    import common  # 导入 Block
    file dev-env.local { # 从文件 `dev-env.local` 中读取 DNS 数据
        reload 30s  # 每 30s 检查一次配置的 Serial，若该值有变更则重载整个 Zone 的配置。
    }
}

# 本地测试环境
test-env.local:53 {
    import common
    file test-env.local {
        reload 30s
    }
}

# 其他
.:53 {
    forward . 114.114.114.114  # 解析公网域名
    log
    errors
    cache
}
```

上面的 Corefile 定义了两个本地域名 `dev-env.local` 和 `test-env.local`，它们的 DNS 数据分别保存在 `file` 指定的文件中。

这个 `file` 指定的文件和 `bind9` 一样，都是使用在 [rfc1035](https://tools.ietf.org/html/rfc1035#section-5.3) 中定义的 Master File 格式，`dig` 命令输出的就是这种格式的内容。示例如下：

```
;; 與整個領域相關性較高的設定包括 NS, A, MX, SOA 等標誌的設定處！
$TTL    30
@                       IN SOA   dev-env.local. devops.dev-env.local. (
                                     20200202 ; SERIAL，每次修改此文件，都应该同步修改这个“版本号”，可将它设为修改时间。
                                     7200     ; REFRESH
                                     600      ; RETRY
                                     3600000  ; EXPIRE
                                     60)      ; MINIMUM
@                       IN NS    dns1.dev-env.local.   ; DNS 伺服器名稱
dns1.dev-env.local.    IN A     192.168.23.2         ; DNS 伺服器 IP


redis.dev-env.local.         IN A     192.168.23.21
mysql.dev-env.local.         IN A     192.168.23.22
elasticsearch.dev-env.local. IN A     192.168.23.23
ftp                          IN A     192.168.23.25  ; 這是簡化的寫法！
```

详细的格式说明参见 [鳥哥的 Linux 私房菜 - DNS 正解資料庫檔案的設定](http://linux.vbird.org/linux_server/0350dns.php#DNS_master_name)
`test-env.local` 也是一样的格式，根据上面的模板修改就行。这两个配置文件和 Corefile 放在同一个目录下：

```
root@test-ubuntu:~/dns-server# tree
.
├── coredns  # coredns binary
├── Corefile
├── dev-env.local
└── test-env.local
```

然后通过 `./coredns` 启动 coredns。通过 dig 检验：
![](https://img2018.cnblogs.com/blog/968138/202002/968138-20200211182339141-1135337933.png)

可以看到 `ftp.dev-env.local` 已经被成功解析了。

### 3. [可选插件（External Plugins）](https://coredns.io/explugins/)

CoreDNS 提供的预编译版本，不包含 [External Plugins](https://coredns.io/explugins/) 中列出的部分，如果你需要，可以自行修改 `plugin.cfg`，然后手动编译。

不得不说 Go 语言的编译，比 C 语言是方便太多了。自动拉取依赖，一行命令编译！只要配好 [GOPROXY](https://github.com/goproxy/goproxy.cn)，启用可选插件其实相当简单。

### 4. 设置 DNS 集群

单台 DNS 服务器的性能是有限的，而且存在单点故障问题。因此在要求高可用或者高性能的情况下，就需要设置 DNS 集群。

虽然说 CoreDNS 本身也支持各种 DNS Zone 传输，主从 DNS 服务器等功能，不过我想最简单的，可能还是直接用 K8s。

直接用 ConfigMap 存配置，通过 Deployment 扩容就行，多方便。

要修改起来更方便，还可以启用可选插件：redis，直接把配置以 json 的形式存在 redis 里，通过 redis-desktop-manager 进行查看与修改。

## 参考

- [DNS 原理入门](http://www.ruanyifeng.com/blog/2016/06/dns.html)
- [What Is DNS? | How DNS Works - Cloudflare](https://www.cloudflare.com/learning/dns/what-is-dns/)
- [What is DNS? - Amazon AWS](https://aws.amazon.com/cn/route53/what-is-dns/?nc1=h_ls)
- [鸟哥的 Linux 私房菜——主機名稱控制者： DNS 伺服器](http://linux.vbird.org/linux_server/0350dns.php#DNS_resolver_whois)
- [CoreDNS - Manual](https://coredns.io/manual/toc/)
- [Kubernetes - DNS for Services and Pods](https://kubernetes.io/docs/concepts/services-networking/dns-pod-service/)
- [Kubernetes - Customizing DNS Service](https://kubernetes.io/docs/tasks/administer-cluster/dns-custom-nameservers/)
