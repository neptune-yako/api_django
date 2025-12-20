<template>
  <div class="app-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span class="title">Jenkins 服务器管理</span>
          <el-button type="primary" @click="handleAdd">
            <el-icon class="el-icon--left"><Plus /></el-icon>添加服务器
          </el-button>
        </div>
      </template>

      <el-table 
        v-loading="loading" 
        :data="tableData" 
        style="width: 100%" 
        border
      >
        <el-table-column prop="name" label="服务器名称" width="180" />
        <el-table-column prop="url" label="Jenkins URL" min-width="200" show-overflow-tooltip />
        <el-table-column prop="username" label="用户名" width="120" />
        <el-table-column prop="is_active" label="状态" width="100">
          <template #default="scope">
            <el-tag :type="scope.row.is_active ? 'success' : 'info'">
              {{ scope.row.is_active ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="connection_status" label="连接状态" width="120">
          <template #default="scope">
            <StatusTag :status="scope.row.connection_status" type="connection" />
          </template>
        </el-table-column>
        <el-table-column prop="last_check_time" label="最后检查时间" width="180">
          <template #default="scope">
            {{ formatTime(scope.row.last_check_time) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="300" fixed="right">
          <template #default="scope">
            <el-button 
              size="small" 
              type="warning" 
              @click="handleTestConnection(scope.row)"
              :loading="scope.row.testing"
            >
              测试连接
            </el-button>
            <el-button size="small" type="primary" @click="handleEdit(scope.row)">编辑</el-button>
            <el-button size="small" type="danger" @click="handleDelete(scope.row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 添加/编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogType === 'add' ? '添加 Jenkins 服务器' : '编辑 Jenkins 服务器'"
      width="500px"
      @close="resetForm"
    >
      <el-form 
        ref="formRef" 
        :model="formData" 
        :rules="rules" 
        label-width="100px"
      >
        <el-form-item label="名称" prop="name">
          <el-input v-model="formData.name" placeholder="请输入服务器名称" />
        </el-form-item>
        <el-form-item label="URL" prop="url">
          <el-input v-model="formData.url" placeholder="http://jenkins.example.com" />
        </el-form-item>
        <el-form-item label="用户名" prop="username">
          <el-input v-model="formData.username" placeholder="请输入认证用户名" />
        </el-form-item>
        <el-form-item label="Token" prop="token">
          <el-input 
            v-model="formData.token" 
            type="password" 
            :placeholder="dialogType === 'add' ? '请输入 API Token' : '留空则保持原有 Token 不变'"
            show-password
          />
        </el-form-item>
        <el-form-item label="状态" prop="is_active">
          <el-switch v-model="formData.is_active" />
          <span style="margin-left: 10px">{{ formData.is_active ? '启用' : '禁用' }}</span>
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input v-model="formData.description" type="textarea" :rows="3" />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitForm" :loading="submitting">
            确定
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, reactive, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { 
  getJenkinsServers, 
  addJenkinsServer, 
  updateJenkinsServer, 
  deleteJenkinsServer,
  testJenkinsConnection 
} from '@/api/jenkins'
import StatusTag from '../common/StatusTag.vue'
import { parseList } from '../utils/response-parser'
import { formatTime } from '../utils/formatters'

// 状态变量
const loading = ref(false)
const tableData = ref([])
const dialogVisible = ref(false)
const dialogType = ref('add') // 'add' or 'edit'
const submitting = ref(false)
const formRef = ref(null)

// 表单数据
const formData = reactive({
  id: undefined,
  name: '',
  url: '',
  username: '',
  token: '',
  is_active: true,
  description: ''
})

// 表单验证规则
const rules = computed(() => {
  const commonRules = {
    name: [{ required: true, message: '请输入服务器名称', trigger: 'blur' }],
    url: [
      { required: true, message: '请输入 Jenkins URL', trigger: 'blur' },
      { type: 'url', message: '请输入有效的 URL', trigger: 'blur' }
    ],
    username: [{ required: true, message: '请输入用户名', trigger: 'blur' }]
  }
  
  if (dialogType.value === 'add') {
    return {
      ...commonRules,
      token: [{ required: true, message: '请输入 API Token', trigger: 'blur' }]
    }
  }
  
  return commonRules
})

// 获取数据
const fetchData = async () => {
  loading.value = true
  try {
    const res = await getJenkinsServers()
    // 使用工具类解析数据，修复 "not iterable" 报错
    tableData.value = parseList(res)
  } catch (error) {
    console.error('Failed to fetch servers:', error)
  } finally {
    loading.value = false
  }
}

// 对应操作处理
const handleAdd = () => {
  dialogType.value = 'add'
  dialogVisible.value = true
}

const handleEdit = (row) => {
  dialogType.value = 'edit'
  dialogVisible.value = true
  // 填充表单
  Object.assign(formData, {
    id: row.id,
    name: row.name,
    url: row.url,
    username: row.username,
    token: row.token,
    is_active: row.is_active,
    description: row.description
  })
}

const handleDelete = (row) => {
  ElMessageBox.confirm(
    `确定要删除服务器 "${row.name}" 吗?`,
    '警告',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    }
  ).then(async () => {
    try {
      await deleteJenkinsServer(row.id)
      ElMessage.success('删除成功')
      fetchData()
    } catch (error) {
      console.error(error)
    }
  })
}

const handleTestConnection = async (row) => {
  row.testing = true
  try {
    const res = await testJenkinsConnection({
      url: row.url,
      username: row.username,
      token: row.token
    })
    
    if (res.status === 'success' || res.code === 200 || res.success) {
      ElMessage.success('连接成功!')
      fetchData()
    } else {
       ElMessage.error(res.message || '连接失败')
    }
  } catch (error) {
    ElMessage.error('连接测试失败')
  } finally {
    row.testing = false
  }
}

// 提交表单
const submitForm = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (valid) {
      submitting.value = true
      try {
        if (dialogType.value === 'add') {
          await addJenkinsServer(formData)
          ElMessage.success('添加成功')
        } else {
          await updateJenkinsServer(formData.id, formData)
          ElMessage.success('更新成功')
        }
        dialogVisible.value = false
        fetchData()
      } catch (error) {
        console.error(error)
      } finally {
        submitting.value = false
      }
    }
  })
}

const resetForm = () => {
  if (formRef.value) formRef.value.resetFields()
  Object.assign(formData, {
    id: undefined,
    name: '',
    url: '',
    username: '',
    token: '',
    is_active: true,
    description: ''
  })
}

onMounted(() => {
  fetchData()
})
</script>

<style scoped>
.app-container {
  padding: 20px;
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.title {
  font-weight: bold;
  font-size: 16px;
}
</style>
