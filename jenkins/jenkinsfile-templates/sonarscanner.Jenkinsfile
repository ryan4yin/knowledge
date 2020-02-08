// 一个普通的 Jenkins 任务的模板
// 以 Python 代码的质量扫描为例
pipeline {
    agent {label "sonarscanner && python"}
    // agent {label "sonarscanner && dotnet"}  // for dotnet

    environment {
        // 使用凭据，对不同的凭据，Jenkins 会设置不同的环境变量
        //   1. 对文件凭据，下列环境变量就是文件的路径
        //  2. 对账号密码，下列环境变量内容为 $USER:$PASSOWRD，用冒号分隔账号和密码。
        //      同时也提供 $XXX_CREDENTIAL_USR（账号）和 $XXX_CREDENTIAL_PSW（密码）
        // XXX_CREDENTIAL = credentials('xxx-user-password')

        // 用于彩色输出
        RED ='\033[31m'
        NC='\033[0m'
    }

    options {
        timeout(time: 10, unit: 'MINUTES')
        disableConcurrentBuilds()  // 不允许并发构建同一个任务
        buildDiscarder(logRotator(daysToKeepStr: '20', numToKeepStr: '30'))  // 日志轮转
        ansiColor('xterm')  // 日志彩色输出
    }

    parameters {
        string(name: 'BRANCH', defaultValue: "dev", description: '使用哪个 git 分支？')
        booleanParam(name: 'TEST', defaultValue: true, description: '是否进行测试')
    }

    stages {
        stage("TEST") {
            // stage 的运行条件
            when {
                environment name: 'TEST', value: 'true'
            }
            steps {
                sh 'pytest'
            }
        }

        stage("Sonar 代码审查") {
            steps {
                dir(env.TARGET_PROJECT_DIR) {
                    sh "git checkout -b ${params.BRANCH}"  // 添加分支属性
                    withSonarQubeEnv('sonarqube') {
                        script{
                            // SonarQube 要求路径中不包含中文文件夹！否则 sonarscanner 什么 bug 都扫不到！！！

                            // 1. 通用扫描器
                            def sqScannerHome = tool name: 'sonarscanner', type: 'hudson.plugins.sonar.SonarRunnerInstallation'
                            sh "${sqScannerHome}/bin/sonar-scanner -Dsonar.projectKey=${JOB_BASE_NAME}"

                            // 2. dotnet 扫描器
                            // def sqScannerMsBuildHome = tool name: 'sonarscanner-msbuild', type: 'hudson.plugins.sonar.MsBuildSQRunnerInstallation'
                            // sh "dotnet ${sqScannerMsBuildHome}/SonarScanner.MSBuild.dll begin /k:${JOB_BASE_NAME}"
                            // sh "dotnet restore -s http://baget.local/v3/index.json -s https://api.nuget.org/v3/index.json"  // resotre with private nuget server
                            // sh "dotnet build --no-restore"
                            // sh "dotnet ${sqScannerMsBuildHome}/SonarScanner.MSBuild.dll end"
                        }
                    }
                }
            }
        }

        stage("Quality Gate") {
            steps {
                timeout(time: 5, unit: 'MINUTES') {
                    waitForQualityGate abortPipeline: true
                }
            }
        }
    }
    
    // 文档 https://jenkins.io/zh/doc/book/pipeline/syntax/#post
    post {
        always {

        }

        success {
            cleanWs cleanWhenFailure: true, notFailBuild: true
        }

        failure {

        }

        aborted {

        }
    }
}

