# Milk-V

Milk-V （深圳市群星闪耀科技股份有限公司）是家才成立没多久的公司，2023 年刚推出它最初的三款产品，估计公司目前也没几个人，也算尝鲜了（看它发展轨迹跟宣传，跟 Sipeed 有些类似，都是科技爱好者创建的公司）。

最近整了俩 Milk-V 的开发版，这家目前专做 RISC-V 架构相关的板子，主要用算能家的芯片。

- Milk-V Duo:
  - 打折 70 大洋两块，确实便宜。
  - 用的算能 CV1800B 芯片，C906 1GHz + C906 700Hz 双核心，还带了 AI 推理用的 TPU （详细参数无）跟许多预置算法。不过目前仅开放了主核 Linux 系统，协处理器还没开放文档跟 SDK。
  - 比 Sipeed 家的 M1s 强很多，M1s 用的 BL808 主核才 480MHz，仅支持 Linux 的基础功能。
    - M1s 主推的是当 MCU 使用，还必须用它官方提供的 GUI 工具烧录固件，不太方便。
    - M1s 的 Linux SDK 上次更新还是 2022 年，说明基本也没推进。
- Milk-V Mars
  - 用的 StarFive 家的 JH7110 芯片，但是比赛昉的板子便宜很多，还是白色的 SBC，很 milky.


## Milk-V Duo

https://github.com/ryan4yin/milkv-duo-buildroot-sdk

## Milk-V Mars

只提供了一个 buildroot 构建仓库，其内容跟 StarFive 的上游仓库没任何区别。

https://github.com/milkv-mars/mars-buildroot-sdk

官方仅提供了一个 Debian 镜像，文档匮乏，这个镜像是如何生成的也不太清楚。

测试了可以直接使用 NickCao 给 StarFive 2 制作的镜像，系统能正常启动：

https://github.com/NickCao/nixos-riscv

它的 pinout 也没文档，不过看板型跟 Raspberry Pi 4B 是完全一致的，试了下 pinout 也确实一致，所以可以直接参考 Pi 4B 的 pinout：

https://linuxhint.com/gpio-pinout-raspberry-pi/

用串口线连接到 Mars 的 UART0 接口，波特率 115200，可以看到启动信息。



