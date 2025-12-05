<template>
  <div class="main_box">
    <!-- 左侧 -->
    <div class="card left_box">
      <!-- 顶部标题 -->
      <div class="title_box">
        <img src="@/assets/icons/environment.png" width="25" alt="">
        <div class="name">测试环境</div>
        <el-button @click='addEnv' type="primary" size="small" icon='CirclePlus' plain>环境</el-button>
        <el-button plain @click='getEvnList' type="success" icon="Refresh" size="small">刷新</el-button>
      </div>
      <!-- 环境列表 -->
      <el-menu :default-active="EnvInfo.id+''">
        <el-menu-item @click='selectEnv(item)' :index="item.id.toString()" v-for='item in envList' key="item.id">
          <img src="@/assets/icons/environment.png" width="20" style="margin-right: 10px;" alt="">
          <span v-if='item.name.length < 15'>{{ item.name }}</span>
          <span v-else>{{ item.name.slice(0, 15) }}...</span>
        </el-menu-item>
      </el-menu>
    </div>

    <!-- 中间 -->
    <div class="card center_box">
      <el-divider content-position="center"><b>基本信息</b></el-divider>
      <el-input v-model="env_name" placeholder="请输入环境名称" clearable>
        <template #prepend>测试环境名称</template>
      </el-input>
      <el-input v-model="env_host" placeholder="请输入base_url" style="margin-top: 5px;" clearable>
        <template #prepend>服务器域名/IP</template>
      </el-input>
      <el-divider content-position="center"><b>请求头/数据库</b></el-divider>
      <el-tabs type="border-card" stretch>
        <el-tab-pane label="全局请求头">
          <Editor lang="json" v-model="env_headers"></Editor>
        </el-tab-pane>
        <el-tab-pane label="数据库">
          <DatabaseConfig :configs="parsedConfigs" @updateConfigs="handleUpdateConfigs"/>
        </el-tab-pane>
      </el-tabs>
      <el-divider content-position="center"><b>全局变量</b></el-divider>
      <el-tabs type="border-card" stretch>
        <el-tab-pane label="全局变量">
          <Editor lang="json" v-model="env_global_variable"></Editor>
        </el-tab-pane>
        <el-tab-pane label="调试全局变量">
          <Editor lang="json" v-model="env_debug_global_variable"></Editor>
        </el-tab-pane>
      </el-tabs>
    </div>

    <!-- 右侧 -->
    <div class="card right_box">
      <el-divider content-position="center"><b>全局工具函数</b></el-divider>
      <Editor lang="python" v-model="env_global_func"></Editor>
    </div>
  </div>
  <div class="button" v-show='EnvInfo.id'>
    <el-button @click='saveEnv' type="primary" plain icon='FolderChecked'>保存</el-button>
    <el-button @click='copyEnv' type="primary" plain icon='DocumentCopy'>复制</el-button>
    <el-button @click='clickDeleteEnv' type="danger" plain icon='Delete'>删除</el-button>
  </div>
</template>

<script setup>
import http from '@/api/index'
import {ref, onMounted, computed} from 'vue'
import {ProjectStore} from '@/stores/module/ProStore'
import {ElMessage, ElMessageBox, ElNotification} from 'element-plus'
import Editor from '@/components/Editor.vue'
import DatabaseConfig from "@/views/environment/DatabaseConfig.vue"
import {UserStore} from '@/stores/module/UserStore'

const uStore = UserStore()
let envList = ref([])
const pstore = ProjectStore()

// 获取测试环境列表
async function getEvnList() {
  const project = pstore.proList.id
  const response = await http.environmentApi.getEnvironment(project)
  if (response.status === 200) {
    envList.value = response.data
    // 在pinia中保存测试环境列表
    pstore.envList = response.data
  }
}

// 添加测试环境
async function addEnv() {
  const response = await http.environmentApi.createEnvironment({
    project: pstore.proList.id,
    name: "测试环境",
    username: uStore.userInfo.username,
    host: "http://"
  })
  if (response.status === 201) {
    // 给出提示
    ElNotification({
      title: '测试环境创建成功！',
      type: 'success',
      duration: 1500
    })
    // 更新页面数据
    await getEvnList()
  } else {
    ElNotification({
      title: '环境创建失败！',
      message: response.data.detail,
      type: 'error',
      duration: 1500
    })
  }
}

// 页面数据
let env_name = ref('')
let env_host = ref('')
let env_headers = ref('{}')
let env_db = ref('[]')
let env_global_variable = ref('{}')
let env_debug_global_variable = ref('{}')
let env_global_func = ref('')

// 保存当前选择的测试环境
let EnvInfo = ref({})

function selectEnv(env) {
  // 当前选中的测试环境
  EnvInfo.value = env
  // 更新保存当前环境id
  pstore.env = env.id
  // 页面数据的值
  env_name.value = env.name
  env_host.value = env.host
  env_headers.value = env.headers
  env_db.value = JSON.stringify(env.db, 0, 4) || "[]"
  env_global_variable.value = env.global_variable
  env_debug_global_variable.value = env.debug_global_variable
  env_global_func.value = env.global_func
}

// 数据库配置
const handleUpdateConfigs = (newConfigs) => {
  env_db.value = newConfigs
}
const parsedConfigs = computed(() => {
  try {
    return JSON.parse(env_db.value)
  } catch (e) {
    return []
  }
})

// 页面加载完毕
onMounted(async () => {
  await getEvnList()
  // 组件上数据挂载完毕之后，设置一个默认选中的测试环境
  if (envList.value.length > 0) {
    selectEnv(envList.value[0])
  }
})

// 删除环境的方法
function clickDeleteEnv() {
  ElMessageBox.confirm(
      '此操作不可恢复，确认要删除该测试环境?',
      '警告', {
        confirmButtonText: '确认',
        cancelButtonText: '取消',
        type: 'warning',
        center: true
      })
      .then(async () => {
        const response = await http.environmentApi.deleteEnvironment(EnvInfo.value.id)
        if (response.status === 204) {
          // 提示
          ElNotification({
            title: '测试环境删除成功！',
            type: 'success',
            duration: 1500
          })
          // 更新页面数据
          await getEvnList()
          // 从新设置一个选中的测试环境
          if (envList.value.length > 0) {
            selectEnv(envList.value[0])
          }
        } else {
          ElNotification({
            title: '环境删除失败！',
            message: response.data.detail,
            type: 'error',
            duration: 1500
          })
        }
      })
      .catch(() => {
        ElMessage({
          type: 'info',
          message: '已取消删除操作。',
          duration: 1500
        })
      })
}

// 复制测试环境
async function copyEnv() {
  const params = EnvInfo.value
  params.name = params.name + '-复制'
  const response = await http.environmentApi.createEnvironment(params)
  if (response.status === 201) {
    ElNotification({
      title: '测试环境复制成功！',
      type: 'success',
      duration: 1500
    })
    // 更新页面数据
    await getEvnList()
  } else {
    ElNotification({
      title: '环境复制失败！',
      message: response.data.detail,
      type: 'error',
      duration: 1500
    })
  }
}

// 保存测试环境
async function saveEnv() {
  const env_id = EnvInfo.value.id
  // 修改时传递的参数
  const params = {
    name: env_name.value,
    host: env_host.value,
    global_func: env_global_func.value,
    db: JSON.parse(env_db.value),
    headers: env_headers.value,
    global_variable: env_global_variable.value,
    debug_global_variable: env_debug_global_variable.value,
  }
  const response = await http.environmentApi.updateEnvironment(env_id, params)
  if (response.status === 200 && response.data.code !== 300) {
    // 给出提示
    ElNotification({
      title: '测试环境保存成功！',
      type: 'success',
      duration: 1500
    })
    // 更新页面数据
    await getEvnList()
  } else {
    ElNotification({
      title: '环境保存失败！',
      message: response.data.detail,
      type: 'error',
      duration: 1500
    })
  }
}
</script>

<style lang="scss" scoped>
@use './environment.scss';
</style>