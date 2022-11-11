# 我的 Homelab

## 服务器架构

<img src="_img/my-homelab.webp" style="width:50%">
<img src="_img/my-homlab-internal.webp" style="width:50%">


- Raspberry Pi 4B
  - 定位: 主力设备，超低功耗，7 x 24h 不间断运行
  - CPU: Broadcom BCM2711(1.5 GHz，64-bit，4 Cores，ARM Cortex-A72)
  - MEM: 2G
  - DISK: 128G TF Card
- Minisfroum UM560
  - 定位: 主力设备，低功耗，7 x 24H 不间断运行
  - CPU: AMD R5 5625U, 15W, 6C12T
  - MEM: 32G * 2
  - DISK1: 512G SSD
  - DISK2: 4T * 2 HDD
- Beelink GTR5 AMD Ryzen 9 5900H
  - 定位: 次主力设备，中等功耗，7 x 24H 不间断运行，或者在不需要时关机省电
  - CPU: AMD R9 5900HX, 45W, 8C16T
  - MEM: 16G * 2
  - DISK: 1T SSD

## 软件架构

![](_img/dashy-hompage.webp "Homlab 面板（旧版）")

- Raspberry Pi 4B
  - OS: Raspberry Pi OS
  - APPs
    - k3s worker node
      - 需要添加污点，容忍该污点即可将任务调度到此节点。
      - 这也是当前 k3s 集群中唯一的 arm 节点，主要用于做一些 ARM 相关的测试
      - node_exporter 作为 daemonset
      - etcd
- Minisfroum UM560
  - OS: Proxmox VE
  - VMs
    - Envoy Proxy Server: 1c/1G 32G
      - 边缘网关，设为 DMZ 主机面向公网提供访问
    - OpenMediaVault: 2c/8G 64G
      - 硬盘盒 Sata 直通到此虚拟机，作为家庭 NAS 系统，提供 SMB/SFTP/ISCSI 等局域网 NAS 服务
      - 也通过 docker-compose 运行一些需要访问硬盘盒数据的其他服务，比如
        - Caddy 文件浏览器
        - [jellyfin](https://github.com/jellyfin/jellyfin) 影音系统
        - [Nextcloud](https://github.com/nextcloud) 私有云盘
        - [calibre-web](https://github.com/janeczku/calibre-web) 私有电子书系统，不再需要在每台设备之间同步各种电子书了。
        - [Syncthing](https://github.com/syncthing/syncthing): 在 NAS、Android、MacOS/Windows/Linux 之间自动同步数据，比如说 logseq 笔记。
    - OpenWRT: 2c/1G 16G - host CPU
      - 作为软路由系统，实现网络加速、DDNS 等功能
    - k3s single master 1c/2G 32G
      - 家庭网络，单 master 就够用了，省点性能开销
    - k3s worker node 4c/8G 32G
    - docker-compose server 4c/8G 32G
      - 用于跑一些不需要访问硬盘盒，但是需要常驻的容器化应用
      - [Pihole](https://github.com/pi-hole/pi-hole) 广告屏蔽组件，它底层使用 dnsmasq 作为 DHCP 服务器 + DNS 服务器
      - CoreDNS: 私有 DNS，这样要做些局域网 DNS 配置，就不需要改每台机器的 /etc/hosts 了。
        - 需要将 CoreDNS 设置为 Pihole 的 upstream server.
- Beelink GTR5 AMD Ryzen 9 5900H
  - OS: Proxmox VE
  - VMs
    - k3s worker node
    - Debian Test Server
    - Home Assistant: 干一些自动化的活，比如我到家后自动播放歌曲？？？


k3s 集群里可以跑这些负载：

- 数据库：etcd/mysql/postgresql/presto/minio
- 可观测性：prometheus + vectoriametrics + grafana
- [Tailscale VPN](https://github.com/tailscale/tailscale): 基于 wireguard 的家庭 VPN
- [uptime-kuma](https://github.com/louislam/uptime-kuma): 站点可访问性检测
- [dashy](https://github.com/lissy93/dashy) HomePage 页
  - 在安装了如此多的自托管服务后，一个用于索引所有服务的 Homepage 就显得非常有必要了

局域网有了总共 14C28T 的 amd64 算力后（必要时还能把我的联想笔记本也加入到集群， 再补充 8C16T + Nvidia RTX 3070 的算力），已经可以直接在局域网玩一些需要高算力的任务了，比如说：

- 大数据
  - Spark on K8s on K8s
  - apach pulsar on K8s
  - flink on eks
  - redis cluster
  - programming toolbox Web 版
- 区块链
  - 自建区块链集群


其他从 [awesome-selfhosted](https://github.com/awesome-selfhosted/awesome-selfhosted) 中找到的，比较感兴趣的项目：

- [actionsflow](https://github.com/actionsflow/actionsflow): 完全兼容 Github Action 的自托管 workflow 服务
- [excalidraw](https://github.com/excalidraw/excalidraw): 自托管白板项目
- [【巨大的Docker整合】影视下载全自动化的部署](https://blog.ddsrem.com/archives/film)：很丰富的内容，值得一试
- [CasaOS](https://github.com/IceWhaleTech/CasaOS): 随便玩玩

## 功耗测量

- Raspberry Pi 4B
  - 稳定功耗 3W，电源最大功率 5V x 3A
- Minisfroum UM560
  - 空闲状态下约 6W
  - 工作状态下功耗 15W 多一点
- Beelink GTR5 AMD Ryzen 9 5900H
  - 空闲状态下约 6W
  - 传输数据跑满 1GbE 时是 38W（受限于路由器只能跑到 1GbE）
- 双盘位硬盘盒
  - 插满两块 4T 硬盘，功耗稳定在 12W
- 小米 AX1800
  - 约 6W
- 中兴 ZTE AX5400OPro+
  - 约 10W
  - 测试 AX210 网卡连接此 WIFI，能跑到 180MiB/s


## 参考

暂无
