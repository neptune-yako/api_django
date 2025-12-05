import http from '../requests'

export default {
    // 添加接口
    createInterface(params) {
        return http.post('/interface/', params)
    },
    // 获取接口列表
    getInterface(params) {
        return http.get('/interface/', {
            params: params
        })
    },
    // 编辑接口
    updateInterface(id, params) {
        return http.patch(`/interface/${id}/`, params)
    },
    // 删除接口
    deleteInterface(id) {
        return http.delete(`/interface/${id}/`)
    }
}