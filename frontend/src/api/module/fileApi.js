import http from '../requests'

export default {
    // 上传文件接口信息
    uploadFile: {
        url: http.defaults.baseURL + '/file/',
    },
    // 获取文件列表
    getFile(params) {
        return http.get('/file/', {
            params: params
        })
    },
    // 删除文件
    deleteFile(id) {
        return http.delete(`/file/${id}/`)
    }
}