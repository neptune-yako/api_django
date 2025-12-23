import request from '@/api/requests'

/**
 * ==================== Jenkins Job 模板管理 API ====================
 * 对应后端: backend/jenkins_integration/views/template_views.py
 * 
 * 功能模块:
 * - 获取模板列表
 * - 获取指定模板内容
 * 
 * 说明:
 * Job 模板用于快速创建预定义配置的 Jenkins Job
 * 后端提供多种类型的模板 (如 maven, gradle, python 等)
 */

/**
 * 获取所有可用模板列表
 * GET /api/jenkins/templates/
 * 
 * @returns {Promise<{code: number, data: Array<Object>, message: string}>}
 * @returns {Object} return.data[] - 模板列表
 * @returns {string} return.data[].type - 模板类型 (如 'maven', 'gradle', 'python')
 * @returns {string} return.data[].name - 模板名称 (如 'Maven 项目模板')
 * @returns {string} return.data[].description - 模板描述
 * 
 * @example
 * const templates = await getJenkinsTemplates()
 * console.log(templates.data)
 * // [
 * //   { type: 'maven', name: 'Maven 项目模板', description: '...' },
 * //   { type: 'gradle', name: 'Gradle 项目模板', description: '...' }
 * // ]
 */
export function getJenkinsTemplates() {
    return request({
        url: '/api/jenkins/templates/',
        method: 'get'
    })
}

/**
 * 获取指定类型的模板内容
 * GET /api/jenkins/template/{template_type}/
 * 
 * @param {string} templateType - 模板类型 (如 'maven', 'gradle', 'python')
 * 
 * @returns {Promise<{code: number, data: Object, message: string}>}
 * @returns {Object} return.data - 模板内容
 * @returns {string} return.data.type - 模板类型
 * @returns {string} return.data.name - 模板名称
 * @returns {string} return.data.config_xml - Jenkins Job 配置 XML
 * @returns {Object} return.data.parameters - 可配置参数说明
 * 
 * @example
 * const template = await getJenkinsTemplateDetail('maven')
 * console.log('XML 配置:', template.data.config_xml)
 * 
 * // 可以用这个 XML 创建新 Job:
 * // await createJob({ job_name: 'new-job', config_xml: template.data.config_xml })
 */
export function getJenkinsTemplateDetail(templateType) {
    return request({
        url: `/api/jenkins/template/${templateType}/`,
        method: 'get'
    })
}
