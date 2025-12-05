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
    }
}