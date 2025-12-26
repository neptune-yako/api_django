<template>
  <el-dialog
    v-model="dialogVisible"
    title="创建 Jenkins Job"
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
      
      <el-form-item label="Jenkins 服务器" prop="server">
        <el-select 
          v-model="form.server" 
          placeholder="选择 Jenkins 服务器" 
          style="width: 100%"
        >
          <el-option
            v-for="server in serverList"
            :key="server.id"
            :label="server.name"
            :value="server.id"
          >
            <span>{{ server.name }}</span>
            <span style="float: right; color: #8492a6; font-size: 13px">{{ server.url }}</span>
          </el-option>
        </el-select>
      </el-form-item>
      
      <el-form-item label="Job 名称" prop="name">
        <el-input
          v-model="form.name"
          placeholder="输入 Job 名称（英文、数字、下划线）"
          maxlength="100"
          show-word-limit
        >
          <template #append>
            <el-button
              @click="generateTimestampName"
              :icon="RefreshRight"
              title="生成时间戳名称"
            />
          </template>
        </el-input>
        <span style="font-size: 12px; color: #909399; display: block; margin-top: 5px">
          ⚠️ Job 名称创建后不可修改 | 点击右侧按钮生成时间戳名称
        </span>
      </el-form-item>
      
      <el-form-item label="Job 类型" prop="job_type">
        <el-select 
          v-model="form.job_type" 
          placeholder="选择 Job 类型" 
          style="width: 100%"
          @change="handleTypeChange"
        >
          <el-option label="Pipeline (流水线)" value="Pipeline">
            <el-tag type="success" size="small">Pipeline</el-tag>
            <span style="margin-left: 10px; color: #909399">使用 Jenkinsfile 定义流程</span>
          </el-option>
          <el-option label="FreeStyle (自由风格)" value="FreeStyle">
            <el-tag type="primary" size="small">FreeStyle</el-tag>
            <span style="margin-left: 10px; color: #909399">最常用，适合简单任务</span>
          </el-option>
          <el-option label="Maven (Maven 项目)" value="Maven">
            <el-tag type="warning" size="small">Maven</el-tag>
            <span style="margin-left: 10px; color: #909399">Java Maven 项目构建</span>
          </el-option>
        </el-select>
        <span style="font-size: 12px; color: #909399; display: block; margin-top: 5px">
          💡 切换类型会自动加载对应模板
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
      <el-divider content-position="left">业务关联（可选）</el-divider>
      
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
              lang="groovy"
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
                useWorker: false
              }"
              style="height: 400px; width: 100%; border: 1px solid #dcdfe6; border-radius: 4px"
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
              useWorker: true
            }"
            style="height: 400px; width: 100%; border: 1px solid #dcdfe6; border-radius: 4px"
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
            💡 XML 会根据选择的类型自动加载模板，您可以在此基础上修改
          </span>
        </el-form-item>
      </template>
    </el-form>
    
    <template #footer>
      <el-button @click="handleCancel">取消</el-button>
      <el-button
        type="primary"
        @click="handleCreate"
        :loading="creating"
        :disabled="creating"
      >
        {{ creating ? '创建中...' : '创建' }}
      </el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, computed, watch, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { RefreshRight } from '@element-plus/icons-vue'
import { VAceEditor } from 'vue3-ace-editor'
import ace from 'ace-builds'
import 'ace-builds/src-noconflict/mode-xml'
import 'ace-builds/src-noconflict/theme-chrome'
import 'ace-builds/src-noconflict/ext-language_tools'

// 配置 ACE 基础路径
ace.config.set('basePath', 'https://cdn.jsdelivr.net/npm/ace-builds@' + ace.version + '/src-noconflict/')

import { createJenkinsJob } from '@/api/jenkins'
import { getJenkinsTemplateDetail } from '@/api/jenkins/template'
import { useJobFormOptions } from '@/composables/useJobFormOptions'
import http from '@/api/index'

// 导入 PipelineBuilder 组件
import PipelineBuilder from './components/PipelineBuilder.vue'

// Props & Emits
const props = defineProps({
  visible: Boolean
})

const emit = defineEmits(['update:visible', 'success'])

// 状态
const dialogVisible = computed({
  get: () => props.visible,
  set: (val) => emit('update:visible', val)
})

const formRef = ref(null)
const loading = ref(false)
const creating = ref(false)
const aceEditorRef = ref(null)

// 表单数据
const form = ref({
  server: null,
  name: '',
  job_type: 'Pipeline',  // 默认 Pipeline
  description: '',
  is_active: true,
  config_xml: '',
  project: null,
  environments: [],
  plan: null,
  target_node: null,
  target_nodes: [],      // 新增：多节点选择
  multi_node_mode: 'parallel',  // 新增：多节点模式
  pipeline_config: {},   // 新增：Pipeline 可视化配置
  use_visual_builder: true  // 新增：使用可视化构建器
})

// Pipeline 配置
const pipelineConfig = ref({})

// 表单验证
const rules = {
  server: [
    { required: true, message: '请选择 Jenkins 服务器', trigger: 'change' }
  ],
  name: [
    { required: true, message: 'Job 名称不能为空', trigger: 'blur' },
    { pattern: /^[a-zA-Z0-9_-]+$/, message: 'Job 名称只能包含字母、数字、下划线和横线', trigger: 'blur' },
    { min: 3, max: 100, message: '长度在 3 到 100 个字符', trigger: 'blur' }
  ],
  job_type: [
    { required: true, message: '请选择 Job 类型', trigger: 'change' }
  ],
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
  
  // 获取第一个选择的环境
  const firstEnvId = form.value.environments[0]
  const env = environmentList.value.find(e => e.id === firstEnvId)
  
  // 返回环境关联的 Jenkins 节点
  return env?.jenkins_node || null
})

// 节点列表
const nodeList = ref([])

// 加载节点列表（保留用于其他功能）
const loadNodes = async () => {
  try {
    const res = await http.get('/api/jenkins/nodes/')
    if (res.code === 200) {
      nodeList.value = (res.data || []).filter(node => node.is_online)
    }
  } catch (error) {
    console.error('加载节点列表失败:', error)
  }
}

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

// Pipeline 配置变更处理
const handlePipelineConfigChange = (config) => {
  form.value.pipeline_config = config
  console.log('Pipeline 配置更新:', config)
}

// 新增：构建器模式切换处理
const handleBuilderModeChange = (useVisual) => {
  if (!useVisual) {
    // 切换到高级模式，加载默认模板
    loadTemplateXml(form.value.job_type).then(template => {
      form.value.config_xml = template
    })
  }
}

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
let forceCreate = false

// 模板内容缓存
const templateCache = ref({})

// 加载模板 XML
const loadTemplateXml = async (jobType) => {
  // 如果已缓存，直接返回
  if (templateCache.value[jobType]) {
    return templateCache.value[jobType]
  }
  
  // 类型映射：前端使用 PascalCase，后端使用 lowercase
  const typeMap = {
    'Pipeline': 'pipeline',
    'FreeStyle': 'freestyle',
    'Maven': 'maven'
  }
  
  const backendType = typeMap[jobType] || 'pipeline'
  
  try {
    // 从后端 API 获取模板
    const res = await getJenkinsTemplateDetail(backendType)
    
    if (res.data && res.data.code === 200 && res.data.data) {
      const template = res.data.data.xml_content
      templateCache.value[jobType] = template
      return template
    } else {
      throw new Error(res.data?.message || '获取模板失败')
    }
  } catch (error) {
    console.error('加载模板失败:', error)
    ElMessage.error('加载模板失败: ' + error.message)
    return ''
  }
}

// 处理类型切换
const handleTypeChange = async (newType) => {
  try {
    loading.value = true
    const template = await loadTemplateXml(newType)
    form.value.config_xml = template
    
    // 更新编辑器内容
    nextTick(() => {
      if (aceEditorRef.value) {
        validateXmlInEditor(aceEditorRef.value._editor)
      }
    })
    
    ElMessage.success(`已加载 ${newType} 模板`)
  } catch (error) {
    ElMessage.error('加载模板失败: ' + error.message)
  } finally {
    loading.value = false
  }
}

// 处理项目变化
const handleProjectChange = async (projectId) => {
  // 清空环境和计划选择
  form.value.environments = []  // 改为空数组
  form.value.plan = null
  
  if (projectId) {
    // 重新加载该项目下的环境和计划
    await Promise.all([
      loadEnvironments(projectId),
      loadPlans(projectId)
    ])
  }
}

// 打开对话框时初始化
watch(dialogVisible, async (visible) => {
  if (visible) {
    // 重置表单
    form.value = {
      server: null,
      name: '',
      job_type: 'Pipeline',
      description: '',
      is_active: true,
      config_xml: '',
      project: null,
      environments: [],
      plan: null,
      target_node: null,
      target_nodes: [],
      multi_node_mode: 'parallel',
      pipeline_config: {},
      use_visual_builder: true
    }

    forceCreate = false
    xmlValidation.value = { valid: true, error: '' }

    // 加载选项
    loadAllOptions()

    // 加载节点列表
    await loadNodes()

    // 如果使用可视化构建器，不需要加载模板
    if (!form.value.use_visual_builder) {
      const template = await loadTemplateXml('Pipeline')
      form.value.config_xml = template
    }
  }
})

// ACE 编辑器初始化回调
const handleEditorInit = (editor) => {
  const session = editor.getSession()
  session.setUseSoftTabs(true)
  
  session.on('change', () => {
    nextTick(() => {
      validateXmlInEditor(editor)
    })
  })
  
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
      const errorText = errors[0].textContent || 'XML 格式错误'
      const annotations = [{
        row: 0,
        column: 0,
        text: errorText,
        type: 'error'
      }]
      editor.getSession().setAnnotations(annotations)
      xmlValidation.value = { valid: false, error: '🔴 XML 格式错误' }
    } else {
      editor.getSession().setAnnotations([])
      xmlValidation.value = { valid: true, error: '' }
    }
  } catch (e) {
    const annotations = [{
      row: 0,
      column: 0,
      text: 'XML 解析失败: ' + e.message,
      type: 'error'
    }]
    editor.getSession().setAnnotations(annotations)
    xmlValidation.value = { valid: false, error: '🔴 XML 解析失败' }
  }
}

// 创建
const handleCreate = async () => {
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
    creating.value = true

    // 构建请求 payload
    const payload = {
      server: form.value.server,
      name: form.value.name,
      job_type: form.value.job_type,
      description: form.value.description,
      is_active: form.value.is_active,
      project: form.value.project || undefined,
      environments: form.value.environments.length > 0 ? form.value.environments : undefined,
      plan: form.value.plan || undefined,
      force: forceCreate
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

    const res = await createJenkinsJob(payload)
    
    // 4. 处理响应
    if (res.data.code === 200) {
      ElMessage.success('✅ 创建成功')
      forceCreate = false
      dialogVisible.value = false
      emit('success')
    } else if (res.data.code === 5004) {
      // XML 验证失败，显示强制保存确认
      handleXmlError(res.data.data.errors)
    } else {
      ElMessage.error(res.data.message || '创建失败')
    }
    
  } catch (error) {
    console.error('创建失败:', error)
    // 优先获取后端返回的具体错误信息
    const errorMsg = error.response?.data?.message || error.message || '创建失败'
    ElMessage.error(errorMsg)
  } finally {
    creating.value = false
  }
}

// 处理 XML 错误（后端验证失败）
const handleXmlError = (errors) => {
  const errorMsg = errors && errors.length > 0
    ? errors.join('\n')
    : 'XML 验证失败'
  
  ElMessageBox.confirm(
    `后端 XML 验证失败：\n\n${errorMsg}\n\n是否强制创建到 Jenkins？`,
    '⚠️ XML 验证警告',
    {
      confirmButtonText: '强制创建',
      cancelButtonText: '取消',
      type: 'warning',
      dangerouslyUseHTMLString: false
    }
  ).then(() => {
    // 用户确认强制创建
    forceCreate = true
    handleCreate()  // 再次调用创建
  }).catch(() => {
    // 用户取消
    forceCreate = false
  })
}

// 取消
const handleCancel = () => {
  dialogVisible.value = false
  forceCreate = false
}

// 生成时间戳名称
const generateTimestampName = () => {
  const now = new Date()
  const year = now.getFullYear()
  const month = String(now.getMonth() + 1).padStart(2, '0')
  const day = String(now.getDate()).padStart(2, '0')
  const hour = String(now.getHours()).padStart(2, '0')
  const minute = String(now.getMinutes()).padStart(2, '0')

  form.value.name = `${year}${month}${day}-${hour}${minute}`
  ElMessage.success(`已生成时间戳名称: ${form.value.name}`)
}
</script>

<style scoped>
/* ACE Editor 已经自带样式，无需额外定制 */
</style>
