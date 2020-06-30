# 通过虚拟机运行原装 MacOS X

通过 VMware/VirtualBox 虚拟机运行 MacOS X，可以用来无痛尝鲜 MacOS X，也可以用来完成一些苹果相关的自动化任务。


## 一、下载 MacOS X 原版镜像

使用脚本：https://github.com/munki/macadmin-scripts/blob/main/installinstallmacos.py

开源脚本从官方下载路径下载原版的 MacOS X 镜像。


## 二、通过 VMware Workstation 运行 MacOS X 虚拟机

### 1. 安装 VMware Workstation

这个应该不需要解释，很常用。

### 2. 安装 unlocker 补丁

最初的 unlocker 仓库已经被 404 了，接盘侠提供的下载路径：https://github.com/paolo-projects/unlocker

这个脚本会从官方拉取 fusion 相关的两个 `zip.tar` 文件，其中有个文件比较大，有 600M+，下载速度比较慢。
可以自己用 aria2 开多线程下载好，然后修改 `gettool.py` 让它使用已下载好的文件。



