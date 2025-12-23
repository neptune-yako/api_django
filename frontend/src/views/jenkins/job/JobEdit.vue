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
      <el-divider content-position="left">高级配置</el-divider>
      
      <el-form-item label="配置 XML">
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
import http from '@/api/index'

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
  description: '',
  is_active: true,
  config_xml: '',
  project: null,
  environment: null,
  plan: null
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

// 筛选选项
const projectList = ref([])
const environmentList = ref([])
const planList = ref([])

// 强制保存标记
let forceEdit = false

// 监听 jobData 变化，初始化表单
watch(() => props.jobData, (newData) => {
  if (newData) {
    form.value = {
      id: newData.id,
      name: newData.name,
      description: newData.description || '',
      is_active: newData.is_active !== false,
      config_xml: newData.config_xml || '',
      project: newData.project || null,
      environment: newData.environment || null,
      plan: newData.plan || null
    }
    xmlValidation.value = { valid: true, error: '' }
    forceEdit = false
  }
}, { immediate: true })

// 加载筛选选项
const loadOptions = async () => {
  try {
    // 加载项目列表
    const projectRes = await http.projectApi.getProjectList({ page: 1, size: 100 })
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
    
    // 加载计划列表（如果有的话）
    // TODO: 根据实际 API 调整
    // const planRes = await http.planApi.getPlanList()
    // planList.value = planRes.data || []
    
  } catch (error) {
    console.error('加载选项失败:', error)
  }
}

// 打开对话框时加载选项
watch(dialogVisible, (visible) => {
  if (visible) {
    loadOptions()
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
    
    const res = await editJenkinsJob({
      id: form.value.id,
      description: form.value.description,
      config_xml: form.value.config_xml || undefined,
      is_active: form.value.is_active,
      project: form.value.project || undefined,
      environment: form.value.environment || undefined,
      plan: form.value.plan || undefined,
      force: forceEdit
    })
    
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
    ElMessage.error('保存失败: ' + error.message)
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
