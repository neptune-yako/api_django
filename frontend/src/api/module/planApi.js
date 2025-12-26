import http from '../requests'

export default {
    // 获取测试计划列表
    getPlan(params) {
        return http.get('/plan/', {
            params: params
        })
    },
    // 创建测试计划
    createPlan(params) {
        return http.post('/plan/', params)
    },
    // 修改测试计划
    updatePlan(id, params) {
        return http.patch(`/plan/${id}/`, params)
    },
    // 删除测试计划
    deletePlan(id) {
        return http.delete(`/plan/${id}/`)
    },
    // 获取单个测试计划
    getPlanInfo(id) {
        return http.get(`/plan/${id}/`)
    },
    // 运行测试计划
    runPlan(params) {
        return http.post('/plan/run/', params)
    },
    // 导出测试计划脚本
    exportPlanScript(id, params) {
        return http.post(`/plan/${id}/export_script/`, params, {
            responseType: 'blob'
        })
    },
    // 上传Python测试脚本
    uploadScript(id, formData) {
        return http.post(`/plan/${id}/upload_script/`, formData, {
            headers: {
                'Content-Type': 'multipart/form-data'
            }
        })
    },
    // 下载测试脚本
    downloadScript(id) {
        return http.get(`/plan/${id}/download_script/`, {
            responseType: 'blob'
        })
    },
    // 解绑测试脚本
    unbindScript(id, params) {
        return http.post(`/plan/${id}/unbind_script/`, params)
    }
}