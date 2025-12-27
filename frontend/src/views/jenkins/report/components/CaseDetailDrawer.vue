<template>
  <el-drawer
    :model-value="visible"
    :title="caseData.name"
    direction="rtl"
    size="40%"
    @update:model-value="handleClose"
  >
    <div v-if="caseData.name" class="case-detail">
      <!-- 状态头部 -->
      <div class="detail-header">
        <el-tag :type="getStatusType(caseData.status)" size="large">
          {{ getStatusLabel(caseData.status) }}
        </el-tag>
      </div>
      
      <!-- 基本信息 -->
      <el-descriptions title="基本信息" :column="1" border style="margin-top: 20px">
        <el-descriptions-item label="测试类">{{ caseData.test_class || '-' }}</el-descriptions-item>
        <el-descriptions-item label="测试方法">{{ caseData.test_method || '-' }}</el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="getStatusType(caseData.status)">
            {{ getStatusLabel(caseData.status) }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="耗时">
          {{ (caseData.duration_in_ms / 1000).toFixed(2) }}s
        </el-descriptions-item>
        <el-descriptions-item label="开始时间">
          {{ formatTimestamp(caseData.start_time) }}
        </el-descriptions-item>
        <el-descriptions-item label="结束时间">
          {{ formatTimestamp(caseData.stop_time) }}
        </el-descriptions-item>
      </el-descriptions>
      
      <!-- 描述 -->
      <div v-if="caseData.description" style="margin-top: 20px">
        <h4>描述</h4>
        <el-card shadow="never">
          {{ caseData.description }}
        </el-card>
      </div>
      
      <!-- 层级路径 -->
      <div style="margin-top: 20px">
        <h4>层级路径</h4>
        <el-breadcrumb separator="→">
          <el-breadcrumb-item v-if="caseData.parent_suite">{{ caseData.parent_suite }}</el-breadcrumb-item>
          <el-breadcrumb-item v-if="caseData.suite">{{ caseData.suite }}</el-breadcrumb-item>
          <el-breadcrumb-item v-if="caseData.sub_suite">{{ caseData.sub_suite }}</el-breadcrumb-item>
        </el-breadcrumb>
      </div>
    </div>
  </el-drawer>
</template>

<script setup>
defineProps({
  visible: {
    type: Boolean,
    default: false
  },
  caseData: {
    type: Object,
    default: () => ({})
  }
})

const emit = defineEmits(['update:visible'])

const handleClose = (value) => {
  emit('update:visible', value)
}

// 状态类型映射
const getStatusType = (status) => {
  const map = {
    passed: 'success',
    failed: 'danger',
    skipped: 'warning',
    broken: 'danger',
    unknown: 'info'
  }
  return map[status] || 'info'
}

// 状态标签映射
const getStatusLabel = (status) => {
  const map = {
    passed: '✓ 通过',
    failed: '✗ 失败',
    skipped: '⏸ 跳过',
    broken: '⚠ 中断',
    unknown: '? 未知'
  }
  return map[status] || status
}

// 格式化时间戳
const formatTimestamp = (timestamp) => {
  if (!timestamp) return '-'
  // 如果是毫秒时间戳
  if (timestamp.length > 10) {
    return new Date(parseInt(timestamp)).toLocaleString('zh-CN')
  }
  // 如果是秒级时间戳
  return new Date(parseInt(timestamp) * 1000).toLocaleString('zh-CN')
}
</script>

<style scoped>
.case-detail {
  padding: 20px;
}

.detail-header {
  text-align: center;
  padding: 10px 0;
}

.case-detail h4 {
  margin: 10px 0;
  color: #303133;
}
</style>
