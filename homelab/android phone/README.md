# 二手安卓手机拯救计划

用旧手机当 Linux ARM 服务器，有两个方案，下面分别介绍。

## 方案一：在安卓系统上运行 AidLux / Termux

在安卓系统上装个 [AidLux](https://github.com/aidlearning/AidLearning-FrameWork) 或者
[termux/proot-distro](https://github.com/termux/proot-distro)，直接享受完整的 Linux 环境，而且还能无
痛使用安卓系统的各种硬件外设，包括 AI 加速器。它的好处是各类安卓手机都能用，因为是跑在官方安卓系统上
的，兼容性很好，缺点是性能可能就拉了。

TODO 待补充

## 方案二：刷入 postmarketOS/Ubuntu Touch 系统

直接裸机安装 Linux 系统，主要是 postmarketOS 跟 Ubuntu Touch，可以从
[Devices - postmarketOS](https://wiki.postmarketos.org/wiki/Devices) 跟
[Ubuntu Touch Devices](https://devices.ubuntu-touch.io/) 中找兼容性比较好的机器，性价比最高的貌似是
就是一加 6 跟一加 5，骁龙 835/845 比我手上几个国产派的 RK3588s 弱一点点，但买个有瑕疵的价格大概只要
300 - 350。优势是比方案一性能好外设多（屏幕之类的外设用处可能也不大...），缺点就是得有时间折腾...没
AidLux 那么开箱即用。

要刷非官方系统，首先需要解锁 Bootloader，具体解锁方法可参考
[新手入门向-安卓手机通用刷机保姆级全教程（一）解锁BL锁](https://zhuanlan.zhihu.com/p/469315721)

以我闲鱼买的二手一加手机为例，流程如下：

1. 首先关机后长按「电源键」+「音量上键」进入 fastboot 页面，但是此时应该会显示「state」为
   「locked」，这时是无法刷机的。
2. 电脑上下载 android adb 与 fastboot 工具，可以直接从 android 官方文档给的链接下
   载：[安卓 SDK 平台工具](https://developer.android.com/studio/releases/platform-tools?hl=zh-cn)
   1. 对 arch 系列 Linux，aur 或者 archlinuxcn 中都有 `android-sdk-platform-tools` 可以直接安装。
3. 安装或配置驱动，详见官方文档
   [在硬件设备上运行应用](https://developer.android.com/studio/run/device?hl=zh-cn)
   1. 根据官方文档，Windows 需要安装文档中提供的 USB 驱动程序，而 Linux 则需要配置好 Udev 相关权限。
4. 通过 `fastboot flashing unlock` 命令打开解锁页面，然后通过音量上下键选择 Unlock，按电源键确认，这
   样就完成了 BL 解锁。

之后就是根据 postmarketOS 或 Ubuntu Touch 的官方文档刷入系统了，我刷一加 5 手机时这一步没遇到啥坑，
只是要注意打开全局梯子，不然下东西太慢了。

但是 Ubuntu Touch 刷完后用不了 apt，因为 `/` 根卷默认会被挂载成 read-only，解决方法是，在对系统卷做
任何更改前，手动跑下下面这个命令：

> 参考了
> [Lomiri - the graphical UI - Make / (root) writable](https://docs.ubports.com/en/latest/porting/configure_test_fix/Lomiri.html?highlight=rw#make-root-writable)

```c
sudo mount -o remount,rw /
```

这条命令临时将 `/` 重新挂载为可读，重启后就失效了。

> 因为一般也不怎么需要改系统卷，尤其是 ubuntu touch 还不能随便跑 `apt upgrade`，感觉重启失效也可以接
> 受

这搞定后，后续基本就是：

- 安装 vim vscode 之类的编辑器
- 使用 systemctl 启用 ssh 服务器
- etc...

其他玩法就参见 Ubuntu Touch 的官方文档
吧：[Advanced use - UBports Docs](https://docs.ubports.com/en/latest/userguide/advanceduse/index.html)
