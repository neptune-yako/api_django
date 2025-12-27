<template>
  <div class="case-list">
    <el-divider>
      <span style="font-weight: bold">{{ suiteName }} - 用例列表 (共 {{ cases.length }} 条)</span>
    </el-divider>
    <el-table :data="cases" style="width: 100%" v-loading="loading">
      <el-table-column prop="name" label="用例名称" min-width="250">
        <template #default="{ row }">
          <el-button type="text" @click="handleViewDetail(row)">
            {{ row.name }}
          </el-button>
        </template>
      </el-table-column>
      <el-table-column prop="status" label="状态" width="100" align="center">
        <template #default="{ row }">
          <el-tag :type="getStatusType(row.status)" size="small">
            {{ getStatusLabel(row.status) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="test_class" label="测试类" width="200" />
      <el-table-column prop="test_method" label="测试方法" width="200" />
      <el-table-column prop="duration_in_ms" label="耗时" width="120" align="center">
        <template #default="{ row }">
          {{ (row.duration_in_ms / 1000).toFixed(2) }}s
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script setup>
defineProps({
  cases: {
    type: Array,
    default: () => []
  },
  suiteName: {
    type: String,
    default: ''
  },
  loading: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['view-detail'])

const handleViewDetail = (caseItem) => {
  emit('view-detail', caseItem)
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
</script>

<style scoped>
.case-list {
  margin-top: 20px;
}
</style>
