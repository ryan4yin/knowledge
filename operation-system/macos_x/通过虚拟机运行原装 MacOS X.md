# 通过虚拟机运行原装 MacOS X

通过 VMware/VirtualBox 虚拟机运行 MacOS X，可以用来无痛尝鲜 MacOS X，也可以用来完成一些苹果相关的自动化任务。


## 一、下载制作 MacOS X 原版镜像

首先你得有一台可用的 MacOS X 机器。

在 MacOS X 系统中使用脚本：https://github.com/munki/macadmin-scripts/blob/main/installinstallmacos.py

上面提供的开源脚本会从官方下载路径下载原版的 MacOS X 镜像，然后在脚本所在目录下创建一个 dmg 安装镜像。
**注意这个 dmg 镜像不能直接当成 boot disk 使用！可引导的 dmg 镜像还是需要自己手动制作。**

下载完成后可以通过 [apple-installer-checksums](https://github.com/notpeter/apple-installer-checksums) 验证镜像内容的 hash 值。

第二步是制作可引导的 dmg 镜像：

```shell
# 1. 创建一个空的 dmg 镜像，会将它制作成可引导的 dmg
hdiutil create -o MacOS15.dmg -size 9000m -layout SPUD -fs HFS+J
# 2. 挂载刚刚创建好的 dmg 镜像
hdiutil attach MacOS15.dmg -noverify -mountpoint /Volumes/new_mac_installer
# 3. 挂载 installinstallmacos.py 创建好的 dmg 镜像
hdiutil attach Install_macOS_10.15.5-19F2200.dmg -noverify -mountpoint /Volumes/MacOS_Installer
# 4. 创建可引导的数据卷
/Volumes/MacOS_Installer/Install\ macOS\ Catalina.app/Contents/Resources/createinstallmedia --volume /Volumes/new_mac_installer
# 5. 卸载创建完成的数据卷
hdiutil detach /Volumes/Install\ macOS\ Catalina/
```

这样就得到了可引导的数据卷：`MacOS15.dmg`

最后一步是将 dmg 镜像转换成 vmware/virtualbox 使用的 iso 格式：

```shell
hdiutil convert MacOS15.dmg -format UDTO -o macOS_10.15.5-19F2200.cdr
mv Install_macOS_10.15.5-19F2200.cdr Install_macOS_10.15.5-19F2200.iso
```

大功告成。

## 二、通过 VMware Workstation 运行 MacOS X 虚拟机

### 1. 安装 VMware Workstation

这个应该不需要解释，很常用。

### 2. 安装 unlocker 补丁

最初的 unlocker 仓库已经被 404 了，接盘侠提供的下载路径：https://github.com/paolo-projects/unlocker

这个脚本会从官方拉取 fusion 相关的两个 `zip.tar` 文件，其中有个文件比较大，有 600M+，下载速度比较慢。
可以自己用 aria2 开多线程下载好，然后修改 `gettool.py` 让它使用已下载好的文件。

直接通过仓库提供的 `win-install.sh`/`lnx-install.sh` 安装补丁就行。

VMware ESXi 请使用专用版本：https://github.com/shanyungyang/esxi-unlocker

### 3. 使用 iso 镜像创建 MacOS X 虚拟机

安装好 unlocker 后，通过 VMware Workstation 创建虚拟机流程如下：

1. 硬件兼容性选择：WOrkstation 15.x
2. 选择使用之前创建好的 iso 映像文件
3. 操作系统选择：[Apple Mac OS X] - [macOS 10.15]，版本和你的 iso 文件要对应
4. 设置好 CPU/RAM 大小。
5. 硬盘兼容 APFS: 

然后启动，正常情况下应该就会显示一个白苹果和进度条，后面就都是走流程了。

## 参考

- [制作macOS系统dmg包及iso可引导镜像](https://www.newlearner.site/2019/03/07/macos-dmg-iso.html)
- [使用PD和VM虚拟机安装macOS](https://www.newlearner.site/2019/03/23/macos-pd-vm.html)
- [macOS完整安装包下载方法](https://www.newlearner.site/2019/07/22/full-size-macos.html)

