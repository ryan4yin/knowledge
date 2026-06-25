# 3D 打印

我的 3D 打印机：ELEGOO Neptune 3 Pro，入手价格 1499 元。现已刷入
[Klipper](https://github.com/Klipper3d/klipper) 固件，配置文件仓库：
[neptune3pro-klipper](https://github.com/ryan4yin/neptune3pro-klipper)。

我买这台打印机参考的网友建议有：

- 新手一定要买知名品牌如创想三维、ELEGOO、ANYCUBIC，而且一定要有自动调平功能。
  - 千万别买自组机，因为自组机非常耗费时间跟精力，新手玩很容易弃坑（除非你有足够的时间跟精力慢慢组
    装、调试机器）。
- 新手一定要买 FDM 熔积成型类型的打印机
  - 不要买光固化，光固化虽然速度快且足够精细，但后期处理很繁琐很耗费精力，容易劝退新手。
- 买了第一台打印机后，如果成功玩上了，下一步显然是 DIY，所以建议买 I3 结构的成品机，网上成熟的 DIY
  方案很多。因此不建议买著名的 K3MS，虽然极其稳定但是太贵了。

等玩熟了之后可以再考虑 DIY 一台自己的 Core-XY 打印机，或者上 3D 光固化。

最终选择了目前性价比最高的 ELEGOO Neptune 3 Pro，同价位配置相对很高，被称为「卷王」。朋友说这个价格
已经相当便宜了，很值得入手。

### 如何找 3D 模型

- 国内最流行的 3D 打印社区，拓竹官方平台，模型/打印配置/耗材参数一站式下载：
  [MakerWorld](https://makerworld.com.cn/zh)
- 国外最大的模型站，可直接下载 STL 文件： [Printables](https://www.printables.com/)（Prusa 官方平
  台）、 [Thingiverse](https://www.thingiverse.com/)
- 二次元模型
  - 模之屋，不过这个还不清楚该怎么打印：https://www.aplaybox.com/article
  - 日本二次元模型站点：https://bowlroll.net/
- 其他
  - https://www.cgtrader.com/3d-print-models
  - https://free3d.com/zh/
  - https://www.turbosquid.com/Search/3D-Models/free
  - ...

### 如何转换与打印模型

1. 首先需要有已经准备好的 OBJ/STL/3MF 格式的模型，这个模型可以在前面提供的网站上下载，也可以自己学习
   使用参数化建模软件来设计。
2. 打印前，要考虑好基本的物理支撑结构，找到需要的「额外支撑」最少的摆放方式，并据此调整模型角度，通
   常这样打印出的东西结构强度也最高。
3. 使用开源的切片软件 [OrcaSlicer](https://github.com/SoftFever/OrcaSlicer) 调整模型，内置多种校准工
   具（流量校准、压力提前、温度塔等），对 Klipper 支持极好，是目前最流行的开源切片软件。
4. 切片后的 G-code 通过网络直接上传到打印机（Klipper + Moonraker），无需 U 盘插拔。

### 打印机耗材

我手上只有 FDM 打印机，所以直接看 FDM 耗材：

- PLA 聚乳酸: 使用淀粉制作的新型可再生生物降解材料，具有良好的拉伸强度，经济实惠。但是机械强度不高，
  适合打印概念模型
  - ELEGOO 官方卖的 PLA 是 69 一卷 1KG
  - 目前看到卖最离谱的是创想三维，溢价太高了。
- ABS 塑料: 具有持久的机械强度跟稳定性，适合打印最终成品
  - 是市面上最常见的塑料材质，打印气味大
- TPU: 软性材料，高伸長率，良好的柔韧性和拉伸性，耐磨性和抗撕裂性
  - 典型應用包括柔性軟管、導管、進氣管、密封件、防護罩和減震器等
- PETG: 同时拥有 ABS 的刚性和机械性能以及 PLA 的易打印、无异味

耗材相关品牌，知名的有「易生」，不过贵。另外最近很多人推荐天瑞的 PETG-ECO 这款耗材，相当便宜而且据说
不坑。

上述耗材还有许多变种，不同材料、加入的杂质不同，都会影响打印效果。大家说普通 PLA 最好打原因就是它不
易拉丝、欠挤出、翘边，但是如果换其他材料，就可能会出各种问题，需要通过调整热床温度、挤出头温度、热床
涂胶水防翘边等等手段来解决。

另外所有耗材都需要防潮。如果受潮了，网上有线材专用烘干机卖不过比较贵。省钱的话像我用三面围挡式的暖脚
宝来烘干也行，重点是温度不能太高，40 - 50 度左右就行。

### 模型后处理

个人适用的方法：

- 打磨
  - 首先用粗砂纸磨去层纹，再用细砂纸打磨光滑，最后上漆
  - 缺点就是比较费时费力...
- PETG 涂层

此外如果是精细手办等模型，还需要上色，这个感觉也是个手艺活...后面再研究吧。

### 如何设计自己的 3D 打印件

目前最流行的 3D 打印设计软件貌似是 Autodesk 家的 Fusion 360，不过我作为开源爱好者与 Linux 爱好者，当
然倾向于选择开源且支持 Linux 的软件。

了解了一番发现 3D 设计软件按底层原理分类有两类：

1. 多边形建模：流行的开源 3D 设计与动画制作软件 Blender 的特点就是多边形建模，适合做动画，但是不适合
   做仿真，用它设计 3D 打印件有困难。
2. 参数化建模：刚刚提到的 Fusion 360，以及开源的 FreeCAD，都是这个类别。
   1. FreeCAD 据说已经勉强能胜任产品级的设计了，不过相比商业软件还有较大差距。对我个人玩耍而言，应该
      可堪一用了。

因此，看起来如果要玩 3D 设计，还想打印些手办啥的，FreeCAD 应该是比较好的选择，手办的话 Blender 也得
学一学。

### 打印机改造

我的 Neptune 3 Pro 已通过 [kiauh](https://github.com/dw-0/kiauh) 刷入 Klipper 固件。Klipper 将运动计
算卸载到上位机（树莓派），实现更高精度和更快的打印速度，并支持 Web 远程管理、输入整形（减少振动）、
压力提前等高级功能。

配置文件仓库：[neptune3pro-klipper](https://github.com/ryan4yin/neptune3pro-klipper)，包含：

- Klipper 打印机配置（`klipper-config/`）
- OrcaSlicer 适配 Klipper 的切片配置文件（`orca-slicer/`）
- 配置验证脚本（`scripts/validate_config.py`）
- 常见问题排错（`TROUBLESHOOTING.md`）

Klipper 配套组件：

- [Moonraker](https://github.com/Arksine/moonraker)：Klipper 的 Web API 层
- [Mainsail](https://github.com/mainsail-crew/mainsail) /
  [Fluidd](https://github.com/fluidd-core/fluidd)：Web 管理界面，替代传统的 OctoPrint
- [Crowsnest](https://github.com/mainsail-crew/crowsnest)：摄像头推流，支持延时摄影

刷入 Klipper 后，效果基本等同于 Neptune 4 Pro——Neptune 4 Pro 相比 3 Pro 的主要升级就是换用了 Klipper
固件和 ARM CPU 上位机。

### DIY 打印机

- [VoronDesign](https://github.com/VoronDesign): 朋友说这个 voron2 现在很火，core-xy 结构速度应该能
  比我的 i3 机器快很多。
- 打印机固件
  - [Klipper](https://github.com/Klipper3d/klipper): 目前最流行的 Linux 3D 打印机固件，将运动规划卸
    载到上位机，性能远超传统 MCU 固件。我的 Neptune 3 Pro 已刷入。
  - [Marlin](https://github.com/MarlinFirmware/Marlin): 最流行的基于 MCU 的 3D 打印机固件，Neptune 3
    Pro 出厂预装此固件。
- 切片软件
  - [OrcaSlicer](https://github.com/SoftFever/OrcaSlicer): 基于 Bambu Studio 的开源切片软件，内置校
    准工具，对 Klipper 支持最好，是目前最流行的切片软件。
  - [PrusaSlicer](https://github.com/prusa3d/PrusaSlicer): Prusa 官方切片软件，OrcaSlicer 的祖先。
  - [Cura](https://github.com/Ultimaker/Cura): UltiMaker 官方切片软件，早年很流行，但近年逐渐被
    OrcaSlicer 替代。
- 其他
  - [OctoPrint](https://github.com/OctoPrint/OctoPrint): 传统 Marlin 打印机的 Web UI。Klipper 用户一
    般用 Mainsail 或 Fluidd 替代。
