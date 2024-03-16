# Guix 笔记

用了几个月 NixOS 后，我现在对 Guix 又产生了兴趣，打算玩一玩看。

我的配置文件地址： https://github.com/ryan4yin/guix-config

## 系统安装

使用 Guix 官方提供的 ISO 镜像安装即可，要注意的是：

1. 其图形化安装程序，无法设置国内镜像源，下载奇慢无比，所以最好使用命令行安装程序。
2. 为了简化安装，可以先用图形化安装程序一路设置好磁盘分区、`config.scm` 配置生成，然后在实际执行时，
   再 ctrl+c 退出进入命令行安装程序

命令行安装的步骤参考官方文档
[Proceeding with the Installation - Guix Manual](https://guix.gnu.org/manual/en/html_node/Proceeding-with-the-Installation.html)
即可：

```bash
# 挂载 root 分区
mount /dev/sda4 /mnt
# 挂载 efi 分区
mount /dev/sda1 /mnt/boot/efi

# 必须首先执行此命令，将 /gnu/store 挂载到 /mnt 磁盘，否则默认使用内存，很快就会报错 no space left on device
herd start cow-store /mnt

# 执行安装程序
# 这一步我跑了两三遍，前面在跑到一半遇到了 permission denied 之类的错，重启系统再重来就好了
guix system init /mnt/etc/config.scm /mnt
```

现在重启系统，就可以进入 Guix 了。

## 配置

修改配置文件后，使用如下命令更新系统：

```bash
# 更新 channel
guix pull

# 更新系统，当然配置文件也可以移动到其他位置
sudo guix system reconfigure /etc/config.scm
```

## 其他常用命令

```bash
# 临时使用某个程序（类似 nix shell nixpkgs#package-name）
guix environment --ad-hoc <package>
```

## 参考资料

入门必读：[GNU Guix Cookbook](https://guix.gnu.org/en/cookbook/en/guix-cookbook.html)

参考配置（dotfiles）：

- https://github.com/rakino/Testament/tree/trunk
  - 这个配置结构是我比较喜欢的，一目了然。
- https://github.com/Tass0sm/dotfiles
- https://github.com/engstrand-config/guix-dotfiles
- https://github.com/podiki/dot.me
- https://github.com/abcdw/rde
- https://github.com/Millak/guix-config
- https://github.com/kitnil/dotfiles
- https://github.com/aartaka/guix-config
- https://github.com/migalmoreno/guix-config
- https://github.com/rsauex/dotfiles
- https://github.com/hiecaq/guix-config
