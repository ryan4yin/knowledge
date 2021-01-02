Manjaro
---

Manjaro 是一个基于 Arch Linux 的 Linux 滚动发行版，用着挺舒服的。
最大的特点，是包仓库很丰富，而且都很新。代价是偶尔会出些小毛病。

## 一、pacman/yay 的基础命令

Manjaro 装好后，需要运行的第一条命令：

```sh
sudo pacman -Syy ## 强制更新 package 目录
sudo pacman-mirrors --interactive --country China  # 列出所有国内的镜像源，并提供交互式的界面手动选择镜像源
sudo pacman -Syyu  # 强制更新 package 目录，并尝试更新已安装的所有 packages.
sudo pacman -S yay  # 安装 yay
```

pacman 是 arch/manjaro 的官方包管理器，而刚刚安装的 yay，则是一个能查询 arch linux 的 aur 仓库的第三方包管理器，非常流行。

pacman 的常用命令语法：

```sh
pacman -S package_name        # 安装软件  
pacman -S extra/package_name  # 安装不同仓库中的版本
pacman -Syu                   # 升级整个系统，y是更新数据库，yy是强制更新，u是升级软件
pacman -Ss string             # 在包数据库中查询软件
pacman -Si package_name       # 显示软件的详细信息
pacman -Sc                    # 清除软件缓存，即/var/cache/pacman/pkg目录下的文件
pacman -R package_name        # 删除单个软件
pacman -Rs package_name       # 删除指定软件及其没有被其他已安装软件使用的依赖关系
pacman -Qs string             # 查询已安装的软件包
pacman -Qi package_name       # 查询本地安装包的详细信息
pacman -Ql package_name       # 获取已安装软件所包含的文件的列表
pacman -U package.tar.zx      # 从本地文件安装
pactree package_name          # 显示软件的依赖树
```

yay 的用法和 pacman 完全类似，上述所有 `pacman xxx` 命令，均可替换成 `yay xxx` 执行。

此外，还有一条 `yay` 命令值得记一下：

```sh
yay -c  # 卸载所有无用的依赖。类比 apt-get autoremove
```

## 常用软件与配置

### 1. 添加 archlinux 中文社区仓库

[Arch Linux 中文社区仓库](https://www.archlinuxcn.org/archlinux-cn-repo-and-mirror/) 是由 Arch Linux 中文社区驱动的非官方用户仓库，包含一些额外的软件包以及已有软件的 git 版本等变种。部分软件包的打包脚本来源于 AUR。

一些国内软件，如果直接从 aur 安装，那就会有一个编译过程，有点慢。而 archlinuxcn 有已经编译好的包，可以直接安装。更新速度也很快，推荐使用。

配置方法见 [Arch Linux Chinese Community Repository](https://github.com/archlinuxcn/repo)。

### 2. 安装常用软件

```sh
sudo pacman -S google-chrome  firefox         # 浏览器
sudo pacman -S netease-cloud-music     # 网易云音乐
sudo pacman -S noto-fonts-cjk wqy-bitmapfont wqy-microhei wqy-zenhei   # 中文字体：思源系列、文泉系列
sudo pacman -S wps-office ttf-wps-fonts

sudo pacman -S vim                     # 命令行编辑器
sudo pacman -S git                     # 版本管理工具
sudo pacman -S clang make cmake gdb    # 编译调试环境
sudo pacman -S visual-studio-code-bin  # 代码编辑器

sudo pacman -S wireshark-qt  mitmproxy         # 抓包工具
sudo pacman -S docker  # docker 容器
```

其中 docker 和 wireshark 需要额外配置，否则会要求管理员权限：

```sh
sudo groupadd wireshark
sudo gpasswd --add $USER wireshark  #  将你添加到 wireshark 用户组中

sudo groupadd docker
sudo gpasswd --add $USER docker  # 同上
```

### 3. 中文输入法

有两个选择：[中州韵（rime）](https://rime.im/)和[搜狗拼音（sogoupinyin）](https://aur.archlinux.org/packages/fcitx-sogoupinyin/)。

简单省事用搜狗，要用特殊的输入方案（五笔、音形、二笔等等）就只有 rime 可选了。

#### 3.1 fcitx5-rime 配置小鹤音形

首先安装 fcitx5-rime, 注意这些组件一个都不能省略：
```shell
sudo pacman -S fcitx5  fcitx5-chinese-addons fcitx5-gtk  fcitx5-qt  kcm-fcitx5 fcitx5-rime
```

第二步是修改环境变量，将 fcitx5-rime 设为默认输入法并自动启动。

添加 `~/.pam_environment` 文件，内容如下：

```conf
INPUT_METHOD  DEFAULT=fcitx5
GTK_IM_MODULE DEFAULT=fcitx5
QT_IM_MODULE  DEFAULT=fcitx5
XMODIFIERS    DEFAULT=@im=fcitx5
```

[pam-env](https://wiki.archlinux.org/index.php/PAM_(%E7%AE%80%E4%BD%93%E4%B8%AD%E6%96%87)) 模块会在所有登录会话中读取上面的配置文件，包括 X11 会话和 Wayland 会话。

添加自动启动：

```shell
# ~/.xprofile 是 x11 GUI 的环境变量配置文件
echo 'fcitx5 &' >> ~/.xprofile
```

然后，从 http://flypy.ys168.com/ 下载最新的鼠须管（MacOS）配置文件，将解压得到的 rime 文件夹拷贝到 ~/.local/share/fcitx5/ 下：

```shell
mv rime ~/.local/share/fcitx5/
```

现在重启系统，在 fcitx5 配置里面添加 rime，就可以正常使用小鹤音形了。

## 坑

使用过程中，我也遇到了一些坑：

1. 安装软件包时，无法在线安装旧版本！除非你本地有旧版本的安装包没清除，才可以通过缓存安装旧版本。
      - 这种问题没遇到时好说，但有时候新版本有问题，旧安装包也清理掉了无法回退，就非常麻烦。
      - 而且就算你回退了版本，一升级它就又更新了。。


## 参考

- [Arch Linux Wiki - 中文](https://wiki.archlinux.org/index.php/Main_page_(%E7%AE%80%E4%BD%93%E4%B8%AD%E6%96%87))
- [AUR 仓库](https://aur.archlinux.org/packages)
- [Arch Linux 中文社区仓库](https://www.archlinuxcn.org/archlinux-cn-repo-and-mirror/)
- [yay - Yet another Yogurt - An AUR Helper written in Go ](https://github.com/Jguer/yay)
- [安装Manjaro之后的配置 ](https://panqiincs.me/2019/06/05/after-installing-manjaro/)
- [Arch Linux Wiki - Fcitx5](https://wiki.archlinux.org/index.php/Fcitx5_(%E7%AE%80%E4%BD%93%E4%B8%AD%E6%96%87))