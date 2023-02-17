# ESP32 系列芯片

我目前手上已有的 ESP 芯片：

- ESP8266 * 3
  - 乐鑫最早的产品，一切的开始，发布于 2014 年。我手上现在有 ESP-01S * 2，NodeMCU ESP8266 * 1
  - 这款芯片火遍全球，应用相当广泛，现在在智能家居 DIY 领域仍然有很多应用的。
  - 不过它太老了，功耗也大，官方生态已经不再对它提供支持，所以不推荐玩了。
- NodeMCU ESP-WROOM-32 (ESP32) * 2
  - ESP32 是乐鑫的主力产品，发布于 2016 年，功耗比 ESP8266 低了很多。
  - 目前仍然是乐鑫外设最全面的芯片，支持各种常见传感器，生态也很丰富，可玩性高。
- ESP32-C3 * 2（两块合宙的开发版，便宜）
  - 这是乐鑫的第一款 RISC-V 芯片，32 位。
  - 引脚比 ESP32 少很多，不过优势就是更便宜。
- ESP32-S3 * 2（也是两块合宙的开发版，便宜）
  - 乐鑫目前最新的旗舰芯片，添加了神经网络计算需要的向量指令，主要目标是 AIoT 领域。
  - 也是目前 ESP32 系列中性能最强的芯片，当然价格显然也最高。

至于 ESP32 的固件开发方法，我已知目前有这几种：

- 乐鑫官方的 [ESP-IDF](https://www.espressif.com/zh-hans/products/sdks/esp-idf)
- 乐鑫官方的 [Arduino-ESP32](https://github.com/espressif/arduino-esp32) 开发工具包
- [MicroPython for ESP32](https://docs.micropython.org/en/latest/esp32/quickref.html)
- [esp-rs](https://github.com/espressif?q=&type=all&language=&sort=stargazers): esp 官方的 rust 支持项目，很活跃
  - [espressif-trainings](https://github.com/ferrous-systems/espressif-trainings)
- [toitlang](https://github.com/toitlang): 在乐鑫 2022 年开发者大会上看到的新鲜玩意儿，在 MCU 上整 VM 跑微服务...这有机会不得试试...
- [nuttx](https://github.com/apache/nuttx): 对 POSIX 标准兼容最好的 RTOS，这意味着很多 Linux 的东西，都可以做少量修改就移植上来，适合做游戏啥的。原生支持 ESP32 当前所有主流芯片。
- [TinyGo](https://tinygo.org/docs/reference/microcontrollers/esp32-coreboard-v2/): 它目前（2023/2/15）对 ESP32 的支持还比较鸡肋，WIFI/Bluetooth/PWM/I2C/ADC 都不支持，没啥可玩性，不推荐使用。

目前官方最推荐的是 ESP-IDF，但它比较偏底层，而且环境比较复杂，使用了 CMake、Kconfig 等环境配置工具，又搞了 Ninja 模板语言、还用 Python 写测试，对新手而言陌生的东西太多，是个很大的挑战。

因此对新手而言，目前更推荐使用 Arduino-ESP32 或者 MicroPython 进行开发。

于我而言，我目前其实更想练手 C 语言，所以正在从 ESP-IDF 入门，然后后面再学习 Arduino-ESP32，Arduino 对我而言可能更适合作为 IDF 的一个组件来使用，以利用上 Arduino 丰富的生态，详见官方文档 [Arduino as an ESP-IDF component](https://docs.espressif.com/projects/arduino-esp32/en/latest/esp-idf_component.html)。

## 使用 VSCode + ESP-IDF 进行程序开发

- 首先参考 esp-idf 官方文档进行配置，copy 一个 example 项目并成功烧录进开发板
- 然后解决下语法提示的问题，根据 VSCode ESP-IDF 插件文档 [Configuration of c_cpp_properties.json file](https://github.com/espressif/vscode-esp-idf-extension/blob/master/docs/C_CPP_CONFIGURATION.md)，可通过 Ctrl + Shift + P 组合键打开命令搜索面板，输入 `Add vscode configuration folder` 并回车，就能自动添加好 C/C++ 的库引用配置，这样 VSCode 的语法提示就正常了。

为了更好地使用，最好是再看下 VSCode 插件的官方文档 [ONBOARDING - vscode-esp-idf-extension](https://github.com/espressif/vscode-esp-idf-extension/blob/master/docs/ONBOARDING.md)

另外 ESP-IDF 的环境依赖较多，配置起来有点复杂，如果你熟悉 Docker，其实前面的官方文档就提供了使用 Docker 进行开发的教程：[Using Docker Container - vscode-esp-idf-extension](https://github.com/espressif/vscode-esp-idf-extension/blob/master/docs/tutorial/using-docker-container.md)，不过仅针对 Windows 环境，Linux 环境可能还得做点调整（比如需要在 `/etc/udev/rules.d` 中添加 `openocd.rules`）。

## ESP-IDF 学习路线

基本上就是先跟着官方文档的 Quick Start 入个门，然后跟一下官方的 jumpstart 入门教程开发一个完整的 Demo 应用：

- [espressif/esp-jumpstart](https://github.com/espressif/esp-jumpstart)


这样就算入门了，之后就是根据自身需要从官方的 exmaples 中找出自己需要的例子来玩耍：

- [esp-idf/examples](https://github.com/espressif/esp-idf/tree/master/examples)
- [esp-iot-solution/examples](https://github.com/espressif/esp-iot-solution/tree/master/examples)

要注意的是，目前这些 idf 之外的组件基本都仅支持到 idf v4.4，如果要用最新的 v5.0，大概要自己参照官方兼容表，改下代码才行。

至于其他组件，我在 [2022 乐鑫全球开发者大会](https://space.bilibili.com/538078399/channel/collectiondetail?sid=793367) 中淘到不少好东西，强烈建议你翻一翻这个开发者大会的视频列表，肯定能找到不少你感兴趣的内容。

我目前搜集到的一些好东西：

- [Wokwi - Online ESP32 & Arduino Simulator](https://wokwi.com/): ESP32 模拟器，支持 C/Arudino/MicroPython 等多种开发环境。
- [Rust on Wokwi - Online ESP32 Simulator](https://wokwi.com/rust): Rust 版的 ESP32 在线模拟器


## ESPHome 篇

我从 ESPHome 入坑开始慢慢熟悉电子电路，陆续在多个淘宝店买了许多相关组件，罗列如下：

- 开发版
  - ESP32
  - ESP32-C3
  - ESP8266 系列（在 Homelab 里很流行啊，主要够成熟，生态支持够好）
    - ESP-12F mini D1 开发版
    - ESP-01S 无线模块 + 2 个 Relay 继电器模块
      - 核心也是 ESP8266 但是只引出了 8 个针脚，适合用在智能插座等场景
    - ESP32-CAM 开发版 + OV2640 摄像头
- 各种传感器：光敏、粉尘、空气质量、人体红外感应、红外发射接收、霍尔磁力、光强度、温湿度、液晶显示屏（单色/全彩）、麦克风等等
- 其他
  - USB 转 TTL 串口板
  - microUSB 数据线（一定注意得是数据线，买东西送的线很多都是纯电源线不能用）
  - 830/400 孔面包板 + 面包板专用电源 * 4
  - 面包线一盒 + 母对母杜邦线 40P（即 40 根） + 母对公杜邦线 40P + 热缩管一盒
  - 10 格零件盒 + 大号 8 格零件盒
  - 镊子一套 6 个
  - 防静电手环（冬天玩电子设备必备）
  - USB 升压线（USB 5v 输入，DC 12v 输出）
  - 万用表（建议买个好点的自动量程表，当然几十块的手动量程也完全够用...）

## 彩色灯带相关仓库

- [WLED](https://github.com/Aircoookie/WLED): Control WS2812B and many more types of digital RGB LEDs with an ESP8266 or ESP32 over WiFi! 
- [blinker-library](https://github.com/blinker-iot/blinker-library): 物联网接入方案，可以通过它将彩色灯带接入到小米之家里，用小爱同学控制。


