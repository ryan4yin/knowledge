# Home Automation

随着网络的普及，智能家居相关产品变得越来越受欢迎。

搞了个 Homelab 后，我就在想，能不能搞个智能家居系统实现诸如定时开关空调、回家后自动打开灯光、播放音乐、语音控制等等。

## 硬件

智能家居的核心是数据，数据来源则是各类传感器，传感器对智能家居是非常重要的。细数下大概需要这些：

- 传感器：体感、门磁、光感、温湿度、压感、震感等各类传感器
- 红外光发射器：主要用来遥控空调、电视等传统家居电器
- 麦克风 + 扬声器
- 摄像头：可以实现家庭监控、或者单纯记录自己晚上睡觉情况也行...

上述各类输入输出传感器，可以自己折腾 ESPHome 这类 DIY 方案，也可以买封装好的智能家居产品。
以小米米家为例，「小爱音箱 Pro」就是一个集成度较高的 iot 蓝牙网关 + 传感器 + 音箱的组合。

### 1. 品牌智能家居产品

针对我现在的环境「仅半年租期的租房，床是复式吊顶构造」，目前我的智能家居清单如下：

- 小爱音箱 Pro
  - 全屋智能的接入口之一，另一个全屋智能接入口是 Home Assistant
- nioye 米家追光灯带 3m
  - 小房间的智能灯光就全靠它了
- 小米人体移动传感器 + 小米温湿度传感器
  - 因为看着也不贵，就先买个成品了。后续也考虑自己用 ESPHome 折腾下 DIY
- 小米门窗传感器2
  - 开窗自动关闭空调、关窗户且温度高时自动开空调
- 小白摄像头 室内云台 A2（小米生态链）
- 云米泉先净饮机（小米生态链）
- 华为体脂秤
- 力博得智能牙刷（华为生态链）
- 小米平板5 Pro
- Oppo 智能手表
- ZTE AX5400 Pro+ 无线路由器
- Homelab + NAS: 8T 机械硬盘存储 + 三台 mini 主机 + 树莓派 4B（四台机器均带有 wifi 蓝牙模块）

### 2. ESPHome 系列

前面提到除了上面的品牌智能家居产品，用 [ESPHome](https://github.com/esphome/esphome) + Home Assistant 做智能家居 DIY 目前在国内外也很流行。
它流行的主要原因显然是价格相当便宜，上手难度也不高（基本只需要写 yaml，完全不需要写任何代码）。
一个 ESP8266 就算是开发版也才 13 块钱，ESP32-C3 开发版也就买 20 块钱左右，各种传感器更是白菜价。
跟前述的品牌智能家居产品相比便宜太多了。

我对 ESPHome 也相当感兴趣，因此又在淘宝上买了一堆 DIY 组件。
方便起见，我在淘宝上对比后找了几家性价比较高且销量不错的店（信泰微电子 + 都会明电子），买了上述所有硬件，具体有如下这些：

- 各种传感器：光敏、粉尘、空气质量、人体红外感应、红外发射接手、霍尔磁力、光强度、温湿度、液晶显示屏（单色/全彩）、麦克风等等
  - 注意家里没电烙铁的纯新手（比如我），一定注意买已经焊接好引脚的传感器，否则就得考虑买电烙铁了（要多花百来块钱，如果确定长期玩，可以入手）。
- ESP32 开发版（ESP32-WROOM-32 模组）
- ESP32-C3 开发版
  - ESP32-C3-MINI-1 模组，开发版型号为 `esp32-c3-devkitm-1`
  - 这个板子比较新，引脚也偏少，esphome 生态中一些模块直接用在它上面会报错，需要魔改。
- ESP8266 开发版（型号 `esp01_1m`）
- ESP-01S 无线模块 + 2 个 Relay 继电器模块
  - ESP-01S 就是 ESP8266 但是只引出了 8 个针脚，适合用在智能插座等场景
- ESP32-CAM 开发版 + OV2640 摄像头
- USB 转 TTL 串口小板 + microUSB 连接线
- MB-102 830 孔面包板 * 2 + 400 孔面包板 * 4 + 面包板专用电源 * 4
- 面包线一盒（840 根） + 母对母杜邦线 40P（即 40 根） + 母对公杜邦线 40P + 热缩管一盒
- 10 格零件盒 + 大号 8 格零件盒
- 防静电手环（冬天玩电子设备必备）
  - 液晶屏之类的零件很容易被静电搞坏
- USB 升压线（USB 5v 输入，DC 12v 输出）
- microUSB 数据线
- ESD10-15 镊子一套 6 个
- 万用表
- （没额外买电容电阻因为貌似都已经集成在各种模块上了）

作为物理转 IT 的硬件小白，我在玩上述硬件时也补充了不少硬件相关知识，基本上是遇到啥不会就查一下：

- 什么是开发版，以及如何使用
- 什么是 TTL 串口与串口驱动，以及如何使用
- 什么是 GPIO 引脚，以及开发版的引脚各有什么功能
- 如何使用 USB 转 TTL 串口版给 ESP32/ESP8266 刷固件
- 面包板的构造与用法
- 面包板电源的输出如何切换电压
- 杜邦线、面包线的区别与用法
- 如何使用万用表测电压、电流、电阻（N 年前学这玩意儿时用的是最简单易懂的物理指针表，但是实际显然是电子的用着更方便）
- 什么元件需要防静电，以及有线防静电手环/台垫

烧完智能家居后又想烧智能小车、机械臂，又在淘宝上下单了（如果 ESP32 不好用就改用我闲置的树莓派 4B）：

- 4 自由度木板机械臂 + 4 个 SG90 舵机
- 智能小车底盘（四驱 + 双层）
- 三轴加速度传感器
- 超声波测距传感器
- 双轴摇杆
- L9110S 四路直流电机驱动板

>等智能小车烧完，下一步估计得是烧 PCB 版设计、3D 建模打印、机器人、飞控穿越机了。

案例：

- [[插件集成] HA自带的微软TTS引擎的全面改进威力加强版](https://bbs.hassbian.com/thread-13480-1-3.html)
- 其他在淘宝 B 站上看一些 Makers 做的项目
  - LED 风扇全息显示器
  - 自制激光投影仪
  - 超声波驻波悬浮摆件
  - 自平衡方块（动量惯性轮）
  - 等等

#### 电子电路工具套装

ESPHome 之类的电子电路稍微深入点，焊接工具基本是必不可少的。

PCB 板子的设计与打印（俗称打版）会是更进阶的内容，不过低烧阶段可以直接靠面包板做测试原型，靠玻纤洞洞板 + 焊接电路做些成品出来玩玩。

提前收藏下一个开源硬件平台 [立创开源硬件平台](https://oshwhub.com/)，视发烧程度后面可能会搞上....


电烙铁主要考虑的是温度保持能力、升温速度，便宜的电烙铁基本都有升温慢、焊接中途失温等毛病。
目前总结的电烙铁信息如下：

- 便携电烙铁：入门级别推荐
  - 优缺点：便携、价格低。但是升温相对焊台要慢一些，另外无电气隔离无接地，需要考虑静电啥的
  - 貌似主要推荐广东黄花 907 电烙铁，淘宝官方店买个刀头的 54 大洋
- 焊台：进阶推荐，也可考虑一步到位...
  - 优缺点：升温快、焊接基本不会断，缺点是要贵一些，另外体积也更大，相对没那么便携
  - 貌似主要推荐白菜白光 T12 恒温焊台，淘宝上「永鑫科技」卖 90 大洋
- 二合一焊台：焊台自带热风枪 + 电烙铁两件套，高手必备（一般拆机才会用到热风枪）
  - 反正就很高级也很贵啦。我现阶段买了它也是浪费钱，所以没了解具体型号啥的了

关于电烙铁头，貌似刀头是最推荐的，因为它用途最广泛，基本适用所有场景。

再有就是关于焊材：

- 焊丝：最常见的焊材，不过稍微要求一点焊接技术，可能需要大约半个小时熟悉下。
- 锡膏：新型焊接材料，由焊锡粉、助焊剂以及其它的表面活性剂等混合成的膏状物，
  - 最常用的场景是复杂 PCB 板子，直接用定制的钢丝网覆盖 PCB 板子刷上锡膏、直接就把触点都刷上了，然后再用镊子手工贴上贴片元器件。不过这个有难度...已经是高手玩法了。最省心是花钱直接找 PCB 厂子给打印 + 焊接（钞能力）。
  - 入门阶段也可直接用它配合电烙铁用，据说比焊丝好用。
- 助焊剂：最便宜常用的就是松香了，一般焊个传感器跟普通 PCB 板子完全够用。更好些的就是专用助焊剂。

其他进阶工具：

- 吸锡器：主要用于电器拆焊
  - 场景：一是焊错了或者锡多了，拆焊后重新焊接。二是拆焊其他电路
  - 这玩意儿一个便宜的才十多块，入门阶段买一个也行
- 热风枪：前面提过了，也是拆焊用的
  - 这个入门阶段买就有点浪费了，起码等用的到再考虑吧

如果还要继续烧下去，那就是示波器、稳压电源、3D 打印机，甚至频谱分析仪了，还有看到直接买贴片机的大佬，这都不是我等凡人现在该考虑的事...

## Home Assistant 使用指南

>请注意，由于我家里有软路由全局代理，如下内容均未考虑国内网络问题。

HA 是一个需要花费大量精力去折腾才能玩好的智能家居控制台，我最近玩了几天，深感它的强大与复杂。

HA 大部分的功能确实都是已有的功能，完全不需要自己写代码，只需要写 yaml 配置即可。
但是即使作为一个专业 yaml 工程师，天天写 kubernetes yaml 配置的我而言，搞懂 HA 的各项配置并做出符合需求的效果，也不是一蹴而就的事。
必须要慢工出细活，不断踩坑填坑，理解它的设计逻辑、使用方法。

### 1. 安装各种必备插件

首先 Home Assistant 的部署没啥可说的，官方推荐使用虚拟机或者 Docker 容器方式运行。

跑起来之后一些建议安装的官方 Add-ons 插件有：

- ESPHome:  前文提过了，如果你打算玩智能家居 DIY，这个是必装的
- File Editor: yaml 编辑器，必装
- Terminal & SSH: 经常会需要 scp/rsync 上传下载一些字体、yaml 配置、自定义组件代码，这个也是必备的
- Grafana: 自定义一些好看的监控面板

然后就是第三方的集成:

- [HACS (Home Assistant Community Store)](https://github.com/hacs/integration): 包含各类流行的社区插件，必装

装好 HACS 后就可以用它安装各类社区插件了，常见的 HACS 插件有：

- Intergrations
  - [hass-xiaomi-miot](https://github.com/al-one/hass-xiaomi-miot): 家里有小米智能设备的话，这个必装
- Frontend
  - [ha-floorplan](https://github.com/ExperienceLovelace/ha-floorplan)
    - 一个重量级的家庭布局图方案，使用 inkscape 生成 svg 图导入过来，比较费时间，但是效果惊艳。
    - 有发烧友直接用平板或触摸屏 + ESP32 制作了家庭中控面板，再把这个可交互的 HA 布局图投上去，效果非常 Nice
  - [mini-graph-card](https://github.com/kalkih/mini-graph-card): 一个非常流行的 HA 图标插件，可以非常简单地配置出各种图表。

上述插件都安装好后，建议按照各插件的官方文档一步步配置。

之后再给家里的安卓手机/平板安装上 HA 客户端，各种安装流程就告一段落了。

### 2. 入门 HA 的使用

建议首先阅读 HA 官方的 [Getting Started](https://www.home-assistant.io/getting-started/) 了解个大概。

其中最重要的是「Advance Configuration」部分，通过 File Editor 修改 HA 的 `configuration.yaml` 是一个非常常用的功能，并不「Advance」！

- 首先点击左下角头像，为自己启用「Advance Mode」

其他关键点：

- 改了 `configuration.yaml` 后必须在 「developer tools」 中 restart 系统
- 在 `cofiguration.yaml` 中间接引用的 `xxx.yaml` 的修改，则可以立即生效，不需要重启。

### 3. 前端 UI 定制

>官方文档：[Multiple Dashboards](https://www.home-assistant.io/dashboards/dashboards/)

官方 Dashboard 的项目名称是 lovelace，进「Settings」=>「Dashboards」就能发现它的 URL Path 为 `/config/lovelace/dashboards`。

在 HACS 的 Frontend 中有很多 lovelace UI 插件可用，但是如果你使用了 yaml 方式配置插件，安装完 lovelace 插件后，还需要手动修改对应的 yaml 配置才行。

比如说你的 `configuration.yaml` 中包含如下配置：

```yaml
lovelace:
  # yaml 模式下，默认 Overview 页面的配置将保存在名为 `ui-lovelace.yaml` 的文件中
  mode: yaml
  resources:
  - url: /hacsfiles/ha-floorplan/floorplan.js
    type: module
  - url: /hacsfiles/lovelace-mushroom/mushroom.js
    type: module
  - url: /hacsfiles/mini-graph-card/mini-graph-card-bundle.js
    type: module
  - url: /hacsfiles/button-card/button-card.js
    type: module
  - url: /hacsfiles/mini-media-player/mini-media-player-bundle.js
    type: module
```

我现在 `ui-lovelace.yaml` 的配置内容为：

```yaml
title: Ryan's Home
views:
    # View tab title.
  - title: Main Tab
    # Unique path for direct access /lovelace/${path}
    path: home
    # Each view can have a different theme applied. Theme should be defined in the frontend.
    theme: dark-mode
    # The cards to show on this view.
    cards:
      # 是的，到目前为止，我还只加了一个音响音乐控件...
      - type: custom:mini-media-player
        entity: media_player.xiao_ai_yin_xiang_1685
```

每次改完配置后，都需要重启 HA，通过 UI 重启 HA 大概只需要 10 秒种即可完成，而且会先进行 yaml 文件参数校验。

### 4. 如何为 HA 写插件

如果有些传感器插件有 bug 或者无法支撑你的需求，那就需要考虑自己写插件了（仅针对有开发能力的程序员而言）。

- [有些硬件太小众了怎么自己写插件](https://bbs.hassbian.com/thread-8054-1-1.html)

## 参考

- [Home Assistant 中文社区](https://bbs.hassbian.com/)
- [HomeAssistant 的插件系统](https://aqzscn.cn/archives/homeassistant-adds-on)
- 品牌智能家居产品相关
  - [铺设智能家居，有哪些传感器和感应器是值得安装的？](https://www.zhihu.com/question/455627729)
  - [如何搭建一个完善的智能家居系统？](https://www.zhihu.com/question/395318023)
  - [智能家居怎么做？](https://www.zhihu.com/question/373947946)
