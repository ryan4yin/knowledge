# M0s

M0s 启动后默认进入的就是正常运行模式，模式切换方法：

1. 先按住 BOOT 键，再接通电源，然后再放开 BOOT 键，这样能切换到烧录模式。
2. 直接断电重新上电，默认就会进入正常运行模式

## 环境配置方法

跟着官方文档配就
行：[Build with Linux or WSL - BouffaloSDK](https://bl-mcu-sdk.readthedocs.io/zh_CN/latest/get_started/linux_wsl.html)

## 烧录方法

要注意的有两点：

1. 通过 sudo 提权，使烧录器其能正常访问 USB 设备
2. COMX 的值需要设为设备路径，我这里是 `/dev/ttyACM0`

```shell
sudo make flash CHIP=bl616 COMX=/dev/ttyACM0
```
