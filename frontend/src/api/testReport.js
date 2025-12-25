/**
 * 测试报告相关 API
 */
import http from '@/api/requests'

/**
 * 单次同步 Allure 报告
 * @param {Object} data - { job_name, build_number }
 */
export function syncSingleReport(data) {
    return http({ url: '/api/test-report/sync/', method: 'post', data })
}

/**
 * 批量同步 Job 构建报告
 * @param {Object} data - { job_name, start_build, end_build }
 */
export function syncJobBuilds(data) {
    return http({ url: '/api/test-report/sync-job/', method: 'post', data })
}

/**
 * 查询任务状态
 * @param {String} taskId - 任务 ID
 */
export function getTaskStatus(taskId) {
    return http({ url: `/api/test-report/task-status/${taskId}/`, method: 'get' })
}

/**
 * 查询测试执行列表
 * @param {Object} params - { job_id, page, size, start_date, end_date }
 */
export function getExecutionList(params) {
    return http({ url: '/api/test-report/executions/', method: 'get', params })
}

/**
 * 查询测试执行详情
 * @param {Number} id - 执行记录 ID
 */
export function getExecutionDetail(id) {
    return http({ url: `/api/test-report/executions/${id}/`, method: 'get' })
}
