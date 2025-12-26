<template>
  <el-dialog
    v-model="dialogVisible"
    :title="dialogTitle"
    width="600px"
    :close-on-click-modal="false"
  >
    <el-form
      ref="formRef"
      :model="form"
      :rules="rules"
      label-width="120px"
      v-loading="loading"
    >
      <el-alert
        v-if="!hasParams"
        type="info"
        :closable="false"
        style="margin-bottom: 20px"
      >
        <template #title>
          该 Job 不包含动态参数，将直接触发构建
        </template>
      </el-alert>

      <template v-if="hasParams">
        <el-alert
          type="success"
          :closable="false"
          style="margin-bottom: 20px"
        >
          <template #title>
            检测到 {{ params.length }} 个动态参数，请填写后构建
          </template>
        </el-alert>

        <el-form-item
          v-for="param in params"
          :key="param"
          :label="param"
          :prop="`paramValues.${param}`"
          :rules="[
            { required: true, message: `请填写 ${param}`, trigger: 'blur' }
          ]"
        >
          <el-input
            v-model="form.paramValues[param]"
            :placeholder="`请填写 ${param}`"
            type="textarea"
            :rows="2"
            clearable
          >
            <template #append>
              <el-tooltip content="清空" placement="top">
                <el-button
                  :icon="Delete"
                  @click="form.paramValues[param] = ''"
                />
              </el-tooltip>
            </template>
          </el-input>
          <span style="font-size: 12px; color: #909399; display: block; margin-top: 5px">
            💡 支持多行文本输入
          </span>
        </el-form-item>
      </template>
    </el-form>

    <template #footer>
      <el-button @click="handleCancel">取消</el-button>
      <el-button
        type="primary"
        @click="handleBuild"
        :loading="building"
        :disabled="building"
      >
        {{ building ? '构建中...' : '立即构建' }}
      </el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { Delete } from '@element-plus/icons-vue'
import { checkJobParams, buildJenkinsJob } from '@/api/jenkins'

// Props & Emits
const props = defineProps({
  visible: Boolean,
  jobData: Object  // { id, name }
})

const emit = defineEmits(['update:visible', 'success'])

// 状态
const dialogVisible = computed({
  get: () => props.visible,
  set: (val) => emit('update:visible', val)
})

const dialogTitle = computed(() => {
  return props.jobData ? `构建 - ${props.jobData.name}` : '构建 Job'
})

const formRef = ref(null)
const loading = ref(false)
const building = ref(false)
const params = ref([])  // 参数列表 ['score', 'env']

// 表单数据
const form = ref({
  paramValues: {}  // 参数值 { score: '95', env: 'prod' }
})

// 表单验证规则
const rules = ref({})

// 是否有参数
const hasParams = computed(() => params.value.length > 0)

// 检查 Job 参数
const checkParams = async () => {
  if (!props.jobData || !props.jobData.id) return

  loading.value = true
  try {
    const res = await checkJobParams(props.jobData.id)
    
    if (res.data.code === 200) {
      params.value = res.data.data.params || []
      
      // 初始化表单值
      const paramValues = {}
      params.value.forEach(param => {
        // 尝试从 LocalStorage 加载上次填写的值
        const savedValue = localStorage.getItem(`job_param_${props.jobData.id}_${param}`)
        paramValues[param] = savedValue || ''
      })
      form.value.paramValues = paramValues
    } else {
      ElMessage.warning('检查参数失败，将使用普通构建')
      params.value = []
    }
  } catch (error) {
    console.error('检查参数失败:', error)
    ElMessage.error('检查参数失败: ' + (error.message || '未知错误'))
    params.value = []
  } finally {
    loading.value = false
  }
}

// 监听对话框打开
watch(dialogVisible, (visible) => {
  if (visible) {
    // 重置表单
    form.value.paramValues = {}
    params.value = []
    
    // 检查参数
    checkParams()
  }
})

// 构建
const handleBuild = async () => {
  // 如果有参数，先验证表单
  if (hasParams.value) {
    if (!formRef.value) return
    
    try {
      await formRef.value.validate()
    } catch {
      ElMessage.warning('请填写所有必需参数')
      return
    }
  }

  building.value = true
  try {
    const payload = {
      job_name: props.jobData.name
    }

    // 如果有参数，添加到请求中
    if (hasParams.value) {
      payload.build_params = form.value.paramValues
      
      // 保存到 LocalStorage
      params.value.forEach(param => {
        const value = form.value.paramValues[param]
        if (value) {
          localStorage.setItem(
            `job_param_${props.jobData.id}_${param}`,
            value
          )
        }
      })
    }

    const res = await buildJenkinsJob(payload)
    
    if (res.data.code === 200) {
      ElMessage.success('✅ 构建已触发')
      dialogVisible.value = false
      emit('success')
    } else {
      ElMessage.error(res.data.message || '构建触发失败')
    }
  } catch (error) {
    console.error('构建失败:', error)
    const errorMsg = error.response?.data?.message || error.message || '构建触发失败'
    ElMessage.error(errorMsg)
  } finally {
    building.value = false
  }
}

// 取消
const handleCancel = () => {
  dialogVisible.value = false
}
</script>

<style scoped>
:deep(.el-form-item__label) {
  font-weight: 500;
}

:deep(.el-textarea__inner) {
  font-family: 'Courier New', monospace;
  font-size: 13px;
}
</style>
