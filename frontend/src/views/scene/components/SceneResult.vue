<template>
  <div class="container">
    <el-descriptions :column=4>
      <el-descriptions-item label="用例总数：">{{ results.all }}条</el-descriptions-item>
      <el-descriptions-item label="通过用例：">{{ results.success }}条</el-descriptions-item>
      <el-descriptions-item label="失败用例：">{{ results.fail }}条</el-descriptions-item>
      <el-descriptions-item label="错误用例：">{{ results.error }}条</el-descriptions-item>
    </el-descriptions>
    <el-table :data="results.cases" style="width: 100%" stripe :header-cell-style="{'text-align':'center'}"
              :cell-style="{'text-align':'center'}">
      <el-table-column type="expand">
        <template #default="props">
          <Result :result='props.row' :hideBtn="true"></Result>
        </template>
      </el-table-column>
      <el-table-column label="序号" type="index" width="80"/>
      <el-table-column label="用例名称" prop="name"/>
      <el-table-column label="请求方法" prop="method"/>
      <el-table-column label="状态码" prop="status_code"/>
      <el-table-column label="执行结果" prop="state">
        <template #default="scope">
          <span v-if="scope.row.state === '成功'" style="color: green;">成功</span>
          <span v-else-if="scope.row.state === '失败'" style="color: coral">失败</span>
          <span v-else style="color: red">错误</span>
        </template>
      </el-table-column>
    </el-table>
  </div>
  <div class="button">
    <el-button type="primary" @click="closeDrawer" plain>确定</el-button>
  </div>
</template>

<script setup>
import Result from '@/components/Result.vue'

const prop = defineProps({
  results: {
    type: Object,
    required: true,
    default: () => ({
      all: 0,
      success: 0,
      fail: 0,
      error: 0,
      cases: []
    })
  }
})

// 关闭窗口
const emit = defineEmits(['close'])
function closeDrawer() {
  emit('close')
}
</script>

<style lang="scss" scoped>
@use './sceneresult.scss';
</style>