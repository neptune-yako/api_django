import http from '../requests'

export default {
    // 获取测试环境列表
    getEnvironment(id) {
        return http.get('/environment/', {
            params: {
                project: id
            }
        })
    },
    // 获取环境信息
    getEnvironmentInfo(params) {
        return http.get(`/environment/${params}/`)
    },
    // 添加测试环境
    createEnvironment(params) {
        return http.post('/environment/', params)
    },
    // 修改测试环境
    updateEnvironment(id, params) {
        return http.patch(`/environment/${id}/`, params)
    },
    // 删除测试环境
    deleteEnvironment(id) {
        return http.delete(`/environment/${id}/`)
    }
}