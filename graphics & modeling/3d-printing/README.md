# 3D 打印

我的装备：

- 3D 打印机：ELEGOO Neptune 3 Pro
- 3D 建模软件：Blender

我买这台打印机参考的网友建议有：

- 新手一定要买知名品牌如创想三维、ELEGOO、ANYCUBIC，而且一定要有自动调平功能。
  - 千万别买便宜的自组机，因为自组机非常耗费时间跟精力，新手玩很容易弃坑。
- 新手一定要买 FDM 熔积成型类型的打印机
  - 不要买光固化，光固化虽然速度快且足够精细，但后期处理很繁琐很耗费精力，容易劝退新手。
- 买了第一台打印机后，如果成功玩上了，下一步显然是 DIY，所以建议买 I3 结构的成品机，网上成熟的 DIY 方案很多。因此不建议买著名的 K3MS，虽然极其稳定但是太贵了，也不好 DIY。

等玩熟了之后可以再考虑 DIY 一台自己的 Core-XY 打印机，或者上 3D 光固化。

最终选择了目前性价比最高的 ELEGOO Neptune 3 Pro，1499 的价格，配置跟创想三维的 Ender-3 S1 Pro 有的一拼了。
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
3. 需要使用开源的软件 [Cura](https://github.com/Ultimaker/Cura) 调整模型，它会通过内置算法设定好合适的打印走线方式。
4. 将模型导出并复制到 U 盘，然后插入打印机开始打印。

