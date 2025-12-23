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
      
      <el-form-item label="Job 名称" prop="name">
        <el-input 
          v-model="form.name" 
          placeholder="输入 Job 名称（英文、数字、下划线）" 
          maxlength="100"
          show-word-limit
        />
        <span style="font-size: 12px; color: #909399; display: block; margin-top: 5px">
          ⚠️ Job 名称创建后不可修改
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
        <el-select v-model="form.project" clearable placeholder="选择项目" style="width: 100%">
          <el-option
            v-for="project in projectList"
            :key="project.id"
            :label="project.name"
            :value="project.id"
          />
        </el-select>
      </el-form-item>
      
      <el-form-item label="测试环境">
        <el-select v-model="form.environment" clearable placeholder="选择环境" style="width: 100%">
          <el-option
            v-for="env in environmentList"
            :key="env.id"
            :label="env.name"
            :value="env.id"
          />
        </el-select>
      </el-form-item>
      
      <el-form-item label="测试计划">
        <el-select v-model="form.plan" clearable placeholder="选择计划" style="width: 100%">
          <el-option
            v-for="plan in planList"
            :key="plan.id"
            :label="plan.name"
            :value="plan.id"
          />
        </el-select>
      </el-form-item>
      
      <!-- 高级配置 -->
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
import { VAceEditor } from 'vue3-ace-editor'
import ace from 'ace-builds'
import 'ace-builds/src-noconflict/mode-xml'
import 'ace-builds/src-noconflict/theme-chrome'
import 'ace-builds/src-noconflict/ext-language_tools'

// 配置 ACE 基础路径
ace.config.set('basePath', 'https://cdn.jsdelivr.net/npm/ace-builds@' + ace.version + '/src-noconflict/')

import { createJenkinsJob } from '@/api/jenkins'
import { getJenkinsTemplateDetail } from '@/api/jenkins/template'
import http from '@/api/index'

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
  name: '',
  job_type: 'Pipeline',  // 默认 Pipeline
  description: '',
  is_active: true,
  config_xml: '',
  project: null,
  environment: null,
  plan: null
})

// 表单验证
const rules = {
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

// 筛选选项
const projectList = ref([])
const environmentList = ref([])
const planList = ref([])

// 强制保存标记
let forceCreate = false

// 模板内容缓存
const templateCache = ref({})

// 加载筛选选项
const loadOptions = async () => {
  try {
    // 加载项目列表
    const projectRes = await http.projectApi.getProject({ page: 1, size: 100 })
    projectList.value = projectRes.data.list || []
    
    // 加载环境列表
    try {
      const { ProjectStore } = await import('@/stores/module/ProStore')
      const pstore = ProjectStore()
      if (pstore.proList && pstore.proList.id) {
        const envRes = await http.environmentApi.getEnvironment(pstore.proList.id)
        environmentList.value = envRes.data || []
      }
    } catch (e) {
      console.warn('加载环境列表失败:', e)
    }
  } catch (error) {
    console.error('加载选项失败:', error)
  }
}

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

// 打开对话框时初始化
watch(dialogVisible, async (visible) => {
  if (visible) {
    // 重置表单
    form.value = {
      name: '',
      job_type: 'Pipeline',
      description: '',
      is_active: true,
      config_xml: '',
      project: null,
      environment: null,
      plan: null
    }
    
    forceCreate = false
    xmlValidation.value = { valid: true, error: '' }
    
    // 加载选项
    loadOptions()
    
    // 加载默认模板
    const template = await loadTemplateXml('Pipeline')
    form.value.config_xml = template
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
    
    const res = await createJenkinsJob({
      name: form.value.name,
      job_type: form.value.job_type,
      description: form.value.description,
      config_xml: form.value.config_xml,
      is_active: form.value.is_active,
      project: form.value.project || undefined,
      environment: form.value.environment || undefined,
      plan: form.value.plan || undefined,
      force: forceCreate
    })
    
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
    ElMessage.error('创建失败: ' + error.message)
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
</script>

<style scoped>
/* ACE Editor 已经自带样式，无需额外定制 */
</style>
