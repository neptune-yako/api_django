<template>
  <div class="app-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span class="card-title">测试报告列表</span>
          <div class="header-actions">
            <el-button type="primary" @click="handleBatchSync">
              <el-icon class="el-icon--left"><Upload /></el-icon>批量同步
            </el-button>
          </div>
        </div>
      </template>

      <!-- 筛选条件 -->
      <div class="filter-container">
        <el-select
          v-model="filters.serverId"
          placeholder="选择 Server"
          clearable
          style="width: 200px; margin-right: 10px"
          @change="handleServerChange"
        >
          <el-option
            v-for="server in serverList"
            :key="server.id"
            :label="server.name"
            :value="server.id"
          />
        </el-select>
        <el-select
          v-model="filters.jobId"
          placeholder="选择 Job"
          clearable
          :disabled="!filters.serverId"
          style="width: 200px; margin-right: 10px"
          @change="handleJobChange"
        >
          <el-option
            v-for="job in jobList"
            :key="job.id"
            :label="job.name"
            :value="job.id"
          />
        </el-select>
        <el-date-picker
          v-model="dateRange"
          type="daterange"
          range-separator="至"
          start-placeholder="开始日期"
          end-placeholder="结束日期"
          style="margin-right: 10px"
          @change="handleDateChange"
        />
        <el-button type="primary" @click="handleSearch">查询</el-button>
        <el-button @click="handleReset">重置</el-button>
      </div>

      <!-- 表格 -->
      <el-table
        :data="tableData"
        v-loading="loading"
        style="width: 100%; margin-top: 20px"
      >
        <el-table-column prop="report_title" label="报告标题" min-width="200" />
        <el-table-column prop="job_name" label="Job 名称" width="180" />
        <el-table-column prop="total_cases" label="总用例" width="100" align="center" />
        <el-table-column prop="passed_cases" label="通过" width="100" align="center">
          <template #default="{ row }">
            <span style="color: #67c23a">{{ row.passed_cases }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="failed_cases" label="失败" width="100" align="center">
          <template #default="{ row }">
            <span style="color: #f56c6c">{{ row.failed_cases }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="pass_rate" label="通过率" width="120" align="center">
          <template #default="{ row }">
            <el-tag :type="row.pass_rate >= 90 ? 'success' : row.pass_rate >= 70 ? 'warning' : 'danger'">
              {{ row.pass_rate }}%
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="execution_time" label="执行时长" width="150" />
        <el-table-column prop="status" label="状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="row.status === 'success' ? 'success' : 'danger'">
              {{ row.status === 'success' ? '成功' : '失败' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180">
          <template #default="{ row }">
            {{ formatTime(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="120" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="handleViewDetail(row.id)">
              查看详情
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

    <!-- 批量同步对话框 -->
    <el-dialog v-model="syncDialogVisible" title="批量同步测试报告" width="500px">
      <el-form :model="syncForm" label-width="100px">
        <el-form-item label="Server">
          <el-select 
            v-model="syncForm.serverId" 
            placeholder="请选择 Server"
            @change="handleSyncServerChange"
          >
            <el-option
              v-for="server in serverList"
              :key="server.id"
              :label="server.name"
              :value="server.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="Job 名称">
          <el-select 
            v-model="syncForm.jobName" 
            placeholder="请选择 Job"
            :disabled="!syncForm.serverId"
          >
            <el-option
              v-for="job in syncJobList"
              :key="job.id"
              :label="job.name"
              :value="job.name"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="起始构建号">
          <el-input-number v-model="syncForm.startBuild" :min="1" />
        </el-form-item>
        <el-form-item label="结束构建号">
          <el-input-number v-model="syncForm.endBuild" :min="1" />
          <span style="color: #909399; font-size: 12px; margin-left: 10px">
            留空则同步到最新
          </span>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="syncDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleConfirmSync" :loading="syncing">
          开始同步
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { Upload } from '@element-plus/icons-vue'
import { useRouter } from 'vue-router'
import { getExecutionList, syncJobBuilds, getTaskStatus } from '@/api/testReport'
import { getJenkinsServers, getJenkinsJobs } from '@/api/jenkins'
import { parseList, parsePagination } from '../utils/response-parser'
import { formatTime } from '../utils/formatters'

const router = useRouter()

// 数据
const loading = ref(false)
const syncing = ref(false)
const tableData = ref([])
const serverList = ref([])
const jobList = ref([])
const syncJobList = ref([])
const syncDialogVisible = ref(false)

// 筛选条件
const filters = ref({
  serverId: null,
  jobId: null
})
const dateRange = ref([])

// 分页
const pagination = ref({
  page: 1,
  pageSize: 20,
  total: 0
})

// 同步表单
const syncForm = ref({
  serverId: null,
  jobName: '',
  startBuild: 1,
  endBuild: null
})

// 加载 Server 列表
const fetchServers = async () => {
  try {
    const res = await getJenkinsServers({ page: 1, size: 100 })
    serverList.value = parseList(res)
    
    // 默认选中第一个 Server
    if (serverList.value.length > 0) {
      filters.value.serverId = serverList.value[0].id
      await fetchJobs(filters.value.serverId)
      await fetchData()
    }
  } catch (error) {
    console.error('加载 Server 列表失败:', error)
  }
}

// 加载 Job 列表（根据 Server）
const fetchJobs = async (serverId) => {
  if (!serverId) {
    jobList.value = []
    return
  }
  
  try {
    const res = await getJenkinsJobs({ server: serverId, page: 1, size: 100 })
    jobList.value = parseList(res)
  } catch (error) {
    console.error('加载 Job 列表失败:', error)
    jobList.value = []
  }
}

// 加载同步对话框的 Job 列表
const fetchSyncJobs = async (serverId) => {
  if (!serverId) {
    syncJobList.value = []
    return
  }
  
  try {
    const res = await getJenkinsJobs({ server: serverId, page: 1, size: 100 })
    syncJobList.value = parseList(res)
  } catch (error) {
    console.error('加载 Job 列表失败:', error)
    syncJobList.value = []
  }
}

// Server 切换事件
const handleServerChange = async (serverId) => {
  filters.value.jobId = null  // 清空 Job 选择
  await fetchJobs(serverId)
  await fetchData()
}

// 同步对话框 Server 切换事件
const handleSyncServerChange = async (serverId) => {
  syncForm.value.jobName = ''  // 清空 Job 选择
  await fetchSyncJobs(serverId)
}

// Job 切换事件
const handleJobChange = () => {
  pagination.value.page = 1  // 重置到第一页
  fetchData()
}

// 日期切换事件
const handleDateChange = () => {
  pagination.value.page = 1  // 重置到第一页
  fetchData()
}

// 加载数据
const fetchData = async () => {
  loading.value = true
  try {
    // 调试日志
    console.log('[ReportList] filters:', filters.value)
    console.log('[ReportList] jobId:', filters.value.jobId)
    console.log('[ReportList] dateRange:', dateRange.value)
    
    // 格式化日期为 YYYY-MM-DD
    const formatDate = (date) => {
      if (!date) return undefined
      const d = new Date(date)
      const year = d.getFullYear()
      const month = String(d.getMonth() + 1).padStart(2, '0')
      const day = String(d.getDate()).padStart(2, '0')
      return `${year}-${month}-${day}`
    }
    
    const params = {
      page: pagination.value.page,
      size: pagination.value.pageSize,
      server_id: filters.value.serverId || undefined,
      job_id: filters.value.jobId || undefined,
      start_date: formatDate(dateRange.value?.[0]),
      end_date: formatDate(dateRange.value?.[1])
    }
    
    console.log('[ReportList] API params:', params)
    
    const res = await getExecutionList(params)
    tableData.value = parseList(res)
    
    const paginationData = parsePagination(res)
    if (paginationData) {
      pagination.value.total = paginationData.total
    }
  } catch (error) {
    console.error('加载数据失败:', error)
    tableData.value = []
    pagination.value.total = 0
  } finally {
    loading.value = false
  }
}

// 查询
const handleSearch = () => {
  pagination.value.page = 1
  fetchData()
}

// 重置
const handleReset = () => {
  filters.value.jobId = null
  dateRange.value = []
  pagination.value.page = 1
  fetchData()
}

// 分页
const handleSizeChange = () => {
  fetchData()
}

const handlePageChange = () => {
  fetchData()
}

// 批量同步
const handleBatchSync = () => {
  syncForm.value.serverId = filters.value.serverId  // 默认使用当前选中的 Server
  if (syncForm.value.serverId) {
    fetchSyncJobs(syncForm.value.serverId)
  }
  syncDialogVisible.value = true
}

const handleConfirmSync = async () => {
  if (!syncForm.value.serverId) {
    ElMessage.warning('请选择 Server')
    return
  }
  if (!syncForm.value.jobName) {
    ElMessage.warning('请选择 Job')
    return
  }
  
  syncing.value = true
  try {
    const res = await syncJobBuilds({
      job_name: syncForm.value.jobName,
      start_build: syncForm.value.startBuild,
      end_build: syncForm.value.endBuild || undefined
    })
    
    const taskId = res.data.data.task_id
    ElMessage.success('批量同步任务已启动')
    syncDialogVisible.value = false
    
    // 轮询任务状态
    pollTaskStatus(taskId)
  } catch (error) {
    console.error('启动同步任务失败:', error)
  } finally {
    syncing.value = false
  }
}

// 轮询任务状态
const pollTaskStatus = (taskId) => {
  const interval = setInterval(async () => {
    try {
      const res = await getTaskStatus(taskId)
      const data = res.data.data
      
      if (data.status === 'SUCCESS') {
        clearInterval(interval)
        ElMessage.success(`同步完成！成功 ${data.success_count} 条，失败 ${data.failed_count} 条`)
        fetchData() // 刷新列表
      } else if (data.status === 'FAILURE') {
        clearInterval(interval)
        ElMessage.error(`同步失败: ${data.error}`)
      }
    } catch (error) {
      clearInterval(interval)
      console.error('查询任务状态失败:', error)
    }
  }, 2000)
}

// 查看详情
const handleViewDetail = (id) => {
  router.push({ name: 'ReportDetail', params: { id } })
}

onMounted(() => {
  fetchServers()
})
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-title {
  font-size: 18px;
  font-weight: bold;
}

.filter-container {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 10px;
}
</style>
