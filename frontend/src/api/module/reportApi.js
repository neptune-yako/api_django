import http from '../requests'

export default {
    // 获取测试报告数据
    getReport(id) {
        return http.get(`/report/${id}/`)
    }
}