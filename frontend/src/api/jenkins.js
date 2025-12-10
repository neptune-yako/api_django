import request from '@/utils/request'

// Jenkins服务器管理
export function getServerList() {
  return request({ url: '/jenkins/server/', method: 'get' })
}

export function testConnection(id) {
  return request({ url: `/jenkins/server/${id}/test_connection/`, method: 'post' })
}

// Jenkins任务管理
export function getJobList(params) {
  return request({ url: '/jenkins/job/', method: 'get', params })
}

export function triggerBuild(data) {
  return request({ url: '/jenkins/job/trigger_build/', method: 'post', data })
}

// 构建记录
export function getBuildList(params) {
  return request({ url: '/jenkins/build/', method: 'get', params })
}

export function getAllureReport(params) {
  return request({ url: '/jenkins/report/by_build/', method: 'get', params })
}