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

拉取 git 仓库：
```groovy
// 使用 git 插件拉取，jenkins 能记录到 git 仓库的 reversion
dir("sub_git_dir"){  // 如果此文件夹不存在，会自动创建它
  // 使用 git 插件，好处是插件会记录当前的 git reversion(web 页面上能看到)，方便排查。
  git branch: 'dev', credentialsId: 'git-ssh-credentials-ID', url: 'http://gitlab.svc.local/test_repo'
}
```

自动注入 ssh 密钥用于 git 操作：

```groovy
dir("sub_git_dir"){
    // 需要插件 sshagent
    sshagent (credentials: ['git-ssh-credentials-ID']) {
      sh("git tag -a some_tag -m 'Jenkins'")
      sh('git push <REPO> --tags')
  }
}
```

### 2. 批量任务

在所有 labels 匹配的节点上运行某个命令：

```groovy
def nodes = [:]

// 需要插件：Pipeline Utility Steps
// 会忽略所有不在线的节点！
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
      sh("python3 run.py operation.clean_old_data")
    }
  }
}

parallel nodes
```

## 3. json/yaml 等文件的读写

读文件很简单：`readCSV`/`readJSON`/`readYaml`/`readFile` 等

而写文件，比如输出 json，完整的 pipeline 如下：

```groovy
import groovy.json.JsonOutput

pipeline {
  stages {
    stage("Xxx") {
      steps {
        script {  // groovy 代码需要放到 script 中
          // 将 groovy 字典转换成 json，写入到 build 描述中
          def git_hash = sh(  // 目标项目的 hash 值存在 description 里面
              encoding: 'utf-8',
              returnStdout: true,
              script: "git rev-parse HEAD"  // 获取 HEAD 所在的 ref 的值
          ).trim()
          def build_description = [
              "git_hash": git_hash,
          ]
          // 需要安装插件：[Build Name and Description Setter]
          buildDescription JsonOutput.toJson(build_description)
        }
      }
}
```

## Pipeline 代码复用

可以使用专门的 git 仓库来存放一些可复用的 pipeline 片段，详见：

- [Extending with Shared Libraries - Jenkins Docs](https://www.jenkins.io/doc/book/pipeline/shared-libraries/)


## 参考

- [Pipeline Examples - Jenkins Docs](https://jenkins.io/doc/pipeline/examples)
- [Running Jenkins job simultaneously on all nodes](https://stackoverflow.com/questions/17286614/running-jenkins-job-simultaneously-on-all-nodes#answer-61692506)
