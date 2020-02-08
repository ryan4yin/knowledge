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
                    Jenkins.instance.getItemByFullName(folderName).allJobs.each {
                        build job: job_name, wait: true, propagate: true, quietPeriod: 1,  parameters: [
                            string(name: 'BRANCH', value: params.BRANCH),
                            string(name: 'BUILD_MODE', value: params.BUILD_MODE),  // choice 的值就是普通的 string
                            booleanParam(name: 'XXX', value: params.XXX)
                        ]
                    }
                }
            }
        }
    }
}
