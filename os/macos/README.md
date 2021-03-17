# MacOS X 开发环境配置

## 一、[Homebrew](https://github.com/Homebrew/install)

homebrew 是 MacOS X 的包管理工具，对 CLI 爱好者而言，它基本可以取代 App Store.

### 1. 安装 Homebrew

Homebrew 的官方安装命令为：`/usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"`


如果有代理，可以直接使用代理加速 git 仓库拉取：
`export http_proxy="socks5://127.0.0.1:1080"`
`export https_proxy="socks5://127.0.0.1:1080"`

>说实话，这年头没个代理，真的寸步难行。。还是建议买个代理，别委屈了自己。。。

安装脚本的 URL 在国内经常是被墙的，为了解决被墙的问题，就需要手动到 `https://github.com/Homebrew/install/blob/master/install` 中将将脚本内容复制下来，保存为可执行脚本 `install-brew`

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

### 2. hombrew 常用命令

```shell
# 通过关键字搜索 fomula
brew search xxx

# 从 hombrew 的仓库中查找 fomula 进行安装，基本都是 cli 工具或依赖包
brew install xxx
# 从 homebrew-cask 仓库中查找 fomula 进行安装，所有 GUI 或其他非常大的软件，都会被放在这个 cask 仓库中
brew install --cask xxx

brew update # 更新 Homebrew 在服务器端上的包目录
brew list --versions # 查看安装过的包版本
```

## 二、安装常用软件

首先，安装 apple 命令行开发工具：

```shell
xcode-select --install
```

这个命令会安装 clang/make 等编译相关的基础工具，基本上任何和编译有关的操作都要求先安装好这些工具。

### 1. Python3

最新的 macOS 10.15 已经自带 Python3.7 了，对版本没有要求的话可以直接使用系统默认的 python，然后使用 venv/poetry 管理虚拟环境。

有需要可以安装一个 pyenv 来管理多版本的 python，

### 2. OpenJDK

推荐安装 AdoptOpenJDK：

1. Homebrew 安装：https://github.com/AdoptOpenJDK/homebrew-openjdk
   - 不开代理的话速度有些感人。
2. 手动安装：https://adoptopenjdk.net/releases.html?variant=openjdk8&jvmVariant=hotspot
   - 手动下载安装包进行安装。

### 3. 设置环境变量

macOS 10.15 将默认 shell 由 bash 替换为了 zsh，要记得修改环境变量配置文件。

## 三、其他设置

设置软件开机自启（Service）:

- 方法一：使用 hombrew service
- 方法二：[使用 supervisord 设置应用开机启动 ](https://www.cnblogs.com/kirito-c/p/12170126.html)

## 设置静态 IP、启用 SSH 远程登录

测试机就需要做这类设置，方法如下：

1. 在「设置」-「网络」中设置静态 IP、路由器、DNS 等网络参数。
2. 在「设置」-「共享」中启用「远程登录」，即 SSH 服务器。


## 四、桌面开发环境设置

要把 MacOS X 调教地比较适合用做主力开发环境，建议安装如下工具：

```
brew install --cask visual-studio-code docker wireshark iterm2 firefox google-chrome
# 安装视频播放器
brew install --cask iina
# 安装常用命令行工具
brew install fzf tmux zsh-autosuggestions aria2
# 容器相关命令行工具
brew install skopeo helm kubectl 
# 安装编程语言 SDK
brew install go
```

使用 [starship](https://github.com/starship/starship) 美化命令行提示符：

```shell
# 先安装 starship 需要的字体
brew tap homebrew/cask-fonts && brew install --cask font-fira-code-nerd-font
brew install starship
# 然后将如下内容添加到 ~/.zshrc 的末尾，再重新进 terminal，就大功告成了
eval "$(starship init zsh)"
```


finder 相关设置：

```shell
# 显示当前当前文件夹的完整路径
defaults write com.apple.finder _FXShowPosixPathInTitle -bool true; killall Finder
# 让 finder 默认显示所有文件(包括隐藏文件)
defaults write com.apple.finder AppleShowAllFiles Yes && killall Finder
# 安装 finder 插件，添加右键菜单
brew install --cask openinterminal-lite
# 然后按官方文档的方法将图标添加到 finder 的 toolbar 中：https://github.com/Ji4n1ng/OpenInTerminal/blob/master/Resources/README-Lite.md
```

上方的 status bar 相关工具：

```shell
brew install --cask iglance
```

## 其他软件

mindnote - 思维导图

## 其他

触摸板相关配置：
- 在「辅助功能」中启用「三指拖移」
- 在「触摸板」中启用：
   - 「辅助点按」 - 「轻点或双指点按」
   - 「轻点来点按」

在桌面与屏保中设置触发角

学会用 spotlight 全局搜索，熟悉后可以考虑装个 alfred

finder 相关：
- 把 home 和 codes 文件夹添加到左侧栏


## 2K 显示器的分辨率问题

由于苹果系统原因，外接 2K 显示器会导致字体特别小，非常难受。

建议使用 [one-key-hidpi](https://github.com/xzhih/one-key-hidpi)，跑完脚本重启，就能将外接 2K 显示器变成 retina 屏，就能获得类似 windows 的分辨率缩放体验了。
