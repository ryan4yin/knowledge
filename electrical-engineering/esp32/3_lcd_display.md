# LCD 液晶显示屏

我手上有这几块 LCD 显示屏：

- LCD 液晶显示屏：0.96 寸，128 * 64，使用 I2C 协议，四个引脚，驱动 IC 为 SSD1315
- TFT SPI 显示屏
  - [2.8 寸，320 * 240，使用 4 数据线 SPI 协议，驱动 IC 为 ILI9341](http://www.lcdwiki.com/2.8inch_SPI_Module_ILI9341_SKU:MSP2807)
  - [3.5 寸电阻触摸屏，480 * 320，同样是 SPI 协议，驱动 IC 为 ILI9488](http://www.lcdwiki.com/3.5inch_SPI_Module_ILI9488_SKU:MSP3520)

一番查询，找到如下几个 stars 数较高的显示屏驱动库：

- [Bodmer/TFT_eSPI](https://github.com/Bodmer/TFT_eSPI): 一个基于 Arudino 框架的 tft 显示屏驱动，支持 STM32/ESP32 等多种芯片。
- [lv_port_esp32](https://github.com/lvgl/lv_port_esp32): 一个 MCU 图形库，官方就提供 esp32 的兼容层，但是目前仅支持到 esp-idf v4。


## 程序



