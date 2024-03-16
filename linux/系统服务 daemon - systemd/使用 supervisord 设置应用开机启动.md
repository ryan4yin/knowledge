以前一直是[用 systemd 设置开机启动的服务](https://www.cnblogs.com/kirito-c/p/10331598.html)，因为它
不需要装额外的软件，方便。

但是最近遇到个问题，就是我还需要在 OS X 上设置 Jenkins Agent 的开机自启，为此专门学习了下 launchctl
的使用，最后还是功亏一篑，败在了环境变量设置这一步——不知道为啥，我在
`/Library/LaunchDaemons/io.jenkinsagent.plist` 里设置的 `EnvironmentVariables` 字段无法生效，搞了半
天没找到问题。

今天才突然想起，为何不用 [supervisord](https://github.com/Supervisor/supervisor) 呢？！关键这个还跨
平台，一份配置稍微改改就可以同时用在 MacOS 和 Linux 上。

## 一、MacOS X 安装 supervisord

显然我不希望自己再写个 LaunchDaemons 的 plist 文件来把 supervisord 弄成开机自启。好在
[homebrew](https://brew.sh/index_zh-cn) 有提供傻瓜式方案，安装方式如下：

```shell
brew services  # homebrew 的 service 让我们脱离手工编写 plist 的“低级趣味”。
brew install supervisor  # 安装 supervisord
brew services start supervisor  # 借助 service 使 supervisor 开机启动
```

> homebrew services 的详细使用方法可见
> [github- homebrew service](https://github.com/Homebrew/homebrew-services)

> 如需加速安装，可参考
> [homebrew 清华镜像源使用说明](https://mirrors.tuna.tsinghua.edu.cn/help/homebrew/)

安装启动后，可查看 supersivor 的配置文件 `/usr/local/etc/supervisord.ini`，如需添加自启动程序，可将
配置文件添加到 `/usr/local/etc/supervisor.d/` 中，该文件夹中的配置会被主配置文件 include.

详细的说明见后。

## 使用 supervisord

### 编写配置文件

> **注意**：属性名称错误，不会给出任何提示！！！所以无法运行时，请仔细检查配置中的属性是否有拼写错
> 误！

以 Jenkins-Agent 为例，编写 `/usr/local/etc/supervisor.d/jenkins-agent.ini`，内容如下：

```ini
[program:jenkins-agent]
command=/bin/bash /Users/jenkins/jenkins_home/connect.sh  ; 从 jenkins web 页面复制的连接命令
autostart=true
startsecs=5        ; 启动 5 秒后没有异常退出，就当作已经正常启动了
autorestart=true   ; 程序异常退出后自动重启
startretries=3     ; 启动失败自动重试次数，默认是 3
stopasgroup=true
redirect_stderr=true  ; 将 stderr 重定向到 stdout
stdout_logfile=/Users/jenkins/jenkins_home/jenkins-agent.log   ; 日志输入位置
stdout_logfile_maxbytes=1MB
environment=PATH="/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"
```

supervisor 启动服务时，只会包含系统的环境变量。而上面的配置文件，显然也并不方便设置多个环境变量。因
此推荐的做法是在启动脚本中进行相关的环境设置：

```shell
# connect.sh 的内容

# java for jenkins-agent
export PATH="/Applications/openjdk8/Contents/Home/bin:$PATH"

# flutter
export PUB_HOSTED_URL=https://pub.flutter-io.cn
export FLUTTER_STORAGE_BASE_URL=https://storage.flutter-io.cn
export PATH="/Applications/flutter/bin:$PATH"

# connect jenkins master
cd /Users/jenkins/jenkins_home/
# 下面是 jenkins 连接命令
java -jar agent.jar -jnlpUrl ......
```

这样就能在启动程序前，设置好需要的环境。

### 启用配置

通过 `supervisorctl` 操作 supervisor:

1. 连接 supervisor 后端：`supervisorctl -c /usr/local/etc/supervisord.ini`，注意必须指定启动
   supervisor 时用的配置文件。
1. 然后就可以通过 `help` 查看 supervisorctl 支持的命令了，常用的有 `reload` 重载配置，`restart all`
   重启所有应用。

通过 `start all` 就可以启动配置好的应用了。

## 二、Linux 安装 supervisor

一般建议通过包管理器安装，好处是不用手写 systemd 配置，缺点是更新太慢。

```shell
sudo apt-get install supervisor  # 安装
sudo systemctl enable supervisor  # 启用开机启动
sudo systemctl start supervisor   # 现在启动
```

如果需要新版本的功能，可以通过 pip 安装最新版，但是需要手动编写 systemd 配置（或者先用 apt-get 装老
版本，把 systemd 配置拷下来）。详见 [installing supervisor](http://supervisord.org/installing.html)

## 使用方法

用法见前面的 MacOS X，基本上可以套用，只有如下几个区别：

1. 默认的配置文件路径不同，主配置文件是 `/etc/supervisor/supervisord.conf`，自定义配置路径
   `/etc/supervisor/conf.d/*.conf`
1. 注意 Linux 中配置的后缀是 `.conf`，而在 OS X 中默认使用 `.ini`

## 画外：Windows 呢？

Windows 也有自己的 Service 功能，不过就和 OS X 的 launchd 一样，我对它的了解程度小于 1%。

因此同样依靠懒人方法，推荐使用 [winsw](https://github.com/kohsuke/winsw)。

不过目前这个方法我还没用过，因为目前没有啥需要设置成 Windows Service 的应用。
