import request from '@/api/requests'

/**
 * ==================== Allure 报告代理 API ====================
 * 对应后端: backend/jenkins_integration/views/allure_views.py
 * 
 * 功能模块:
 * - Allure 报告代理访问 (解决跨域问题)
 * - 报告数据同步
 * 
 * 说明:
 * Jenkins Allure 报告通常有跨域限制，无法直接在前端访问
 * 后端提供代理接口，将 Jenkins 的 Allure 报告代理到自己的域名下
 */

/**
 * 获取 Allure 报告代理 URL (主页)
 * 
 * 注意: 这个 URL 通常用于在 iframe 中嵌入 Allure 报告
 * 
 * @param {string} jobName - Job 名称
 * @param {number} buildNumber - 构建编号
 * @returns {string} 代理 URL
 * 
 * @example
 * const url = getAllureProxyUrl('test-job', 123)
 * // 返回: '/api/jenkins/allure-proxy/test-job/123/'
 * 
 * // 在 iframe 中使用
 * <iframe :src="getAllureProxyUrl(jobName, buildNumber)" />
 */
export function getAllureProxyUrl(jobName, buildNumber) {
    return `/api/jenkins/allure-proxy/${jobName}/${buildNumber}/`
}

/**
 * 获取 Allure 报告代理 URL (指定文件)
 * 
 * @param {string} jobName - Job 名称
 * @param {number} buildNumber - 构建编号
 * @param {string} filePath - 文件路径 (如 'index.html', 'data/suites.json')
 * @returns {string} 代理 URL
 * 
 * @example
 * const url = getAllureProxyFileUrl('test-job', 123, 'data/suites.json')
 * // 返回: '/api/jenkins/allure-proxy/test-job/123/data/suites.json'
 */
export function getAllureProxyFileUrl(jobName, buildNumber, filePath) {
    return `/api/jenkins/allure-proxy/${jobName}/${buildNumber}/${filePath}`
}

/**
 * NOTE: Allure 代理接口不需要直接调用，通常通过 iframe 嵌入
 * 如果需要获取报告数据，请使用 build.js 中的 getBuildAllureUrl
 */
