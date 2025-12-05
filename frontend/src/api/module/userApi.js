import http from '../requests'

export default {
    // 登录接口
    login(params) {
        return http.post('/login/', params)
    },
    // 校验token是否有效
    verifyToken(params) {
        return http.post('/verify/', params)
    },
    // 注册接口
    register(params) {
        return http.post('/register/', params)
    },
    // 退出登录
    logout() {
        return http.post('/logout/')
    },
    // 获取所有用户
    getUser(params) {
        return http.get('/user/', {
            params: params
        })
    },
    // 修改用户
    updateUser(id, params) {
        return http.patch(`/user/${id}/`, params)
    },
    // 删除用户
    deleteUser(id) {
        return http.delete(`/user/${id}/`)
    }
}