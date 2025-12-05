import http from '../requests'

export default {
    // 获取所有角色
    getRole() {
        return http.get('/role/')
    },
    // 创建角色
    createRole(params) {
        return http.post('/role/', params)
    },
    // 更新角色
    updateRole(id, params) {
        return http.patch(`/role/${id}/`, params)
    },
    // 删除角色
    deleteRole(id) {
        return http.delete(`/role/${id}/`)
    }
}