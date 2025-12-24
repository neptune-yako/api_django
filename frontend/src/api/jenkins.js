import axios from 'axios'
import { UserStore } from '@/stores/module/UserStore'
import { ElNotification } from 'element-plus'
import router from "@/router/index.js"

// 创建 Jenkins 专用的 axios 实例，增加超时时间
const jenkinsHttp = axios.create({
  baseURL: import.meta.env.VITE_BASE_API,
  validateStatus: function (status) {
    return status >= 200 && status < 300
  },
  withCredentials: false,
  crossDomain: true,
  headers: { 'Content-Type': 'application/json;charset=utf-8' },
  // Jenkins API 可能需要更长时间，设置 60 秒超时
  timeout: 60000
})

// 请求拦截器
jenkinsHttp.interceptors.request.use(
  config => {
    if (config.url !== '/login/' && config.url !== '/register/' && config.url !== '/verify/' && config.url !== '/refresh/') {
      const ustore = UserStore()
      const token = ustore.userInfo.token
      config.headers.Authorization = 'Bearer ' + token
    }
    return config
  },
  error => Promise.reject(error)
)

// 响应拦截器（与 requests.js 类似）
jenkinsHttp.interceptors.response.use(
  function (response) {
    if (response.status === 200 || response.status === 201 || response.status === 204) {
      const res = response.data
      if (res.code !== undefined) {
        if (res.code !== 200) {
          ElNotification({
            title: '操作失败',
            message: res.message || '请求失败',
            type: 'error',
            duration: 3000
          })
          return Promise.reject(new Error(res.message))
        }
      }
      return response
    }
    return response
  },
  function (error) {
    if (error.code === 'ECONNABORTED') {
      ElNotification({
        title: '请求超时',
        message: 'Jenkins API 响应超时，请稍后重试',
        type: 'warning',
        duration: 3000
      })
      return Promise.reject(error)
    }
    if (error.code === 'ERR_NETWORK' || error.message.includes('Network Error')) {
      ElNotification({
        title: '网络错误',
        message: '网络错误，请检查网络是否正常',
        type: 'error',
        duration: 1500
      })
      return Promise.reject(error)
    }
    return Promise.reject(error)
  }
)

// 封装为与 http 相同的格式
const http = ({ url, method, params, data }) => {
  return jenkinsHttp({
    url,
    method,
    params,
    data
  }).then(response => response).catch(error => {
    throw error
  })
}

// Jenkins服务器管理
export function getServerList() {
  return http({ url: '/api/jenkins/server/', method: 'get' })
}

export function getJenkinsServers(params) {
  return http({ url: '/api/jenkins/server/', method: 'get', params })
}

export function addJenkinsServer(data) {
  return http({ url: '/api/jenkins/server/', method: 'post', data })
}

export function updateJenkinsServer(id, data) {
  return http({ url: `/api/jenkins/server/${id}/`, method: 'put', data })
}

export function deleteJenkinsServer(id) {
  return http({ url: `/api/jenkins/server/${id}/`, method: 'delete' })
}

export function testConnection(id) {
  return http({ url: `/api/jenkins/server/${id}/test_connection/`, method: 'post' })
}

export function testConnectionById(id) {
  return http({ url: `/api/jenkins/server/${id}/test_connection/`, method: 'post' })
}

// Jenkins任务管理
export function getJobList(params) {
  return http({ url: '/api/jenkins/pipeline/', method: 'get', params })
}

export function getJenkinsJobs(params) {
  return http({ url: '/api/jenkins/pipeline/', method: 'get', params })
}

export function syncJenkinsJobs() {
  return http({ url: '/api/jenkins/jobs/sync/', method: 'post' })
}

export function createJenkinsJob(data) {
  return http({ url: '/api/jenkins/job/manage/', method: 'post', data })
}

export function getJenkinsJobDetail(jobId) {
  return http({ url: `/api/jenkins/pipeline/${jobId}/`, method: 'get' })
}

export function editJenkinsJob(data) {
  return http({ url: '/api/jenkins/job/manage/', method: 'put', data })
}

export function deleteJenkinsJob(jobId) {
  return http({ url: `/api/jenkins/pipeline/${jobId}/`, method: 'delete' })
}

export function triggerBuild(data) {
  return http({ url: '/api/jenkins/job/trigger_build/', method: 'post', data })
}

export function buildJenkinsJob(data) {
  return http({ url: '/api/jenkins/job/build/', method: 'post', data })
}

export function getTaskStatus(taskId) {
  return http({ url: `/api/jenkins/task/${taskId}/status/`, method: 'get' })
}

// 构建记录
export function getBuildList(params) {
  return http({ url: '/api/jenkins/build/', method: 'get', params })
}

export function getAllureReport(params) {
  return http({ url: '/api/jenkins/report/by_build/', method: 'get', params })
}

// ==================== Jenkins节点管理 ====================

// 查询节点列表
export function getNodesList(params) {
  return http({ url: '/api/jenkins/nodes/', method: 'get', params })
}

// 创建SSH节点
export function createNode(data) {
  return http({ url: '/api/jenkins/nodes/create/', method: 'post', data })
}

// 获取节点配置和当前IP
export function getNodeConfig(nodeName) {
  return http({ url: `/api/jenkins/nodes/${nodeName}/config/`, method: 'get' })
}

// 获取节点详细信息
export function getNodeInfo(nodeName) {
  return http({ url: `/api/jenkins/nodes/${nodeName}/info/`, method: 'get' })
}

// 更新节点IP
export function updateNodeIP(nodeName, data) {
  return http({ url: `/api/jenkins/nodes/${nodeName}/ip/`, method: 'patch', data })
}

// 启用/禁用节点
export function toggleNode(nodeName, data) {
  return http({ url: `/api/jenkins/nodes/${nodeName}/toggle/`, method: 'post', data })
}

// 重新连接节点
export function reconnectNode(nodeName) {
  return http({ url: `/api/jenkins/nodes/${nodeName}/reconnect/`, method: 'post' })
}

// 更新节点标签
export function updateNodeLabels(nodeName, data) {
  return http({ url: `/api/jenkins/nodes/${nodeName}/labels/`, method: 'patch', data })
}

// 删除节点
export function deleteNode(nodeName) {
  return http({ url: `/api/jenkins/nodes/${nodeName}/delete/`, method: 'delete' })
}

// 从 Jenkins 同步所有节点到数据库
export function syncNodesFromJenkins() {
  return http({ url: '/api/jenkins/nodes/sync-from-jenkins/', method: 'post' })
}

// ==================== Jenkins凭证管理 ====================

// 获取凭证列表
export function getCredentialsList() {
  return http({ url: '/api/jenkins/credentials/', method: 'get' })
}

// 默认导出
export default {
  // 服务器管理
  getServerList,
  getJenkinsServers,
  addJenkinsServer,
  updateJenkinsServer,
  deleteJenkinsServer,
  testConnection,
  testConnectionById,
  // 任务管理
  getJobList,
  getJenkinsJobs,
  syncJenkinsJobs,
  createJenkinsJob,
  getJenkinsJobDetail,
  editJenkinsJob,
  deleteJenkinsJob,
  triggerBuild,
  buildJenkinsJob,
  getTaskStatus,
  getBuildList,
  getAllureReport,
  // 节点管理
  getNodesList,
  createNode,
  getNodeConfig,
  getNodeInfo,
  updateNodeIP,
  toggleNode,
  reconnectNode,
  updateNodeLabels,
  deleteNode,
  syncNodesFromJenkins,
  // 凭证管理
  getCredentialsList
}