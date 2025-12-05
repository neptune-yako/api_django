import http from '../requests'

export default {
    runCase(params) {
        return http.post('/case/run/', params)
    },
    // 获取用例详情的接口
    getCaseInfo(id) {
        return http.get(`/case/${id}/`)
    },
    // 添加测试用例
    createCase(params) {
        return http.post('/case/', params)
    },
    // 修改用例
    updateCase(id, params) {
        return http.patch(`/case/${id}/`, params)
    },
    // 删除用例
    deleteCase(id) {
        return http.delete(`/case/${id}/`)
    }
}