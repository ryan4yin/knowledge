# nixpkg 使用

## 为什么选择 nix

nixpkg 相比其他包管理器，拥有完全不同的设计哲学，你可以将它理解成用 git 的方式管理软件包，git 最大的好处是啥？那显然就是多版本管理，可以随时回退到任一历史环境。

nixpkgs 的优点：

- 完全不同的包管理方式，可以随时回退到任一历史环境，所以也是最稳定的包管理方式，出了问题随时可以回滚。
- 声明式环境，可复现，甚至可以在其他机器上还原整个环境
  - nix 通过函数式语言的方式描述了软件包的依赖关系，这使得 nix 可以在不同机器上生成完全一致的环境
  - 这一点跟 docker 有点类似，不过 docker 是容器环境，会有些区别。另外也可以在 dockerfile 里用 nix 来构建环境，这也完全可行。
- 没有任何依赖冲突问题，因为 nix 中每个软件包都拥有唯一的 hash，其安装路径中也会包含这个 hash 值，因此可以多版本共存。任何其他依赖了某个特定包的 nix 包，都会在其配置文件中声明依赖的包的 hash，这样它只能看到这个 hash 对应的包，就不存在冲突。

但是软件包可比代码文档之类的东西大多了，这使利用了多版本管理技术的 nixpkgs 有一个比较明显的缺点——非常吃硬盘空间，但是可以定期使用 nix-collect-garbage 来删除其中旧的软件版本或者不需要的文件。即使如此，也建议配置个更大的硬盘。

而另一个缺点，当属系统的复杂度了，如果你希望系统完全可复现，并且避免各种不当使用导致的坑，那就需要学习 nix 函数语言，并用它配置你的系统。再者许多在普通 Linux 发行版上常用的与文件系统查找相关的工具比如 pkg-config，在 nix 环境下都会出问题，因为 nix 的安装路径与普通 Linux 完全不一样，所以这些工具都会找不到 nix 安装的软件包。这些都导致了 nix 的学习曲线比较陡峭，因此不适合新手。

最后一个比较明显的缺点就是 nixpkgs 的包数量比较少，第三方包也有一些，但是总体估计比较难跟 arch linux 竞争。

因为 nix 声明式、可复现的特性，它也受到许多商业用户的欢迎，被讨论最多的，就是用它管理各种开发编译环境。
在其他 OS 上要维护一个可复现的编译环境很麻烦，构建环境一不小心就可能因为更新或安装被破坏，但在 nix 上没有这些问题。

## 安装

>https://mirrors.bfsu.edu.cn/help/nix/

可以使用 tuna/bfsu 的镜像源加速安装，多用户安装命令：

```shell
sh <(curl https://mirrors.bfsu.edu.cn/nix/latest/install) --daemon
```

## cache 镜像

cache 镜像同样可以使用 tuna/bfsu 镜像源加速，nixpkg 多用户安装时修改 `/etc/nix/nix.conf` 添加如下内容：

```conf
substituters = https://mirrors.bfsu.edu.cn/nix-channels/store https://cache.nixos.org/
```

改完后要重启 nix-daemon 服务才能生效，对于 nix-darwin，可以使用如下命令重启：

```shell
sudo launchctl stop org.nixos.nix-daemon
sudo launchctl start org.nixos.nix-daemon
```

对于 nixos 等基于 systemd 的 linux 系统，可以使用如下命令重启：

```shell
sudo systemctl restart nix-daemon
```

## nixpkgs channel 镜像

>https://nixos.wiki/wiki/Nix_channels

>https://mirrors.bfsu.edu.cn/help/nix-channels/

[nixpkgs](https://github.com/NixOS/nixpkgs) 是一个包含了所有 nix 包与 nixos 模块/配置的 Git 仓库，其 master 分支包含最新的 nix 包与 nixos 模块/配置。
而 nixpkgs channel 共有四个，分别是 stable/unstable，以及 large/small。它们本质上都对应了 nixpkgs 仓库的不同 commit。

使用 bfsu 镜像源加速 nixpkgs nixpkgs-unstable channel 的方法如下：

```shell
nix-channel --add https://mirrors.bfsu.edu.cn/nix-channels/nixpkgs-unstable nixpkgs
nix-channel --list
nix-channel --update
```
