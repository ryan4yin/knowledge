# jenkins master 的部署、更新

Jenkins 是一款用于持续集成与持续部署（CI & CD）的软件，用于自动化各种任务，包括构建、测试和部署软
件。

这里按照[官方文档](https://jenkins.io/zh/doc/book/installing/)的推荐，使用 `jenkinsci/blueocean` 镜
像进行部署。

## 一、部署 Jenkins Master

使用 docker-compose 运行：

```shell
docker-compose up -d
```

## 三、配置 jenkins

启动好后我们得到一个全新的 Jenkins，现在需要进行一些配置：

1. 安装常用插件
   - `Pipeline Utility Steps`: 一些实用的 steps
   - `ansiColor`: 彩色日志输出
   - `Workspace Cleanup Plugin`: 构建完成后清理工作目录，防止 slave 磁盘满溢
   - `Job DSL`: 批量创建 Jobs，而且自动提前解析 parameters。（还未测试）
   - `Localization: Chinese (Simplified)`: 中文本地化插件
   - `SSH Agent`: SSH 密钥注入，可用于 git ssh 拉取代码/连接远程主机
   - `Build Name and Description Setter`: 通过插件设置 Build Name 和 Description
   - `Kubernetes`: 通过 k8s 对 slave 进行自动扩缩容，但是它貌似和许多插件不兼容。
   - `Rebuilder`: 提供一个「重新构建」的按钮，可使用当前 Build 的参数运行一个新 Build.
   - `LDAP`/`Active Directory` + `Role-based Authorization Strategy`: 企业用的 LDAP/AD 集成验证插
     件，以及权限管理插件
   - `Mailer Plugin`/`DingTalk`: 构建通知
   - `Publish Over SSH`/
   - `Python Plugin`: 使用 `python` 编写 build steps
   - `SonarQube Scanner for Jenkins`: 代码质量扫描，配合
     [sonarscanner.Jenkinsfile](./../jenkinsfile-templates/sonarscanner.Jenkinsfile) 使用
   - [`Simple Theme Plugin`](https://github.com/jenkinsci/simple-theme-plugin): 切换 UI 主题。
   - `Hashicorp Vault Pipeline`: 敏感信息存放在 Vault 中，通过插件去读取。Vault 比 Jenkins 自带
     的`Credentials(凭据)`功能丰富很多。包括 API/第三方集成等。
1. 在「系统设置」设置好各插件的配置项。（LDAP/email/git/等）
1. 设置凭据：用于拉取 git 仓库的 ssh 凭据等
1. 设置权限管理（`Role-based Authorization Strategy`）：用户、角色、权限
1. 进入 `<jenkins-url>/scriptApproval/`，批准有使用到的 java 接口。

然后就可以开始使用了

## 二、更新 jenkins-master

2. 在 jenkins 宿主机上 pull 新镜像
3. 再次`docker-compose up -d`
