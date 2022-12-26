# 3D 打印

我的 3D 打印机：ELEGOO Neptune 3 Pro，入手价格 1499 元。

我买这台打印机参考的网友建议有：

- 新手一定要买知名品牌如创想三维、ELEGOO、ANYCUBIC，而且一定要有自动调平功能。
  - 千万别买自组机，因为自组机非常耗费时间跟精力，新手玩很容易弃坑（除非你有足够的时间跟精力慢慢组装、调试机器）。
- 新手一定要买 FDM 熔积成型类型的打印机
  - 不要买光固化，光固化虽然速度快且足够精细，但后期处理很繁琐很耗费精力，容易劝退新手。
- 买了第一台打印机后，如果成功玩上了，下一步显然是 DIY，所以建议买 I3 结构的成品机，网上成熟的 DIY 方案很多。因此不建议买著名的 K3MS，虽然极其稳定但是太贵了。

等玩熟了之后可以再考虑 DIY 一台自己的 Core-XY 打印机，或者上 3D 光固化。

最终选择了目前性价比最高的 ELEGOO Neptune 3 Pro，同价位配置相对很高，被称为「卷王」。
朋友说这个价格已经相当便宜了，很值得入手。

### 如何找 3D 模型

- 貌似很多人推荐的 3D 打印模型网，可以直接下载 STL 文件：https://www.thingiverse.com/
- 二次元模型
  - 模之屋，不过这个还不清楚该怎么打印：https://www.aplaybox.com/article
  - 日本二次元模型站点：https://bowlroll.net/
- 其他的
  - https://www.cgtrader.com/3d-print-models
  - https://free3d.com/zh/
  - https://www.turbosquid.com/Search/3D-Models/free 
  - ...

### 如何转换与打印模型


1. 首先需要有已经准备好的 OBJ/STL 格式的模型，这个模型可以通过流行商业软件 Fusion 360 或者 Blender、SolidWorks 等 3D 建模软件设计并导出，也可以在前面提供的网站上下载。
2. 打印前，要考虑好基本的物理支撑结构，找到需要的「额外支撑」最少的摆放方式，并据此调整模型角度，通常这样打印出的东西结构强度也最高。
3. 需要使用开源的切片软件 [Cura](https://github.com/Ultimaker/Cura) 调整模型，它会通过内置算法设定好合适的打印走线方式。
4. 将模型导出并复制到 U 盘，然后插入打印机开始打印。


### 打印机耗材

我手上只有 FDM 打印机，所以直接看 FDM 耗材：

- PLA 聚乳酸: 使用淀粉制作的新型可再生生物降解材料，具有良好的拉伸强度，经济实惠。但是机械强度不高，适合打印概念模型
  - ELEGOO 官方卖的 PLA 是 69 一卷 1KG，第三方有更便宜的
- ABS 塑料: 具有持久的机械强度跟稳定性，适合打印最终成品
  - 是市面上最常见的塑料材质，打印气味大
- TPU: 软性材料，高伸長率，良好的柔韧性和拉伸性，耐磨性和抗撕裂性
  - 典型應用包括柔性軟管、導管、進氣管、密封件、防護罩和減震器等
- PETG: 同时拥有 ABS 的刚性和机械性能以及 PLA 的易打印、无异味

### 模型后处理

个人适用的方法：

- 打磨
  - 首先用粗砂纸磨去层纹，再用细砂纸打磨光滑，最后上漆
  - 缺点就是比较费时费力...
- PETG 涂层

此外如果是精细手办等模型，还需要上色，这个感觉也是个手艺活...后面再研究吧。

### 打印机改造

TODO


### DIY 打印机

- [VoronDesign](https://github.com/VoronDesign): 朋友说这个 voron2 现在很火，core-xy 结构速度应该能比我的 i3 机器快很多。
- 打印机固件
  - [klipper](https://github.com/Klipper3d/klipper): 最流行的 Linux 3D 打印机固件
  - [Marlin](https://github.com/MarlinFirmware/Marlin): 最流行的基于 MCU 的 3D 打印机固件
- 其他
  - [OctoPrint](https://github.com/OctoPrint/OctoPrint): 打印机的 Web UI，让你无痛远程打印。
  - 还可以加装摄像头延时摄影啥的，反正玩法很多啦
