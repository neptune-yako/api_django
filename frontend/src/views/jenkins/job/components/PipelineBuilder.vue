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
            <el-button @click="removeStage(index)" type="danger" link>
              删除
            </el-button>
          </div>

          <el-input
            v-model="stage.script"
            type="textarea"
            :rows="4"
            placeholder="Shell 脚本内容"
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
    name: '准备环境',
    script: 'pip install -r requirements.txt'
  },
  {
    name: '执行测试',
    script: 'pytest tests/ --alluredir=allure-results -v'
  }
])

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
  // 获取节点名称
  let agentDirective = 'any'
  if (nodes && nodes.length > 0) {
    const nodeNames = nodes.map(n => n.name).join(' ')
    agentDirective = `label '${nodeNames}'`
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

  return `pipeline {
    agent ${agentDirective}

    stages {
${stages}
    }

    post {
        success {
            echo '✅ Pipeline 执行成功'
        }
        failure {
            echo '❌ Pipeline 执行失败'
        }
    }
}`
}

// 生成自定义 Pipeline
const generateCustomPipeline = (isMultiNode, nodes) => {
  // 获取节点名称
  let agentDirective = 'any'
  if (nodes && nodes.length > 0) {
    const nodeNames = nodes.map(n => n.name).join(' ')
    agentDirective = `label '${nodeNames}'`
  }
  console.log('generateCustomPipeline - agentDirective:', agentDirective)

  const stagesScript = customStages.value.map(stage => `        stage('${stage.name}') {
            steps {
                sh '''${stage.script}'''
            }
        }`).join('\n\n')

  return `pipeline {
    agent ${agentDirective}

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

// 添加 Stage
const addStage = () => {
  customStages.value.push({
    name: `Stage ${customStages.value.length + 1}`,
    script: ''
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
watch([simpleConfig, customStages, pipelineType], () => {
  emit('update:config', {
    type: pipelineType.value,
    simple: simpleConfig.value,
    custom: customStages.value
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
</style>
