<template>
  <div class="app-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span class="title">Jenkins 任务管理</span>
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
            <el-button type="success" @click="handleSync" :loading="syncing">
              <el-icon class="el-icon--left"><Refresh /></el-icon>同步所有任务
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

        <el-form-item label="环境">
          <el-select 
            v-model="filters.environment" 
            placeholder="全部环境" 
            clearable
            style="width: 200px"
            @change="handleFilterChange"
          >
            <el-option
              v-for="env in environmentList"
              :key="env.id"
              :label="env.name"
              :value="env.id"
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
        <el-table-column prop="name" label="任务名称" min-width="200" show-overflow-tooltip>
          <template #default="scope">
            <span class="job-name">{{ scope.row.name }}</span>
            <el-tag v-if="scope.row.job_type" size="small" type="info" style="margin-left: 5px">
              {{ scope.row.job_type }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column prop="server_name" label="所属服务器" width="150" show-overflow-tooltip />
        
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
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Refresh, VideoPlay, Edit } from '@element-plus/icons-vue'
import { 
  getJenkinsJobs, 
  syncJenkinsJobs, 
  getTaskStatus,
  buildJenkinsJob 
} from '@/api/jenkins'
import { getJenkinsServers } from '@/api/jenkins'
import http from '@/api/index'
import StatusTag from '../common/StatusTag.vue'
import JobEdit from './JobEdit.vue'
import { parseList, parsePagination } from '../utils/response-parser'
import { formatTime } from '../utils/formatters'

// 状态
const loading = ref(false)
const syncing = ref(false)
const tableData = ref([])
const searchKeyword = ref('')

// 编辑对话框
const editDialogVisible = ref(false)
const currentJob = ref(null)

// 分页
const pagination = ref({
  page: 1,
  pageSize: 20,
  total: 0
})

// 筛选器
const filters = ref({
  server: null,
  project: null,
  environment: null
})

// 筛选器选项
const serverList = ref([])
const projectList = ref([])
const environmentList = ref([])

// 获取服务器列表
const fetchServerList = async () => {
  try {
    const res = await getJenkinsServers()
    serverList.value = parseList(res)
  } catch (error) {
    console.error('获取服务器列表失败:', error)
  }
}

// 获取项目列表
const fetchProjectList = async () => {
  try {
    const res = await http.projectApi.getProjectList({ page: 1, size: 100 })
    projectList.value = res.data.list || []
  } catch (error) {
    console.error('获取项目列表失败:', error)
  }
}

// 获取环境列表
const fetchEnvironmentList = async () => {
  try {
    // 从 Pinia store 获取当前项目
    const { ProjectStore } = await import('@/stores/module/ProStore')
    const pstore = ProjectStore()
    
    if (pstore.proList && pstore.proList.id) {
      const res = await http.environmentApi.getEnvironment(pstore.proList.id)
      environmentList.value = res.data || []
    } else {
      console.warn('未选择项目，无法加载环境列表')
      environmentList.value = []
    }
  } catch (error) {
    console.error('获取环境列表失败:', error)
    environmentList.value = []
  }
}

// 获取数据
const fetchData = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.value.page,
      page_size: pagination.value.pageSize
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
    if (filters.value.environment) {
      params.environment = filters.value.environment
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
    project: null,
    environment: null
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
  syncing.value = true
  try {
    const res = await syncJenkinsJobs()
    const taskId = res.data.data.task_id
    
    if (taskId) {
      ElMessage.info('同步任务已启动，正在后台执行...')
      pollTaskStatus(taskId)
    } else {
      ElMessage.warning('同步任务启动，但未返回任务ID')
    }
  } catch (error) {
    console.error(error)
    ElMessage.error('同步任务启动失败')
    syncing.value = false
  }
}

// 轮询任务状态
const pollTaskStatus = async (taskId) => {
  const poll = async () => {
    try {
      const res = await getTaskStatus(taskId)
      const status = res.data.data.status
      
      if (status === 'SUCCESS') {
        ElMessage.success('✅ Jenkins Job 同步完成，已自动刷新列表')
        syncing.value = false
        fetchData() // 刷新列表
      } else if (status === 'FAILURE') {
        const errorMsg = res.data.data.result || '未知错误'
        ElMessage.error(`❌ 同步失败: ${errorMsg}`)
        syncing.value = false
      } else {
        // 继续轮询 (PENDING, STARTED, RETRY)
        setTimeout(poll, 2000)
      }
    } catch (error) {
      console.error('查询任务状态失败:', error)
      syncing.value = false
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
    fetchServerList(),
    fetchProjectList(),
    fetchEnvironmentList()
  ])
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
</style>
