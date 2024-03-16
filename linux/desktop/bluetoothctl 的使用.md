# Bluetooth 工具

> https://wiki.archlinux.org/title/Bluetooth

蓝牙，常用场景有：

- 蓝牙游戏手柄
- 蓝牙鼠标键盘
- 低功耗蓝牙智能家居产品
- ...

通常的 Linux 桌面或者 Windows/MacOS/Android 系统都能很容易地通过 UI 界面连接上安卓，但是对于无 UI 的
场景，就需要通过 bluetoothctl 进行相关操作。

这通常发生在通过 ssh 使用 raspberrypi，或者桌面为 i3wm/sway 等窗口管理系统的场景。

以我的 endeavour 系统 + i3wm 桌面为例，它自带蓝牙相关的程序，但是默认根本不启用蓝牙。

使用流程如下：

1. 首先通过 systemctl 启用蓝牙服务

```shell
sudo systemctl enable bluetooth
sudo systemctl start bluetooth
```

2. 然后确保 rfkill 没有禁掉 bluetooth 功能
   ```shell
   rkfill block bluetooth
   rkfill unblock bluetooth
   ```
3. 现在通过 `bluetoothctl` 命令进入其交互 CLI，然后输入如下命令启动蓝牙
   ```shell
   # 启动蓝牙
   power on
   agent on
   default-agent
   ```
4. 打开你要连接的蓝牙设备，使其进入配对模式，并提前确认好该设备的蓝牙名称（设备名称一般会写在说明书
   或者设备铭牌中）。
5. 使用如下命令连接该蓝牙设备：
   ```shell
   # 启动蓝牙扫描，然后在打印的日志中找到你的蓝牙名称，复制日志中该设备的 MAC 地址
   scan on
   # 首先与该设备配对，然后信任该设备，最后再连接该设备
   # 请将 <device-mac-addr> 替换为你的设备 mac 地址
   pair <device-mac-addr>
   trust <device-mac-addr>
   connect <device-mac-addr>
   ```
