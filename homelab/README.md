# HomeLab


## 一、树莓派4b

树莓派本身安装 Raspberry Pi OS，即  raspbian 系统，然后通过社区提供的脚本安装 [NAS](NAS/README.md) 系统。

树莓派目前所有的工作负载如下，全部使用 docker-compose 运行：

1. ali-ddns: [sanjusss/aliyun-ddns](https://github.com/sanjusss/aliyun-ddns)
2. aria2: [p3terx/aria2-pro](https://github.com/p3terx/aria2-pro) + [](https://github.com/p3terx/ariang)
3. 监控：[netdata](https://github.com/netdata/netdata)
    - 这玩意比较吃性能，介意的话不要装。
4. BT 下载：[linuxserver/docker-transmission](https://github.com/linuxserver/docker-transmission)

所有硬件的功耗测量结果如下：

1. 树莓派4B：稳定功耗大概 3W，普通使用状态功耗基本没有升高。电源最大功率 5v*3A。
2. 硬盘盒（带风扇）：单个西数 4T，稳定功耗 6W。
3. WiFi 路由: 小米 AX1800，稳定功耗 6W。
4. 电信光猫：稳定功耗 6W

总功耗不到 21W，24h 不间断运行。
