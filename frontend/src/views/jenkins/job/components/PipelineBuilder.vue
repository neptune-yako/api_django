<template>
  <div class="pipeline-builder">
    <!-- 模式选择 -->
    <el-form-item label="Pipeline 模式">
      <el-radio-group v-model="pipelineType" @change="handleTypeChange">
        <el-radio label="simple">
          <strong>简单模板</strong>
          <span style="color: #909399; font-size: 12px; margin-left: 10px">
            前置脚本 → 测试命令 → 后置脚本
          </span>
        </el-radio>
        <el-radio label="custom">
          <strong>自定义 Stage</strong>
          <span style="color: #909399; font-size: 12px; margin-left: 10px">
            自定义多个执行步骤
          </span>
        </el-radio>
      </el-radio-group>
    </el-form-item>

    <!-- 高级配置折叠面板 -->
    <el-collapse v-model="activeAdvanced" class="advanced-config">
      <el-collapse-item title="⚙️ 高级配置(可选)" name="advanced">
        <!-- Library 导入 -->
        <el-form-item label="@Library 导入">
          <el-input
            v-model="advancedConfig.library"
            placeholder="例如: jenkins-lib@devel"
          />
          <span style="font-size: 12px; color: #909399; display: block; margin-top: 5px">
            💡 Jenkins共享库,格式: 库名@分支
          </span>
        </el-form-item>

        <!-- Options 配置 -->
        <el-form-item label="Options 配置">
          <div style="margin-bottom: 10px">
            <el-checkbox v-model="advancedConfig.options.disableConcurrentBuilds">
              禁用并发构建 (disableConcurrentBuilds)
            </el-checkbox>
          </div>
          <div style="margin-bottom: 10px">
            <el-checkbox v-model="advancedConfig.options.timestamps">
              显示时间戳 (timestamps)
            </el-checkbox>
          </div>
          <div style="display: flex; align-items: center; gap: 10px">
            <el-checkbox v-model="advancedConfig.options.enableTimeout">
              超时设置 (timeout)
            </el-checkbox>
            <el-input-number
              v-if="advancedConfig.options.enableTimeout"
              v-model="advancedConfig.options.timeoutValue"
              :min="1"
              :max="24"
              style="width: 120px"
            />
            <el-select
              v-if="advancedConfig.options.enableTimeout"
              v-model="advancedConfig.options.timeoutUnit"
              style="width: 100px"
            >
              <el-option label="分钟" value="MINUTES" />
              <el-option label="小时" value="HOURS" />
              <el-option label="天" value="DAYS" />
            </el-select>
          </div>
        </el-form-item>

        <!-- Environment 环境变量 -->
        <el-form-item label="Environment 环境变量">
          <div class="env-list">
            <div
              v-for="(env, index) in advancedConfig.environment"
              :key="index"
              class="env-item"
            >
              <el-input
                v-model="env.key"
                placeholder="变量名"
                style="width: 35%"
              />
              <span>=</span>
              <el-input
                v-model="env.value"
                placeholder="变量值"
                style="width: 55%"
              />
              <el-button
                @click="removeEnvVar(index)"
                type="danger"
                link
                icon="Delete"
              />
            </div>
            <el-button @click="addEnvVar" type="primary" link size="small">
              + 添加环境变量
            </el-button>
          </div>
        </el-form-item>
      </el-collapse-item>
    </el-collapse>

    <!-- 简单模式 -->
    <div v-if="pipelineType === 'simple'" class="simple-mode">
      <el-form-item label="前置脚本">
        <el-input
          v-model="simpleConfig.preScript"
          type="textarea"
          :rows="3"
          placeholder="例如：pip install -r requirements.txt"
        />
        <span style="font-size: 12px; color: #909399; display: block; margin-top: 5px">
          💡 可选，在执行测试前运行
        </span>
      </el-form-item>

      <el-form-item label="测试命令">
        <el-input
          v-model="simpleConfig.testCommand"
          type="textarea"
          :rows="3"
          placeholder="例如：pytest tests/ --alluredir=allure-results -v"
        />
        <span style="font-size: 12px; color: #909399; display: block; margin-top: 5px">
          💡 主要的测试执行命令
        </span>
      </el-form-item>

      <el-form-item label="后置脚本">
        <el-input
          v-model="simpleConfig.postScript"
          type="textarea"
          :rows="2"
          placeholder="例如：allure generate allure-results"
        />
        <span style="font-size: 12px; color: #909399; display: block; margin-top: 5px">
          💡 可选，在测试完成后运行
        </span>
      </el-form-item>
    </div>

    <!-- 自定义 Stage 模式 -->
    <div v-if="pipelineType === 'custom'" class="custom-mode">
      <div class="stage-list">
        <div
          v-for="(stage, index) in customStages"
          :key="index"
          class="stage-item"
        >
          <div class="stage-header">
            <el-input
              v-model="stage.name"
              placeholder="Stage 名称"
              style="width: 200px"
            />
            <div style="display: flex; gap: 10px; align-items: center">
              <el-radio-group v-model="stage.execType" size="small">
                <el-radio-button label="sh">Shell</el-radio-button>
                <el-radio-button label="script">Script</el-radio-button>
              </el-radio-group>
              <el-button @click="removeStage(index)" type="danger" link>
                删除
              </el-button>
            </div>
          </div>

          <el-input
            v-model="stage.script"
            type="textarea"
            :rows="6"
            :placeholder="stage.execType === 'script' 
              ? 'Groovy Script 内容 (支持 dir、bat、def 等语法)' 
              : 'Shell 脚本内容'"
          />
        </div>

        <el-button @click="addStage" type="primary" link>
          + 添加 Stage
        </el-button>
      </div>
    </div>

    <!-- 实时预览 -->
    <el-form-item label="Pipeline 预览">
      <el-button @click="showPreview = !showPreview" size="small">
        {{ showPreview ? '隐藏' : '显示' }}预览
      </el-button>
    </el-form-item>

    <el-collapse v-if="showPreview" class="preview-section">
      <el-collapse-item title="生成的 Pipeline 脚本" name="pipeline">
        <pre class="pipeline-preview">{{ generatedPipeline }}</pre>
      </el-collapse-item>
    </el-collapse>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'

const props = defineProps({
  nodes: Array,
  environments: Array
})

const emit = defineEmits(['update:config'])

const pipelineType = ref('simple')
const showPreview = ref(false)

// 简单模式配置
const simpleConfig = ref({
  preScript: '',
  testCommand: 'pytest tests/ --alluredir=allure-results -v',
  postScript: 'allure generate allure-results'
})

// 自定义 Stage 列表
const customStages = ref([
  {
    name: 'TEST',
    script: `dir("\${TEST_DIR}") {
    // 执行测试
    bat 'xcopy /y %SOURCE_DIR% %TEST_DIR% /s /e /q'
    bat 'python run_test_debug.py'
    bat 'xcopy /y %TEST_RESULT_DIR% %SOURCE_RESULT_DIR% /s /e /q'
    
    // 生成报告
    def timestamp=''
    timestamp = readFile encoding: 'utf-8', file: 'timestamp_file.txt'
    echo "timestamp = \${timestamp}"

    allure([
        includeProperties: false,
        jdk: '',
        properties: [],
        reportBuildPolicy: 'ALWAYS',
        report: "test_result/\${timestamp}/allure-report",
        results: [
            [path: "test_result/\${timestamp}/allure-results"]
        ]
    ])

    dir("test_result/\${timestamp}"){
        // 合并历史信息
        // 获取 Jenkins 构建历史
        bat """
        curl -X GET -H "Accept: application/json" "http://10.0.20.230:8080/jenkins/view/test/job/%JOB_NAME%/api/json?tree=allBuilds%%5Bnumber,result%%5D" -o jenkins_build.json
        """
        // 解析 Jenkins 构建历史
        def jenkinsBuilds = readJSON file: 'jenkins_build.json'
        def lastSuccessOrUnstablebuild = jenkinsBuilds.allBuilds.find { (it.result == 'SUCCESS' || it.result == 'UNSTABLE') && it.number != BUILD_NUMBER.toInteger()
        }
        echo "Last Success Or Unstable Build: \${lastSuccessOrUnstablebuild.number}"

        copyArtifacts filter: 'allure-report.zip', fingerprintArtifacts: true, projectName: "\${JOB_NAME}", selector: specific("\${lastSuccessOrUnstablebuild.number}")

        bat """
        mkdir temp
        7z x allure-report.zip -otemp\\\\
        del /F /Q allure-report.zip
        @xcopy ".\\\\..\\\\..\\\\test_utils\\\\custom_allure_report.py" "." /Y
        python -c "import custom_allure_report as cus; cus.merge_json_files('./temp/allure-report/history', './allure-report/history')"
        del /F /Q allure-results\\\\history
        mkdir allure-results\\\\history
        xcopy /y temp\\\\allure-report\\\\history allure-results\\\\history /s /e /q
        rmdir /S /Q temp\\\\
        """
        // 修改报告标题
        bat 'generate-allure-report.bat'

        // 更改部分中文
        bat '''
        @xcopy ".\\\\..\\\\..\\\\test_data\\\\report_data\\\\favicon.ico" "allure-report\\\\" /Y
        python -c "import custom_allure_report as cus; cus.change_chinese_character('./allure-report/app.js')"
        del /F /Q custom_allure_report.py
        rmdir /S /Q __pycache__\\\\
        '''

        bat '''
        7z a -tzip allure-report.zip allure-report\\\\
        '''

        archiveArtifacts allowEmptyArchive: true, artifacts: "allure-report.zip",
        fingerprint: true, followSymlinks: false, onlyIfSuccessful: true
    }
    // 日志备份
    bat """
    python -c "from test_utils import env; env.backup_venus_log_for_jenkins('\${timestamp}')"
    """
}`,
    execType: 'script' // 'sh' 或 'script'
  }
])

// 高级配置折叠状态
const activeAdvanced = ref([])

// 高级配置
const advancedConfig = ref({
  library: '', // @Library导入
  options: {
    disableConcurrentBuilds: false,
    timestamps: false,
    enableTimeout: false,
    timeoutValue: 10,
    timeoutUnit: 'HOURS'
  },
  environment: [
    { key: 'TEST_DIR', value: '${WORKSPACE}\\\\ci_autotest' },
    { key: 'SOURCE_DIR', value: 'D:\\\\CI\\\\source\\\\test_venus_dev\\\\ci_autotest' },
    { key: 'TEST_RESULT_DIR', value: '${WORKSPACE}\\\\ci_autotest\\\\test_result' },
    { key: 'SOURCE_RESULT_DIR', value: 'D:\\\\CI\\\\source\\\\test_venus_dev\\\\ci_autotest\\\\test_result' },
    { key: 'RESULT_DIR', value: 'test_result' },
    { key: 'REPORT_HOST', value: '10.0.240.26' },
    { key: 'GNB_HOST_0', value: '192.168.0.125' },
    { key: 'GNB_HOST_1', value: '192.168.0.126' },
    { key: 'GNB_TEST_DIR', value: 'ci_test_venus' },
    { key: 'UE_STACK_HOST', value: '192.168.0.127' },
    { key: 'UE_STACK_TEST_DIR', value: 'ci_test_ue_stack' }
  ] // 环境变量数组
})

// 添加环境变量
const addEnvVar = () => {
  advancedConfig.value.environment.push({
    key: '',
    value: ''
  })
}

// 删除环境变量
const removeEnvVar = (index) => {
  advancedConfig.value.environment.splice(index, 1)
}

// 生成Pipeline头部(Library、Options、Environment)
const generatePipelineHeader = () => {
  let header = ''
  
  // @Library导入
  if (advancedConfig.value.library) {
    header += `@Library('${advancedConfig.value.library}') _\n`
  }
  
  return header
}

// 生成Options块
const generateOptionsBlock = () => {
  const opts = advancedConfig.value.options
  const enabledOpts = []
  
  if (opts.disableConcurrentBuilds) {
    enabledOpts.push('disableConcurrentBuilds abortPrevious: true')
  }
  if (opts.enableTimeout) {
    enabledOpts.push(`timeout(time: ${opts.timeoutValue}, unit: '${opts.timeoutUnit}')`)
  }
  if (opts.timestamps) {
    enabledOpts.push('timestamps()')
  }
  
  if (enabledOpts.length === 0) return ''
  
  return `    
    options {
        ${enabledOpts.join('\n        ')}
    }
`
}

// 生成Environment块
const generateEnvironmentBlock = () => {
  const envVars = advancedConfig.value.environment.filter(e => e.key && e.value)
  if (envVars.length === 0) return ''
  
  const envLines = envVars.map(e => `        ${e.key} = "${e.value}"`).join('\n')
  return `    
    environment {
${envLines}
    }
`
}

// 计算生成的 Pipeline
const generatedPipeline = computed(() => {
  const nodes = props.nodes || []
  const nodeCount = nodes.length
  const isMultiNode = nodeCount > 1

  // 调试日志
  console.log('PipelineBuilder - nodes:', nodes)
  console.log('PipelineBuilder - nodeCount:', nodeCount)
  console.log('PipelineBuilder - isMultiNode:', isMultiNode)

  if (pipelineType.value === 'simple') {
    return generateSimplePipeline(isMultiNode, nodes)
  } else {
    return generateCustomPipeline(isMultiNode, nodes)
  }
})

// 生成简单 Pipeline
const generateSimplePipeline = (isMultiNode, nodes) => {
  // 多节点使用 matrix 模式，单节点使用 label 模式
  if (isMultiNode && nodes && nodes.length > 1) {
    return generateMatrixPipeline(nodes)
  }

  // 单节点模式
  let agentDirective = 'any'
  if (nodes && nodes.length > 0) {
    const nodeNames = nodes.map(n => n.name).join(' ')
    agentDirective = `label "${nodeNames}"`
  }
  console.log('generateSimplePipeline - agentDirective:', agentDirective)

  let stages = ''
  if (simpleConfig.value.preScript) {
    stages += `        stage('准备环境') {
            steps {
                sh '''${simpleConfig.value.preScript}'''
            }
        }

`
  }

  stages += `        stage('执行测试') {
            steps {
                sh '''${simpleConfig.value.testCommand || 'echo "测试执行完成"'}'''
            }
        }`

  if (simpleConfig.value.postScript) {
    stages += `

        stage('生成报告') {
            steps {
                sh '''${simpleConfig.value.postScript}'''
            }
        }`
  }

  const header = generatePipelineHeader()
  const options = generateOptionsBlock()
  const environment = generateEnvironmentBlock()

  return `${header}pipeline {
    agent {
        ${agentDirective}
    }
${options}${environment}
    stages {
${stages}
    }

    post {
        success {
            echo 'Pipeline 执行成功'
        }
        failure {
            echo 'Pipeline 执行失败'
        }
    }
}`
}

// 生成 Matrix Pipeline（多节点并行）
const generateMatrixPipeline = (nodes) => {
  const nodeLabels = nodes.map(n => `'${n.name}'`).join(', ')
  const preScript = simpleConfig.value.preScript || ''
  const testCommand = simpleConfig.value.testCommand || 'echo "测试执行完成"'
  const postScript = simpleConfig.value.postScript || ''

  // 构建完整的 pipeline 字符串
  let pipeline = `pipeline {
    agent none

    stages {
        stage('多节点并行执行') {
            matrix {
                axes {
                    axis {
                        name 'NODE_LABEL'
                        values ${nodeLabels}
                    }
                }
                stages {
                    stage('环境信息') {
                        steps {
                            echo "=========================================="
                            echo "多节点并行测试"
                            echo "节点: $\${NODE_LABEL}"
                            echo "=========================================="
                        }
                    }`

  if (preScript) {
    pipeline += `
                    stage('准备环境') {
                        steps {
                            sh '''${preScript}'''
                        }
                    }`
  }

  pipeline += `
                    stage('执行测试') {
                        steps {
                            node("$\${NODE_LABEL}") {
                                sh '''${testCommand}'''
                            }
                        }
                    }`

  if (postScript) {
    pipeline += `
                    stage('生成报告') {
                        steps {
                            sh '''${postScript}'''
                        }
                    }`
  }

  pipeline += `
                }
            }
        }
    }

    post {
        always {
            echo '=========================================='
            echo '多节点 Pipeline 执行完成'
            echo '=========================================='
        }
        success {
            echo '多节点 Pipeline 执行成功'
        }
        failure {
            echo '多节点 Pipeline 执行失败'
        }
    }
}`

  return pipeline
}

// 生成自定义 Pipeline
const generateCustomPipeline = (isMultiNode, nodes) => {
  // 多节点使用 matrix 模式
  if (isMultiNode && nodes && nodes.length > 1) {
    return generateCustomMatrixPipeline(nodes)
  }

  // 单节点模式
  let agentDirective = 'any'
  if (nodes && nodes.length > 0) {
    const nodeNames = nodes.map(n => n.name).join(' ')
    agentDirective = `label "${nodeNames}"`
  }
  console.log('generateCustomPipeline - agentDirective:', agentDirective)

  const stagesScript = customStages.value.map(stage => {
    // 根据execType生成不同的steps内容
    let stepsContent = ''
    if (stage.execType === 'script') {
      // Script模式:使用script块
      stepsContent = `                script {
${stage.script.split('\n').map(line => '                    ' + line).join('\n')}
                }`
    } else {
      // Shell模式:使用sh命令
      stepsContent = `                sh '''${stage.script}'''`
    }
    
    return `        stage('${stage.name}') {
            steps {
${stepsContent}
            }
        }`
  }).join('\n\n')

  const header = generatePipelineHeader()
  const options = generateOptionsBlock()
  const environment = generateEnvironmentBlock()

  return `${header}pipeline {
    agent {
        ${agentDirective}
    }
${options}${environment}
    stages {
${stagesScript}
    }

    post {
        always {
            echo 'Pipeline 执行完成'
        }
    }
}`
}

// 生成自定义 Matrix Pipeline（多节点并行）
const generateCustomMatrixPipeline = (nodes) => {
  const nodeNames = nodes.map(n => n.name)
  const axisValues = nodeNames.map(name => `'${name}'`).join(', ')

  const stagesScript = customStages.value.map(stage => {
    // 根据execType生成不同的steps内容
    let stepsContent = ''
    if (stage.execType === 'script') {
      // Script模式:在node块中使用script
      stepsContent = `                            node("\${NODE_LABEL}") {
                                script {
${stage.script.split('\n').map(line => '                                    ' + line).join('\n')}
                                }
                            }`
    } else {
      // Shell模式:在node块中使用sh
      stepsContent = `                            node("\${NODE_LABEL}") {
                                sh '''${stage.script}'''
                            }`
    }
    
    return `                    stage('${stage.name}') {
                        steps {
${stepsContent}
                        }
                    }`
  }).join('\n')

  return `pipeline {
    agent none

    stages {
        stage('多节点并行执行 - 自定义Stages') {
            matrix {
                axes {
                    axis {
                        name 'NODE_LABEL'
                        values ${axisValues}
                    }
                }
                stages {
                    stage('环境信息') {
                        steps {
                            echo "=========================================="
                            echo "节点: \${NODE_LABEL}"
                            echo "实际节点: \${env.NODE_NAME}"
                            echo "=========================================="
                        }
                    }
${stagesScript}
                }
            }
        }
    }

    post {
        always {
            echo '=========================================='
            echo '自定义 Matrix Pipeline 执行完成'
            echo '=========================================='
        }
        success {
            echo '✅ 所有节点执行成功'
        }
        failure {
            echo '❌ 部分节点执行失败'
        }
    }
}`
}

// 添加 Stage
const addStage = () => {
  customStages.value.push({
    name: `Stage ${customStages.value.length + 1}`,
    script: '',
    execType: 'sh' // 默认使用Shell模式
  })
}

// 删除 Stage
const removeStage = (index) => {
  if (customStages.value.length > 1) {
    customStages.value.splice(index, 1)
  }
}

// 监听 nodes 变化，自动显示预览
watch(() => props.nodes, (newNodes) => {
  console.log('PipelineBuilder - nodes changed:', newNodes)
  if (newNodes && newNodes.length > 0) {
    showPreview.value = true
  }
}, { immediate: true, deep: true })

// 向父组件发送配置更新
watch([simpleConfig, customStages, pipelineType, advancedConfig], () => {
  emit('update:config', {
    type: pipelineType.value,
    simple: simpleConfig.value,
    custom: customStages.value,
    advanced: advancedConfig.value
  })
}, { deep: true })

const handleTypeChange = () => {
  showPreview.value = true
}
</script>

<style scoped>
.stage-item {
  margin-bottom: 15px;
  padding: 15px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  background-color: #fafafa;
}

.stage-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.stage-list {
  margin-bottom: 15px;
}

.pipeline-preview {
  background-color: #f5f5f5;
  padding: 15px;
  border-radius: 4px;
  font-size: 12px;
  white-space: pre-wrap;
  word-break: break-all;
}

.preview-section {
  margin-top: 15px;
}

.advanced-config {
  margin-bottom: 20px;
}

.env-list {
  width: 100%;
}

.env-item {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 10px;
}

.env-item span {
  padding: 0 5px;
  color: #909399;
}
</style>

