<template>
  <div class="main_box">
    <!-- 左侧 -->
    <div class="card left_box">
      <!-- 顶部标题 -->
      <div class="title_box">
        <img src="@/assets/icons/environment.png" width="25" alt="">
        <div class="name">测试环境</div>
        <el-button @click='openCreateDialog' type="primary" size="small" icon='CirclePlus' plain>新增</el-button>
        <el-button plain @click='refreshAll' type="success" icon="Refresh" size="small" :loading="isRefreshing" :disabled="isRefreshing">刷新</el-button>
      </div>
      <!-- 环境列表 -->
      <el-menu :default-active="EnvInfo.id+''">
        <el-menu-item @click='selectEnv(item)' :index="item.id.toString()" v-for='item in mixedEnvironments' :key="item.id" style="display: flex; justify-content: space-between; align-items: center;">
          <div style="display: flex; align-items: center;">
            <img src="@/assets/icons/environment.png" width="20" style="margin-right: 10px;" alt="">
            <span v-if='item.name.length < 15'>{{ item.name }}</span>
            <span v-else>{{ item.name.slice(0, 15) }}...</span>
          </div>
          <!-- 显示自动化节点信息 -->
          <div v-if="getMatchedNode(item)" style="display: flex; align-items: center; gap: 6px;">
            <span class="status-dot" :style="{ backgroundColor: getNodeColor(getMatchedNode(item)) }"></span>
            
            <!-- 如果是虚拟环境（未关联的节点），显示标记 -->
            <el-tag v-if="item.is_virtual" size="small" type="info" effect="plain" style="transform: scale(0.8);">未关联</el-tag>
            
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
      <!-- 自动化节点信息显示 -->
      <div v-if="getMatchedNode(EnvInfo)" style="margin-top: 10px; padding: 10px; background-color: #f5f7fa; border-radius: 4px; border-left: 3px solid" :style="{ borderLeftColor: getNodeColor(getMatchedNode(EnvInfo)) }">
        <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 8px;">
          <div style="display: flex; align-items: center; gap: 8px;">
            <span class="status-dot" :style="{ backgroundColor: getNodeColor(getMatchedNode(EnvInfo)) }"></span>
            <span style="font-weight: bold; color: #303133;">自动化节点: {{ getMatchedNode(EnvInfo).display_name }}</span>
          </div>
          <!-- 节点管理操作按钮组 -->
          <el-button-group size="small">
            <el-button @click="openEditIPDialog" type="primary" icon="Edit" plain>修改IP</el-button>
            <el-button @click="openEditLabelsDialog" type="primary" icon="PriceTag" plain>标签</el-button>
            <el-dropdown @command="handleNodeCommand">
              <el-button type="primary" plain>
                更多<el-icon class="el-icon--right"><ArrowDown /></el-icon>
              </el-button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item :command="{action: 'info', node: getMatchedNode(EnvInfo)}" icon="InfoFilled">查看详情</el-dropdown-item>
                  <el-dropdown-item :command="{action: 'toggle', node: getMatchedNode(EnvInfo)}" :icon="getMatchedNode(EnvInfo).is_online ? 'VideoPause' : 'VideoPlay'">
                    {{ getMatchedNode(EnvInfo).is_online ? '禁用节点' : '启用节点' }}
                  </el-dropdown-item>
                  <el-dropdown-item :command="{action: 'reconnect', node: getMatchedNode(EnvInfo)}" icon="Connection">重新连接</el-dropdown-item>
                  <el-dropdown-item divided :command="{action: 'delete', node: getMatchedNode(EnvInfo)}" icon="Delete">删除节点</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </el-button-group>
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
    <el-button @click='saveEnv' type="primary" plain icon='FolderChecked' :loading="isSaving" :disabled="isSaving">{{ EnvInfo.is_virtual ? '保存并创建' : '保存' }}</el-button>
    <el-button @click='copyEnv' type="primary" plain icon='DocumentCopy' v-if="!EnvInfo.is_virtual" :loading="isCopying" :disabled="isCopying">复制</el-button>
    <el-button @click='clickDeleteEnv' type="danger" plain icon='Delete' v-if="!EnvInfo.is_virtual" :loading="isDeleting" :disabled="isDeleting">删除</el-button>
  </div>
  
  <!-- 统一创建对话框 -->
  <el-dialog 
    v-model="createDialogVisible" 
    title="创建" 
    width="650px"
    :close-on-click-modal="false"
  >
    <el-tabs v-model="createType" type="border-card">
      <!-- 创建测试环境选项卡 -->
      <el-tab-pane label="测试环境" name="environment">
        <div style="padding: 20px;">
          <el-alert
            title="提示"
            type="info"
            :closable="false"
            show-icon
            style="margin-bottom: 20px;"
          >
            创建一个新的测试环境配置
          </el-alert>
          
          <el-form label-width="120px">
            <el-form-item label="环境名称">
              <el-input v-model="newEnvName" placeholder="请输入环境名称，如: 测试环境" clearable></el-input>
            </el-form-item>
            <el-form-item label="服务器地址">
              <el-input v-model="newEnvHost" placeholder="请输入服务器地址，如: http://192.168.1.100" clearable></el-input>
            </el-form-item>
          </el-form>
        </div>
      </el-tab-pane>
      
      <!-- 创建自动化节点选项卡 -->
      <el-tab-pane label="自动化节点" name="node">
        <div style="padding: 20px;">
          <el-alert
            title="提示"
            type="warning"
            :closable="false"
            show-icon
            style="margin-bottom: 20px;"
          >
            创建一个新的自动化 SSH 节点，需要确保目标机器已安装 Java 并配置 SSH
          </el-alert>
          
          <el-form :model="createNodeForm" :rules="createNodeRules" ref="createNodeFormRef" label-width="120px">
            <el-form-item label="节点名称" prop="name">
              <el-input v-model="createNodeForm.name" placeholder="如: build-node-01" clearable></el-input>
            </el-form-item>
            
            <el-form-item label="主机IP/域名" prop="host">
              <el-input v-model="createNodeForm.host" placeholder="如: 192.168.1.100" clearable></el-input>
            </el-form-item>
            
            <el-collapse>
              <el-collapse-item title="高级选项（点击展开）" name="1">
                <el-form-item label="SSH凭证ID">
                  <el-select 
                    v-model="createNodeForm.credential_id" 
                    placeholder="请选择或输入SSH凭证ID" 
                    filterable 
                    allow-create
                    clearable
                    :loading="isLoadingCredentials"
                    style="width: 100%;"
                  >
                    <template #header>
                      <el-button 
                        type="primary" 
                        size="small" 
                        @click.stop="loadCredentials"
                        :loading="isLoadingCredentials"
                        style="width: 100%; margin-bottom: 8px;"
                      >
                        {{ isLoadingCredentials ? '加载中...' : '刷新凭证列表' }}
                      </el-button>
                    </template>
                    <el-option
                      v-for="cred in credentialsList"
                      :key="cred.id"
                      :label="`${cred.id} ${cred.description ? '- ' + cred.description : ''}`"
                      :value="cred.id"
                    >
                      <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span>{{ cred.id }}</span>
                        <el-tag v-if="cred.typeName.includes('SSH')" type="success" size="small">{{ cred.typeName }}</el-tag>
                        <el-tag v-else size="small">{{ cred.typeName }}</el-tag>
                      </div>
                      <div v-if="cred.description" style="font-size: 12px; color: #909399; margin-top: 2px;">
                        {{ cred.description }}
                      </div>
                    </el-option>
                  </el-select>
                  <span style="font-size: 12px; color: #909399;">点击"刷新凭证列表"按钮从服务器获取</span>
                </el-form-item>
                
                <el-form-item label="SSH端口">
                  <el-input-number v-model="createNodeForm.port" :min="1" :max="65535"></el-input-number>
                </el-form-item>
                
                <el-form-item label="远程工作目录">
                  <el-input v-model="createNodeForm.remote_fs" placeholder="/home/jenkins" clearable></el-input>
                </el-form-item>
                
                <el-form-item label="节点标签">
                  <el-input v-model="createNodeForm.labels" placeholder="如: linux docker java11" clearable></el-input>
                </el-form-item>
                
                <el-form-item label="执行器数量">
                  <el-input-number v-model="createNodeForm.num_executors" :min="1" :max="20"></el-input-number>
                </el-form-item>
                
                <el-form-item label="节点描述">
                  <el-input v-model="createNodeForm.description" type="textarea" :rows="2" placeholder="可选"></el-input>
                </el-form-item>
              </el-collapse-item>
            </el-collapse>
          </el-form>
        </div>
      </el-tab-pane>
    </el-tabs>
    
    <template #footer>
      <span class="dialog-footer">
        <el-button @click="createDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleCreate" :loading="isCreating">
          {{ createType === 'environment' ? '创建环境' : '创建节点' }}
        </el-button>
      </span>
    </template>
  </el-dialog>
  
  <!-- 修改IP对话框 -->
  <el-dialog 
    v-model="editIPDialogVisible" 
    title="修改自动化节点IP" 
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
      <el-form-item label="SSH凭证">
        <el-select 
          v-model="editIPForm.credentialId" 
          placeholder="选择SSH凭证（可选）" 
          filterable 
          clearable
          allow-create
          :loading="isLoadingCredentials"
          style="width: 100%;"
        >
          <el-option
            v-for="cred in credentialsList"
            :key="cred.id"
            :label="`${cred.id} ${cred.description ? '- ' + cred.description : ''}`"
            :value="cred.id"
          >
            <div style="display: flex; justify-content: space-between; align-items: center;">
              <span>{{ cred.id }}</span>
              <el-tag v-if="cred.typeName.includes('SSH')" type="success" size="small">{{ cred.typeName }}</el-tag>
              <el-tag v-else size="small">{{ cred.typeName }}</el-tag>
            </div>
          </el-option>
        </el-select>
        <span style="font-size: 12px; color: #909399;">留空则保持不变</span>
      </el-form-item>
    </el-form>
    <template #footer>
      <span class="dialog-footer">
        <el-button @click="editIPDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleUpdateIP" :loading="isUpdatingIP">确定</el-button>
      </span>
    </template>
  </el-dialog>
  
  <!-- 节点详情对话框 -->
  <el-dialog 
    v-model="nodeInfoDialogVisible" 
    title="自动化节点详情" 
    width="600px"
  >
    <el-descriptions :column="2" border v-if="currentNodeInfo">
      <el-descriptions-item label="节点名称">{{ currentNodeInfo.name }}</el-descriptions-item>
      <el-descriptions-item label="显示名称">{{ currentNodeInfo.displayName }}</el-descriptions-item>
      <el-descriptions-item label="状态">
        <el-tag :type="currentNodeInfo.offline ? 'danger' : 'success'">
          {{ currentNodeInfo.offline ? '离线' : '在线' }}
        </el-tag>
      </el-descriptions-item>
      <el-descriptions-item label="执行器数量">{{ currentNodeInfo.numExecutors }}</el-descriptions-item>
      <el-descriptions-item label="空闲状态">
        <el-tag :type="currentNodeInfo.idle ? 'success' : 'warning'">
          {{ currentNodeInfo.idle ? '空闲' : '忙碌' }}
        </el-tag>
      </el-descriptions-item>
      <el-descriptions-item label="临时离线">
        {{ currentNodeInfo.temporarilyOffline ? '是' : '否' }}
      </el-descriptions-item>
      <el-descriptions-item label="标签" :span="2">{{ currentNodeInfo.labels || '无' }}</el-descriptions-item>
      <el-descriptions-item label="描述" :span="2">{{ currentNodeInfo.description || '无' }}</el-descriptions-item>
      <el-descriptions-item label="离线原因" :span="2" v-if="currentNodeInfo.offline">
        {{ currentNodeInfo.offlineCauseReason || '无' }}
      </el-descriptions-item>
    </el-descriptions>
  </el-dialog>
  
  <!-- 更新标签对话框 -->
  <el-dialog 
    v-model="editLabelsDialogVisible" 
    title="更新节点标签" 
    width="500px"
    :close-on-click-modal="false"
  >
    <el-form :model="editLabelsForm" label-width="100px">
      <el-form-item label="节点名称">
        <el-input v-model="editLabelsForm.nodeName" disabled></el-input>
      </el-form-item>
      <el-form-item label="当前标签">
        <el-tag v-for="tag in editLabelsForm.currentLabels.split(',')" :key="tag" style="margin-right: 5px;">
          {{ tag.trim() }}
        </el-tag>
        <span v-if="!editLabelsForm.currentLabels">无</span>
      </el-form-item>
      <el-form-item label="新标签" required>
        <el-input 
          v-model="editLabelsForm.newLabels" 
          placeholder="请输入新的标签,用空格分隔(如: linux docker java11)" 
          clearable
        ></el-input>
        <span style="font-size: 12px; color: #909399;">提示: 多个标签用空格分隔</span>
      </el-form-item>
    </el-form>
    <template #footer>
      <span class="dialog-footer">
        <el-button @click="editLabelsDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleUpdateLabels" :loading="isUpdatingLabels">确定</el-button>
      </span>
    </template>
  </el-dialog>
</template>

<script setup>
import http from '@/api/index'
import {ref, onMounted, computed} from 'vue'
import {ProjectStore} from '@/stores/module/ProStore'
import {ElMessage, ElMessageBox, ElNotification} from 'element-plus'
import { ArrowDown } from '@element-plus/icons-vue'
import Editor from '@/components/Editor.vue'
import DatabaseConfig from "@/views/environment/DatabaseConfig.vue"
import {UserStore} from '@/stores/module/UserStore'
import { 
  updateNodeIP, 
  getNodeInfo, 
  toggleNode, 
  reconnectNode, 
  updateNodeLabels, 
  deleteNode,
  createNode,
  getCredentialsList,
  syncNodesFromJenkins
} from '@/api/jenkins'

const uStore = UserStore()
let envList = ref([])
const pstore = ProjectStore()
const isRefreshing = ref(false)

// Loading状态
const isSaving = ref(false)
const isDeleting = ref(false)
const isCopying = ref(false)
const isLoading = ref(false)
const isDeletingNode = ref(false)  // 删除Jenkins节点的loading状态

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

// 混合显示环境和节点
const mixedEnvironments = computed(() => {
  const envs = [...envList.value]
  if (!jenkinsNodes.value) return envs

  // 遍历所有 Jenkins 节点
  jenkinsNodes.value.forEach(node => {
    // 检查是否已经有对应的环境 (匹配名称)
    const exists = envs.find(e => e.name === node.name || e.name === node.display_name)
    
    // 如果没有对应的环境，创建一个"虚拟环境"用于显示
    if (!exists) {
      envs.push({
        id: 'node-' + node.name,  // 使用特殊前缀的ID
        name: node.name,
        host: node.ip_address || '',
        is_virtual: true,         // 标记为虚拟环境
        // 默认空字段
        headers: '{}',
        db: [],
        global_variable: '{}',
        debug_global_variable: '{}',
        global_func: ''
      })
    }
  })
  
  return envs
})

// 获取Jenkins节点列表（支持自动同步）
async function getJenkinsNodes(autoSync = false) {
  await pstore.getJenkinsNodes(autoSync)
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

    // 先从 Jenkins 同步节点到数据库
    try {
      const syncResponse = await syncNodesFromJenkins()
      if (syncResponse.data.code === 200) {
        console.log('从 Jenkins 同步节点成功:', syncResponse.data.message)
      }
    } catch (syncError) {
      console.warn('从 Jenkins 同步节点失败,继续查询:', syncError)
    }

    // 然后获取环境列表和节点列表
    await Promise.all([
      getEvnList(),
      pstore.getJenkinsNodes()  // 从数据库获取最新节点列表
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

// ==================== 统一创建对话框 ====================

// 统一创建对话框
const createDialogVisible = ref(false)
const createType = ref('environment') // 'environment' 或 'node'
const isCreating = ref(false)

// 环境创建数据
const newEnvName = ref('测试环境')
const newEnvHost = ref('http://')

// 打开统一创建对话框
function openCreateDialog() {
  // 重置为环境选项卡
  createType.value = 'environment'
  
  // 重置环境表单
  newEnvName.value = '测试环境'
  newEnvHost.value = 'http://'
  
  // 重置节点表单
  createNodeForm.value = {
    name: '',
    host: '',
    credential_id: '',
    port: 22,
    remote_fs: '/home/jenkins',
    labels: '',
    num_executors: 2,
    description: ''
  }
  
  // 清除节点表单验证
  if (createNodeFormRef.value) {
    createNodeFormRef.value.clearValidate()
  }
  
  // 自动加载SSH凭证列表（后台静默加载）
  loadCredentials().catch(() => {
    // 静默失败，用户可以稍后手动刷新
    console.warn('自动加载凭证列表失败，用户可点击"刷新凭证列表"按钮手动加载')
  })
  
  createDialogVisible.value = true
}

// 统一处理创建
async function handleCreate() {
  if (createType.value === 'environment') {
    await handleCreateEnvironment()
  } else {
    await handleCreateNode()
  }
}

// 创建测试环境
async function handleCreateEnvironment() {
  try {
    isCreating.value = true
    
    const response = await http.environmentApi.createEnvironment({
      project: pstore.proList.id,
      name: newEnvName.value,
      username: uStore.userInfo.username,
      host: newEnvHost.value
    })
    
    if (response.status === 201) {
      ElNotification({
        title: '测试环境创建成功！',
        type: 'success',
        duration: 1500
      })
      
      // 关闭对话框
      createDialogVisible.value = false
      
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
  } catch (error) {
    ElMessage.error('创建环境失败: ' + (error.message || '未知错误'))
  } finally {
    isCreating.value = false
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
  // 加载Jenkins节点列表（启用自动同步）
  await getJenkinsNodes(true)
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
        try {
          isDeleting.value = true
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
        } catch (error) {
          ElNotification({
            title: '环境删除失败！',
            message: error.message || '未知错误',
            type: 'error',
            duration: 1500
          })
        } finally {
          isDeleting.value = false
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
  try {
    isCopying.value = true
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
  } catch (error) {
    ElNotification({
      title: '环境复制失败！',
      message: error.message || '未知错误',
      type: 'error',
      duration: 1500
    })
  } finally {
    isCopying.value = false
  }
}

// 保存测试环境
async function saveEnv() {
  try {
    isSaving.value = true
    
    // 如果是虚拟环境，通过保存操作创建新环境
    if (EnvInfo.value.is_virtual) {
      const params = {
        project: pstore.proList.id,
        name: env_name.value,
        username: uStore.userInfo.username,
        host: env_host.value,
        // 带上其他配置
        global_func: env_global_func.value,
        db: JSON.parse(env_db.value),
        headers: env_headers.value,
        global_variable: env_global_variable.value,
        debug_global_variable: env_debug_global_variable.value,
      }
      
      const response = await http.environmentApi.createEnvironment(params)
      
      if (response.status === 201) {
        ElNotification({
          title: '环境创建成功！',
          message: '已将Jenkins节点关联为测试环境',
          type: 'success',
          duration: 1500
        })
        
        // 刷新列表
        await getEvnList()
        
        // 尝试选中新创建的环境
        const newEnv = envList.value.find(e => e.name === params.name)
        if (newEnv) {
          selectEnv(newEnv)
        }
      } else {
        ElNotification({
          title: '环境创建失败！',
          message: response.data.detail,
          type: 'error',
          duration: 1500
        })
      }
      return
    }

    // 常规保存逻辑
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
  } catch (error) {
    ElNotification({
      title: '操作失败！',
      message: error.message || '未知错误',
      type: 'error',
      duration: 1500
    })
  } finally {
    isSaving.value = false
  }
}

// 修改IP对话框相关
const editIPDialogVisible = ref(false)
const isUpdatingIP = ref(false)
const editIPForm = ref({
  nodeName: '',
  currentIP: '',
  newIP: '',
  sshPort: 22,
  credentialId: ''
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
    sshPort: 22,
    credentialId: ''
  }
  
  // 打开对话框时自动加载凭证（如果还没加载）
  if (credentialsList.value.length === 0) {
    loadCredentials().catch(() => {
      // 静默失败，用户可以稍后手动刷新
    })
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
      ssh_port: editIPForm.value.sshPort,
      credential_id: editIPForm.value.credentialId
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
      
      // 刷新Jenkins节点列表(IP更新不影响环境列表结构)
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

// ==================== 节点管理新增功能 ====================

// 节点详情对话框
const nodeInfoDialogVisible = ref(false)
const currentNodeInfo = ref(null)

// 查看节点详情
async function viewNodeInfo(node) {
  try {
    const response = await getNodeInfo(node.name)
    if (response.data.code === 200) {
      currentNodeInfo.value = response.data.data
      nodeInfoDialogVisible.value = true
    } else {
      ElMessage.error(response.data.message || '获取节点详情失败')
    }
  } catch (error) {
    ElMessage.error(error.response?.data?.message || '获取节点详情失败')
  }
}

// 启用/禁用节点
async function handleToggleNode(node) {
  const action = node.is_online ? 'disable' : 'enable'
  const actionText = node.is_online ? '禁用' : '启用'
  
  try {
    let message = ''
    if (action === 'disable') {
      const result = await ElMessageBox.prompt('请输入禁用原因(可选)', `${actionText}节点`, {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        inputPattern: /.*/,
        inputPlaceholder: '可选输入禁用原因'
      })
      message = result.value || ''
    }
    
    const response = await toggleNode(node.name, { action, message })
    
    if (response.data.code === 200) {
      ElNotification({
        title: '成功',
        message: response.data.message,
        type: 'success',
        duration: 2000
      })
      // 刷新节点列表(启用/禁用不影响环境列表结构)
      await getJenkinsNodes()
    } else {
      ElMessage.error(response.data.message || `${actionText}节点失败`)
    }
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error(error.response?.data?.message || `${actionText}节点失败`)
    }
  }
}

// 重新连接节点
async function handleReconnectNode(node) {
  try {
    ElNotification({
      title: '正在重新连接...',
      message: `正在重新连接节点 ${node.name}`,
      type: 'info',
      duration: 2000
    })
    
    const response = await reconnectNode(node.name)
    
    if (response.data.code === 200) {
      ElNotification({
        title: '成功',
        message: response.data.message,
        type: 'success',
        duration: 2000
      })
      // 刷新节点列表(重连不影响环境列表结构)
      await getJenkinsNodes()
    } else {
      ElMessage.error(response.data.message || '重新连接失败')
    }
  } catch (error) {
    ElMessage.error(error.response?.data?.message || '重新连接失败')
  }
}

// 删除节点
async function handleDeleteNode(node) {
  try {
    await ElMessageBox.confirm(
      `确定要删除节点 "${node.name}" 吗? 此操作不可撤销!`,
      '警告',
      {
        confirmButtonText: '确定删除',
        cancelButtonText: '取消',
        type: 'warning',
        center: true
      }
    )
    
    // 显示删除中的通知
    const loadingNotification = ElNotification({
      title: '正在删除...',
      message: `正在删除节点 ${node.name}`,
      type: 'info',
      duration: 0  // 不自动关闭
    })
    
    try {
      isDeletingNode.value = true
      
      // 记录当前选中的ID，以便后续判断是否需要重置选择
      const currentSelectedId = EnvInfo.value.id
      const isDeletingCurrent = currentSelectedId === 'node-' + node.name
      
      const response = await deleteNode(node.name)
      
      // 关闭loading通知
      loadingNotification.close()
      
      if (response.data.code === 200) {
        ElNotification({
          title: '成功',
          message: response.data.message,
          type: 'success',
          duration: 2000
        })
        
        // 必须同时刷新环境列表和节点列表，以确保视图正确更新
        // 对于虚拟节点，刷新节点列表即可移除
        // 对于关联节点，刷新节点列表可更新环境状态点
        await Promise.all([
          getJenkinsNodes(),
          getEvnList()
        ])
        
        // 如果删除的是当前选中的虚拟节点，重置选择到第一个环境
        if (isDeletingCurrent) {
          if (mixedEnvironments.value.length > 0) {
            selectEnv(mixedEnvironments.value[0])
          } else {
            EnvInfo.value = {}
          }
        }
      } else {
        ElMessage.error(response.data.message || '删除节点失败')
      }
    } catch (error) {
      // 关闭loading通知
      loadingNotification.close()
      
      if (error !== 'cancel') {
        ElMessage.error(error.response?.data?.message || '删除节点失败')
      }
    } finally {
      isDeletingNode.value = false
    }
  } catch (error) {
    // 用户取消删除
    if (error !== 'cancel') {
      ElMessage.error('操作失败')
    }
  }
}

// 标签编辑对话框
const editLabelsDialogVisible = ref(false)
const isUpdatingLabels = ref(false)
const editLabelsForm = ref({
  nodeName: '',
  currentLabels: '',
  newLabels: ''
})

// 打开标签编辑对话框
function openEditLabelsDialog() {
  const matchedNode = getMatchedNode(EnvInfo.value)
  if (!matchedNode) {
    ElMessage.warning('未找到匹配的Jenkins节点')
    return
  }
  
  editLabelsForm.value = {
    nodeName: matchedNode.name,
    currentLabels: matchedNode.labels || '',
    newLabels: matchedNode.labels || ''
  }
  editLabelsDialogVisible.value = true
}

// 处理更新标签
async function handleUpdateLabels() {
  if (!editLabelsForm.value.newLabels.trim()) {
    ElMessage.warning('请输入新的标签')
    return
  }
  
  try {
    isUpdatingLabels.value = true
    
    const response = await updateNodeLabels(editLabelsForm.value.nodeName, {
      labels: editLabelsForm.value.newLabels.trim()
    })
    
    if (response.data.code === 200) {
      ElNotification({
        title: '成功',
        message: response.data.message,
        type: 'success',
        duration: 2000
      })
      
      // 关闭对话框
      editLabelsDialogVisible.value = false
      
      // 刷新Jenkins节点列表(标签更新不影响环境列表结构)
      await getJenkinsNodes()
    } else {
      ElMessage.error(response.data.message || '更新标签失败')
    }
  } catch (error) {
    ElMessage.error(error.response?.data?.message || '更新标签失败')
  } finally {
    isUpdatingLabels.value = false
  }
}

// 处理节点操作下拉菜单命令
function handleNodeCommand(command) {
  const { action, node } = command
  
  switch (action) {
    case 'info':
      viewNodeInfo(node)
      break
    case 'toggle':
      handleToggleNode(node)
      break
    case 'reconnect':
      handleReconnectNode(node)
      break
    case 'delete':
      handleDeleteNode(node)
      break
  }
}

// ==================== 创建节点功能 (整合到统一对话框) ====================

// 节点表单引用 (已在统一对话框中使用)
const createNodeFormRef = ref(null)

// 创建节点表单数据 (已在统一对话框中使用)
const createNodeForm = ref({
  name: '',
  host: '',
  credential_id: '',
  port: 22,
  remote_fs: '/home/jenkins',
  labels: '',
  num_executors: 2,
  description: ''
})

// 表单验证规则
const createNodeRules = {
  name: [
    { required: true, message: '请输入节点名称', trigger: 'blur' },
    { min: 2, max: 50, message: '长度在 2 到 50 个字符', trigger: 'blur' }
  ],
  host: [
    { required: true, message: '请输入主机IP或域名', trigger: 'blur' }
  ]
}

// Jenkins凭证列表
const credentialsList = ref([])
const isLoadingCredentials = ref(false)

// 加载凭证列表
async function loadCredentials() {
  try {
    isLoadingCredentials.value = true
    
    const response = await getCredentialsList()
    
    if (response.data.code === 200) {
      credentialsList.value = response.data.data || []
      // 只在有凭证时显示提示
      if (credentialsList.value.length > 0) {
        ElMessage.success(`已加载 ${credentialsList.value.length} 个SSH凭证`)
      } else {
        ElMessage.warning('未找到SSH凭证，请先在Jenkins中配置')
      }
    } else {
      ElMessage.error(response.data.message || '加载凭证列表失败')
    }
  } catch (error) {
    ElMessage.error(error.response?.data?.message || '加载凭证列表失败')
  } finally {
    isLoadingCredentials.value = false
  }
}

// 处理创建节点 (从统一对话框调用)
async function handleCreateNode() {
  // 表单验证
  if (!createNodeFormRef.value) return
  
  try {
    await createNodeFormRef.value.validate()
  } catch (error) {
    ElMessage.warning('请检查表单填写是否正确')
    return
  }
  
  try {
    isCreating.value = true
    
    const response = await createNode({
      name: createNodeForm.value.name.trim(),
      host: createNodeForm.value.host.trim(),
      credential_id: createNodeForm.value.credential_id?.trim() || '',
      port: createNodeForm.value.port,
      remote_fs: createNodeForm.value.remote_fs.trim(),
      labels: createNodeForm.value.labels?.trim() || '',
      num_executors: createNodeForm.value.num_executors,
      description: createNodeForm.value.description?.trim() || ''
    })
    
    if (response.data.code === 200) {
      ElNotification({
        title: '✓ 节点创建成功',
        message: '节点已创建，详细状态信息正在后台同步中...',
        type: 'success',
        duration: 3000
      })
      
      // 关闭对话框
      createDialogVisible.value = false
      
      // 立即刷新列表显示基本信息
      await Promise.all([
        getJenkinsNodes(),
        getEvnList()
      ])
      
      // 提示用户稍后刷新查看完整状态
      setTimeout(() => {
        ElMessage.info('建议10秒后手动刷新，查看节点完整状态')
      }, 1500)
    } else {
      ElMessage.error(response.data.message || '创建节点失败')
    }
  } catch (error) {
    ElMessage.error(error.response?.data?.message || '创建节点失败')
  } finally {
    isCreating.value = false
  }
}
</script>

<style lang="scss" scoped>
@use './environment.scss';
</style>