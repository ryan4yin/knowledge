## 部署 Jenkins Salve

### 1. 容器化部署

以当前文件夹下的 `docker-compose.yaml` 为模板进行容器化部署，可部署 c#/golang/android 等的自动化构建环境。

需要注意的是模板中的每一个参数，都是有意义的，不能随便省略。

比如 `init` 是用于清理僵尸进程，
`container_name` 和 `networks.[xxx].name` 是用于指定容器/网络的名称，避免 docker-compose 自动生成。

[docker-compose.yaml 各参数说明](https://docs.docker.com/compose/compose-file)

### 2. 部署 UI 测试/IOS 构建机

这类机器很难通过容器化方式部署，因此采用手动部署。
需要使用自动化安装脚本安装好构建环境，并将 Jenkins Agent 设为自动启动。部分操作可能需要手动进行。

各操作系统中将应用设为自动启动的方法，参见 [使用 supervisord 设置应用开机启动](https://www.cnblogs.com/kirito-c/p/12170126.html)，
文末也有提到 Windows 设置开机启动的方法。


### Bugs 归档

- [「Bug」Jenkins Slave 卡顿与僵尸进程](https://www.cnblogs.com/kirito-c/p/12153528.html)
