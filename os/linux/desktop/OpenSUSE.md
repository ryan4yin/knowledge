OpenSUSE
---

OpenSUSE 是一个基于 RPM 的发行版，这和 RHEL/CentOS 一致。
但是它的官方包管理器是专有的 zypper，挺好用的，软件也很新。

我最近从 Manjaro 切换到了 OpenSUSE，发现 KDE 桌面确实比 Manjaro 更丝滑，而且社区源 OBS 体验下来比 AUR 更舒服。
尤其是容器/Kubernetes 方面，源里面的东西比 AUR 更丰富，而且是官方维护的。
本文算是对迁移流程做的一个总结。

>本文以 OpenSUSE Leap 15.2 为基础编写，因此部分软件需要手动添加 OBS 源，才能获得到更新的版本。
>你也可以考虑使用 Tumbleweed，它是滚动更新的，软件要比 Leap 新很多。

## 一、zypper 的基础命令

zypper 的源在国内都比较慢，可以考虑配一下国内镜像源：

```shell
# 禁用原有的四个官方软件源
sudo zypper mr --disable repo-oss repo-non-oss repo-update repo-update-non-oss
# 添加北外镜像源，注意单引号不能省略！
sudo zypper ar -fcg 'https://mirrors.bfsu.edu.cn/opensuse/distribution/leap/$releasever/repo/oss' BFSU:OSS
sudo zypper ar -fcg 'https://mirrors.bfsu.edu.cn/opensuse/distribution/leap/$releasever/repo/non-oss' BFSU:Non-OSS
sudo zypper ar -fcg 'https://mirrors.bfsu.edu.cn/opensuse/update/leap/$releasever/oss' BFSU:Update-OSS
sudo zypper ar -fcg 'https://mirrors.bfsu.edu.cn/opensuse/update/leap/$releasever/non-oss' BFSU:Update-Non-OSS
```

镜像源配置好后，首先更新下系统软件：

```shell
sudo zypper refresh  # refresh all repos
sudo zypper update   # update all softwares
```

实测不设置镜像源时，平均速度大概 300kb/s，使用软件源速度能达到 10MB/s，我的带宽也就这么大。

## Install Softwares

>这里需要用到 [OBS(Open Build Service, 类似 arch 的 AUR，但是是预编译的包)](https://mirrors.opensuse.org/list/bs.html)，因为 OBS 东西太多了，因此不存在完整的国内镜像，平均速度大概 300kb/s。
>建议有条件可以在路由器上加智能代理提速。

安装需要用到的各类软件: 

```shell
# 启用 Packman 仓库，使用北交镜像源（注意单引号不能省略！）
sudo zypper ar -cfp 90 'https://mirror.bjtu.edu.cn/packman/suse/openSUSE_Leap_$releasever/' packman-bjtu

# install video player and web browser
sudo zypper install mpv ffmpeg chromium firefox

# install screenshot and other utils
# 安装好后可以配个截图快捷键 alt+a => `flameshot gui`
sudo zypper install flameshot peek nomacs

# install git clang/make/cmake
sudo zypper install git gcc clang make cmake

# install wireshark
sudo zypper install wireshark
sudo gpasswd --add $USER wireshark  #  将你添加到 wireshark 用户组中
```

### IDE + 编程语言

```shell
# install vscode: https://en.opensuse.org/Visual_Studio_Code
sudo rpm --import https://packages.microsoft.com/keys/microsoft.asc
sudo zypper addrepo https://packages.microsoft.com/yumrepos/vscode vscode
sudo zypper refresh
sudo zypper install code

# 安装 dotnet 5: https://docs.microsoft.com/en-us/dotnet/core/install/linux-opensuse#opensuse-15-
sudo rpm --import https://packages.microsoft.com/keys/microsoft.asc
sudo zypper addrepo https://packages.microsoft.com/opensuse/15/prod/ microsoft-prod
sudo zypper refresh
sudo zypper install dotnet-sdk-5.0

# 安装新版本的 go（注意单引号不能省略！）
sudo zypper addrepo 'https://download.opensuse.org/repositories/devel:/languages:/go/openSUSE_Leap_$releasever' devel-go
sudo zypper refresh
sudo zypper install go
```

通过 tarball/script 安装：

```shell
# rustup，rust 环境管理器
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

# jetbrains toolbox app，用于安装和管理 pycharm/idea/goland/android studio 等 IDE
# 参见：https://www.jetbrains.com/toolbox-app/

# 系统自带的 python3 太老，用 miniconda 装 python3.8
# 参考：https://github.com/ContinuumIO/docker-images/blob/master/miniconda3/debian/Dockerfile
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O /tmp/miniconda.sh
sudo /bin/bash /tmp/miniconda.sh -b -p /opt/conda
rm /tmp/miniconda.sh
sudo /opt/conda/bin/conda clean -tipsy
sudo ln -s /opt/conda/etc/profile.d/conda.sh /etc/profile.d/conda.sh
echo ". /opt/conda/etc/profile.d/conda.sh" >> ~/.bashrc
echo "conda activate base" >> ~/.bashrc
# miniconda 的 entrypoint 默认安装在如下目录，添加到 PATH 中
echo "export PATH=\$PATH:\$HOME/.local/bin" >> ~/.bashrc
```


接下来安装 VSCode 插件，下列是我的插件列表：

1. 语言：
    1. python/go/rust/c#/julia/flutter
    2. xml/yaml/toml
    3. vscode proto3
2. ansible/terraform
3. markdown all in one + Markdown Preview Enhanced
4. 美化：
   1. community material theme
   2. vscode icons
   3. glasslt-vsc
5. docker/kubernetes
6. IntelliJ IDEA Keybindings
7. gitlens
8. prettier
9. utils
    1. comment translate
    2. path intellisense
    3. svg
    4. visual studio intellicode
10. antlr4
11. remote ssh + remote containers
12. rest client
13. vscode databases

### 容器 + Kubernetes

```shell
# 时髦的新容器套装: https://documentation.suse.com/sles/15-SP2/html/SLES-all/cha-podman-overview.html
sudo zypper in podman skopeo buildah katacontainers
# 安装 kubernetes 相关工具，使用 kubic 源，它里面的软件更新一些（注意单引号不能省略！）
sudo zypper addrepo 'https://download.opensuse.org/repositories/devel:/kubic/openSUSE_Leap_$releasever' kubic
sudo zypper refresh
sudo zypper in kubernetes1.18-client k9s helm kompose

# 本地测试目前还是 docker-compose 最方便，docker 仍有必要安装
sudo zypper in docker
sudo gpasswd --add $USER docker
sudo systemctl enable docker
sudo systemctl start docker

# 简单起见，直接用 pip 安装 docker-compose 和 podman-compose
sudo pip install docker-compose podman-compose
```


### 办公、音乐、聊天

```shell
# 添加 opensuse_zh 源（注意单引号不能省略！）
sudo zypper addrepo 'https://download.opensuse.org/repositories/home:/opensuse_zh/openSUSE_Leap_$releasever' opensuse_zh
sudo zypper refresh
sudo zypper install wps-office netease-cloud-music 

# linux qq: https://im.qq.com/linuxqq/download.html
# 虽然简陋但也够用，发送文件比 KDE Connect 要方便一些。
sudo rpm -ivh linux_qq.rpm
```

### 安装输入法

我用的输入法是小鹤音形，首先安装 fcitx-rime:

```shell
# 添加 m17n obs 源：https://build.opensuse.org/repositories/M17N
# 源的 url，在「Repositories」页面找到自己的系统版本如「openSUSE_Leap_15.2」，下方「下载按钮」的链接，就是如下命令需要使用的链接
sudo zypper addrepo 'https://download.opensuse.org/repositories/M17N/openSUSE_Leap_$releasever' m17n
sudo zypper refresh
sudo zypper install fcitx5 fcitx5-configtool fcitx5-qt5 fcitx5-rime
```

然后，从 http://flypy.ys168.com/ 下载最新的鼠须管（MacOS）配置文件，将解压得到的 rime 文件夹拷贝到 ~/.local/share/fcitx5/ 下：

```shell
mv rime ~/.local/share/fcitx5/
```

现在重启系统，在 fcitx5 配置里面添加 rime「中州韵」，就可以正常使用小鹤音形了。


### QEMU/KVM

不得不说，OpenSUSE 安装 KVM 真的超方便，纯 GUI 操作：

```shell
# see: https://doc.opensuse.org/documentation/leap/virtualization/html/book-virt/cha-vt-installation.html
sudo yast2 virtualization
# enter to terminal ui, select kvm + kvm tools, and then install it.
```

KVM 的详细文档参见 [KVM/README.md](../../virutal%20machine/KVM/README.md)

### KDE Connect

KDE Connect 是一个 PC 手机协同工具，可以在电脑和手机之间共享剪切版、远程输入、发送文件、共享文件夹、通知同步等等。
总而言之非常好用，只要手机和 PC 处于同一个局域网就行，不需要什么数据线。

如果安装系统时选择了打开防火墙，KDE Connect 是连不上的，需要手动开放端口号：

```shell
# see: https://userbase.kde.org/KDEConnect#firewalld
sudo firewall-cmd --zone=public --permanent --add-port=1714-1764/tcp
sudo firewall-cmd --zone=public --permanent --add-port=1714-1764/udp
sudo systemctl restart firewalld.service
```

然后手机（Android）安装好 KDE Connect，就能开始享受了。

目前存在的 Bug:

- [ ] Android 10 禁止了后台应用读取剪切版，这导致 KDE Connect 只能从 PC 同步到手机，而无法反向同步。
    - 如果你有 ROOT 权限，可以参考 [Fix clipboard permission on Android 10](https://szclsya.me/posts/android/fix-clipboard-android-10/) 的方法，安装 ClipboardWhitelist 来打开权限。
    - 否则，貌似就只能使用手机端的「远程输入」模块来手动传输文本了。

### Qv2ray 代理

Qv2ray 是我用过的比较好用的 GUI 代理工具，通过插件可支持常见的所有代理协议。

```shell
# see: https://build.opensuse.org/repositories/home:zzndb
# 注意单引号不能省略！
sudo zypper addrepo 'https://download.opensuse.org/repositories/home:/zzndb/openSUSE_Leap_$releasever' qv2ray
sudo zypper refresh
sudo zypper install Qv2ray QvPlugin-Trojan QvPlugin-SS
```

## 其他设置

从 Windows 带过来的习惯是单击选中文件，双击才打开，这个可以在「系统设置」-「工作空间行为」-「常规行为」-「点击行为」中修改。



