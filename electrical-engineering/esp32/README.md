# ESP32 系列芯片

我目前手上已有的 ESP 芯片：

- ESP-01S (ESP8266) * 3
  - 乐鑫的早期产品，发布于 2014 年。
  - 这款芯片火遍全球，应用相当广泛，现在在智能家居 DIY 领域仍然有很多应用的。
  - 不过它太老了，功耗也大，官方生态已经不再对它提供支持，所以不推荐玩了。
- NodeMCU ESP-WROOM-32 (ESP32) * 2
  - 乐鑫的主力产品，发布于 2016 年，功耗比 ESP8266 低了很多。
  - ESP32 目前仍然是乐鑫外设最全面的芯片，支持各种常见传感器，生态也很丰富，可玩性高。
- ESP32-C3 * 2
  - 这是乐鑫的第一款 RISC-V 芯片，32 位。
  - 引脚比 ESP32 少很多，不过优势就是更便宜。
- ESP32-S3 * 2
  - 乐鑫目前最新的旗舰芯片，添加了神经网络计算需要的向量指令，主要目标是 AIoT 领域。
  - 也是目前 ESP32 系列中性能最强的芯片，当然价格显然也最高。

至于 ESP32 的固件开发方法，目前有这几种：

- 乐鑫官方的 [ESP-IDF](https://github.com/espressif/esp-idf)
- 乐鑫官方的 [Arduino-ESP32](https://github.com/espressif/arduino-esp32) 开发工具包
- [MicroPython for ESP32](https://docs.micropython.org/en/latest/esp32/quickref.html)
- [Rust on ESP](https://esp-rs.github.io/book/)
- [TinyGo](https://tinygo.org/docs/reference/microcontrollers/esp32-coreboard-v2/): 它目前（2023/2/15）对 ESP32 的支持还比较鸡肋，WIFI/Bluetooth/PWM/I2C/ADC 都不支持，没啥可玩性。

目前官方最推荐的是 ESP-IDF，但它比较偏底层，而且环境比较复杂，使用了 CMake、Kconfig 等环境配置工具，又搞了 Python 来做测试，对新手而言陌生的东西太多，是个很大的挑战。

因此对新手而言，目前更推荐使用 Arduino-ESP32 或者 MicroPython 进行开发。

于我而言，我目前其实更想练手 C 语言，所以打算 ESP-IDF 与 Arduino-ESP32 都尝试一下。


