import http from '../requests'

export default {
    //获取定时任务列表
    getCronjob(id, params) {
        return http.get('/cronjob/', {
            params: {
                project: id,
                ...params
            }
        })
    },
    // 删除定时任务
    deleteCronjob(id) {
        return http.delete(`/cronjob/${id}/`)
    },
    // 添加定时任务
    createCronjob(params) {
        return http.post('/cronjob/', params)
    },
    // 修改定时任务
    updateCronjob(id, params) {
        return http.patch(`/cronjob/${id}/`, params)
    }
}