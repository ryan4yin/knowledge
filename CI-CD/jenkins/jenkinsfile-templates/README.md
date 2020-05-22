# Jenkins Pipeline


## 加快 Pipeline 构建速度

在 「系统管理」-「系统配置」-「Pipeline Speed/Durability Settings」，将它设为 「Performance Optimized」

这也能避免因为 Groovy 脚本没有使用 `@CPS` 注解而报错！


## Jenkinsfile 与 CI/CD 代码管理

企业级的 Jenkinsfile 往往同质化严重，每个环节中的几十个仓库，它们用到的 Jenkinsfile 和构建逻辑都是一模一样的。
因此完全不需要在每个仓库中放一个 Jenkinfile——这加大了运维成本。

比较优越的解决方案是将 Jenkinsfile 和它用到的 CI/CD 代码放在一起，达成 Jenkinsfile 和 CI/CD 代码的复用。

比如一个专用于运维的代码仓库，结构如下：

```tree
├───jenkinsfiles
│   ├─── xxx.Jenkinsfile  # 别的运维相关 Jenkinsfiles
│   ├───batch「文件夹」  # 批量任务的 Jenkinsfiles，只负责批量调用子任务
│   ├───cleaning「文件夹」  # 日志、镜像、缓存等历史数据清理的 Jenkinsfiles
│   └───schedulers「文件夹」  # 统一管理定时执行的 Jenkinsfiles，其中大部分都只负责定时调用其他子任务。
├───operation  # 上述 Jenkinsfiles 需要用到的 Python 代码
│   ├─── vmware  # 与 vmware 相关的脚本（虚拟机的 CURD）
│   ├─── ftp  # 与 ftp 服务器相关的脚本（数据清理）
```

我们目前是将 jenkinsfiles 和 CI/CD 代码分成了七个 Git 仓库进行管理：

1. 四个直接使用源码的仓库：运维、前端、后端、测试的 CI/CD 仓库，结构前面讲过了
1. 三个打成 package 使用的仓库：
   3. job_config: 保存了所有 Git 源码仓库和 Jenkins Job 的映射关系，所有任务都通过它提供的 api 获取源码的 git_url/branch 等信息。
      - 提供按类别查询的功能
      - 提供自动通过映射关系创建 Jenkins 任务的功能。
   4. operation_utils: 运维的实用工具包，通用的代码抽取到这里面 
   6. common_config: 一些通用的配置，以 class 等方式定义在这个包里面。


## 脚本片段

>这里省略了 `pipeline.stages.stage.steps` 等外部代码块(block)。
如果出现 grovvy 脚本（标志性特征是: 控制流语句 if-else/while、变量定义 def），下列代码片段还需要使用 `script` 包裹。


### 1. git 仓库相关操作

自动注入 ssh 密钥用于 git 操作：

```groovy
// For SSH private key authentication, try the sshagent step from the SSH Agent plugin.
sshagent (credentials: ['git-ssh-credentials-ID']) {
    sh("git tag -a some_tag -m 'Jenkins'")
    sh('git push <REPO> --tags')
}
```


拉取 git 仓库：
```groovy
// 代码拉到当前文件夹中
// 使用 git 插件拉取，jenkins 能记录到 git 仓库的 reversion 
git branch: 'dev', credentialsId: 'git-ssh-credentials-ID', url: 'http://gitlab.local/test_repo'

// 代码拉到文件夹 test_dir 中，会新建文件夹
// 缺点是不会 jenkins 记录不到仓库的 reversion！
sshagent (credentials: ['git-ssh-credentials-ID']) {
    sh("git clone --branch dev 'http://gitlab.local/text_repo' test_dir")
}
```


### 2. 批量任务

在所有 labels 匹配的节点上运行某个命令：

```groovy
def nodes = [:]

// 需要插件：Pipeline Utility Steps
nodesByLabel('docker').each {
  nodes[it] = { ->
    node(it) {
      // 清理 docker 的所有历史数据
      sh('docker system prune --all --force')
    }
  }
}

parallel nodes
```

如果还需要在多个节点之间共用某些文件/代码/配置，可以使用 `stash`/`unstash`:

```groovy
// stash 当前文件夹下的所有内容
stash includes: '**', name: 'operation-scripts', useDefaultExcludes: false

def nodes = [:]

// 需要插件：Pipeline Utility Steps
nodesByLabel('docker').each {
  nodes[it] = { ->
    node(it) {
      // 将之前暂存的文件再取出到当前节点上。
      unstash 'operation-scripts'
      // 清理所有历史数据
      sh("python3 run.py operation.")
    }
  }
}

parallel nodes
```

## 参考

- [Pipeline Examples - Jenkins Docs](https://jenkins.io/doc/pipeline/examples)
- [Running Jenkins job simultaneously on all nodes](https://stackoverflow.com/questions/17286614/running-jenkins-job-simultaneously-on-all-nodes#answer-61692506)
