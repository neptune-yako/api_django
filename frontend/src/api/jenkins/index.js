/**
 * ==================== Jenkins API 统一导出 ====================
 * 
 * 所有 Jenkins 相关接口的导出汇总
 * 类似后端的 urls.py，作为 API 的"目录"
 * 
 * 使用方式:
 * import { getJenkinsServers, buildJenkinsJob } from '@/api/jenkins'
 */

// ==================== 服务器管理 ====================
export { getJenkinsServers } from './server'        // 获取服务器列表
export { addJenkinsServer } from './server'         // 添加服务器
export { updateJenkinsServer } from './server'      // 更新服务器
export { deleteJenkinsServer } from './server'      // 删除服务器
export { testJenkinsConnection } from './server'    // 测试连接 (手动输入凭据)
export { testConnectionById } from './server'       // 测试连接 (通过 ID)

// ==================== Job 管理 ====================
export { getJenkinsJobs } from './job'              // 获取 Job 列表 (本地 DB)
export { syncJenkinsJobs } from './job'             // 同步 Jobs (异步任务)
export { getTaskStatus } from './job'               // 查询任务状态
export { buildJenkinsJob } from './job'             // 触发构建
export { copyJenkinsJob } from './job'              // 复制 Job
export { toggleJenkinsJob } from './job'            // 启用/禁用 Job
export { updateJobRelation } from './job'           // 更新本地关联信息
export { editJenkinsJob } from './job'              // 编辑 Job (同步 Jenkins + DB)
export { createJenkinsJob } from './job'            // 创建 Job

// ==================== 构建管理 ====================
export { getBuildLatestStatus } from './build'      // 查询最新构建状态 (轮询用)
export { getBuildAllureUrl } from './build'         // 获取 Allure 报告 URL
export { syncBuildResult } from './build'           // 同步构建结果到数据库

// ==================== Allure 报告 ====================
export { getAllureProxyUrl } from './allure'        // 获取 Allure 代理 URL (主页)
export { getAllureProxyFileUrl } from './allure'    // 获取 Allure 代理 URL (指定文件)

// ==================== 模板管理 ====================
export { getJenkinsTemplates } from './template'    // 获取模板列表
export { getJenkinsTemplateDetail } from './template' // 获取模板详情

// ==================== 节点管理 ====================
export { getNodesList } from './node'               // 获取节点列表
export { getNodeConfig } from './node'              // 获取节点配置
export { updateNodeIP } from './node'               // 更新节点IP

// ==================== 默认导出（兼容旧的导入方式） ====================
import * as server from './server'
import * as job from './job'
import * as build from './build'
import * as allure from './allure'
import * as template from './template'
import * as node from './node'

export default {
    ...server,
    ...job,
    ...build,
    ...allure,
    ...template,
    ...node
}
