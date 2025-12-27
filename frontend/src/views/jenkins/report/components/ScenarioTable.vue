<template>
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
</template>

<script setup>
defineProps({
  scenarios: {
    type: Array,
    default: () => []
  }
})
</script>
