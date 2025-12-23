import request from '@/api/requests'

/**
 * ==================== Jenkins 节点管理 API ====================
 * 对应后端: backend/jenkins_integration/views/node_views.py
 * 
 * 功能模块:
 * - 节点列表查询
 * - 节点配置获取
 * - 节点 IP 更新
 */

/**
 * 获取 Jenkins 节点列表
 * GET /api/jenkins/nodes/
 * 
 * @param {Object} [params] - 查询参数
 * @param {string} [params.name] - 节点名称（模糊搜索）
 * @param {boolean} [params.offline] - 是否离线
 * @param {number} [params.page] - 页码
 * @param {number} [params.page_size] - 每页数量
 * 
 * @returns {Promise<{code: number, data: Array<Object>, message: string}>}
 * @returns {Object} return.data[] - 节点列表
 * @returns {string} return.data[].name - 节点名称
 * @returns {string} return.data[].displayName - 显示名称
 * @returns {string} return.data[].description - 描述
 * @returns {number} return.data[].numExecutors - 执行器数量
 * @returns {string} return.data[].labels - 标签
 * @returns {string} return.data[].ip_address - IP地址
 * @returns {boolean} return.data[].offline - 是否离线
 * @returns {boolean} return.data[].idle - 是否空闲
 * @returns {string} return.data[].offlineCauseReason - 离线原因
 * 
 * @example
 * const nodes = await getNodesList()
 * console.log(nodes.data) // [{ name: 'node-1', ip_address: '192.168.1.100', ... }]
 */
export function getNodesList(params) {
    return request({
        url: '/api/jenkins/nodes/',
        method: 'get',
        params
    })
}

/**
 * 获取节点配置和当前IP
 * GET /api/jenkins/nodes/{node_name}/config/
 * 
 * @param {string} nodeName - 节点名称
 * 
 * @returns {Promise<{code: number, data: Object, message: string}>}
 * @returns {Object} return.data - 节点配置信息
 * @returns {string} return.data.node_name - 节点名称
 * @returns {string} return.data.current_ip - 当前IP地址
 * @returns {string} return.data.ssh_port - SSH端口
 * @returns {string} return.data.config_xml - 完整配置XML（可选）
 * 
 * @example
 * const config = await getNodeConfig('node-1')
 * console.log('当前IP:', config.data.current_ip)
 * console.log('SSH端口:', config.data.ssh_port)
 */
export function getNodeConfig(nodeName) {
    return request({
        url: `/api/jenkins/nodes/${nodeName}/config/`,
        method: 'get'
    })
}

/**
 * 更新节点IP地址
 * PATCH /api/jenkins/nodes/{node_name}/ip/
 * 
 * @param {string} nodeName - 节点名称
 * @param {Object} data - 更新数据
 * @param {string} data.new_ip - 新的IP地址（必填）
 * @param {string} [data.ssh_port] - SSH端口（可选）
 * 
 * @returns {Promise<{code: number, data: Object, message: string}>}
 * @returns {Object} return.data - 更新结果
 * @returns {string} return.data.node_name - 节点名称
 * @returns {string} return.data.old_ip - 旧IP地址
 * @returns {string} return.data.new_ip - 新IP地址
 * @returns {boolean} return.data.updated - 是否成功更新
 * 
 * @example
 * const result = await updateNodeIP('node-1', {
 *   new_ip: '192.168.1.101',
 *   ssh_port: '22'
 * })
 * console.log('IP更新:', result.data.old_ip, '→', result.data.new_ip)
 */
export function updateNodeIP(nodeName, data) {
    return request({
        url: `/api/jenkins/nodes/${nodeName}/ip/`,
        method: 'patch',
        data
    })
}
