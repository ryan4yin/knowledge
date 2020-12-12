# MacOS X 配置基础开发测试环境

## 1. 安装 [Homebrew](https://github.com/Homebrew/install)

>如果有代理，可以直接使用代理加速 git 仓库拉取：
`export http_proxy="socks5://127.0.0.1:1080"`
`export https_proxy="socks5://127.0.0.1:1080"`

Homebrew 的官方安装命令为：`/usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"`

但是命令中的脚本 URL 在国内经常是被墙的，需要手动到 `https://github.com/Homebrew/install/blob/master/install` 中将将脚本内容复制下来，保存为可执行脚本 `install-brew`

脚本保存完后，先将脚本中两个 Git 仓库修改为国内源，再运行此安装脚本，以加速安装：

```
# BREW_REPO = "https://github.com/Homebrew/brew".freeze
BREW_REPO = "https://mirrors.tuna.tsinghua.edu.cn/git/homebrew/brew.git".freeze
# CORE_TAP_REPO = "https://github.com/Homebrew/homebrew-core".freeze
CORE_TAP_REPO = "https://mirrors.tuna.tsinghua.edu.cn/git/homebrew/homebrew-core.git".freeze
```

现在运行脚本：`chmod +x insall-brew && install-brew` 进行安装。


```
# brew 程序本身，Homebrew/Linuxbrew 相同
git -C "$(brew --repo)" remote set-url origin https://mirrors.tuna.tsinghua.edu.cn/git/homebrew/brew.git

# 以下针对 mac OS 系统上的 Homebrew
git -C "$(brew --repo homebrew/core)" remote set-url origin https://mirrors.tuna.tsinghua.edu.cn/git/homebrew/homebrew-core.git
git -C "$(brew --repo homebrew/cask)" remote set-url origin https://mirrors.tuna.tsinghua.edu.cn/git/homebrew/homebrew-cask.git
git -C "$(brew --repo homebrew/cask-fonts)" remote set-url origin https://mirrors.tuna.tsinghua.edu.cn/git/homebrew/homebrew-cask-fonts.git
git -C "$(brew --repo homebrew/cask-drivers)" remote set-url origin https://mirrors.tuna.tsinghua.edu.cn/git/homebrew/homebrew-cask-drivers.git

# 更换后测试工作是否正常
brew update

echo 'export HOMEBREW_BOTTLE_DOMAIN=https://mirrors.tuna.tsinghua.edu.cn/homebrew-bottles' >> ~/.bash_profile
source ~/.bash_profile
```

## 2. 安装常用软件

### 2.1 Python3

最新的 macOS 10.15 已经自带 Python3.7 了，对版本没有要求的话可以直接使用系统默认的 python，然后使用 venv/poetry 管理虚拟环境。

### 2.2 OpenJDK

推荐安装 AdoptOpenJDK：

1. Homebrew 安装：https://github.com/AdoptOpenJDK/homebrew-openjdk
   1. 不翻墙的话速度有些感人。
2. 手动安装：https://adoptopenjdk.net/releases.html?variant=openjdk8&jvmVariant=hotspot
   1. 手动下载安装包进行安装。

### 2.3 设置环境变量

macOS 10.15 将默认 shell 由 bash 替换为了 zsh，要记得修改环境变量配置文件。

## 3. 设置软件开机自启（Service）

参见 [使用 supervisord 设置应用开机启动 ](https://www.cnblogs.com/kirito-c/p/12170126.html)


## 设置静态 IP、启用 SSH 远程登录

1. 在「设置」-「网络」中设置静态 IP、路由器、DNS 等网络参数。
2. 在「设置」-「共享」中启用「远程登录」，即 SSH 服务器。
