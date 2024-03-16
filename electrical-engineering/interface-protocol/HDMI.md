# HDMI 接口与协议

> 官方文档：https://hdmi.org/spec/index 与 https://hdmiforum.org/specifications/

> wiki: https://en.wikipedia.org/wiki/HDMI

> 竞品 DP 接口：https://www.displayport.org/

HDMI 是一种音视频传输协议，它同时也定义了 HDMI 物理接口，跟 USB 一样它也存在许多版本，也有命名混乱问
题，下面列下市面上能见到的 HDMI 版本：

- [HDMI 1.4](https://hdmi.org/spec/hdmi1_4b)
  - 最初发布于 2009 年 6 月，其最新版本 HDMI 1.4b 于 2011 年 10 月发布
    - HDMI 证书管理机构仅签发 HDMI 1.4b 的证书，所以新设备用的都是 HDMI 1.4b
  - 仅支持到 4k@24Hz 与 1080p@120Hz
    - 主要应用在 1080p 的廉价显示器上。
  - 另外为了省钱，一些支持 HDMI 2.x 的显示器送的 HDMI 线是 HDMI 1.4 的，需要自己额外购买 HDMI 2.x 的
    线才能达到理想效果。
- [HDMI 2.0](https://hdmiforum.org/hdmi-forum-releases-version-2-0-hdmi-specification/)
  - 最初发布于 2013 年 11 月，其最新版本 HDMI 2.0b 于 2016 年 3 月发布
  - 带宽可达 18Gbps，最高支持 4k@60Hz、2k@144Hz、1080p@240Hz
    - 因为带宽限制，只在低分辨率或者低帧率下才支持 HDR 与 HDR10
    - 主要应用在 4K@60Hz 与 2K@144Hz 的显示器上
  - 此命名已被废弃，HDMI 2.0 被重命名为 HDMI 2.1 TMDS（新瓶装旧酒，真会玩...）
- [HDMI 2.1a](https://hdmi.org/spec/hdmi2_1)
  - 发布时间：2017 年 11 月
  - HDMI 2.1 FRL 支持 8K@60Hz 与 4K@120Hz 识别传输，动态 HDR，带宽可达 48Gbps，不过需要使用 Ultra
    High Speed HDMI 连接线才能达到如此高速
    - 主要应用在 4K@144Hz 高分辨率高帧率的显示器上。
  - 需要注意，HDMI 2.1 TMDS 实际是旧的 HDMI 2.0（发布于 2013 年 11 月），带宽只能跑到 18Gbps，而
    HDMI 2.1 FRL 则是新的 HDMI 2.1，带宽可达 48Gbps。

### 物理接口

HDMI 接口有 19 个物理管脚，并分为如下几种接口类型：

- Type A（最常见的）
  - 笔记本 PC 显示器 电视剧的 HDMI 接口都是这个
- Type B
  - 从未被用到，忽略即可
- Type C
  - 也叫 Mini-HDMI，在树莓派等 SBC 单板电脑上较常见
- Type D
  - 也叫 micro-HDMI connector，我没接触到过
- Type E
  - 拥有自锁功能，用于防止 HDMI 线松动，我也没接触过

此外为了顺应时代，也为了跟 DisplayPort 对抗，HDMI 也提出了
[HDMI Alt Mode for USB Type-C](https://www.hdmi.org/spec/typec)，它能直接通过 USB Type-C 接口来传输
HDMI 数据，这样就能使用一根廉价 USB Type-C 转 HDMI 转接线来连接显示器与 USB Type-C 设备了，不需要使
用额外的适配芯片。

### HDMI 与 DP 的区别

- HDMI 是电视机厂商(主要是一些日本企业)主导的，是一个非开放标准，每生产一台 HDMI 设备或者一条 HDMI线
  缆都需要上缴授权费用。
  - 发布更早，有先发优势。
- DP 是 VESA 协会(主要成员为 PC、显示器厂商)主导的，DP 是一个开放标准，不收费。

那么该选择哪个接口呢？

1. 看你的设备支持啥接口，因为 HDMI 更流行，很多设备都支持 HDMI，而 DP 则不一定。
2. 另一方面，更推荐选择 DP1.4 接口，因为当前（2023 年）主流显示器的 DP 大多是 DP1.4 版本，而搭载
   HDMI 2.1 接口的显示器还是不多。

## HDMI 协议

跟 USB 设备分为 Host 与 Device 一样，HDMI 设备也有不同，它分为两类：

- Source: 即 HDMI 信号源，比如电视盒子、笔记本电脑、游戏机、手机等
- Sink: 即接收 HDMI 信号的设备，比如显示器、电视机等

Source 跟 Sink 不能混用，如果你的笔记本电脑上有 HDMI 接口，那么它只能作为 Source（输出音视频信号），
而不能作为 Sink（作为显示器使用）。

通常如果你想将某台设备的 HDMI 信号使用笔记本电脑或者手机来展示，那么你需要使用一个 HDMI 捕获卡，它可
以将 HDMI 信号转换为 USB 的 UVC 信号，然后你的笔记本电脑或者手机就可以通过 UVC 接收信号了（UVC 是
USB Video Camera，所以 HDMI 信号通常会被识别为 USB 摄像头）。

### 参考

- [HDMI 1.4 协议 - 爱洋葱](https://blog.csdn.net/zhoutaopower/article/details/112182490)
- [看完终于明白，现在的HDMI2.1有这么多套路！带你了解接口改名史](https://new.qq.com/rain/a/20211214A05WZ500)
- [显示器是接DP还是接HDMI？](https://www.zhihu.com/question/291593794)
- [HDMI和DP有什么区别？那个更高清？为什么DP没有HDMI普及？](https://zhuanlan.zhihu.com/p/90658066)
