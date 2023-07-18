## 全身追踪方案 - SlimeVR

目前最牛逼的开源方案就是 [SlimeVR - VR Full Body Tracking](https://github.com/SlimeVR/SlimeVR-Tracker-ESP)，正道的光！

使用 ESP32 + IMU 惯性传感器，通过 WiFi 传输数据到 PC，然后通过 SteamVR Driver 传输到 SteamVR，最后 Beat Saber 里就可以看到全身追踪的效果了。

整个方案完全可以自己动手搞定，PCB 打板用嘉立创再自己手工焊接，外壳 3D 打印可以用淘宝（如果自己有打印机也可以自己打）。

当然嫌麻烦也完全可以闲鱼淘宝买现成的。

SlimeVR 包含两个部分，Tracker 和 Driver，Tracker 是 ESP32 + IMU 惯性传感器，Driver 是 SteamVR Driver，用于将 Tracker 传输到 SteamVR，它们的文档如下：

- [Slime Tracker DIY Guide](https://docs.slimevr.dev/diy/index.html): Tracker 的 DIY 教程，包含 PCB 打板、焊接、3D 打印、烧录固件等。
- [SlimeVR Setup](https://docs.slimevr.dev/server/index.html): 在 Tracker 都调试并烧录好固件后，再根据这个教程配置 Driver，使整套追踪系统可以在你玩 Steam 游戏时正常工作。

废话不多说，总之我打算自己 DIY 一套 SlimeVR 系统，这里记录下我 DIY 的过程。

### 一、Tracker


