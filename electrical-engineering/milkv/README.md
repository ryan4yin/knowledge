# Milk-V

Milk-V （深圳市群星闪耀科技股份有限公司）是家才成立没多久的公司，2023 年刚推出它最初的三款产品，估计公司目前也没几个人，也算尝鲜了（看它发展轨迹跟宣传，跟 Sipeed 有些类似，都是科技爱好者创建的公司）。

最近整了俩 Milk-V 的开发版，这家目前专做 RISC-V 架构相关的板子，主要用算能家的芯片。

- Milk-V Duo:
  - 打折 70 大洋两块，确实便宜。
  - 用的算能 CV1800B 芯片，C906 1GHz + C906 700Hz 双核心。不过目前仅开放了主核 Linux 系统，协处理器还没开放文档跟 SDK。
  - 比 Sipeed 家的 M1s 强很多，M1s 用的 BL808 主核才 480MHz，仅支持 Linux 的基础功能。
    - M1s 主推的是当 MCU 使用，还必须用它官方提供的 GUI 工具烧录固件，不太方便。
    - M1s 的 Linux SDK 上次更新还是 2022 年，说明基本也没推进。
- Milk-V Mars
  - 用的 StarFive 家的 JH7110 芯片，但是比赛昉的板子便宜很多，还是白色的 SBC，很 milky.
  - 买了一块，还没发货。


## Milk-V Duo

https://github.com/ryan4yin/milkv-duo-buildroot-sdk

## Milk-V Mars

TODO 还没发货，等发货呢