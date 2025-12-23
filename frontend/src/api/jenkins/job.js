import request from '@/api/requests'

/**
 * ==================== Jenkins Job 管理 API ====================
 * 对应后端: 
 * - backend/jenkins_integration/views/job_local_views.py (本地数据)
 * - backend/jenkins_integration/views/job_remote_views.py (远程操作)
 * 
 * 功能模块:
 * - Job 列表查询 (本地数据库)
 * - Job 同步 (从 Jenkins 拉取)
 * - Job 构建触发
 * - Job 复制
 * - Job 启用/禁用
 */

/**
 * 获取 Jenkins Job 列表 (本地数据)
 * GET /api/jenkins/pipeline/
 * 
 * @param {Object} [params] - 查询参数
 * @param {string} [params.name] - Job 名称（模糊搜索）
 * @param {number} [params.server] - 服务器 ID
 * @param {number} [params.project] - 项目 ID
 * @param {number} [params.plan] - 测试计划 ID
 * @param {number} [params.environment] - 环境 ID
 * @param {boolean} [params.is_active] - 是否启用
 * 
 * @returns {Promise<{code: number, data: Array<Object>, message: string}>}
 * @returns {Object} return.data[] - Job 列表
 * @returns {number} return.data[].id - Job ID
 * @returns {string} return.data[].name - Job 名称
 * @returns {string} return.data[].server_name - 所属服务器
 * @returns {string} return.data[].last_build_status - 最后构建状态: SUCCESS/FAILURE/UNSTABLE/ABORTED
 * @returns {number} return.data[].last_build_number - 最后构建编号
 * @returns {string} return.data[].last_build_time - 最后构建时间
 * @returns {boolean} return.data[].is_buildable - 是否可构建
 * @returns {string} return.data[].job_type - Job 类型
 * 
 * @example
 * // 获取所有 Job
 * const jobs = await getJenkinsJobs()
 * 
 * // 搜索特定名称
 * const jobs = await getJenkinsJobs({ name: 'test' })
 * 
 * // 按服务器筛选
 * const jobs = await getJenkinsJobs({ server: 1 })
 */
export function getJenkinsJobs(params) {
    return request({
        url: '/api/jenkins/pipeline/',
        method: 'get',
        params
    })
}

/**
 * 同步 Jenkins Jobs (异步任务)
 * POST /api/jenkins/jobs/sync/
 * 
 * 从 Jenkins 服务器拉取所有 Job 信息并更新到本地数据库
 * 注意: 这是一个异步任务，会在后台执行，不会立即返回结果
 * 
 * @returns {Promise<{code: number, data: Object, message: string}>}
 * @returns {Object} return.data - 任务信息
 * @returns {string} return.data.task_id - Celery 任务 ID
 * 
 * @example
 * const result = await syncJenkinsJobs()
 * console.log('同步任务已启动, ID:', result.data.task_id)
 * // 建议延迟 2-3 秒后刷新列表
 * setTimeout(() => {
 *   fetchJobList()
 * }, 3000)
 */
export function syncJenkinsJobs() {
    return request({
        url: '/api/jenkins/jobs/sync/',
        method: 'post'
    })
}

/**
 * 触发 Job 构建
 * POST /api/jenkins/job/build/
 * 
 * @param {Object} data - 构建参数
 * @param {string} data.job_name - Job 名称 (必填)
 * @param {Object} [data.parameters] - 构建参数 (可选, 参数化构建时使用)
 * @param {string} [data.parameters.BRANCH] - 分支名称 (示例)
 * @param {string} [data.parameters.ENV] - 环境变量 (示例)
 * 
 * @returns {Promise<{code: number, data: Object, message: string}>}
 * @returns {number} return.code - 200 成功, 5005 构建失败
 * @returns {Object} return.data - 构建信息
 * @returns {number} return.data.build_number - 构建编号 (如果有)
 * 
 * @example
 * // 简单构建
 * await buildJenkinsJob({ job_name: 'test-job' })
 * 
 * // 参数化构建
 * await buildJenkinsJob({
 *   job_name: 'test-job',
 *   parameters: {
 *     BRANCH: 'master',
 *     ENV: 'production'
 *   }
 * })
 */
export function buildJenkinsJob(data) {
    return request({
        url: '/api/jenkins/job/build/',
        method: 'post',
        data
    })
}

/**
 * 复制 Job
 * POST /api/jenkins/job/copy/
 * 
 * @param {Object} data - 复制参数
 * @param {string} data.source_job - 源 Job 名称 (必填)
 * @param {string} data.new_job - 新 Job 名称 (必填)
 * 
 * @returns {Promise<{code: number, data: Object, message: string}>}
 * @returns {number} return.code - 200 成功, 5002 源 Job 不存在, 5003 新 Job 已存在
 * 
 * @example
 * await copyJenkinsJob({
 *   source_job: 'test-job',
 *   new_job: 'test-job-copy'
 * })
 */
export function copyJenkinsJob(data) {
    return request({
        url: '/api/jenkins/job/copy/',
        method: 'post',
        data
    })
}

/**
 * 启用/禁用 Job
 * POST /api/jenkins/job/toggle/
 * 
 * @param {Object} data - 操作参数
 * @param {string} data.job_name - Job 名称 (必填)
 * @param {string} data.action - 操作类型: 'enable' | 'disable' (必填)
 * 
 * @returns {Promise<{code: number, message: string}>}
 * @returns {number} return.code - 200 成功, 5002 Job 不存在
 * 
 * @example
 * // 启用 Job
 * await toggleJenkinsJob({ job_name: 'test-job', action: 'enable' })
 * 
 * // 禁用 Job
 * await toggleJenkinsJob({ job_name: 'test-job', action: 'disable' })
 */
export function toggleJenkinsJob(data) {
    return request({
        url: '/api/jenkins/job/toggle/',
        method: 'post',
        data
    })
}

/**
 * 更新 Job 本地关联信息
 * PUT /api/jenkins/pipeline/{id}/
 * 
 * 只更新本地数据库中的关联字段 (project, plan, environment)
 * 不会修改 Jenkins 服务器上的 Job 配置
 * 
 * @param {number} id - Job ID
 * @param {Object} data - 更新数据
 * @param {number} [data.project] - 关联项目 ID
 * @param {number} [data.plan] - 关联测试计划 ID
 * @param {number} [data.environment] - 关联环境 ID
 * 
 * @returns {Promise<{code: number, data: Object, message: string}>}
 * 
 * @example
 * await updateJobRelation(1, {
 *   project: 5,
 *   plan: 10,
 *   environment: 2
 * })
 */
export function updateJobRelation(id, data) {
    return request({
        url: `/api/jenkins/pipeline/${id}/`,
        method: 'put',
        data
    })
}
