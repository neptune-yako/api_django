import request from '@/api/requests'

/**
 * ==================== Jenkins 服务器管理 API ====================
 * 对应后端: backend/jenkins_integration/views/server_views.py
 * 
 * 功能模块:
 * - 服务器 CRUD (增删改查)
 * - 连接测试
 */

/**
 * 获取 Jenkins 服务器列表
 * GET /api/jenkins/server/
 * 
 * @param {Object} [params] - 查询参数
 * @param {string} [params.name] - 服务器名称（模糊搜索）
 * @param {boolean} [params.is_active] - 是否启用
 * @param {number} [params.page] - 页码
 * @param {number} [params.page_size] - 每页数量
 * 
 * @returns {Promise<{code: number, data: Array<Object>, message: string}>}
 * @returns {number} return.code - 200 成功, 5xxx 错误
 * @returns {Array} return.data - 服务器列表
 * @returns {Object} return.data[].id - 服务器 ID
 * @returns {string} return.data[].name - 服务器名称
 * @returns {string} return.data[].url - Jenkins URL
 * @returns {string} return.data[].username - 用户名
 * @returns {boolean} return.data[].is_active - 是否启用
 * @returns {string} return.data[].connection_status - 连接状态: connected/failed/unknown
 * @returns {string} return.data[].last_check_time - 最后检查时间
 * @returns {number} return.data[].jobs_count - Job 数量
 * @returns {number} return.data[].nodes_count - Node 数量
 * 
 * @example
 * const servers = await getJenkinsServers({ name: 'prod' })
 * console.log(servers.data) // [{ id: 1, name: 'Jenkins-Prod', ... }]
 */
export function getJenkinsServers(params) {
    return request({
        url: '/api/jenkins/server/',
        method: 'get',
        params
    })
}

/**
 * 添加 Jenkins 服务器
 * POST /api/jenkins/server/
 * 
 * @param {Object} data - 服务器信息
 * @param {string} data.name - 服务器名称 (必填)
 * @param {string} data.url - Jenkins URL (必填, 例如: http://jenkins.example.com)
 * @param {string} data.username - 用户名 (必填)
 * @param {string} data.token - API Token (必填, write-only)
 * @param {boolean} [data.is_active=true] - 是否启用
 * @param {string} [data.description] - 描述
 * 
 * @returns {Promise<{code: number, data: Object, message: string}>}
 * @returns {number} return.code - 200 成功, 400 参数错误, 5001 Jenkins 连接失败
 * 
 * @example
 * const result = await addJenkinsServer({
 *   name: 'Jenkins-Prod',
 *   url: 'http://jenkins.example.com',
 *   username: 'admin',
 *   token: 'your-api-token',
 *   is_active: true
 * })
 */
export function addJenkinsServer(data) {
    return request({
        url: '/api/jenkins/server/',
        method: 'post',
        data
    })
}

/**
 * 更新 Jenkins 服务器
 * PUT /api/jenkins/server/{id}/
 * 
 * @param {number} id - 服务器 ID
 * @param {Object} data - 更新的服务器信息
 * @param {string} [data.name] - 服务器名称
 * @param {string} [data.url] - Jenkins URL
 * @param {string} [data.username] - 用户名
 * @param {string} [data.token] - API Token (可选, 留空则保持不变)
 * @param {boolean} [data.is_active] - 是否启用
 * @param {string} [data.description] - 描述
 * 
 * @returns {Promise<{code: number, data: Object, message: string}>}
 * 
 * @example
 * // 只更新名称，不改 token
 * await updateJenkinsServer(1, { name: 'Jenkins-Prod-New' })
 * 
 * // 更新 token
 * await updateJenkinsServer(1, { token: 'new-token' })
 */
export function updateJenkinsServer(id, data) {
    return request({
        url: `/api/jenkins/server/${id}/`,
        method: 'put',
        data
    })
}

/**
 * 删除 Jenkins 服务器
 * DELETE /api/jenkins/server/{id}/
 * 
 * @param {number} id - 服务器 ID
 * 
 * @returns {Promise<{code: number, message: string}>}
 * @returns {number} return.code - 200 成功, 404 服务器不存在
 * 
 * @example
 * await deleteJenkinsServer(1)
 */
export function deleteJenkinsServer(id) {
    return request({
        url: `/api/jenkins/server/${id}/`,
        method: 'delete'
    })
}

/**
 * 测试 Jenkins 连接
 * POST /api/jenkins/test/
 * 
 * @param {Object} data - 连接信息
 * @param {string} data.url - Jenkins URL (必填)
 * @param {string} data.username - 用户名 (必填)
 * @param {string} data.token - API Token (必填)
 * 
 * @returns {Promise<{code: number, data: Object, message: string}>}
 * @returns {Object} return.data - 连接结果
 * @returns {string} return.data.version - Jenkins 版本
 * @returns {Object} return.data.user - 用户信息
 * @returns {string} return.data.user.id - 用户 ID
 * @returns {string} return.data.user.fullName - 用户全名
 * 
 * @throws {Error} 连接失败时抛出错误 (code: 5001)
 * 
 * @example
 * try {
 *   const result = await testJenkinsConnection({
 *     url: 'http://jenkins.example.com',
 *     username: 'admin',
 *     token: 'test-token'
 *   })
 *   console.log('Jenkins 版本:', result.data.version)
 * } catch (error) {
 *   console.error('连接失败:', error.message)
 * }
 */
export function testJenkinsConnection(data) {
    return request({
        url: '/api/jenkins/test/',
        method: 'post',
        data
    })
}

/**
 * 通过服务器 ID 测试连接 (推荐)
 * POST /api/jenkins/server/{id}/test-connection/
 * 
 * 后端从数据库获取完整凭据进行测试，前端无需传递敏感信息
 * 适用于已保存的服务器，避免 token write_only 导致的前端无法获取问题
 * 
 * @param {number} id - 服务器 ID
 * 
 * @returns {Promise<{code: number, data: Object, message: string}>}
 * @returns {Object} return.data - 连接结果
 * @returns {string} return.data.version - Jenkins 版本
 * @returns {Object} return.data.user - 用户信息
 * 
 * @example
 * try {
 *   const result = await testConnectionById(1)
 *   console.log('连接成功!, Jenkins 版本:', result.data.version)
 * } catch (error) {
 *   console.error('连接失败:', error.message)
 * }
 */
export function testConnectionById(id) {
    return request({
        url: `/api/jenkins/server/${id}/test-connection/`,
        method: 'post'
    })
}
