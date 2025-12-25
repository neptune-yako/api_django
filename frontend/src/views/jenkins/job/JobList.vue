<template>
  <div class="app-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <div class="left-actions">
            <span class="title">Jenkins 任务管理</span>
          </div>
          <div class="right-actions">
            <el-input
              v-model="searchKeyword"
              placeholder="搜索任务名称"
              style="width: 200px; margin-right: 10px"
              clearable
              @clear="handleSearch"
              @keyup.enter="handleSearch"
            >
              <template #append>
                <el-button @click="handleSearch"><el-icon><Search /></el-icon></el-button>
              </template>
            </el-input>
          
          <!-- 同步操作组 -->
          <div class="sync-group">
            <span class="sync-label">同步来源:</span>
            <el-select
              v-model="selectedServerId"
              placeholder="选择服务器"
              style="width: 180px"
              :disabled="syncing"
            >
              <el-option
                v-for="server in serverList"
                :key="server.id"
                :label="server.name"
                :value="server.id"
                :disabled="server.connection_status !== 'connected'"
              >
                <span :style="{ color: server.connection_status === 'connected' ? '#67C23A' : '#909399' }">
                  {{ server.name }}
                  <el-tag 
                    v-if="server.connection_status === 'failed'" 
                    type="danger" 
                    size="small"
                    style="margin-left: 8px"
                  >
                    连接失败
                  </el-tag>
                </span>
              </el-option>
            </el-select>
            <el-button 
              type="success" 
              @click="handleSync" 
              :loading="syncing"
              :disabled="!selectedServerId"
            >
              <el-icon class="el-icon--left"><Refresh /></el-icon>同步 Jobs
            </el-button>
            <el-button 
              type="warning" 
              @click="handleCleanup" 
              :loading="cleaning"
              :disabled="!selectedServerId"
            >
              <el-icon class="el-icon--left"><Delete /></el-icon>清理失效 Jobs
            </el-button>
          </div>
            <el-button type="primary" @click="handleCreate">
              <el-icon class="el-icon--left"><Plus /></el-icon>创建 Job
            </el-button>
          </div>
        </div>
      </template>

      <!-- 筛选器 -->
      <el-form :inline="true" class="filter-form">
        <el-form-item label="服务器">
          <el-select 
            v-model="filters.server" 
            placeholder="全部服务器" 
            clearable
            style="width: 200px"
            @change="handleFilterChange"
          >
            <el-option
              v-for="server in serverList"
              :key="server.id"
              :label="server.name"
              :value="server.id"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="项目">
          <el-select 
            v-model="filters.project" 
            placeholder="全部项目" 
            clearable
            style="width: 200px"
            @change="handleFilterChange"
          >
            <el-option
              v-for="project in projectList"
              :key="project.id"
              :label="project.name"
              :value="project.id"
            />
          </el-select>
        </el-form-item>

        <el-form-item>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>

      <el-table 
        v-loading="loading" 
        :data="tableData" 
        style="width: 100%" 
        border
      >
        <el-table-column prop="name" label="任务名称" min-width="180" show-overflow-tooltip>
          <template #default="scope">
            <span class="job-name">{{ scope.row.name }}</span>
          </template>
        </el-table-column>
        
        <el-table-column prop="job_type" label="类型" width="120">
          <template #default="scope">
            <el-tag 
              v-if="scope.row.job_type" 
              :type="getJobTypeTagType(scope.row.job_type)" 
              size="small"
            >
              {{ scope.row.job_type }}
            </el-tag>
            <span v-else style="color: #909399">-</span>
          </template>
        </el-table-column>
        
        <el-table-column prop="server_name" label="所属服务器" width="150" show-overflow-tooltip />
        
        <el-table-column prop="environment_names" label="测试环境" width="200">
          <template #default="scope">
            <div v-if="scope.row.environment_names && scope.row.environment_names.length > 0">
              <el-tag 
                v-for="(envName, index) in scope.row.environment_names" 
                :key="index"
                size="small"
                style="margin: 2px"
              >
                {{ envName }}
              </el-tag>
            </div>
            <span v-else style="color: #909399">-</span>
          </template>
        </el-table-column>
        
        <el-table-column label="执行节点" width="150">
          <template #default="scope">
            <span v-if="scope.row.target_node_name">
              {{ scope.row.target_node_name }}
            </span>
            <span v-else style="color: #909399;">any</span>
          </template>
        </el-table-column>
        
        <el-table-column prop="last_build_status" label="最后构建状态" width="150">
          <template #default="scope">
            <StatusTag :status="scope.row.last_build_status" type="build" />
            <span v-if="scope.row.last_build_number" :style="{ marginLeft: '5px', fontSize: '12px', color: '#909399' }">
              #{{ scope.row.last_build_number }}
            </span>
          </template>
        </el-table-column>
        
        <el-table-column prop="last_build_time" label="最后构建时间" width="180">
          <template #default="scope">
            {{ formatTime(scope.row.last_build_time) }}
          </template>
        </el-table-column>
        
        <el-table-column label="操作" width="280" fixed="right">
          <template #default="scope">
            <el-button 
              size="small" 
              type="primary" 
              link
              @click="handleEdit(scope.row)"
            >
              <el-icon><Edit /></el-icon> 编辑
            </el-button>
            <el-divider direction="vertical" />
            <el-button 
              size="small" 
              type="primary" 
              link
              @click="handleBuild(scope.row)"
              :disabled="!scope.row.is_buildable"
            >
              <el-icon><VideoPlay /></el-icon> 构建
            </el-button>
            <el-divider direction="vertical" />
            <el-button 
              size="small" 
              type="primary" 
              link
              @click="handleManualSync"
            >
              刷新
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.pageSize"
        :page-sizes="[10, 20, 50, 100]"
        :total="pagination.total"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="handleSizeChange"
        @current-change="handlePageChange"
        style="margin-top: 20px; justify-content: flex-end"
      />
    </el-card>
    
    <!-- 编辑对话框 -->
    <JobEdit
      v-model:visible="editDialogVisible"
      :job-data="currentJob"
      @success="handleEditSuccess"
    />
    
    <!-- 创建对话框 -->
    <JobCreate
      v-model:visible="createDialogVisible"
      @success="handleCreateSuccess"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Refresh, VideoPlay, Edit, Plus, Delete } from '@element-plus/icons-vue'
import { 
  getJenkinsJobs, 
  syncJenkinsJobs,
  cleanupJenkinsJobs,
  getTaskStatus,
  buildJenkinsJob 
} from '@/api/jenkins'
import { useJobFormOptions } from '@/composables/useJobFormOptions'
import http from '@/api/index'
import StatusTag from '../common/StatusTag.vue'
import JobEdit from './JobEdit.vue'
import JobCreate from './JobCreate.vue'
import { parseList, parsePagination } from '../utils/response-parser'
import { formatTime } from '../utils/formatters'

// Job 类型标签颜色映射
const getJobTypeTagType = (jobType) => {
  const typeMap = {
    'FreeStyle': 'primary',
    'Pipeline': 'success',
    'Maven': 'warning'
  }
  return typeMap[jobType] || 'info'
}
// 状态
const loading = ref(false)
const syncing = ref(false)
const cleaning = ref(false)  // 清理状态
const selectedServerId = ref(null)  // 选中的服务器ID
const tableData = ref([])
const searchKeyword = ref('')

// 编辑对话框
const editDialogVisible = ref(false)
const currentJob = ref(null)

// 创建对话框
const createDialogVisible = ref(false)

// 分页
const pagination = ref({
  page: 1,
  pageSize: 20,
  total: 0
})

// 筛选器
const filters = ref({
  server: null,
  project: null
})

// 使用 composable 获取筛选选项
const {
  serverList,
  projectList,
  loadServers,
  loadProjects
} = useJobFormOptions()

// 获取数据
const fetchData = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.value.page,
      size: pagination.value.pageSize  // 后端 MyPaginator 使用 'size' 参数
    }
    
    // 搜索关键词
    if (searchKeyword.value) {
      params.name = searchKeyword.value
    }
    
    // 筛选条件
    if (filters.value.server) {
      params.server = filters.value.server
    }
    if (filters.value.project) {
      params.project = filters.value.project
    }
    
    console.log('🔍 请求参数:', params)
    const res = await getJenkinsJobs(params)
    console.log('📦 响应数据:', res)
    
    tableData.value = parseList(res)
    console.log('✅ 解析后的表格数据:', tableData.value.length, '条')
    
    // 解析分页信息
    const paginationData = parsePagination(res)
    if (paginationData) {
      pagination.value.total = paginationData.total
      console.log('📊 分页信息 - 总数:', paginationData.total)
    }
  } catch (error) {
    console.error('❌ 获取数据失败:', error)
  } finally {
    loading.value = false
  }
}

// 搜索处理
const handleSearch = () => {
  pagination.value.page = 1  // 重置到第一页
  fetchData()
}

// 筛选器变化
const handleFilterChange = () => {
  console.log('筛选器变化:', filters.value)
  pagination.value.page = 1  // 重置到第一页
  fetchData()
}

// 重置筛选
const handleReset = () => {
  searchKeyword.value = ''
  filters.value = {
    server: null,
    project: null
  }
  pagination.value.page = 1
  fetchData()
}

// 分页大小变化
const handleSizeChange = (newSize) => {
  pagination.value.pageSize = newSize
  pagination.value.page = 1  // 重置到第一页
  fetchData()
}

// 页码变化
const handlePageChange = (newPage) => {
  pagination.value.page = newPage
  fetchData()
}

// 同步任务
const handleSync = async () => {
  // 校验是否选择了服务器
  if (!selectedServerId.value) {
    ElMessage.warning('请先选择要同步的 Jenkins 服务器')
    return
  }
  
  // 查找选中的服务器对象
  const selectedServer = serverList.value.find(s => s.id === selectedServerId.value)
  
  // 二次校验连接状态
  if (selectedServer && selectedServer.connection_status !== 'connected') {
    ElMessageBox.alert(
      `服务器 "${selectedServer.name}" 连接状态为 ${selectedServer.connection_status},请先前往服务器管理页面测试连接`,
      '无法同步',
      {
        confirmButtonText: '知道了',
        type: 'warning'
      }
    )
    return
  }
  
  syncing.value = true
  try {
    // 传递 server_id 参数
    const res = await syncJenkinsJobs({ server_id: selectedServerId.value })
    const taskId = res.data.data.task_id
    
    if (taskId) {
      const serverName = selectedServer?.name || '选中的服务器'
      ElMessage.info(`正在从 "${serverName}" 同步任务...`)
      pollTaskStatus(taskId)
    } else {
      ElMessage.warning('同步任务启动,但未返回任务ID')
    }
  } catch (error) {
    console.error(error)
    // 错误已由拦截器处理
    syncing.value = false
  }
}

// 清理失效任务
const handleCleanup = async () => {
  // 校验是否选择了服务器
  if (!selectedServerId.value) {
    ElMessage.warning('请先选择要清理的 Jenkins 服务器')
    return
  }
  
  // 查找选中的服务器对象
  const selectedServer = serverList.value.find(s => s.id === selectedServerId.value)
  
  // 二次校验连接状态
  if (selectedServer && selectedServer.connection_status !== 'connected') {
    ElMessageBox.alert(
      `服务器 "${selectedServer.name}" 连接状态为 ${selectedServer.connection_status},请先前往服务器管理页面测试连接`,
      '无法清理',
      {
        confirmButtonText: '知道了',
        type: 'warning'
      }
    )
    return
  }
  
  // 弹出确认对话框（重要！）
  try {
    await ElMessageBox.confirm(
      `确定要清理服务器 "${selectedServer.name}" 的失效任务吗？\n\n此操作将删除本地数据库中存在，但 Jenkins 服务器上已不存在的所有任务。\n\n⚠️ 此操作不可恢复！`,
      '确认清理',
      {
        confirmButtonText: '确定清理',
        cancelButtonText: '取消',
        type: 'warning',
        dangerouslyUseHTMLString: false
      }
    )
  } catch {
    // 用户取消操作
    return
  }
  
  // 用户确认后，开始清理
  cleaning.value = true
  try {
    const res = await cleanupJenkinsJobs({ server_id: selectedServerId.value })
    const taskId = res.data.data.task_id
    
    if (taskId) {
      const serverName = selectedServer?.name || '选中的服务器'
      ElMessage.info(`正在清理 "${serverName}" 的失效任务...`)
      pollTaskStatus(taskId, 'cleanup')  // 传递 'cleanup' 标识
    } else {
      ElMessage.warning('清理任务启动,但未返回任务ID')
      cleaning.value = false
    }
  } catch (error) {
    console.error(error)
    // 错误已由拦截器处理
    cleaning.value = false
  }
}


// 轮询任务状态
const pollTaskStatus = async (taskId, taskType = 'sync') => {
  const poll = async () => {
    try {
      const res = await getTaskStatus(taskId)
      const status = res.data.data.status
      
      if (status === 'SUCCESS') {
        const successMsg = taskType === 'cleanup' 
          ? '✅ Jenkins Job 清理完成，已自动刷新列表'
          : '✅ Jenkins Job 同步完成，已自动刷新列表'
        ElMessage.success(successMsg)
        if (taskType === 'cleanup') {
          cleaning.value = false
        } else {
          syncing.value = false
        }
        fetchData() // 刷新列表
      } else if (status === 'FAILURE') {
        const errorMsg = res.data.data.result || '未知错误'
        const failMsg = taskType === 'cleanup'
          ? `❌ 清理失败: ${errorMsg}`
          : `❌ 同步失败: ${errorMsg}`
        ElMessage.error(failMsg)
        if (taskType === 'cleanup') {
          cleaning.value = false
        } else {
          syncing.value = false
        }
      } else {
        // 继续轮询 (PENDING, STARTED, RETRY)
        setTimeout(poll, 2000)
      }
    } catch (error) {
      console.error('查询任务状态失败:', error)
      if (taskType === 'cleanup') {
        cleaning.value = false
      } else {
        syncing.value = false
      }
    }
  }
  
  // 开始第一次轮询
  poll()
}

// 手动刷新 (列表刷新)
const handleManualSync = () => {
  fetchData()
}

// 编辑 Job
const handleEdit = (row) => {
  currentJob.value = row
  editDialogVisible.value = true
}

// 编辑成功回调
const handleEditSuccess = () => {
  fetchData()  // 刷新列表
}

// 创建
const handleCreate = () => {
  createDialogVisible.value = true
}

const handleCreateSuccess = () => {
  createDialogVisible.value = false
  fetchData()
  ElMessage.success('创建成功，已刷新列表')
}

// 触发构建
const handleBuild = (row) => {
  ElMessageBox.confirm(
    `确定要触发任务 "${row.name}" 的构建吗?`,
    '确认构建',
    {
      confirmButtonText: '立即构建',
      cancelButtonText: '取消',
      type: 'info',
    }
  ).then(async () => {
    try {
      // 🔥 修复：使用正确的参数格式
      // 后端 JenkinsJobBuildView 需要 job_name 参数
      // Jenkins Job 名称在同一个服务器内是唯一的
      const res = await buildJenkinsJob({
        job_name: row.name,
        // 如果需要参数化构建，可以在这里添加 parameters 字段
        // parameters: { BRANCH: 'master' }
      })
      
      // 🔥 修复：正确访问响应数据并处理成功/失败
      if (res.data.code === 200) {
        ElMessage.success(res.data.message || '构建已触发')
        // 稍后刷新状态
        setTimeout(() => {
          fetchData()
        }, 3000)
      } else {
        ElMessage.error(res.data.message || '构建触发失败')
      }
    } catch (error) {
      console.error('构建触发失败:', error)
      ElMessage.error('构建触发失败')
    }
  }).catch(() => {
    // 用户取消操作
  })
}


onMounted(async () => {
  // 并行加载筛选器选项和数据
  await Promise.all([
    loadServers(),
    loadProjects()
  ])
  
  // 默认选择第一个 connected 的服务器
  const connectedServer = serverList.value.find(s => s.connection_status === 'connected')
  if (connectedServer) {
    selectedServerId.value = connectedServer.id
  }
  
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
.right-actions {
  display: flex;
  align-items: center;
}
.job-name {
  font-weight: 500;
  color: #409EFF;
}
.filter-form {
  margin-bottom: 16px;
  padding: 16px;
  background-color: #f5f7fa;
  border-radius: 4px;
}

/* 同步操作组样式 */
.sync-group {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  padding: 6px 12px;
  background: #f0f9ff;
  border: 1px solid #91d5ff;
  border-radius: 4px;
  margin-right: 10px;
}

.sync-label {
  font-size: 14px;
  color: #606266;
  white-space: nowrap;
}

</style>
