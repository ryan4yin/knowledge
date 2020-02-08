// 并行地运行某一文件夹中的所有任务
// 在所有任务全部运行结束后，再统计任务是否全部成功
pipeline {
    agent any

    options {
        timeout(time: 1, unit: 'HOURS')
        disableConcurrentBuilds()  // 不允许并发构建同一个任务
        buildDiscarder(logRotator(daysToKeepStr: '20', numToKeepStr: '30'))
        ansiColor('xterm')
    }

    parameters {
        string(name: 'BRANCH', defaultValue: 'dev', description: 'Git 分支',)
    }

    stages {
        stage ("Build Jobs Parallelly"){
            steps {
                script {
                    def folderName = 'Your Folder Name'

                    def branch = params.BRANCH  // parallel 中不能使用 pipeline 的全局变量，这里先将变量保存到局部
                    def parallel_args = [:] // parallel 的所有参数，键值对 
                    
                    // 彩色输出的代码
                    def GREEN = "\033[1;32m"
                    def RED ='\033[31m'
                    def NC='\033[0m'

                    Jenkins.instance.getItemByFullName(folderName).allJobs.each {
                        parallel_args[it.fullName] = {  // 这个代码块会被交给一个新线程处理
                            def result = build job: it.fullName, wait: true, propagate: false, quietPeriod: 3, parameters: [
                                string(name: 'BRANCH', value: params.BRANCH)
                            ]
                            
                            if (result.result != "SUCCESS") {
                                println "${RED}任务失败：${result.getProjectName()}, 状态：${result.result}${NC}"
                                println "${RED}  链接:${NC} ${result.getAbsoluteUrl()}/console"
                            } else {
                                println "${GREEN}任务名称: ${result.getProjectName()}, 构建结果: ${result.result}${NC}"
                            }

                            result.result
                        }
                    }

                    // 并行构建
                    parallel_args['failFast'] = false  // 任务全部完成后再 fail
                    def result_map = parallel parallel_args

                    // 检查构建结果
                    result_map.each{  // result_map 和 parallel_args 一样，也是一个字典。结构为 key: result
                        if (it.value != "SUCCESS"){
                            sh "exit -1"
                        }
                    }
                }
            }
        }
    }
}
