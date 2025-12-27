<template>
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
    <el-table-column label="操作" width="120" align="center">
      <template #default="{ row }">
        <el-button type="primary" size="small" @click="handleViewCases(row)">
          查看用例
        </el-button>
      </template>
    </el-table-column>
  </el-table>
</template>

<script setup>
defineProps({
  suites: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['view-cases'])

const handleViewCases = (suite) => {
  emit('view-cases', suite)
}
</script>
