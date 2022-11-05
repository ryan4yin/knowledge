# 装机工具

物理机推荐使用如下几种方式安装：

- [Ventoy](https://github.com/ventoy/Ventoy): 万能 USB 启动器，可引导各类 ISO 镜像，支持 Windows/Linux 系统。
- [netboot.xyz](https://github.com/netbootxyz/netboot.xyz): 相比 ventoy，它更进一步，可以直接通过网络安装 iso 文件，都不需要插 U 盘启动盘，支持 Windows/Linux。
- [cobbler](https://github.com/cobbler/cobbler): 通过网络全自动化地安装 Linux 服务器，支持 Windows/Linux.
  - 国内能搜到很多教程。
- [etcher](https://github.com/balena-io/etcher): Flash OS images to SD cards & USB drives, safely and easily.

虚拟机建议克隆/通过模板新建，速度快而且环境绝对一致。


## 定制 ISO 镜像

自动安装系统的工具有了，但是每个系统的软件仍然需要自己安装，还是很繁琐。要是能定制 ISO 镜像就好了。

- Windows: [dism++](https://www.chuyu.me/zh-Hans/)
- Linux: 建议使用虚拟化系统 ProxmoxVE + 虚拟机模板。
  - 非要定制的话，另行找文档吧，好像也不难。
