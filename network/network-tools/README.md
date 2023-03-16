# 常用网络工具

## 0. 瑞士军刀 natcat/socat

见 [Linux 网络工具中的瑞士军刀 - socat & netcat](https://thiscute.world/posts/socat-netcat/)

## 1. 抓包分析

内容已迁移至 [使用 tcpdump 和 Wireshark 进行抓包分析](https://thiscute.world/posts/tcpdump-and-wireshark/)

## 2. 性能测试

wrk/wrk2 是一款非常强悍的压测工具：

>代码量也不多，很适合用于学习 C 语言以及 epoll 模型

- [wrk](https://github.com/wg/wrk)
- [wrk2](https://github.com/giltene/wrk2): 给 wrk 增加了一些功能，比如以恒定的速率请求给定的 URL


## 3. nmap 端口探测、主机探测工具

[nmap](https://github.com/nmap/nmap) 是一个应用广泛的专业网络探测工具。

>参考了 [nmap超详细使用指南](https://crayon-xin.github.io/2018/08/12/nmap%E8%B6%85%E8%AF%A6%E7%BB%86%E4%BD%BF%E7%94%A8%E6%8C%87%E5%8D%97/)

>注意如下命令均需要 root 权限

最简单的用法，执行默认的端口扫描功能：

```shell
❯ sudo nmap 127.0.0.1
Starting Nmap 7.93 ( https://nmap.org ) at 2023-03-16 11:13 CST
Nmap scan report for localhost (127.0.0.1)
Host is up (0.000016s latency).
Not shown: 996 closed tcp ports (reset)
PORT      STATE    SERVICE
5000/tcp  open     upnp
7000/tcp  open     afs3-fileserver
9090/tcp  open     zeus-admin
55056/tcp filtered unknown

Nmap done: 1 IP address (1 host up) scanned in 1.27 seconds
```

服务器版本识别(`-sV`):

```shell
root@kali:~# nmap -sV 192.168.31.13 -p 8080
Starting Nmap 7.70 ( https://nmap.org ) at 2018-08-13 00:02 CST
Nmap scan report for 192.168.31.13
Host is up (0.00076s latency).

PORT     STATE SERVICE VERSION
8080/tcp open  http    Apache Tomcat 8.5.14
MAC Address: 00:0C:29:99:D3:E6 (VMware)

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 12.75 seconds
```

操作系统检测：

```shell
root@kali:~# nmap -O 192.168.31.13 
Starting Nmap 7.70 ( https://nmap.org ) at 2018-08-13 00:03 CST
Nmap scan report for 192.168.31.13
Host is up (0.00072s latency).
Not shown: 998 closed ports
PORT      STATE SERVICE
8080/tcp  open  http-proxy
10010/tcp open  rxapi
MAC Address: 00:0C:29:99:D3:E6 (VMware)
Device type: general purpose
Running: Linux 3.X|4.X
OS CPE: cpe:/o:linux:linux_kernel:3 cpe:/o:linux:linux_kernel:4
OS details: Linux 3.2 - 4.9
Network Distance: 1 hop

OS detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 3.49 seconds
```

另外如果主机禁用了 ping 功能，就需要使用 `-Pn` 关闭 nmap 的 ping 检测功能，这样才能正常进行端口检测。

其他参数介绍：

- TCP 扫描选项
  - `-sT`: TCP 连接扫描，对每个端口都会进行完整的三次握手。这种扫描方式速度比较慢，而且容易被目标主机识别。
    - 不需要 root 权限，是在低权限下 nmap 的默认扫描方式
  - `-sS`: SYN 扫描，仅发送 SYN 包并检测目标主机是否恢复 SYN/ACK，速度非常快，而且目标主机比较难检测到。
    - 需要 root 权限，是在特权模式下 nmap 的默认扫描方式
  - etc...
- UDP 扫描选项
  - `-sU`: UDP 是无连接的，只有这一种扫描方式。
    - 速度慢，因为 Linux 限制内核 1 秒内最多发送一次 ICMP Port Unreachable 信息，扫描一台主机的 65535 个 UDP 端口必定需要超过 18 个小时。
    - 速度优化方法：
      - 并发 UDP 扫描
      - 通过 `-p53,161` 指定端口号，实现优先扫描常用端口。示例仅扫描 53 与 161 两个端口号。
- 目标端口选项
  - `-p 1-1024`: 指定端口范围
  - `-F`: 快速扫描，仅扫描 100 个常用端口
  - `-r`: 从小到大顺序扫描所有端口
  - `--top-ports 1000`: 扫描 nmap-services 文件中的前 1000 个端口，数字可调整。
- Nmap 脚本引擎（NSE）
  - Nmap 脚本引擎自带了许多有用的脚本，同时也支持自定义脚本，可用于各种渗透测试。
  - `--script scipt1,scipt2`: 指定使用某些脚本来扫描端口
  - `-sC`: 等同于 `--script=default`，使用默认脚本来扫描端口。默认使用的脚本有如下特点：速度快、内容丰富、形式简洁、不会侵入目标系统等。
  - 其他自带脚本有（通常存放在 `/usr/share/nmap/scripts` 中）：
    - auth: 使用暴力破解来找出目标系统的认证信息
    - docs: 拒绝服务攻击
    - exploit: 利用目标系统的安全漏洞，危险操作。（需要获取行动许可）
    - fuzzer: 对目标系统进行模糊测试
    - malware: 检测目标系统上的恶意软件或后门
    - vuln: 检测目标系统上的安全漏洞

使用举例：

```shell
nmap --script http-enum,http-headers,http-methods,http-php-version	-p	80 192.168.56.103
```

## 路由追踪 mtr

[mtr](https://github.com/traviscross/mtr) 结合了 traceroute' 与 'ping' 两个工具的功能，常用于探测路由链路。

可以通过源码编译安装 mtr，也可以用各大平台的包管理器（brew/apt/yum/apk）直接安装。

比如MacOS 的安装命令（使用 Homebrew）：

```shell
brew install mtr
# 需要将 /usr/local/bin 加入到环境变量中
echo 'PATH=$PATH:/usr/local/sbin' >> ~/.zshrc
source ~/.zshrc
# 现在就可以用了，注意需要 sudo 权限
sudo mtr baidu.com
```


