// 串行地运行某一文件夹中的所有任务
// 如果中途有任务失败，就终止此批量任务的运行
pipeline {
    agent any

    options {
        timeout(time: 1, unit: 'HOURS')
        disableConcurrentBuilds()  // 不允许并发构建同一个任务
        buildDiscarder(logRotator(daysToKeepStr: '20', numToKeepStr: '30'))  // 日志轮转
        ansiColor('xterm')  // 日志彩色输出
    }

    triggers {
        cron('H(0-5) 9 * * *')  // 每天 09:00-09:05 自动运行
    }

    parameters {
        string(name: 'BRANCH', defaultValue: "dev", description: '使用哪个 git 分支？')
        choice(name: 'BUILD_MODE', choices: ["profile", 'release', 'debug'], description: '选择构建模式')
        booleanParam(name: 'XXX', defaultValue: true, description: 'XXX')
    }

    stages {
        stage ("Batch Job: Build XXX"){
            steps {
                script {
                    def folderName = "Your Folder Name"
                    
                    // 方案一，有任务失败，则批量任务直接中断
                    Jenkins.instance.getItemByFullName(folderName).allJobs.each {
                        build job: it.fullName, wait: true, propagate: true, parameters: [
                            string(name: 'BRANCH', value: params.BRANCH),
                            string(name: 'BUILD_MODE', value: params.BUILD_MODE),  // choice 的值就是普通的 string
                            booleanParam(name: 'XXX', value: params.XXX)
                        ]
                    }


                    // 方案二：所有的子任务都跑一遍，最后再统计结果
                    // def failed_builds = []
                    // Jenkins.instance.getItemByFullName(folderName).allJobs.each {
                    //     def result = build job: it.fullName, wait: true, propagate: false, parameters: [
                    //         string(name: 'BRANCH', value: params.BRANCH),
                    //         string(name: 'BUILD_MODE', value: params.BUILD_MODE),  // choice 的值就是普通的 string
                    //         booleanParam(name: 'XXX', value: params.XXX)
                    //     ]
    
                    //     println "Jobname: ${it.fullName}, Status: ${result.result}"

                    //     if (result.result != "SUCCESS") {
                    //         failed_builds.add(result)
                    //     }
                    // }

                    // // 打印出失败的任务
                    // if (failed_builds.size() > 0) {
                    //     echo "${env.RED}====================批量构建失败，失败的任务如下：====================${env.NC}"
                    //     failed_builds.each {
                    //         echo "${env.RED}任务名称：${it.getProjectName()}, 状态：${it.result}${env.NC}"
                    //         echo "${env.RED}  链接:${env.NC} ${it.getAbsoluteUrl()}/console"
                    //     }
                    //     sh "exit 1"
                    // } else {
                    //     echo "构建成功"
                    // }
                }
            }
        }
    }
}
