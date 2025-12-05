import http from '../requests'

export default {
    // 获取项目列表的接口
    getProject(params) {
        return http.get('/project/', {
            params: params
        })
    },
    // 添加项目
    createProject(params) {
        return http.post('/project/', params)
    },
    // 删除项目
    deleteProject(id) {
        return http.delete(`/project/${id}/`)
    },
    // 编辑项目的接口
    updateProject(id, params) {
        return http.patch(`/project/${id}/`, params)
    },
    // 添加获取项目详情
    getProjectDetail(id) {
        return http.get(`/project/${id}/`)
    }
}