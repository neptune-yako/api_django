import http from '../requests'

export default {
    // 获取测试套件列表
    getScene(params) {
        return http.get('/scene/', {
            params: params
        })
    },
    // 添加测试套件
    createScene(params) {
        return http.post('/scene/', params)
    },
    // 更新测试套件
    updateScene(id, params) {
        return http.patch(`/scene/${id}/`, params)
    },
    // 删除测试套件
    deleteScene(id) {
        return http.delete(`/scene/${id}/`)
    },
    // 运行测试套件
    runScene(params) {
        return http.post('/scene/run/', params)
    },
    // 获取测试套件中的所有用例
    getStep(id, params) {
        return http.get('/step/', {
            params: {
                scene: id,
                ...params
            }
        })
    },
    // 往测试套件中添加用例步骤
    createStep(params) {
        return http.post('/step/', params)
    },
    // 删除测试套件中的用例步骤
    deleteStep(id) {
        return http.delete(`/step/${id}/`)
    },
    // 修改测试套件中用例执行的顺序
    updateStepOrder(params) {
        return http.patch('/step/order/', params)
    }
}