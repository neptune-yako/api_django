import http from "../requests"

export default {
    //获取所有测试运行记录的接口
    getRecord(params) {
        return http.get('/record/', {
            params: params
        })
    },
    getRecordInfo(id) {
        return http.get(`/record/${id}/`)
    },
    // 删除测试记录
    deleteRecord(id) {
        return http.delete(`/record/${id}/`)
    },
}