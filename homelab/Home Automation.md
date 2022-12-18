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

具体的玩法，就请自行探索了。我个人的硬件笔记记录在了 [electrical-engineering](/electrical-engineering) 中

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
