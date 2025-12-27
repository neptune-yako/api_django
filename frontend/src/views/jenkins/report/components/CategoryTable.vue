<template>
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
</template>

<script setup>
defineProps({
  categories: {
    type: Array,
    default: () => []
  }
})

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
</script>
