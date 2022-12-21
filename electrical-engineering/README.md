# 电子电路

小时候同村的一个伙伴买了台遥控赛车，我们羡慕地不行，眼巴巴地希望他能多分一点时间给我玩。但是我从小到大从来没买过任何一台遥控赛车。

受限于金钱，大学学的也不是计算机，大学期间也从未接触过硬件，现在希望能在业余完成这个小时候的赛车玩具梦吧。
比如制作一台遥控小车、带有深度学习功能的自走小车、机器人手臂等等，都感觉很有意思。

更进一步，我能否做一些更有意思的东西呢？比如说机器人！


## 我的学习计划

### 1. Linux 与嵌入式

我自身已经有一定 Linux 基础，最近正在学《Linux/Unix 系统编程手册》，也有丰富的 Linux 运维经验，因此基于我自身的条件，我打算这么学嵌入式：

- 从零开始为树莓派 4B 开发一个操作系统：https://github.com/isometimes/rpi4-osdev
- 《Linux/Unix 系统编程手册》
- [Linux Device Drivers (LDD3) ](https://github.com/d0u9/Linux-Device-Driver): Linux 驱动开发经典书籍
- 《深入理解 Linux 内核》
- 《Linux 内核设计与实现》

我可能的发烧路线图：51 MCU　=> ESP32 MCU => STM32 MCU => FPGA

目前感兴趣的板子：

- Orange Pi 5: 高性能 SBC，支持　8K 视频解码，不过据说 GPU/NPU 的软件栈还需要至少半年迭代（当前 2022/12/21）
- Vision Five 2: 赛昉科技的 RISC-V 开发板，对 RISC-V 有些兴趣，不过没想好买它干啥...

### 2. 电子电路

边玩边学习相关知识是最有意思的，先玩到一定阶段后，再补一补基础知识如《模拟和数字电子电路基础》，并结合 Multisim（元器件仿真）、Proteus（单片机仿真）等仿真软件同步学习。

## 当前我很想玩的项目

如何将 Android/Linux 设备模拟成键盘，实现使用笔记本自带键盘，或者安卓触摸屏，直接进行我家 homelab 的装机。

补充条件：我不想购买任何额外的硬件，比如 Raspberry Zero 或者 Arduino Leonardo.

相关资料：

- [android-usb-gadget](https://github.com/tejado/android-usb-gadget)
- [DIY 一个运维神器 Open IP-KVM](https://zhuanlan.zhihu.com/p/578602475)
- PD充电器诱骗
  - [自制QC2.0诱骗器](https://yuanze.wang/posts/qc2-0-adapter/)
  - 也可以使用成熟的芯片方案，关键词为「PD/QC 取电芯片」

## 相关资料

机器人相关：

- [how-to-learn-robotics](https://github.com/qqfly/how-to-learn-robotics)
- [gobot](https://github.com/hybridgroup/gobot)




