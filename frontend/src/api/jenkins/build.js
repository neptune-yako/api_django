import request from '@/api/requests'

/**
 * ==================== Jenkins 构建状态查询 API ====================
 * 对应后端: backend/jenkins_integration/views/build_views.py
 * 
 * 功能模块:
 * - 查询最新构建状态 (用于前端轮询)
 * - 获取 Allure 报告 URL
 * - 同步构建结果到数据库
 */

/**
 * 查询最新构建状态
 * GET /api/jenkins/build/latest/
 * 
 * 用于前端轮询，实时获取 Job 的最新构建状态
 * 
 * @param {Object} params - 查询参数
 * @param {string} params.job_name - Job 名称 (必填)
 * 
 * @returns {Promise<{code: number, data: Object, message: string}>}
 * @returns {Object} return.data - 构建信息
 * @returns {number} return.data.build_number - 构建编号
 * @returns {string} return.data.result - 构建结果: SUCCESS/FAILURE/ABORTED/UNSTABLE/null(构建中)
 * @returns {boolean} return.data.building - 是否正在构建
 * @returns {number} return.data.duration - 持续时间 (毫秒)
 * @returns {string} return.data.duration_text - 持续时间文本 (如 "5.23秒")
 * @returns {string} return.data.status_text - 状态文本 (如 "正在构建中", "构建成功")
 * @returns {string} return.data.url - 构建 URL
 * @returns {number} return.data.timestamp - 构建开始时间戳
 * 
 * @example
 * // 轮询构建状态
 * const timer = setInterval(async () => {
 *   const result = await getBuildLatestStatus({ job_name: 'test-job' })
 *   if (result.data.building === false) {
 *     clearInterval(timer) // 构建完成，停止轮询
 *     console.log('构建结果:', result.data.result)
 *   }
 * }, 2000) // 每 2 秒查询一次
 */
export function getBuildLatestStatus(params) {
    return request({
        url: '/api/jenkins/build/latest/',
        method: 'get',
        params
    })
}

/**
 * 获取 Allure 报告 URL
 * GET /api/jenkins/build/allure/
 * 
 * @param {Object} params - 查询参数
 * @param {string} params.job_name - Job 名称 (必填)
 * @param {number} params.build_number - 构建编号 (必填)
 * 
 * @returns {Promise<{code: number, data: Object, message: string}>}
 * @returns {Object} return.data - Allure 报告信息
 * @returns {string} return.data.allure_url - Allure 报告 URL (可能通过代理访问)
 * @returns {boolean} return.data.exists - 报告是否存在
 * 
 * @example
 * const result = await getBuildAllureUrl({
 *   job_name: 'test-job',
 *   build_number: 123
 * })
 * if (result.data.exists) {
 *   window.open(result.data.allure_url) // 打开报告
 * }
 */
export function getBuildAllureUrl(params) {
    return request({
        url: '/api/jenkins/build/allure/',
        method: 'get',
        params
    })
}

/**
 * 同步构建结果到数据库
 * POST /api/jenkins/build/sync/
 * 
 * 将 Jenkins 构建结果和 Allure 报告数据同步到本地数据库
 * 注意: 这是一个异步任务
 * 
 * @param {Object} data - 同步参数
 * @param {string} data.job_name - Job 名称 (必填)
 * @param {number} data.build_number - 构建编号 (必填)
 * 
 * @returns {Promise<{code: number, data: Object, message: string}>}
 * @returns {Object} return.data - 同步任务信息
 * @returns {string} return.data.task_id - Celery 任务 ID
 * 
 * @example
 * const result = await syncBuildResult({
 *   job_name: 'test-job',
 *   build_number: 123
 * })
 * console.log('同步任务已启动:', result.data.task_id)
 */
export function syncBuildResult(data) {
    return request({
        url: '/api/jenkins/build/sync/',
        method: 'post',
        data
    })
}

/**
 * 检查 Job 的动态参数
 * GET /api/jenkins/job/{job_id}/check_params
 * 
 * 用于参数化构建前检查 Job 是否包含动态参数
 * 
 * @param {number} jobId - Job 的数据库 ID
 * 
 * @returns {Promise<{code: number, data: Object, message: string}>}
 * @returns {Object} return.data - 参数信息
 * @returns {Array<string>} return.data.params - 参数名列表，如 ['score', 'env']
 * 
 * @example
 * const result = await checkJobParams(36)
 * console.log('检测到参数:', result.data.params)
 */
export function checkJobParams(jobId) {
    return request({
        url: `/api/jenkins/job/${jobId}/check_params`,
        method: 'get'
    })
}
