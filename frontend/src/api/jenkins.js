import request from '@/api/requests'

// 获取 Jenkins 服务器列表
export function getJenkinsServers(params) {
  return request({
    url: '/api/jenkins/server/',
    method: 'get',
    params
  })
}

// 添加 Jenkins 服务器
export function addJenkinsServer(data) {
  return request({
    url: '/api/jenkins/server/',
    method: 'post',
    data
  })
}

// 更新 Jenkins 服务器
export function updateJenkinsServer(id, data) {
  return request({
    url: `/api/jenkins/server/${id}/`,
    method: 'put',
    data
  })
}

// 删除 Jenkins 服务器
export function deleteJenkinsServer(id) {
  return request({
    url: `/api/jenkins/server/${id}/`,
    method: 'delete'
  })
}

// 测试 Jenkins 连接
export function testJenkinsConnection(data) {
  return request({
    url: '/api/jenkins/test/',
    method: 'post',
    data
  })
}
