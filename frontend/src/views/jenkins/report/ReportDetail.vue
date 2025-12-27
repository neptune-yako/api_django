<template>
  <div class="app-container">
    <el-card v-loading="loading">
      <template #header>
        <div class="card-header">
          <el-button type="text" @click="handleBack">
            <el-icon><ArrowLeft /></el-icon> 返回列表
          </el-button>
          <span class="card-title">{{ execution.report_title }}</span>
        </div>
      </template>

      <!-- 概览信息 -->
      <div class="overview-section">
        <el-row :gutter="20">
          <el-col :span="6">
            <el-statistic title="总用例数" :value="execution.total_cases" />
          </el-col>
          <el-col :span="6">
            <el-statistic title="通过用例" :value="execution.passed_cases">
              <template #suffix>
                <span style="color: #67c23a">/ {{ execution.total_cases }}</span>
              </template>
            </el-statistic>
          </el-col>
          <el-col :span="6">
            <el-statistic title="失败用例" :value="execution.failed_cases">
              <template #suffix>
                <span style="color: #f56c6c">/ {{ execution.total_cases }}</span>
              </template>
            </el-statistic>
          </el-col>
          <el-col :span="6">
            <el-statistic title="通过率">
              <template #default>
                <el-tag :type="execution.pass_rate >= 90 ? 'success' : execution.pass_rate >= 70 ? 'warning' : 'danger'" size="large">
                  {{ execution.pass_rate }}%
                </el-tag>
              </template>
            </el-statistic>
          </el-col>
        </el-row>

        <el-row :gutter="20" style="margin-top: 20px">
          <el-col :span="6">
            <div class="info-item">
              <span class="label">执行时长：</span>
              <span class="value">{{ execution.execution_time || '-' }}</span>
            </div>
          </el-col>
          <el-col :span="6">
            <div class="info-item">
              <span class="label">开始时间：</span>
              <span class="value">{{ formatDate(execution.start_time) }}</span>
            </div>
          </el-col>
          <el-col :span="6">
            <div class="info-item">
              <span class="label">结束时间：</span>
              <span class="value">{{ formatDate(execution.end_time) }}</span>
            </div>
          </el-col>
          <el-col :span="6">
            <div class="info-item">
              <span class="label">状态：</span>
              <el-tag :type="execution.status === 'success' ? 'success' : 'danger'">
                {{ execution.status === 'success' ? '成功' : '失败' }}
              </el-tag>
            </div>
          </el-col>
        </el-row>
      </div>

      <!-- Tab 页 -->
      <el-tabs v-model="activeTab" style="margin-top: 30px">
        <!-- 测试套件 -->
        <el-tab-pane label="测试套件" name="suites">
          <el-table :data="suites" style="width: 100%">
            <el-table-column prop="suite_name" label="套件名称" min-width="200" />
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
            <el-table-column prop="duration_seconds" label="执行时长(秒)" width="150" align="center" />
          </el-table>
        </el-tab-pane>

        <!-- 缺陷类别 -->
        <el-tab-pane label="缺陷类别" name="categories">
          <el-table :data="categories" style="width: 100%">
            <el-table-column prop="category_name" label="类别名称" min-width="200" />
            <el-table-column prop="count" label="数量" width="100" align="center" />
            <el-table-column prop="severity" label="严重程度" width="150" align="center">
              <template #default="{ row }">
                <el-tag :type="getSeverityType(row.severity)">
                  {{ getSeverityLabel(row.severity) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="description" label="描述" min-width="300" />
          </el-table>
        </el-tab-pane>

        <!-- 特性场景 -->
        <el-tab-pane label="特性场景" name="scenarios">
          <el-table :data="scenarios" style="width: 100%">
            <el-table-column prop="scenario_name" label="场景名称" min-width="200" />
            <el-table-column prop="total" label="总数" width="100" align="center" />
            <el-table-column prop="passed" label="通过" width="100" align="center">
              <template #default="{ row }">
                <span style="color: #67c23a">{{ row.passed }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="failed" label="失败" width="100" align="center">
              <template #default="{ row }">
                <span style="color: #f56c6c">{{ row.failed }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="pass_rate" label="通过率" width="120" align="center">
              <template #default="{ row }">
                <el-tag :type="row.pass_rate >= 90 ? 'success' : row.pass_rate >= 70 ? 'warning' : 'danger'">
                  {{ row.pass_rate }}%
                </el-tag>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ArrowLeft } from '@element-plus/icons-vue'
import { getExecutionDetail } from '@/api/testReport'

const route = useRoute()
const router = useRouter()

// 数据
const loading = ref(false)
const activeTab = ref('suites')
const execution = ref({})
const suites = ref([])
const categories = ref([])
const scenarios = ref([])

// 加载详情
const fetchDetail = async () => {
  loading.value = true
  try {
    const res = await getExecutionDetail(route.params.id)
    const data = res.data.data
    
    // DRF Serializer 返回的是扁平结构，不再有 execution 嵌套
    execution.value = data
    suites.value = data.suites || []
    categories.value = data.categories || []
    scenarios.value = data.scenarios || []
  } catch (error) {
    console.error(error)
  } finally {
    loading.value = false
  }
}

// 返回列表
const handleBack = () => {
  router.back()
}

// 格式化日期
const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString('zh-CN')
}

// 严重程度类型
const getSeverityType = (severity) => {
  const map = {
    critical: 'danger',
    major: 'warning',
    minor: 'info',
    trivial: ''
  }
  return map[severity] || 'info'
}

// 严重程度标签
const getSeverityLabel = (severity) => {
  const map = {
    critical: '严重',
    major: '重要',
    minor: '次要',
    trivial: '轻微'
  }
  return map[severity] || severity
}

onMounted(() => {
  fetchDetail()
})
</script>

<style scoped>
.card-header {
  display: flex;
  align-items: center;
  gap: 20px;
}

.card-title {
  font-size: 18px;
  font-weight: bold;
}

.overview-section {
  padding: 20px;
  background: #f5f7fa;
  border-radius: 4px;
}

.info-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.info-item .label {
  color: #909399;
  font-size: 14px;
}

.info-item .value {
  color: #303133;
  font-size: 14px;
  font-weight: 500;
}
</style>
