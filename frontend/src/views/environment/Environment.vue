<template>
  <div class="main_box">
    <!-- 左侧 -->
    <div class="card left_box">
      <!-- 顶部标题 -->
      <div class="title_box">
        <img src="@/assets/icons/environment.png" width="25" alt="">
        <div class="name">测试环境</div>
        <el-button @click='addEnv' type="primary" size="small" icon='CirclePlus' plain>环境</el-button>
        <el-button plain @click='refreshAll' type="success" icon="Refresh" size="small" :loading="isRefreshing" :disabled="isRefreshing">刷新</el-button>
      </div>
      <!-- 环境列表 -->
      <el-menu :default-active="EnvInfo.id+''">
        <el-menu-item @click='selectEnv(item)' :index="item.id.toString()" v-for='item in envList' :key="item.id" style="display: flex; justify-content: space-between; align-items: center;">
          <div style="display: flex; align-items: center;">
            <img src="@/assets/icons/environment.png" width="20" style="margin-right: 10px;" alt="">
            <span v-if='item.name.length < 15'>{{ item.name }}</span>
            <span v-else>{{ item.name.slice(0, 15) }}...</span>
          </div>
          <!-- 显示Jenkins节点信息(状态点、节点名和IP) -->
          <div v-if="getMatchedNode(item)" style="display: flex; align-items: center; gap: 6px;">
            <span class="status-dot" :style="{ backgroundColor: getNodeColor(getMatchedNode(item)) }"></span>
            <span style="font-size: 12px; color: #909399;">
              {{ getMatchedNode(item).ip_address || '未知IP' }}
            </span>
          </div>
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
      <!-- Jenkins节点信息显示 -->
      <div v-if="getMatchedNode(EnvInfo)" style="margin-top: 10px; padding: 10px; background-color: #f5f7fa; border-radius: 4px; border-left: 3px solid" :style="{ borderLeftColor: getNodeColor(getMatchedNode(EnvInfo)) }">
        <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 5px;">
          <div style="display: flex; align-items: center; gap: 8px;">
            <span class="status-dot" :style="{ backgroundColor: getNodeColor(getMatchedNode(EnvInfo)) }"></span>
            <span style="font-weight: bold; color: #303133;">Jenkins节点: {{ getMatchedNode(EnvInfo).display_name }}</span>
          </div>
          <el-button @click="openEditIPDialog" type="primary" size="small" icon="Edit" plain>修改IP</el-button>
        </div>
        <div style="font-size: 13px; color: #606266; margin-left: 20px;">
          <div><strong>IP地址:</strong> {{ getMatchedNode(EnvInfo).ip_address || '未配置' }}</div>
          <div><strong>状态:</strong> {{ getMatchedNode(EnvInfo).is_online ? '在线' : '离线' }} / {{ getMatchedNode(EnvInfo).is_idle ? '空闲' : '忙碌' }}</div>
          <div><strong>执行器:</strong> {{ getMatchedNode(EnvInfo).num_executors }}</div>
          <div v-if="getMatchedNode(EnvInfo).labels"><strong>标签:</strong> {{ getMatchedNode(EnvInfo).labels }}</div>
        </div>
      </div>
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
  
  <!-- 修改IP对话框 -->
  <el-dialog 
    v-model="editIPDialogVisible" 
    title="修改Jenkins节点IP" 
    width="500px"
    :close-on-click-modal="false"
  >
    <el-form :model="editIPForm" label-width="100px">
      <el-form-item label="节点名称">
        <el-input v-model="editIPForm.nodeName" disabled></el-input>
      </el-form-item>
      <el-form-item label="当前IP">
        <el-input v-model="editIPForm.currentIP" disabled></el-input>
      </el-form-item>
      <el-form-item label="新IP地址" required>
        <el-input v-model="editIPForm.newIP" placeholder="请输入新的IP地址" clearable></el-input>
      </el-form-item>
      <el-form-item label="SSH端口">
        <el-input-number v-model="editIPForm.sshPort" :min="1" :max="65535" placeholder="默认22"></el-input-number>
      </el-form-item>
    </el-form>
    <template #footer>
      <span class="dialog-footer">
        <el-button @click="editIPDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleUpdateIP" :loading="isUpdatingIP">确定</el-button>
      </span>
    </template>
  </el-dialog>
</template>

<script setup>
import http from '@/api/index'
import {ref, onMounted, computed} from 'vue'
import {ProjectStore} from '@/stores/module/ProStore'
import {ElMessage, ElMessageBox, ElNotification} from 'element-plus'
import Editor from '@/components/Editor.vue'
import DatabaseConfig from "@/views/environment/DatabaseConfig.vue"
import {UserStore} from '@/stores/module/UserStore'
import { updateNodeIP } from '@/api/jenkins'

const uStore = UserStore()
let envList = ref([])
const pstore = ProjectStore()
const isRefreshing = ref(false)

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

// Jenkins节点列表（从store中获取）
const jenkinsNodes = computed(() => pstore.jenkinsNodes)

// 获取Jenkins节点列表
async function getJenkinsNodes() {
  await pstore.getJenkinsNodes()
}

// 同时刷新环境和节点
async function refreshAll() {
  try {
    isRefreshing.value = true
    ElNotification({
      title: '正在刷新环境和节点...',
      type: 'info',
      duration: 1500
    })
    
    // 同时获取环境列表和Jenkins节点列表
    await Promise.all([
      getEvnList(),
      pstore.getJenkinsNodes()
    ])
    
    ElNotification({
      title: '刷新成功！',
      message: '环境和节点列表已更新',
      type: 'success',
      duration: 1500
    })
  } catch (error) {
    ElNotification({
      title: '刷新失败！',
      message: error.message || '未知错误',
      type: 'error',
      duration: 2000
    })
  } finally {
    isRefreshing.value = false
  }
}

// 获取节点状态颜色：绿色-在线空闲，黄色-在线忙碌，红色-离线
function getNodeColor(node) {
  if (!node.is_online) {
    return '#F56C6C'  // 红色 - 离线
  }
  if (node.is_busy) {
    return '#E6A23C'  // 黄色 - 忙碌
  }
  return '#67C23A'    // 绿色 - 在线空闲
}

// 获取与环境匹配的Jenkins节点
function getMatchedNode(env) {
  if (!jenkinsNodes.value || jenkinsNodes.value.length === 0) return null
  return jenkinsNodes.value.find(node => 
    node.display_name === env.name || 
    node.name === env.name
  )
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
  
  // 检查是否匹配Jenkins节点,如果有IP地址则同步,否则显示为空
  const matchedNode = getMatchedNode(env)
  if (matchedNode && matchedNode.ip_address) {
    // 如果Jenkins节点有IP地址,同步到host输入框
    env_host.value = matchedNode.ip_address
  } else {
    // 否则显示为空(不显示原有的host)
    env_host.value = ''
  }
  
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
  // 加载Jenkins节点列表
  await getJenkinsNodes()
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

// 修改IP对话框相关
const editIPDialogVisible = ref(false)
const isUpdatingIP = ref(false)
const editIPForm = ref({
  nodeName: '',
  currentIP: '',
  newIP: '',
  sshPort: 22
})

// 打开修改IP对话框
function openEditIPDialog() {
  const matchedNode = getMatchedNode(EnvInfo.value)
  if (!matchedNode) {
    ElMessage.warning('未找到匹配的Jenkins节点')
    return
  }
  
  editIPForm.value = {
    nodeName: matchedNode.name,
    currentIP: matchedNode.ip_address || '未配置',
    newIP: '',
    sshPort: 22
  }
  editIPDialogVisible.value = true
}

// 处理更新IP
async function handleUpdateIP() {
  if (!editIPForm.value.newIP) {
    ElMessage.warning('请输入新的IP地址')
    return
  }
  
  try {
    isUpdatingIP.value = true
    
    const response = await updateNodeIP(editIPForm.value.nodeName, {
      new_ip: editIPForm.value.newIP,
      ssh_port: editIPForm.value.sshPort
    })
    
    // 修正：读取response.data而不是response
    if (response.data.code === 200) {
      ElNotification({
        title: '成功！',
        message: response.data.message,
        type: 'success',
        duration: 2000
      })
      
      // 关闭对话框
      editIPDialogVisible.value = false
      
      // 刷新Jenkins节点列表
      await getJenkinsNodes()
      
      // 更新当前环境的host字段为新IP,并自动保存
      env_host.value = editIPForm.value.newIP
      await saveEnv()
      
    } else {
      ElNotification({
        title: '更新失败！',
        message: response.data.message || '未知错误',
        type: 'error',
        duration: 2000
      })
    }
  } catch (error) {
    ElNotification({
      title: '更新失败！',
      message: error.response?.data?.message || error.message || '网络错误',
      type: 'error',
      duration: 2000
    })
  } finally {
    isUpdatingIP.value = false
  }
}
</script>

<style lang="scss" scoped>
@use './environment.scss';
</style>