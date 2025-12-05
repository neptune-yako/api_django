import http from '../requests'

export default {
    // 获取所有bug
    getBug(params) {
        return http.get('/bug/', {
            params: params
        })
    },
    // 提交bug记录
    createBug(params) {
        return http.post('/bug/', params)
    },
    // 修改bug状态
    updateBug(id, params) {
        return http.patch(`/bug/${id}/`, params)
    },
    // 查看bug详情
    getBugInfo(id) {
        return http.get(`/bug/${id}/`)
    },
    // 删除bug
    deleteBug(id) {
        return http.delete(`/bug/${id}/`)
    }
}