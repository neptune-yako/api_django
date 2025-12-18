@Library('jenkins-lib@devel') _
pipeline {
    agent {
        label "10.3.240.35"
    }
    
    options {
        disableConcurrentBuilds abortPrevious: true
        timeout(time: 10, unit: 'HOURS')
        timestamps()
    }
    
    environment {
        TEST_DIR = "${WORKSPACE}\\ci_autotest"
        SOURCE_DIR = "D:\\CI\\source\\test_venus_dev\\ci_autotest"
        TEST_RESULT_DIR = "${WORKSPACE}\\ci_autotest\\test_result"
        SOURCE_RESULT_DIR = "D:\\CI\\source\\test_venus_dev\\ci_autotest\\test_result"
        RESULT_DIR = "test_result"
        REPORT_HOST = "10.0.240.26"
        GNB_HOST_0 = "192.168.0.125"
        GNB_HOST_1 = "192.168.0.126"
        GNB_TEST_DIR = "ci_test_venus"
        UE_STACK_HOST = "192.168.0.127"
        UE_STACK_TEST_DIR = "ci_test_ue_stack"
    }

    stages {
        stage('TEST') {
            steps {
				script {
					dir("${TEST_DIR}") {
						// 执行测试
						bat 'xcopy /y %SOURCE_DIR% %TEST_DIR% /s /e /q'
						bat 'python run_test_debug.py'
						bat 'xcopy /y %TEST_RESULT_DIR% %SOURCE_RESULT_DIR% /s /e /q'
						
						// 生成报告
						def timestamp=''
                        timestamp = readFile encoding: 'utf-8', file: 'timestamp_file.txt'
                        echo "timestamp = ${timestamp}"

                        allure([
                            includeProperties: false,
                            jdk: '',
                            properties: [],
                            reportBuildPolicy: 'ALWAYS',
                            report: "test_result/${timestamp}/allure-report",
                            results: [[path: "test_result/${timestamp}/allure-results"]]
                        ])

                        dir("test_result/${timestamp}"){
                            // 合并历史信息

                            // 获取 Jenkins 构建历史
                            bat """
                            curl -X GET -H "Accept: application/json" "http://10.0.20.230:8080/jenkins/view/test/job/%JOB_NAME%/api/json?tree=allBuilds%%5Bnumber,result%%5D" -o jenkins_build.json
                            """
                            // 解析 Jenkins 构建历史
                            def jenkinsBuilds = readJSON file: 'jenkins_build.json'
                            def lastSuccessOrUnstablebuild = jenkinsBuilds.allBuilds.find { (it.result == 'SUCCESS' || it.result == 'UNSTABLE') && it.number != BUILD_NUMBER.toInteger()}
                            echo "Last Success Or Unstable Build: ${lastSuccessOrUnstablebuild.number}"

                            copyArtifacts filter: 'allure-report.zip', fingerprintArtifacts: true, projectName: "${JOB_NAME}", selector: specific("${lastSuccessOrUnstablebuild.number}")

                            bat """
                            mkdir temp
                            7z x allure-report.zip -otemp\\
                            del /F /Q allure-report.zip
                            @xcopy ".\\..\\..\\test_utils\\custom_allure_report.py" "." /Y
                            python -c "import custom_allure_report as cus; cus.merge_json_files('./temp/allure-report/history', './allure-report/history')"
                            del /F /Q allure-results\\history
                            mkdir allure-results\\history
                            xcopy /y temp\\allure-report\\history allure-results\\history /s /e /q
                            rmdir /S /Q temp\\
                            """

                            // 修改报告标题
                            bat 'generate-allure-report.bat'

                            // 更改部分中文
                            bat '''
                            @xcopy ".\\..\\..\\test_data\\report_data\\favicon.ico" "allure-report\\" /Y
                            python -c "import custom_allure_report as cus; cus.change_chinese_character('./allure-report/app.js')"
                            del /F /Q custom_allure_report.py
                            rmdir /S /Q __pycache__\\
                            '''

                            bat '''
                            7z a -tzip allure-report.zip allure-report\\
                            '''

                            archiveArtifacts allowEmptyArchive: true, artifacts: "allure-report.zip",
                            fingerprint: true, followSymlinks: false, onlyIfSuccessful: true
                        }
                        
                        // 日志备份
                        bat """
						python -c "from test_utils import env; env.backup_venus_log_for_jenkins('${timestamp}')"
						"""
					}
				}
            }
        }
    }
}