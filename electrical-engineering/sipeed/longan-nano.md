# Loggan Nano

## 进入烧录模式：

上电后，先按住 BOOT 键，再点击 RESET 键，最后放开 BOOT 键，这样就能切换到烧录模式

## 编译方法

直接用 platformio 创建项目即可，示例程序可以从 [sipeed/platform-gd32v/examples](https://github.com/sipeed/platform-gd32v/tree/master/examples) 里面找。

## 烧录方法

官方文档 [Blink 闪灯程序 - Sipeed Longan Nano](https://wiki.sipeed.com/hardware/zh/longan/Nano/get_started/blink.html) 提供了如下几种烧录方法：

1. 串口 ISP 下载 - 需要额外的 USB 转 TTL 下载器
   1. `platformio.ini` 使用参数 `upload_protocol = serial`
2. JTAG 下载 - 需要 J-link 或 Sipeed RV 调试器
   1. `platformio.ini` 使用参数 `upload_protocol = jlink` 或者 `upload_protocol = sipeed-rv-debugger`
3. USB DFU 下载 - 直接插上 USB 数据线就能用
   1. `platformio.ini` 使用参数 `upload_protocol = dfu`
   2. 测了 Linux 能直接用，windows 看文档是要手动装驱动




