# jenkins master 的部署、更新

Jenkins 是一款用于持续集成与持续部署（CI & CD）的软件，用于自动化各种任务，包括构建、测试和部署软件。

这里按照[官方文档](https://jenkins.io/zh/doc/book/installing/)的推荐，使用 `jenkinsci/blueocean` 镜像进行部署。

## 一、部署 Jenkins Master

使用 docker-compose 运行：

```shell
docker-compose up -d
```


## 三、配置 jenkins

启动好后我们得到一个全新的 Jenkins，现在需要进行一些配置：

1. 安装常用插件
    - Pipeline Utility Steps
    - ansiColor
    - Workspace Cleanup Plugin
    - Localization: Chinese (Simplified)
    - SSH Agent
    - ...
1. 在「系统设置」设置好各插件的配置项。（LDAP/email/git/等）
1. 设置凭据
1. 设置权限管理：用户、角色、权限
1. 进入 `<jenkins-url>/scriptApproval/`，批准有使用到的 java 接口。

然后就可以开始使用了

## 二、更新 jenkins-master

2. 在 jenkins 宿主机上 pull 新镜像
3. 再次`docker-compose up -d`

