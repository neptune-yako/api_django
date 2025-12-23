import http from './requests'

// Jenkins服务器管理
export function getServerList() {
  return http({ url: '/jenkins/server/', method: 'get' })
}

export function testConnection(id) {
  return http({ url: `/jenkins/server/${id}/test_connection/`, method: 'post' })
}

// Jenkins任务管理
export function getJobList(params) {
  return http({ url: '/jenkins/job/', method: 'get', params })
}

export function triggerBuild(data) {
  return http({ url: '/jenkins/job/trigger_build/', method: 'post', data })
}

// 构建记录
export function getBuildList(params) {
  return http({ url: '/jenkins/build/', method: 'get', params })
}

export function getAllureReport(params) {
  return http({ url: '/jenkins/report/by_build/', method: 'get', params })
}

// Jenkins节点管理
export function getNodesList(params) {
  return http({ url: '/api/jenkins/nodes/', method: 'get', params })
}



// 获取节点配置和当前IP
export function getNodeConfig(nodeName) {
  return http({ url: `/api/jenkins/nodes/${nodeName}/config/`, method: 'get' })
}

// 更新节点IP
export function updateNodeIP(nodeName, data) {
  return http({ url: `/api/jenkins/nodes/${nodeName}/ip/`, method: 'patch', data })
}

// 默认导出
export default {
  getServerList,
  testConnection,
  getJobList,
  triggerBuild,
  getBuildList,
  getAllureReport,
  getNodesList,
  getNodeConfig,
  updateNodeIP
}