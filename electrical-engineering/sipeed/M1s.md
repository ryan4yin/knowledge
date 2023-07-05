# M1s

M1s 启动后默认进入的就是烧录模式，模式切换方法：

1. 直接点击 RST 按键，切换到正常模式，开始执行固件。
2. 先按住 BOOT，然后点击 RST 键，然后再放开 BOOT，这样能切换到烧录模式。

如果切换后发现系统仍然没有 `/dev/ttyACMx` 设备，可重启再试试。

>我遇到的问题就是无法挂载上 `/dev/ttyACMx` 设备，原因是我跑了 `yay -Syyu` 更新系统，但是还没重启...手动重启后就恢复了。

## 固件编译

根据官方文档 [sipeed/M1s_BL808_example](https://gitee.com/sipeed/M1s_BL808_example) 配置环境并编译即可，这没啥难度。

## 固件烧录

> 说实话有点离谱，还非得搞 GUI 程序烧录...整个 CLI 又好用又方便，多好啊...

烧录这里，直接根据官方文档下载 `Bouffalo Lab Dev Cube` 使用即可，我在 Arch Linux 上实测可以正常使用其中的 `BLDevCube-ubuntu` 程序，不过需要通过 `sudo` 提供访问 USB 设备的权限。

另外一点是 partition table 不能使用 `Bouffalo Lab Dev Cube` 内置的分区表文件，会导致程序无法正常运行！**必须下载并使用 [M1s_Dock/7_Firmware/partition - Sipeed](https://dl.sipeed.com/shareURL/MAIX/M1s/M1s_Dock/7_Firmware/partition)** 中提供的分区表才能正常工作。
