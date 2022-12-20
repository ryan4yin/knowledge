# 基于 MUC 的一些 demo 程序

## 开发环境搭建

使用基于 [platformio](https://github.com/platformio) 的开源跨平台嵌入式 IDE 开发环境。

platformio 是一个 VSCode 插件，所以先安装好 VSCode，然后直接在插件市场搜索 platformio 安装即可。

安装完成后，在侧边栏的下方就能看到一个蚂蚁头像，点击它即可进入 PlatformIO。

在创建工程的页面，PlatformIO 有提供几乎所有主流单片机平台可选，我个人目前接触到的只有 ESP32、ESP8266、Intel MSC-51(8051) 这三个平台。

创建工程时 platformio 会自动下载对应平台的编译调试工具链（建议使用全局代理），然后就可以玩耍啦。

### Linux 环境特定的配置

对于 Linux 环境，不论是直接使用 esphome web console，还是使用 platformio，都需要将当前用户加入到对应的 group 中，否则浏览器或 platformio 都无法读写 serial port.

详见：[udev-rules and groups for platformio](https://docs.platformio.org/en/latest/core/installation/udev-rules.html)

udev-rules 的配置方法请直接参考上面的链接。
group 的添加方法我简单摘抄如下，对于 arch 用户，需要执行：

```shell
sudo usermod -a -G uucp $USER
sudo usermod -a -G lock $USER
```

对于 debian/ubuntu 用户，需要执行：

```shell
sudo usermod -a -G dialout $USER
sudo usermod -a -G plugdev $USER
```
