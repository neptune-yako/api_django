<template>
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
          <span class="label">执行时长:</span>
          <span class="value">{{ execution.execution_time || '-' }}</span>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="info-item">
          <span class="label">开始时间:</span>
          <span class="value">{{ formatDate(execution.start_time) }}</span>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="info-item">
          <span class="label">结束时间:</span>
          <span class="value">{{ formatDate(execution.end_time) }}</span>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="info-item">
          <span class="label">状态:</span>
          <el-tag :type="execution.status === 'success' ? 'success' : 'danger'">
            {{ execution.status === 'success' ? '成功' : '失败' }}
          </el-tag>
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
defineProps({
  execution: {
    type: Object,
    default: () => ({})
  }
})

const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString('zh-CN')
}
</script>

<style scoped>
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
