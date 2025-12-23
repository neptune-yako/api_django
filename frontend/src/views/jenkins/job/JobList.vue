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
              @clear="fetchData"
              @keyup.enter="fetchData"
            >
              <template #append>
                <el-button @click="fetchData"><el-icon><Search /></el-icon></el-button>
              </template>
            </el-input>
            <el-button type="success" @click="handleSync" :loading="syncing">
              <el-icon class="el-icon--left"><Refresh /></el-icon>同步所有任务
            </el-button>
          </div>
        </div>
      </template>

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
        
        <el-table-column label="操作" width="220" fixed="right">
          <template #default="scope">
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

      <!-- 分页 (如果有需要，暂时不做) -->
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Refresh, VideoPlay } from '@element-plus/icons-vue'
import { 
  getJenkinsJobs, 
  syncJenkinsJobs, 
  buildJenkinsJob 
} from '@/api/jenkins'
import StatusTag from '../common/StatusTag.vue'
import { parseList } from '../utils/response-parser'
import { formatTime } from '../utils/formatters'

// 状态
const loading = ref(false)
const syncing = ref(false)
const tableData = ref([])
const searchKeyword = ref('')

// 获取数据
const fetchData = async () => {
  loading.value = true
  try {
    const params = {}
    if (searchKeyword.value) {
      params.name = searchKeyword.value
    }
    const res = await getJenkinsJobs(params)
    tableData.value = parseList(res)
  } catch (error) {
    console.error(error)
  } finally {
    loading.value = false
  }
}

// 同步任务
const handleSync = async () => {
  syncing.value = true
  try {
    const res = await syncJenkinsJobs()
    // 🔥 修复：正确访问响应数据
    ElMessage.success(res.data.message || '同步任务已在后台启动，请稍后刷新列表')
    // 延迟几秒后刷新一次
    setTimeout(() => {
      fetchData()
    }, 2000)
  } catch (error) {
    console.error(error)
  } finally {
    syncing.value = false
  }
}

// 手动刷新 (列表刷新)
const handleManualSync = () => {
  fetchData()
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
.right-actions {
  display: flex;
  align-items: center;
}
.job-name {
  font-weight: 500;
  color: #409EFF;
}
</style>
