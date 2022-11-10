# 嵌入式开发 Embedded System

嵌入式分两个方向：

- 单片机开发
  - 介绍：单片机的英文名叫 Microcontroller Unit，即 **MCU**. 它是把 CPU、RAM、定时/计数器（timer/counter）、I/O 接口等都集成在一块集成电路芯片上的微型计算机
  - 应用：主要用于前端的无操作系统、以实时控制为主的环境，如电子钟表、电机控制等。在硬件爱好者手中可用于机器人前端控制，四轴飞行器前端控制，3D打印机前端控制等。
  - 典型产品：
    - Arduino: AVR 单片机为核心控制器的单片机应用开发板，是开源硬件，新手友好
    - STM32: 貌似是单片机从业人员的入行首选
  - 补充说明：
    - 单片机非常简单，因为很接近底层，而且硬件配置极差，干不了太多的事。主要的优势就是稳定、开发也简单。
    - 单片机跟硬件的绑定很严重，经常出现一套代码换一个单片机平台，就得完全重写。
- 嵌入式 Linux 开发（Linux Embedded System）
  - 介绍：即运行 Linux 系统的更复杂的计算机系统，行业上最常用 ARM Cortex-A53 系列芯片与 Linux 开发一些嵌入式设备。
  - 应用：路由器、电视盒子、智能家居等。在硬件爱好者手里可以用来做计算机视觉控制小车、WiFi、蓝牙控制中枢等等。
  - 典型产品
    - Raspberry Pi: 使用 ARM Cortex-M 系列 CPU 的微型计算机，开源硬件，社区庞大，生态丰富。
  - 补充说明
    - 嵌入式 Linux 代码的可移植性相对要好很多，因为硬件相关的逻辑都封装在驱动层了。


重要内容：

- 可运行系统
  - bootloader
  - Linux 内核
- 嵌入式裸机（bare-metal）开发相关内容
  - GPIO
  - 中断
  - 定时器
  - 存储器
  - 协议、接口、总线等概念
    - UART、USB、TCP/IP
  - 无线模块
    - Wifi、Bluetooth
  - 传感器
  - AD 转换
  - 交互模块
    - 显示器、触摸屏、键盘、鼠标

## 我的学习计划

我自身已经有一定 Linux 基础，最近正在学《Linux/Unix 系统编程手册》，也有丰富的 Linux 运维经验，因此基于我自身的条件，我打算这么学嵌入式：

- 从零开始为树莓派 4B 开发一个操作系统：https://github.com/isometimes/rpi4-osdev
- 《Linux/Unix 系统编程手册》
- [Linux Device Drivers (LDD3) ](https://github.com/d0u9/Linux-Device-Driver): Linux 驱动开发经典书籍
- 《深入理解 Linux 内核》
- 《Linux 内核设计与实现》


## 当前我很想玩的项目

如何将 Android/Linux 设备模拟成键盘，实现使用笔记本自带键盘，或者安卓触摸屏，直接进行我家 homelab 的装机。

补充条件：我不想购买任何额外的硬件，比如 Raspberry Zero 或者 Arduino Leonardo.

相关资料：

- [android-usb-gadget](https://github.com/tejado/android-usb-gadget)
- [DIY 一个运维神器 Open IP-KVM](https://zhuanlan.zhihu.com/p/578602475)

## 相关资料

- [我花了半个月，整理出了这篇嵌入式开发学习指南（学习路线+知识点梳理）](https://zhuanlan.zhihu.com/p/169316828)：劝退式嵌入式全景图

