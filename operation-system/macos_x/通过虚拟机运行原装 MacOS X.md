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

### 1. 安装 VMware Workstation 或者 vShpere ESXi

VMware Workstation 应该不需要解释，桌面虚拟机软件，很常用。

vShpere ESXi 是 VMware 家的服务器虚拟化系统，基于 Linux。

### 2. 安装 unlocker 补丁

#### 1) VMware Workstation

要在 Windows/Linux 上通过 VMware Workstation 运行 macOS，需要先通过 unlocker 打补丁。使用如下脚本：

1. Unlocker for VMware Workstation ：https://github.com/paolo-projects/unlocker

这个脚本会从官方拉取 fusion 相关的两个 `zip.tar` 文件，其中有个文件比较大，有 600M+，下载速度比较慢。
可以自己用 aria2 开多线程下载好，然后修改 `gettool.py` 让它使用已下载好的文件。

直接通过仓库提供的 `win-install.sh`/`lnx-install.sh` 安装补丁就行。

#### 2) vShpere ESXi

虽然 ESXi 创建虚拟机时，默认就可以选择 macOS 系统，但是它要求使用 Apple 专用硬件。如果使用不兼容的硬件，macOS 会无限重启！！！

为了在常用的服务器上通过 ESXi 运行 macOSs，就需要通过 unlocker 打系统补丁。unlocker 仓库如下：

1. Unlocker for ESXi：https://github.com/shanyungyang/esxi-unlocker

打补丁步骤：

1. 在一台 macOS 上克隆前面提供的 unlocker 仓库
   1. macOS 上需要提前通过 `brew install gnu-tar` 安装好 gnu-tar，对应 gtar 命令！
   2. Linux 应该也可以（未测试），因为这个脚本只是使用 tar 进行压缩而已。不过需要将 `esxi-build.py` 中的 `/usr/local/bin/gtar` 替换成 `tar`。
2. 运行 `python esxi-build.py` 构建好 unlocker 补丁。
3. ESXi 启动 ssh 服务（安全 shll），然后通过 scp 命令（或 winscp 等带 UI 的工具）将上一步得到的东西拷贝到 ESXi 的 `/vmfs/volumes/datastore1/` 中
4. 参考 unlocker 的 README，解压然后运行 `esxi-install.sh`。
5. 根据提示重启 ESXi.
6. 完成。

重启好后，可以再次启用安全 Shell，然后运行 `/vmfs/volumes/datastore1/esxi-smctest.sh` 确认补丁是否生效。正常情况下应该输出如下内容：

```
/bin/vmx
smcPresent = true
custom.vgz     false   32486592 B
```

### 3. 使用 iso 镜像创建 MacOS X 虚拟机

安装好 unlocker 后，通过 VMware Workstation 创建虚拟机流程如下：

1. 硬件兼容性选择：WOrkstation 15.x
2. 选择使用之前创建好的 iso 映像文件
3. 操作系统选择：[Apple Mac OS X] - [macOS 10.15]，版本和你的 iso 文件要对应
4. 设置好 CPU/RAM 大小。其他参数全部使用默认的就行。
5. 然后启动，正常情况下应该就会显示一个白苹果和进度条。
6. 进入磁盘工具，将 VMware 创建好的空硬盘格式化为 APFS 格式。
7. 选择「Install macOS」，后面就完全是走流程，傻瓜式操作了。

在 ESXi 上安装 MacOS 也是差不多的流程。需要注意的是兼容性问题。
只有 ESXi 6.7U3+ 的版本才支持最新的 macOS 10.15。因此你可能需要先升级最新的 ESXi 系统。

详细的兼容性参见官方页面：[VMware Compatibility Guide](https://www.vmware.com/resources/compatibility/search.php?deviceCategory=software&details=1&operatingSystems=261&productNames=15&page=1&display_interval=10&sortColumn=Partner&sortOrder=Asc&testConfig=16)

## 参考

- [制作macOS系统dmg包及iso可引导镜像](https://www.newlearner.site/2019/03/07/macos-dmg-iso.html)
- [使用PD和VM虚拟机安装macOS](https://www.newlearner.site/2019/03/23/macos-pd-vm.html)
- [macOS完整安装包下载方法](https://www.newlearner.site/2019/07/22/full-size-macos.html)
- [VMWare ESXI 配置macOS虚拟机](https://o0xmuhe.github.io/2019/05/10/macOS-on-ESXi/)
