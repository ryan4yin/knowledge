# 矽速科技系列产品

>https://wiki.sipeed.com/

Sipeed 专门做各种开发版、模组、解决方案，主打 AloT，比较有名气，文档、SDK 做得也不错，所以也打算玩一玩看。

它家很多产品都是 RISC-V 指令集，也有部分高性能产品用的是 ARM，芯片供应商有全志、爱芯、博流智能。

## Maix AI 系列

>加粗的是我比较感兴趣的模组或者板子

1. Maix Zero: 小巧、低功耗的 AloT 单片机，对标 ESP32，这个系列 2023 年才刚刚上架，目前软件生态比较拉，基本只有博流智能的官方 SDK 可用，属于战未来系列
   1. M0：开发版价格 29，使用博流智能科技的 BL702 芯片，32bits RISC-V, 132KB RAM，只支持蓝牙
   2. **M0s**: 开发版价格 26.9 - 5，升级到了 BL616 芯片，480KB SRAM + 4MB Flash，支持蓝牙跟 WiFi6，硬件配置可以跟 ESP32-S3 拼，得用博流智能官方的 C/C++ SDK 进行开发
2. Maix I: 高性价比的 AI 单片机，能跑阉割版 Linux
   1. M1W/M1N: 开发版价格 120+，基于嘉楠科技 K210 芯片，64bits RISC-V 双核，8MB SRAM，有 KPU 0.23TOPS 算力（但是不是 NPU，好像这有啥限制在），通过内置的 ESP8285 提供 WiFi 与蓝牙功能。
      1. Sipeed 的 MaixPy 框架（已经停止开发）就是专门适配这款芯片的，在 Github 上有 1k stars，说明还是挺受欢迎的。不过也只支持 Python 开发套件。
      2. 淘宝上架挺久了，看 Maixpy 仓库时间线 19 年就发布了 0.1 版本，比较成熟。
   2. **M1s**: 单开发板价格 69，使用博流智能科技的 BL808 芯片，RISC-V 三核异构（平头哥开源内核），100GOPS AI 算力(0.1TOPS)，768KB SRAM + 64MB UHS PSRAM，还有专用的 H264 编解码模块、WiFi 蓝牙都支持，还比 K210 多了 ETH(RMII), ADC/DAC 等外设。总的来说比 K210 要强，还更便宜。
      1. 2023 年 2 月上架的产品，目前软件生态跟成熟的 K210 没法比，貌似只能用博流智能官方的 C SDK 玩。
      2. 能跑基础的 Linux 系统，不过据说 Linux 目前还用不了 WiFi
3. Maix II: 能跑 Linux 的入门级 AI 板子，都是全志 ARM 芯片，貌似发布于 2021/6
   1. MaixII-Dock: 板子 140 大洋，基于全志 V831 芯片，单核 ARM A7（性能比 K210 强一个级别），64MB DDR2，0.2TOPS AI 算力
      1. 提供 MaixPy3 跟 libmax 两种语言的 SDK
   2. MaixII-S: 板子要大很多，带 WiFi 的版本卖 275，官方宣传适合当人脸识别门禁，带壳整机 卖 659
      1. 基于全志 V833 芯片，单核 ARM A7（主频略高于前面的 V831），128MB DDR3，0.4TOPS AI 算力，属于是加量又加价...
   3. Maix-II-Sense: 开发版卖 329（带显示屏、摄像头），基于全志 R329 芯片，双核 Cortex-A53，0.256 TOPS AI 算力（周易™Z1 AIPU），DDR3 256MB，支持处理 720P 视频、还支持 5 路音频输入或两路音频输出
      1. 支持 armbian 操作系统
4. Maix III: 高性能 Linux AI 板子
   1. **MAIX-III AXera-Pi**: 基于「爱芯元智」的 AX620A 芯片，四核 Cortex A7，3.6TOPS 算力，2GB RAM，卖 419 大洋（不得不说这还是有点贵了），看文档写得热情洋溢，内容很丰富，看起来是现在的主打产品。
      1. 实际芯片包含了 NPU 和 ISP 部分， 在 AX620A 上两个平分算力，即 1.8TOPS@INT8
      2. 2022 年底上架，软件生态跟社区活跃度，看宣传还不错。
   2. 某未发售的产品，基于「爱芯元智」的 AX650N 芯片，八核 Cortex A55，10.8TOPs@INT8 AI 算力
      1. 根据官方 twitter 暗示，跑 chatgpt 类似的模型，速度大概有 10tokens/second(1 token ~ 3/4 word)
      2. 作为对比，LicheePi4A (TH1520, 4xC910@2.0G) 官方测试跑 llama.cpp 的速度大概为 6s/token

## LicheePi Linux 开发版系列

>感觉 M1s 可以替换掉这里的荔枝派 Zero/Nano，性能虽然差点但是有 NPU。

1. Lichee Pi Zero: 低成本，小体积，高性能，易使用，多扩展。
   1. 芯片为 Allwinner V3s (ARM Cortex-A7 CPU, 1.2GHz, 64MB DDR2 integrated)
   2. 2017 年发布，不算拓展板是 90 块钱。
2. Lichee Pi Nano: 
   1. 芯片为 Allwinner F1C100s @ 408Mhz, SIP 32MB DDR1
   2. 2018 年发布，单核心板 58 块钱，WiFi 拓展板卖 12 块。
1. Lichee Pi Zero Plus: 改成了核心板，金手指引出引脚，需要底板共同工作
   1. 基于全志 ARM® Cortex™-A7 @1.2GHz, 128MB DDR3
   2. 2019 年发布，官网都没找到这块板子，未知原因下架了...
2. Lichee RV - Nezha CM: 
   1. 芯片为全志 D1，512MB DDR3，金手指设计，需要与底板共同工作，底板扩容 1G 内存。
   2. 单核心板卖 99 块钱。
3. **Lichee Pi 4A**: 预计 2023 年 3 月发售的板子，我已经预定了两块，第一块带 NPU 的荔枝派开发版，设计的产品线很丰富，甚至畅想了平板、路由器、集群等使用场景。
   1. TH1520, 12nm, RISC-V 1.8G, C910x4 + C906 + E902 
   2. 4TOPS@INT8 AI 算力
   3. GPU 50.7GFLOPS


其他系列：

- 单片机 Longan Nano，发布于 2019 年，好像官方资料不多，还各种 404...但是第三方有些支持。[riscv-rust](https://github.com/riscv-rust) stars 数最高的就是对这块板子的支持
  - 开发套件是基于 PlatformioIO 开发了一个插件。
- Tang FPGA 系列：先忽略，FPGA 暂时玩不动。

## 对我而言哪些板子比较有吸引力

我目前对如下高性能的板子比较感兴趣：

1. Lichee Pi 4A: 已经预定了两块，应该会成为当下性能最强的国产 RISC-V 派，不过价格未知...
2. MAIX-III AXera-Pi: 文档丰富，3.6TOPS 算力（实际只能用上一半）也还可以，反正买来玩玩，后面可以考虑给我妹玩。
3. MCU: 在自己设计 AloT 时 MCU 显然更小巧、经济实惠。
   1. 目前看矽速新出的 M0s 跟 M1s 都不错，已下单一块 M0s，M1s 因为开发版缺货后面再说...


