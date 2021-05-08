>个人笔记，只会列出我自己还不太熟悉的命令，方便自己查阅。

## Linux Shell

```shell
# 1. 后台运行命令
nohup python xxx.py &
# 也可以使用 tmux，tmux 提供的 session 功能比 nohup 更好用，后面会介绍 tmux

# 查找替换

## 只在目录中所有的 .py 和 .dart 文件中递归搜索字符"main()"
grep "main()" . -r --include *.{py, dart}

## 1） 全文搜索并替换
sed -i "s/pattern_str/replace_str/g" `grep "key_pattern" 'path_pattern' -rl`

## 2）文件名搜索，替换文件内容
sed -i "s/pattern_str/replace_str/g" `find . -name "pattern"`

## 3）批量转换大小写
# 将当前文件夹内，所有的 gitlab URL 都转换成小写
# \L 转小写  \U 转大写
sed -i 's@http://GITLAB.*.git@\L&@g' `find . -name pubspec*`


## 4) 拷贝文件，并且保持文件夹结构（--parents 表示保持文件夹结构）
cp --parents `find <src-dir> -name *.py` <dst-dir>

# 文件传输

# 如果使用 ssh 命令进行文件传输，可安装 pv 命令查看传输速度（pipeviewer）
## ubuntu
sudo apt-get install pv
##  centos
sudo yum install epel-release
sudo yum install pv

## 1)从本地上传到服务器

### 使用 ssh 的好处是流式传输不会占用目标机器的存储空间，适合传输可能引起空间不足的大文件，并在目标机器上实时处理该文件。
cat <filename> | pv | ssh <user>@<host> -p 22 "cat - > <new-filename>"
tar cz <filename or foldername or glob> | pv | ssh <user>@<host> -p 22 "tar xz"  # 压缩传输

## scp 命令比 ssh 命令更简洁（但是不适合用于传文件夹，它会破坏文件的权限设置，把文件夹弄得一团糟）
scp -P 22 <filename> <user>@<host>:<folder-name or filename>  # 通过 scp 传输，传文件夹时记得添加 -r 参数（recursive）

## 2) 从服务器下载到本地
ssh <user>@<host> -p 22 "tar cz <filename or foldername or glob>" | pv | tar xz  # 压缩传输
scp -P 22 <user>@<host>:<folder-name or filename> <filename>  # 通过 scp 传输，传文件夹时记得添加 -r 参数（recursive）
```

### Tmux

>参考文档：https://github.com/tmux/tmux/wiki/Getting-Started
>参考文档：https://www.ruanyifeng.com/blog/2019/10/tmux.html

1. 输入 `tmux` 启动一个 tmux 会话。（或者用 `tmux new -s <session-name>` 启动一个命名会话）
2. 输入 `python xxx.py`，python 进程开始运行。
3. 按快捷键 `ctrl+b`，然后再按一下 `d` 脱离(detatch)当前会话。此时 python 进程进入后台运行，关闭当前终端对 python 进程没有影响。
4. 输入 `tmux ls` 可以查看当前正在后台运行的会话。（命名会话会显示名称，否则只显示 id）
5. 通过 `tmux attach -t <session-name/id>` 重新接入后台会话。
   1. 缩写 `tmux a -t <session>`
6. 或者通过 `tmux kill-session -t <session-name/id>` 杀死一个后台会话。


常用快捷键：

```
# prefix 表示 `ctrl`+`b`

# pane 的切分与选择
prefix "  # 在下方新建一个 pane
prefix %  # 在右侧新建一个 pane
prefix `方向键`  # 光标移动到指定方向的 pane 中

# 使用方向键滚动窗口内容
prefix [  # 进入翻页模式，可使用 page up/down，或者方向键来浏览 pane 的内容
# 使用鼠标滚轮来滚动窗口内容（也可以把此命令添加到 `~/.tmux.conf` 中使它永久生效）
prefix `:` 然后输入 `set-window-option -g mode-mouse on`

# （调整 pane 大小）将当前的 pane 向给定的方向扩容 5 行或者 5 列
# 按住 ALT 时快速重复敲击「方向键」，能快速调整，否则就得从 prefix 开始重新输入
prefix `Alt` + `方向键`
# 将当前窗格全屏显示，第二次使用此命令，会将窗格还原
prefix z

# 交换 pane 的位置
prefix {  # 当前窗格与上一个窗格交换位置
prefix }  # 当前窗格与下一个窗格交换位置

# session 相关操作
prefix s  # 查看 session 列表，并通过方向键选择 session
prefix `number`  # 通过数字标签选择 session

# window 相关操作（关系：每个 session 可以包含多个 window，每个 window 里面又可以有多个 pane）
prefix c # 新建 window
prefix w # 通过数字标签选择 window
```

### 文件拷贝/同步命令 rsync

rsync 的功能其实和前面的 scp/(tar+ssh) 是一样的，将文件从一个地方拷贝到另一个地方。
区别在于它只做增量同步，在多次拷贝文件时，只拷贝（同步）修改过的部分，很多场景下可以大大加快拷贝/备份速度。

rsync 的常用命令：

```shell
# 将一个文件夹归档、压缩，并通过 ssh 协议（默认）同步到另一个地方
# -a, --archive   # 归档模式，保留文件的所有元信息，等同于 `-rlptgoD`
# -r, --recursive # 递归复制文件夹，`-a` 隐含了这个参数，通常都用 -a。
# -v, --verbose   # 输出详细信息
# --progress      # 显示传输进度
# -z, --compress  # 传输文件时进行压缩
rsync -avz --progress src host:dest
rsync -avz --progress -e "ssh -p225" /path/src user@host:dest  # 使用非默认的 ssh 端口进行传输
rsync -avz --progress -e "ssh -i id_xxx" /path/src user@host:dest  # 使用指定的私钥连接 ssh 服务端，其他各种 ssh 参数都可以在这里指定

# --exclude 排除掉某些不需要的文件(夹)
rsync -avz --progress --exclude "foor/bar" src user@host:dest

# 有时我们希望在同步数据时修改文件的 user/group
# --chown    # 设置文件的 user:group，必须与 `-og`/`--owner --group` 同时使用！（`-a` 隐含了 `-og`） 
rsync -avz --progress --chown=root:root src user@host:dest  # 传输时修改 user/group 为 root

# 详细说明 src 和 dest 的位置
rsync -avz --progress path/src user@host:/tmp  # 将 src 拷贝到远程主机的 /tmp 中（得到 /tmp/src）
## 注意 src 结尾有 /
rsync -avz --progress path/src/ user@host:/tmp/src  # 将 src 目录中的文件拷贝到远程主机的 /tmp/src 目录中（同样得到 /tmp/src）

# 有时候我们在传输文件时不希望保留文件的元信息

# rsync 默认不会删除 dest 中多余的文件，使用 --delete 可让 rsync 删除这部分无关的文件
# 对 src 文件夹进行完全镜像，保证两个文件夹的内容一模一样，不多不少
rsync -avz --progress --delete src user@host:dest

# 也可以使用 --ignore-existing 让 rsync 忽略掉 dest 已经存在的文件。就是只同步新增的文件。
rsync -avz --progress --ignore-existing src user@host:dest

# 另有使用双冒号 :: 分隔的传输命令，这种命令使用 rsync 协议进行传输，要求目标主机启用 rsync-daemon
# 暂时不做介绍

详见 https://rsync.samba.org/documentation.html

# 用户与群组
## 查看用户属于哪些群组
groups <user-name>  # 方法一
id <username>       # 方法二，它会额外列出 gid/uid
cat /etc/group | grep <user-name>  # 方法三，直接查看配置
## 查看群组中有哪些用户，第一列是群组，最后一列是用户名
cat /etc/group | grep <group-name>
```

## Powershell

powershell 的命令有一致的命名规则：**谓词-名词**，谓词表示动作：Get/Set/Stop/Start 等，名词指示操作对象：Service/Member/ChildItem/Command 等。
这样的命名格式使我们可以很容易地猜测到自己需要的命令的名称。

为了使用方便，powershell 还提供了一些常用命令的缩写，并且添加了大量类似 Linux 命令的别名。

还有就是，Windows 默认不区分字母大小写，日常使用可以全部小写。

```powershell
# 删除文件/文件夹
remove-item xxx  -confirm
ri xxx  # 别名1
rm xxx  # 别名2
rmdir xxx  # etc...

# 复制
copy-item xxx xx -r
cp -r xxx xx

# 显示工作目录
get-location
gl
pwd

# 切换工作目录
set-location xxx
sl xxx
cd xxx

# 查看环境变量
get-childitem env:
gci env:
gci env:PATH  # 查看 PATH 变量

$env:XXX="value"   # 临时设置环境变量
$env:Path += ";SomeRandomPath"  # 临时在 Path 末尾添加新路径
## 以下三行命令只对 windows 有效，linux 下无效
[Environment]::SetEnvironmentVariable("XXX", $env:XXX + ";value", [EnvironmentVariableTarget]::User)  # 修改当前用户的环境变量（永久），只对新进程有效
[Environment]::SetEnvironmentVariable("XXX", "value", [EnvironmentVariableTarget]::Machine)  # 给这台电脑设置环境变量（永久），只对新进程有效，需要管理员权限
[Environment]::SetEnvironmentVariable("XXX", $env:XXX + ";value", "User")  # target 也可用字符串指定

# 删除文件/文件夹
rm xxx  # 删除文件夹时会进入交互界面，按提示输入就行。

# 查看命名位置（类似 Linux Shell 的 which）
get-command xxx
gcm xxx

# 通过关键字查找 powershell 命令
gcm | select-string <keyword>

# 通过关键字查找 powershell 命令和环境变量中的程序，比较慢
gcm * | select-string <keyword>

# 查看别名对应的真实命令
get-alias

# 类似 linux 的 find/ls 命令
get-childitem -Recurse -Include *.py
gci -r -i *.py

# 清空终端的输出
clear-host
clear

# 查看文件内容
get-content xx.py | more
get-content xx.py | out-host -paging
cat xx.py
gc xx.py

# 字符串搜索，不能对对象使用
# 类似 linux 的 grep 命令
cat xxx.log | select-string <pattern>
gci env: | out-string  -stream | select-string <pattern>  # 需要先使用 out-string 将对象转换成 string
gci env: | where-object {$_.Name -like <pattern>}

# 计算输出的行数/对象个数
gci env: | measure-object
gci env: | measure  # 这是缩写

# 查看所有进程
get-process | more
ps | more  # 别名

# 查找某进程（替代掉 tasklist）
get-process -name exp*,power*  # 使用正则查找进程
get-process | select-string <pattern>  # 效果同上

# 通过 id 杀掉某进程（替代掉 taskkill）
# 也可以通过 -Name 用正则匹配进程
stop-process <pid>
kill <pid>  # 别名

# 网络相关命令
## 1. dns 相关(dns-client)
Clear-DnsClientCache  # 清除 dns 缓存（替换掉 `ipconfig /flushdns`）
Get-DnsClientCache  # 查看 dns 缓存
Resolve-DnsName baidu.com  # 解析域名

## 2. TCP/IP 相关命令
Get-Command Get-Net*  # 查看所有 TCP/IP 相关的命令

Get-NetIPAddress  # 查看 IP 地址
Get-NetIPInterface  # 查看 IP 接口
Get-NetRoute        # 查看路由表
Get-NetNeighbor     # 获取链路层 MAC 地址缓存
Get-NetTCPConnection   # 查看 TCP 连接
### 也可以对 TCP/IP 的 IP 地址、接口、路由表进行增删改
New-NetRoute
Remove-NetNeighbor  # 清除 MAC 地址缓存

# 关机/重启
stop-computer
restart-computer

# windows 计算 hash 值
# 功能等同于 linux 下的 sha256sum/sha1sum/sha512sum/md5sum
Get-FileHash -Path /path/to/file -Algorithm SHA256
Get-FileHash -Path /path/to/file -Algorithm SHA256  | Format-List  # 用 format 修改格式化效果

# base64 编解码
[Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes("xxx"))  # base64 编码
[Text.Encoding]::UTF8.GetString([Convert]::FromBase64String("eHh4"))  # 解码

# 另外 windows 同样自带 ssh/scp 命令，参数也和 linux 一致
```

## TCP/UDP/DNS 相关命令

参见 [Socket 状态变迁图及命令行查看方法 ](https://www.cnblogs.com/kirito-c/p/12251900.html)