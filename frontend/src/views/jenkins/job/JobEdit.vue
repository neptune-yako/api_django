<template>
  <el-dialog
    v-model="dialogVisible"
    :title="dialogTitle"
    width="900px"
    :close-on-click-modal="false"
  >
    <el-form
      ref="formRef"
      :model="form"
      :rules="rules"
      label-width="120px"
      v-loading="loading"
    >
      <!-- 基本信息 -->
      <el-divider content-position="left">基本信息</el-divider>
      
      <el-form-item label="Job 名称">
        <el-input v-model="form.name" disabled placeholder="Job 名称不可修改" />
        <span style="font-size: 12px; color: #909399; margin-left: 10px">
          修改 name 会删除旧 Job，如需改名请使用"复制"功能
        </span>
      </el-form-item>
      
      <el-form-item label="Job 类型" v-if="isCreateMode">
        <el-select v-model="form.job_type" placeholder="选择 Job 类型" style="width: 100%">
          <el-option label="FreeStyle (自由风格)" value="FreeStyle">
            <el-tag type="primary" size="small">FreeStyle</el-tag>
            <span style="margin-left: 10px; color: #909399">最常用，适合简单任务</span>
          </el-option>
          <el-option label="Pipeline (流水线)" value="Pipeline">
            <el-tag type="success" size="small">Pipeline</el-tag>
            <span style="margin-left: 10px; color: #909399">使用 Jenkinsfile 定义流程</span>
          </el-option>
          <el-option label="Maven (Maven 项目)" value="Maven">
            <el-tag type="warning" size="small">Maven</el-tag>
            <span style="margin-left: 10px; color: #909399">Java Maven 项目构建</span>
          </el-option>
        </el-select>
        <span style="font-size: 12px; color: #909399; display: block; margin-top: 5px">
          ⚠️ Job 类型创建后不可更改
        </span>
      </el-form-item>
      
      <el-form-item label="Job 类型" v-else>
        <el-tag :type="jobTypeTagType" size="large">{{ form.job_type }}</el-tag>
        <span style="font-size: 12px; color: #909399; margin-left: 10px">
          类型创建后不可更改
        </span>
      </el-form-item>
      
      <el-form-item label="描述" prop="description">
        <el-input
          v-model="form.description"
          type="textarea"
          :rows="3"
          placeholder="输入 Job 描述"
          maxlength="500"
          show-word-limit
        />
      </el-form-item>
      
      <el-form-item label="状态">
        <el-switch
          v-model="form.is_active"
          active-text="启用"
          inactive-text="禁用"
        />
      </el-form-item>
      
      <!-- 业务关联 -->
      <el-divider content-position="left">业务关联（仅本地）</el-divider>
      
      <el-form-item label="关联项目">
        <el-select 
          v-model="form.project" 
          clearable 
          placeholder="选择项目" 
          style="width: 100%"
          @change="handleProjectChange"
        >
          <el-option
            v-for="project in projectList"
            :key="project.id"
            :label="project.name"
            :value="project.id"
          />
        </el-select>
        <span style="font-size: 12px; color: #909399; display: block; margin-top: 5px">
          💡 选择项目后，环境和计划选项将自动过滤
        </span>
      </el-form-item>
      
      <el-form-item label="测试环境">
        <el-select 
          v-model="form.environments" 
          multiple
          clearable 
          placeholder="请先选择项目" 
          style="width: 100%"
          :disabled="!form.project"
        >
          <el-option
            v-for="env in filteredEnvironmentList"
            :key="env.id"
            :label="env.name"
            :value="env.id"
          />
        </el-select>
        <span style="font-size: 12px; color: #909399; display: block; margin-top: 5px">
          💡 可选择多个测试环境
        </span>
      </el-form-item>
      
      <el-form-item label="测试计划">
        <el-select 
          v-model="form.plan" 
          clearable 
          placeholder="请先选择项目" 
          style="width: 100%"
          :disabled="!form.project"
        >
          <el-option
            v-for="plan in filteredPlanList"
            :key="plan.id"
            :label="plan.name"
            :value="plan.id"
          />
        </el-select>
      </el-form-item>
      
      <!-- Pipeline 配置（仅 Pipeline 类型显示） -->
      <template v-if="form.job_type === 'Pipeline'">
        <el-divider content-position="left">
          Pipeline 配置
          <el-switch
            v-model="form.use_visual_builder"
            active-text="可视化"
            inactive-text="高级"
            style="margin-left: 20px"
            @change="handleBuilderModeChange"
          />
        </el-divider>

        <!-- 可视化构建器 -->
        <PipelineBuilder
          v-if="form.use_visual_builder"
          :nodes="selectedEnvironmentNodes.map(e => e.node)"
          :environments="selectedEnvironmentNames"
          @update:config="handlePipelineConfigChange"
        />

        <!-- 高级模式：XML 编辑器 -->
        <template v-else>
          <el-form-item>
            <VAceEditor
              ref="aceEditorRef"
              v-model:value="form.config_xml"
              lang="xml"
              theme="chrome"
              :options="{
                fontSize: 14,
                showPrintMargin: false,
                showGutter: true,
                highlightActiveLine: true,
                enableBasicAutocompletion: true,
                enableLiveAutocompletion: true,
                enableSnippets: true,
                tabSize: 2,
                wrap: true,
                useWorker: true
              }"
              style="height: 400px; width: 100%; border: 1px solid #dcdfe6; border-radius: 4px"
              @blur="handleXmlBlur"
              @init="handleEditorInit"
            />
            <el-alert
              v-if="xmlValidation.error"
              type="warning"
              :title="xmlValidation.error"
              :closable="false"
              style="margin-top: 10px"
            />
          </el-form-item>
        </template>
      </template>

      <!-- 非 Pipeline 类型的 XML 编辑器 -->
      <template v-if="form.job_type !== 'Pipeline'">
        <el-divider content-position="left">配置 XML</el-divider>
        <el-form-item>
          <VAceEditor
            ref="aceEditorRef"
            v-model:value="form.config_xml"
            lang="xml"
            theme="chrome"
            :options="{
              fontSize: 14,
              showPrintMargin: false,
              showGutter: true,
              highlightActiveLine: true,
              enableBasicAutocompletion: true,
              enableLiveAutocompletion: true,
              enableSnippets: true,
              tabSize: 2,
              wrap: true,
              useWorker: true  // 启用 Worker 进行实时验证
            }"
            style="height: 400px; width: 100%; border: 1px solid #dcdfe6; border-radius: 4px"
            @blur="handleXmlBlur"
            @init="handleEditorInit"
          />
          <el-alert
            v-if="xmlValidation.error"
            type="warning"
            :title="xmlValidation.error"
            :closable="false"
            style="margin-top: 10px"
          />
          <span style="font-size: 12px; color: #909399; display: block; margin-top: 5px">
            ⚠️ 修改将同步到 Jenkins。XML 格式会自动验证，验证失败可选择强制保存
          </span>
        </el-form-item>
      </template>
    </el-form>
    
    <template #footer>
      <el-button @click="handleCancel">取消</el-button>
      <el-button
        type="primary"
        @click="handleSave"
        :loading="saving"
        :disabled="saving"
      >
        {{ saving ? '保存中...' : '保存' }}
      </el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, computed, watch, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { VAceEditor } from 'vue3-ace-editor'
import ace from 'ace-builds'
import 'ace-builds/src-noconflict/mode-xml'
import 'ace-builds/src-noconflict/theme-chrome'
import 'ace-builds/src-noconflict/ext-language_tools'

// 配置 ACE 基础路径
ace.config.set('basePath', 'https://cdn.jsdelivr.net/npm/ace-builds@' + ace.version + '/src-noconflict/')

import { editJenkinsJob } from '@/api/jenkins'
import { useJobFormOptions } from '@/composables/useJobFormOptions'
import http from '@/api/index'

// 导入 PipelineBuilder 组件
import PipelineBuilder from './components/PipelineBuilder.vue'

// Props & Emits
const props = defineProps({
  visible: Boolean,
  jobData: Object  // 编辑时传入的 Job 数据
})

const emit = defineEmits(['update:visible', 'success'])

// 状态
const dialogVisible = computed({
  get: () => props.visible,
  set: (val) => emit('update:visible', val)
})

const dialogTitle = computed(() => {
  return props.jobData ? '编辑 Job' : '新建 Job'
})

const formRef = ref(null)
const loading = ref(false)
const saving = ref(false)
const aceEditorRef = ref(null)  // ACE 编辑器引用

// 表单数据
const form = ref({
  id: null,
  name: '',
  job_type: 'FreeStyle',  // 默认 FreeStyle
  description: '',
  is_active: true,
  config_xml: '',
  project: null,
  environments: [],  // 改为数组
  plan: null,
  target_node: null,  // 新增:目标节点
  pipeline_config: {},   // 新增：Pipeline 可视化配置
  use_visual_builder: true  // 新增：使用可视化构建器
})

// 表单验证
const rules = {
  description: [
    { max: 500, message: '描述不能超过 500 字符', trigger: 'blur' }
  ]
}

// XML 验证状态
const xmlValidation = ref({
  valid: true,
  error: ''
})

// 使用 composable 获取表单选项
const {
  serverList,
  projectList,
  environmentList,
  planList,
  loadAllOptions,
  loadEnvironments,
  loadPlans
} = useJobFormOptions()

// 计算属性: 从选择的环境中获取 Jenkins 节点
const selectedEnvironmentNode = computed(() => {
  if (!form.value.environments || form.value.environments.length === 0) {
    return null
  }
  
  const firstEnvId = form.value.environments[0]
  const env = environmentList.value.find(e => e.id === firstEnvId)
  
  return env?.jenkins_node || null
})

// 计算从测试环境获取的执行节点
const selectedEnvironmentNodes = computed(() => {
  if (!form.value.environments || form.value.environments.length === 0) {
    return []
  }

  // 从选择的环境中获取节点信息
  const result = form.value.environments
    .map(envId => {
      const env = environmentList.value.find(e => e.id === envId)
      // 如果找不到环境，返回null
      if (!env) {
        console.warn(`环境 ID ${envId} 未找到`)
        return null
      }
      // 环境名称本身就是节点名称
      return {
        id: envId,
        env: env,
        node: {
          name: env.name,
          display_name: env.name
        }
      }
    })
    .filter(item => item !== null) // 过滤掉null值

  console.log('selectedEnvironmentNodes (环境即节点):', result)
  return result
})

// 获取环境名称列表（用于传递给后端）
const selectedEnvironmentNames = computed(() => {
  return selectedEnvironmentNodes.value
    .filter(item => item && item.env)
    .map(item => item.env.name)
})

// 根据选中的项目过滤环境列表
const filteredEnvironmentList = computed(() => {
  if (!form.value.project) return []
  return environmentList.value.filter(env => env.project === form.value.project)
})

// 根据选中的项目过滤计划列表
const filteredPlanList = computed(() => {
  if (!form.value.project) return []
  return planList.value.filter(plan => plan.project === form.value.project)
})

// 强制保存标记
let forceEdit = false

// 判断是否为新建模式
const isCreateMode = computed(() => !props.jobData || !props.jobData.id)

// Job 类型标签颜色
const jobTypeTagType = computed(() => {
  const typeMap = {
    'FreeStyle': 'primary',
    'Pipeline': 'success',
    'Maven': 'warning'
  }
  return typeMap[form.value.job_type] || 'info'
})

// 监听 jobData 变化，初始化表单
watch(() => props.jobData, async (newData) => {
  if (newData) {
    form.value = {
      id: newData.id,
      name: newData.name,
      job_type: newData.job_type || 'FreeStyle',
      description: newData.description || '',
      is_active: newData.is_active !== false,
      config_xml: newData.config_xml || '',
      project: newData.project || null,
      environments: newData.environments || [],  // 处理环境ID数组
      plan: newData.plan || null,
      target_node: newData.target_node || null,  // 加载节点数据
      pipeline_config: newData.pipeline_config || {},  // 加载 Pipeline 配置
      use_visual_builder: true  // 默认使用可视化构建器
    }
    xmlValidation.value = { valid: true, error: '' }
    forceEdit = false
    
    // 如果有项目，加载对应的环境和计划
    if (newData.project) {
      await Promise.all([
        loadEnvironments(newData.project),
        loadPlans(newData.project)
      ])
    }
  }
}, { immediate: true })

// 处理项目变化
const handleProjectChange = async (projectId) => {
  // 清空环境和计划选择
  form.value.environments = []
  form.value.plan = null
  
  if (projectId) {
    // 重新加载该项目下的环境和计划
    await Promise.all([
      loadEnvironments(projectId),
      loadPlans(projectId)
    ])
  }
}

// Pipeline 配置变更处理
const handlePipelineConfigChange = (config) => {
  form.value.pipeline_config = config
  console.log('Pipeline 配置更新:', config)
}

// 新增：构建器模式切换处理
const handleBuilderModeChange = (useVisual) => {
  if (!useVisual) {
    // 切换到高级模式时，如果没有config_xml，保持当前内容
    console.log('切换到高级模式')
  }
}

// 打开对话框时加载选项
watch(dialogVisible, (visible) => {
  if (visible) {
    loadAllOptions()
  }
})

// XML 失焦验证（前端快速检查）
const handleXmlBlur = () => {
  if (!form.value.config_xml || !form.value.config_xml.trim()) {
    xmlValidation.value = { valid: true, error: '' }
    return
  }
  
  try {
    const parser = new DOMParser()
    const doc = parser.parseFromString(form.value.config_xml, 'text/xml')
    
    const errors = doc.getElementsByTagName('parsererror')
    if (errors.length > 0) {
      xmlValidation.value = {
        valid: false,
        error: '🔴 XML 格式错误，请修正后保存'
      }
    } else {
      xmlValidation.value = { valid: true, error: '' }
    }
  } catch (e) {
    xmlValidation.value = {
      valid: false,
      error: '🔴 XML 解析失败: ' + e.message
    }
  }
}

// ACE 编辑器初始化回调
const handleEditorInit = (editor) => {
  // 配置编辑器会话
  const session = editor.getSession()
  
  // 启用软 Tab
  session.setUseSoftTabs(true)
  
  // 设置验证注解
  session.on('change', () => {
    nextTick(() => {
      validateXmlInEditor(editor)
    })
  })
  
  // 初始验证
  if (form.value.config_xml) {
    validateXmlInEditor(editor)
  }
}

// 在编辑器中进行 XML 实时验证
const validateXmlInEditor = (editor) => {
  const content = editor.getValue()
  if (!content || !content.trim()) {
    editor.getSession().setAnnotations([])
    return
  }
  
  try {
    const parser = new DOMParser()
    const doc = parser.parseFromString(content, 'text/xml')
    const errors = doc.getElementsByTagName('parsererror')
    
    if (errors.length > 0) {
      // 提取错误信息
      const errorText = errors[0].textContent || 'XML 格式错误'
      const annotations = [{
        row: 0,
        column: 0,
        text: errorText,
        type: 'error'
      }]
      editor.getSession().setAnnotations(annotations)
    } else {
      // 验证通过，清除错误标记
      editor.getSession().setAnnotations([])
      
      // 额外检查 Jenkins 特定结构
      const root = doc.documentElement
      if (root && !['project', 'flow-definition', 'maven2-moduleset'].includes(root.tagName)) {
        const warnings = [{
          row: 0,
          column: 0,
          text: `警告：根元素应该是 <project>、<flow-definition> 或 <maven2-moduleset>，当前是 <${root.tagName}>`,
          type: 'warning'
        }]
        editor.getSession().setAnnotations(warnings)
      }
    }
  } catch (e) {
    const annotations = [{
      row: 0,
      column: 0,
      text: 'XML 解析失败: ' + e.message,
      type: 'error'
    }]
    editor.getSession().setAnnotations(annotations)
  }
}

// 保存
const handleSave = async () => {
  // 1. 表单验证
  if (!formRef.value) return
  
  try {
    await formRef.value.validate()
  } catch {
    return
  }
  
  // 2. 前端 XML 快速检查
  if (form.value.config_xml && !xmlValidation.value.valid) {
    ElMessage.warning('请先修正 XML 格式错误')
    return
  }
  
  // 3. 发送请求
  try {
    saving.value = true
    
    // 构建请求 payload
    const payload = {
        id: form.value.id,
        name: form.value.name,
        job_type: form.value.job_type,  // 添加 job_type
        description: form.value.description,
        is_active: form.value.is_active,
        project: form.value.project || undefined,
        environments: form.value.environments || undefined,  // 修改
        plan: form.value.plan || undefined,
        target_node: selectedEnvironmentNode.value?.id || undefined,  // 使用环境关联的节点
        force: forceEdit
    }

    // 根据 Pipeline 类型和构建器模式处理配置
    if (form.value.job_type === 'Pipeline') {
      // 使用可视化构建器或高级模式
      payload.use_visual_builder = form.value.use_visual_builder

      if (form.value.use_visual_builder) {
        // 可视化模式：发送 pipeline_config，不发送 config_xml
        payload.pipeline_config = form.value.pipeline_config
      } else {
        // 高级模式：发送 config_xml
        payload.config_xml = form.value.config_xml
      }
    } else {
      // 非 Pipeline 类型：发送 config_xml
      payload.config_xml = form.value.config_xml
    }
    
      const res = await (isCreateMode.value ? createJenkinsJob(payload) : editJenkinsJob(payload))
    
    // 4. 处理响应
    if (res.data.code === 200) {
      ElMessage.success('✅ 保存成功')
      forceEdit = false
      dialogVisible.value = false
      emit('success')
    } else if (res.data.code === 5004) {
      // XML 验证失败，显示强制保存确认
      handleXmlError(res.data.data.errors)
    } else {
      ElMessage.error(res.data.message || '保存失败')
    }
    
  } catch (error) {
    console.error('保存失败:', error)
    // 优先获取后端返回的具体错误信息
    const errorMsg = error.response?.data?.message || error.message || '保存失败'
    ElMessage.error(errorMsg)
  } finally {
    saving.value = false
  }
}

// 处理 XML 错误（后端验证失败）
const handleXmlError = (errors) => {
  const errorMsg = errors && errors.length > 0
    ? errors.join('\n')
    : 'XML 验证失败'
  
  ElMessageBox.confirm(
    `后端 XML 验证失败：\n\n${errorMsg}\n\n是否强制保存到 Jenkins？`,
    '⚠️ XML 验证警告',
    {
      confirmButtonText: '强制保存',
      cancelButtonText: '取消',
      type: 'warning',
      dangerouslyUseHTMLString: false
    }
  ).then(() => {
    // 用户确认强制保存
    forceEdit = true
    handleSave()  // 再次调用保存
  }).catch(() => {
    // 用户取消
    forceEdit = false
  })
}

// 取消
const handleCancel = () => {
  dialogVisible.value = false
  forceEdit = false
}
</script>

<style scoped>
/* ACE Editor 已经自带样式，无需额外定制 */
</style>
