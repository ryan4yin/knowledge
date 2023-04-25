# yabai 窗口管理器

在 Linux 上用了一段时间 i3wm 后，我就有点忍受不了工作电脑的桌面环境了，公司给配的是 Macbook，一番查找发现 yabai 比较符合我的需求，这里记录下 yabai 的安装与配置过程。

## 安装流程

参考官方 Wiki，首先参考这篇文章 [Disabling System Integrity Protection](https://github.com/koekeishiya/yabai/wiki/Disabling-System-Integrity-Protection) 关闭 SIP，然后参照如下流程安装 yabai 与 skhd。

```shell
# 安装yabai
brew install koekeishiya/formulae/yabai
sudo yabai --install-sa
# 启动yabai 这时候需要授权辅助功能
brew services start yabai

# 安装skhd
brew install koekeishiya/formulae/skhd
# 启动skhd 这时候需要授权辅助功能
brew services start skhd

########### 为 yabai 添加 sudo 权限 ###########
sudo yabai --load-sa
sudo visudo -f /private/etc/sudoers.d/yabai

# 然后输入以下内容 其中 <user> 修改为当前 mac 的用户名
# input the line below into the file you are editing.
#  replace <yabai> with the path to the yabai binary (output of: which yabai).
#  replace <user> with your username (output of: whoami). 
#  replace <hash> with the sha256 hash of the yabai binary (output of: shasum -a 256 $(which yabai)).
#   this hash must be updated manually after running brew upgrade.
<user> ALL=(root) NOPASSWD: sha256:<hash> <yabai> --load-sa
```

上面就完成了安装流程，但是到这里还不能使用，还需要为 skhd 与 yabai 添加配置文件，并添加自定义配置。

```shell
# 创建yabai配置文件
touch ~/.yabairc
chmod +x ~/.yabairc
# 创建skhd配置文件
touch ~/.skhdrc
chmod +x ~/.skhdrc

# 之后在 ~/.yabairc 中添加以下命令
cat <<EOF > ~/.yabairc
#!/usr/bin/env sh

# wiki 要求在配置最前面加这个，看起来是跟 sudo 权限相关的东西
sudo yabai --load-sa
yabai -m signal --add event=dock_did_restart action="sudo yabai --load-sa"
EOF
```

## 自定义 skhd 与 yabai 配置

这里配置的目标是，尽量与 i3wm 的默认快捷键保持一致，因为我在家用的是 Linux，只有办公电脑是 Mac.

我目前的 ~/.yabairc：

```shell
#!/usr/bin/env sh

# wiki 要求在配置最前面加这个，看起来是跟 sudo 权限相关的东西
sudo yabai --load-sa
yabai -m signal --add event=dock_did_restart action="sudo yabai --load-sa"

## 输出 debug 日志，出问题时方便排查
yabai -m config debug_output on

# 窗口平铺
yabai -m space --layout bsp
# 默认拆分规则 first_child second_child
yabai -m config window_placement             second_child
# 窗口间距设置
yabai -m config top_padding                  10
yabai -m config bottom_padding               10
yabai -m config left_padding                 10
yabai -m config right_padding                10
yabai -m config window_gap                   10
# 自动平衡所有窗口始终占据相同的空间
yabai -m config auto_balance                 off
# 如果禁用自动平衡，此项属性定义的是新窗口占用的空间量。0.5意为旧窗口占用50%
yabai -m config split_ratio                 0.50
# 鼠标修饰键 意思就是按着这个键就可以使用鼠标单独修改窗口大小了
yabai -m config mouse_modifier ctrl
# ctrl + 鼠标左键 移动窗口
yabai -m config mouse_action1 move
# ctrl + 鼠标右键 调整窗口大小
yabai -m config mouse_action2 resize
# 焦点跟随鼠标 默认off: 关闭  autoraise:自动提升 autofocus: 自动对焦
yabai -m config focus_follows_mouse          autofocus
# 设置鼠标是否跟随当前活动窗口 默认 off: 关闭 on: 开启
yabai -m config mouse_follows_focus          on

# 浮动窗口问题在顶部
yabai -m config window_topmost               on
# 修改窗口阴影 on: 打开 off: 关闭 float: 只显示浮动窗口的阴影
yabai -m config window_shadow                float

# 窗口透明度设置
yabai -m config window_opacity               on
# 配置活动窗口不透明度
yabai -m config active_window_opacity        0.98
yabai -m config normal_window_opacity        0.9
yabai -m config window_opacity_duration      0.0


# 在所有显示器上的每个空间顶部添加 0 填充 底部添加 0 填充
yabai -m config external_bar all:0:0

# ================================ 规则 ================================
# 打开系统偏好设置，不使用平铺模式
yabai -m rule --add app="^系统偏好设置$" manage=off
yabai -m rule --add app="^提醒事项$" manage=off
yabai -m rule --add app="^关于本机$" manage=off

echo "yabai configuration loaded.."
```

再就是 `~/.skhdrc`:

```shell
# 配置语法 : <modifier> - <key> : <command>
# modifier 可以是单个键比如 cmd, alt, ctrl, 也可以是组合键比如  ctrl + shift, ctrl + alt
# ================================ 打开终端 ================================
# 启动终端
cmd - return : open -a iTerm
# 关闭当前窗口，这个不需要加，macOS 默认是 cmd + q，我 Linux 也这么设置的
# ================================ 窗口设置 ================================
# =============== 为了避免快捷键冲突改用了 ctrl 作为 modifier =================
# ctrl + e 切换为平铺模式
ctrl - e : yabai -m space --layout bsp
# ctrl + s 切换为堆叠模式
ctrl - s : yabai -m space --layout stack
# 浮动/不浮动窗口 float
ctrl - f : yabai -m window --toggle float

# ================================ 多桌面配置  ================================
# 创建一个新桌面，并把当前活动的窗口发送到新桌面，并且自动跳转到新桌面. 需要 jq 支持 brew install jq
shift + cmd - n : yabai -m space --create && index="$(yabai -m query --spaces --display | jq '.| length')" && yabai -m window --space "${index}" && yabai -m space --focus "${index}" && yabai -m space --layout bsp

# 在 stack 模式下通过方向键切换窗口
ctrl - down : yabai -m window --focus stack.next || yabai -m window --focus south
ctrl - up : yabai -m window --focus stack.prev || yabai -m window --focus north
# 在 bsp 模式下通过方向键切换窗口
cmd - left : yabai -m window --focus west
cmd - right : yabai -m window --focus east

# 在 9 个桌面之间切换
ctrl - 1 : yabai -m space --focus 1
ctrl - 2 : yabai -m space --focus 2
ctrl - 3 : yabai -m space --focus 3
ctrl - 4 : yabai -m space --focus 4
ctrl - 5 : yabai -m space --focus 5
ctrl - 6 : yabai -m space --focus 6
ctrl - 7 : yabai -m space --focus 7
ctrl - 8 : yabai -m space --focus 8
ctrl - 9 : yabai -m space --focus 9
# 将窗口发送到某个其他桌面
ctrl + shift - 1 : yabai -m window --space 1
ctrl + shift - 2 : yabai -m window --space 2
ctrl + shift - 3 : yabai -m window --space 3
ctrl + shift - 4 : yabai -m window --space 4
ctrl + shift - 5 : yabai -m window --space 5
ctrl + shift - 6 : yabai -m window --space 6
ctrl + shift - 7 : yabai -m window --space 7
ctrl + shift - 8 : yabai -m window --space 8
ctrl + shift - 9 : yabai -m window --space 9
```

配置加好后重启 yabai 与 skhd:

```shell
brew services restart yabai
brew services restart skhd
```

现在就可以随便打开几个程序试试，正常情况下 yabai 会自动帮你分屏。
再尝试下添加好的这些快捷键，看看是否生效。

## 问题排查

### 1. yabai

如果 yabai 配置没有生效，有可能是权限问题，可以试下这个命令重启 yabai:

```shell
sudo yabai --uninstall-sa; sudo yabai --load-sa; brew services restart yabai
```

其他问题可查看 yabai 的日志解决：

- 错误日志路径: /usr/local/var/log/yabai/yabai.err.log
- 普通日志路径: /usr/local/var/log/yabai/yabai.out.log

### 2. skhd

如果 skhd 配置没有生效，首先可以查看 skhd 的日志:

```shell
cat /usr/local/var/log/skhd/*.log
```

如果日志文件不存在，可以停止 skhd 服务并手动启动它，看看是否有输出报错：

```shell
brew services stop skhd
skhd -c ~/.skhdrc
```

比如我之前改错了配置，执行上述命令就会报错：

```
#27:7 expected modifier
```

提示我配置的第 27 行配置有问题，我就去看了下，发现是我把 `cmd - return` 写成了 `cmd + return`，改正后再 `brew services start skhd` 重启 skhd 就好了。

## 堆叠模式下的可视化

yabai 在堆叠模式下的可视化效果不是很好，可以使用 [stackline](https://github.com/AdamWagner/stackline) 来改善一下。

```shell
# stackline 依赖 hammerspoon，这是一个 macOS 桌面自动化工具
brew install hammerspoon --cask

# 现在将 stackline 安装到 hammerspoon 的配置目录中
git clone https://github.com/AdamWagner/stackline.git ~/.hammerspoon/stackline

# Make stackline run when hammerspoon launches
cd ~/.hammerspoon
echo 'stackline = require "stackline"' >> init.lua
echo 'stackline:init()' >> init.lua
```

现在还需要安装下 hammerspoon 的命令行工具 hs，它用于在脚本中执行 stackline 操作，安装方法如下：

1. 首先搜索打开 Hamerspoon 程序，或者使用命令 `open -a "Hammerspoon"`
   1. 这里启动时会申请权限，需要手动打开下
   2. 同时注意勾选登录时自动启动
2. 在下方的命令输出栏中键入 `hs.ipc.cliInstall()` 再回车，即可完成安装

现在确认下 hs 命令已经可用：

```shell
which hs
```









## 参考

- [mac下的平铺桌面yabai使用 - 月青悠](https://vccv.cc/article/mac-tiling-yabai.html)
- [Yabai setup for i3wm users  - Krever](https://gist.github.com/Krever/74d43fa38c57c42c355df55faa0a00ee)
