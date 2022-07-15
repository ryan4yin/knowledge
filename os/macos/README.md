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

brew update # 更新 Homebrew packages 索引
brew upgrade # 升级所有已安装的 packages 到最新版本
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
brew install coreutils  # sha256sum/md5sum 
brew install --cask visual-studio-code docker wireshark iterm2 firefox google-chrome
# 安装视频播放器
brew install --cask iina
# 安装常用命令行工具
brew install fzf tmux zsh-autosuggestions aria2 p7zip
# 作为 Linux 熟手，当然还需要安装我更熟悉的 gnu-tar 以及 gnu-sed，它们的 cli 名称为 `gtar` `gsed`
brew install gnu-tar gnu-sed
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

## 其他设置

### 其他软件

mindnote - 思维导图

### 文件搜索与找寻

学会用 spotlight 全局搜索，熟悉后可以考虑装个 alfred

finder 相关：
- 把 home 和 codes 文件夹添加到左侧栏
### 触摸板相关配置
- 在「辅助功能」中启用「三指拖移」
- 在「触摸板」中启用：
   - 「辅助点按」 - 「轻点或双指点按」
   - 「轻点来点按」

### 快捷操作（触发角/touchbar/快捷键）

>公司的电脑，为了安全需要人离屏锁屏

方法一：

进入「设置」-「桌面与屏幕保护程序」-「屏幕保护程序」，点击右下角的「触发角」进入触发角设置，这个很实用。

方法二：

进入「设置」-「键盘」，点击右下角的「自定义功能栏」，将图标拖放到底部即可自定义 touchbar 的功能。

### 防止系统在锁屏后自动休眠

锁屏后一段时间 macOS 会自动进入休眠状态，并且断网，这可能会导致各种 ssh 连接直接断掉，
如果没用 tmux/screen 等终端复用器的话，工作环境也会丢失。

为了避免这个问题，可以在「System」-「Battery」-「Power Adapter」中勾选上「防止电脑自动休眠」。

### 键盘「option+字母」组合键输入奇怪字符，无法实现光标跳转？

这个是 MacOS 系统的全局设置，改起来很麻烦。

比较好的解决方法是只修改 Terminal + IDE 程序的设置，将 `option` 映射为 `esc+` 或者 `meta`.
一般光标跳转也只在 Terminal + IDE 中用得到，所以感觉这是个比较简单优雅的解决方案。

这样改好，你就可以在 iterm2 中使用 `option+f` 前进一个单词，`option+b` 回退一个单词了，非常方便。

#### iterm2 的 option 键映射

目前 MacOS 上最流行的 Terminal 是 iterm2，
具体的设置方法为在 iterm2 的「preferences」-「profile」-「keys」中，有两个很显眼的设置项，在这里将左右 option 键都设置为 `esc+` 就大功告成了。

#### vscode 的 option 键映射

vscode 的 option 映射参数如下：

```json
"terminal.integrated.macOptionIsMeta": true
```

直接在 VSCode 配置中搜索 `macOptionIsMeta` 即可找到该选项。

#### jetbrains IDE

jetbrains 系列 IDE 的 2021.2 开始，在「tools」-「terminal」中添加了参数「Use Option as Meta key」，启用该参数即可。

## 2K 显示器的分辨率问题

由于苹果系统原因，外接 2K 显示器会导致字体特别小，非常难受。

建议使用 [one-key-hidpi](https://github.com/xzhih/one-key-hidpi)，跑完脚本重启，就能将外接 2K 显示器变成 retina 屏，就能获得类似 windows 的分辨率缩放体验了。


## MacOS 网络诊断相关命令

查看路由表及对应的网卡：
```
❯ netstat -nr
Routing tables

Internet:
Destination        Gateway            Flags        Netif Expire
default            phicomm.me         UGScg          en0
127                localhost          UCS            lo0
localhost          localhost          UH             lo0
169.254            link#6             UCS            en0      !
192.168.2          link#6             UCS            en0      !
192.168.2.1/32     link#6             UCS            en0      !
phicomm.me         74:7d:24:dc:d:2f   UHLWIir        en0   1200
brt-w09.lan        f2:7:9a:4e:a9:1c   UHLWI          en0   1189
192.168.2.238/32   link#6             UCS            en0      !
224.0.0/4          link#6             UmCS           en0      !
224.0.0.251        1:0:5e:0:0:fb      UHmLWI         en0
239.255.255.250    1:0:5e:7f:ff:fa    UHmLWI         en0
255.255.255.255/32 link#6             UCS            en0      !
```

网卡相关
```
# 列出所有网卡的详细信息
 ifconfig -a
lo0: flags=8049<UP,LOOPBACK,RUNNING,MULTICAST> mtu 16384
	options=1203<RXCSUM,TXCSUM,TXSTATUS,SW_TIMESTAMP>
	inet 127.0.0.1 netmask 0xff000000
	inet6 ::1 prefixlen 128
	inet6 fe80::1%lo0 prefixlen 64 scopeid 0x1
	nd6 options=201<PERFORMNUD,DAD>
gif0: flags=8010<POINTOPOINT,MULTICAST> mtu 1280
stf0: flags=0<> mtu 1280
......
en0: flags=8863<UP,BROADCAST,SMART,RUNNING,SIMPLEX,MULTICAST> mtu 1500
	options=400<CHANNEL_IO>
	ether 14:7d:da:9d:37:a0
	inet6 fe80::42e:3664:dd14:7a29%en0 prefixlen 64 secured scopeid 0x6
	inet 192.168.2.238 netmask 0xffffff00 broadcast 192.168.2.255
	nd6 options=201<PERFORMNUD,DAD>
	media: autoselect
	status: active
......

# 列出所有网卡名称
❯ ifconfig -l
lo0 gif0 stf0 en5 ap1 en0 awdl0 llw0 en1 en2 en3 en4 bridge0 utun0 utun1

# 列出网卡的 ip 地址
ipconfig getifaddr en0
```

其他诸如 traceroute/dig/ping/lsof 的用法，和 linux 基本一致。
