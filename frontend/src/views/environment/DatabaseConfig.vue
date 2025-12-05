<template>
  <div>
    <el-table :data="localConfigs" style="width: 100%" :header-cell-style="{'text-align':'center'}"
              :cell-style="{'text-align':'center'}" stripe>
      <template #empty>
        <div class="table-empty">
          <img src="@/assets/images/none.png" alt="notData" width="85"/>
          <div>暂无数据</div>
        </div>
      </template>
      <el-table-column prop="name" label="名称" width="120">
        <template #default="scope">
          <el-input v-model="scope.row.name" clearable placeholder="请输入名称"></el-input>
        </template>
      </el-table-column>
      <el-table-column prop="type" label="类型" width="130">
        <template #default="scope">
          <el-select v-model="scope.row.type" clearable placeholder="请选择数据库类型">
            <el-option label="mysql" value="mysql"></el-option>
            <el-option label="oracle" value="oracle"></el-option>
            <el-option label="sqlserver" value="sqlserver"></el-option>
          </el-select>
        </template>
      </el-table-column>
      <el-table-column prop="config.host" label="主机" width="180">
        <template #default="scope">
          <el-input v-model="scope.row.config.host" clearable placeholder="请输入数据库服务ip"></el-input>
        </template>
      </el-table-column>
      <el-table-column prop="config.port" label="端口" width="120">
        <template #default="scope">
          <el-input v-model.number="scope.row.config.port" type="number" clearable placeholder="请输入数据库端口"></el-input>
        </template>
      </el-table-column>
      <el-table-column prop="config.database" label="库名" width="120">
        <template #default="scope">
          <el-input v-model="scope.row.config.database" clearable placeholder="请输入数据库名称"></el-input>
        </template>
      </el-table-column>
      <el-table-column prop="config.user" label="用户" width="120">
        <template #default="scope">
          <el-input v-model="scope.row.config.user" clearable placeholder="请输入数据库用户名"></el-input>
        </template>
      </el-table-column>
      <el-table-column prop="config.password" label="密码" width="120">
        <template #default="scope">
          <el-input v-model="scope.row.config.password" type="password" clearable placeholder="请输入数据库密码"></el-input>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="120">
        <template #default="scope">
          <el-button @click="removeConfig(scope.$index)" plain type="danger" icon="Delete" size="small">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
    <el-button @click="addConfig" plain type="primary" icon="CirclePlus" size="small">添加</el-button>
  </div>
</template>

<script setup>
import {ref, watch} from 'vue'

const props = defineProps({
  configs: Array
})

const emit = defineEmits(['updateConfigs'])

const localConfigs = ref([...props.configs])

watch(localConfigs, (newVal) => {
  emit('updateConfigs', JSON.stringify(newVal, null, 2))
}, {deep: true})
watch(() => props.configs, (newConfigs) => {
  localConfigs.value = [...newConfigs]
}, {deep: true})
const addConfig = () => {
  localConfigs.value.push({
    name: 'aliyun',
    type: 'mysql',
    config: {
      host: '',
      port: 3306,
      user: '',
      password: '',
      database: ''
    }
  })
}

const removeConfig = (index) => {
  localConfigs.value.splice(index, 1)
}
</script>

<style scoped lang="scss">
.el-table {
  margin-bottom: 20px;
}
</style>
