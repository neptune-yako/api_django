import axios from 'axios'
import { UserStore } from '@/stores/module/UserStore'
import { ElNotification } from 'element-plus'
import router from "@/router/index.js"

// 创建一个axios实例对象
const request = axios.create({
    // 后端接口的域名设置
    baseURL: import.meta.env.VITE_BASE_API,
    // ==================== 修改点 1: 优化 validateStatus ====================
    // 只将 2xx 视为成功，4xx/5xx 会自动进入 error 拦截器
    // 适配两种后端格式：
    // - Jenkins: 固定返回 200，通过 code 字段判断
    // - 其他模块: 使用标准 HTTP 状态码（200成功 / 400参数错误 / 500服务器错误）
    validateStatus: function (status) {
        return status >= 200 && status < 300  // 只有 2xx 算成功
    },
    // 跨域请求时是否需要使用凭证
    withCredentials: false,
    // 是否允许跨域
    crossDomain: true,
    // 设置请求头
    headers: { 'Content-Type': 'application/json;charset=utf-8' },
    // 接口请求超时时间10s
    timeout: 10000
})

// 请求拦截器，获取token添加到请求头中
request.interceptors.request.use(
    config => {
        // 在发送请求之前做些什么，对登录、注册、刷新、校验接口不做token校验
        if (config.url !== '/login/' && config.url !== '/register/' && config.url !== '/verify/' && config.url !== '/refresh/') {
            // 在请求配置中添加token
            const ustore = UserStore()
            const token = ustore.userInfo.token
            config.headers.Authorization = 'Bearer ' + token
        }
        return config
    }, function (error) {
        // 对请求错误做些什么
        return Promise.reject(error)
    }
)

// ==================== 修改点 2: 优化响应拦截器 ====================
// 添加对两种后端响应格式的兼容处理
request.interceptors.response.use(
    function (response) {
        // ========== 处理成功响应（2xx 状态码）==========
        if (response.status === 200 || response.status === 201 || response.status === 204) {
            const res = response.data

            // ==================== 🔥 兼容点 1: Jenkins 统一响应格式 ====================
            // Jenkins 模块使用统一格式: { code: 200, message: "成功", data: {...} }
            // 其他模块使用标准 DRF 格式: 直接返回数据或 { detail: "..." }
            // 判断依据: 是否存在 code 字段
            if (res.code !== undefined) {
                // ========== Jenkins 格式处理 ==========
                // 后端固定返回 HTTP 200，通过业务 code 区分成功/失败
                // - code: 200 → 成功
                // - code: 5001-5006 → Jenkins 业务错误
                // - code: 400/500 → 通用错误
                if (res.code !== 200) {
                    // 业务错误，弹出后端返回的错误消息
                    ElNotification({
                        title: '操作失败',
                        message: res.message || '请求失败',
                        type: 'error',
                        duration: 3000
                    })
                    return Promise.reject(new Error(res.message))
                }
                // code === 200，业务成功，正常返回
            }
            // ========== 其他模块格式 ==========
            // 无 code 字段，说明是其他模块的标准 DRF 响应
            // HTTP 200 本身就代表成功，直接返回即可

            return response
        }

        // ========== 处理特殊 HTTP 状态码（401、404、500）==========
        // 注意: 由于 validateStatus 已优化，这些状态码通常会进入 error 拦截器
        // 但保留此处代码以防万一（例如某些中间件可能直接返回）

        // 401 未授权: 清除 token，跳转登录页
        if (response.status === 401 && response.config.url !== '/login/' && response.config.url !== '/register/' && response.config.url !== '/verify/' && response.config.url !== '/refresh/') {
            window.localStorage.removeItem('token')
            ElNotification({
                title: '请求失败',
                message: 'token已过期或者未传递过去，您无权限访问接口:' + response.config.url,
                type: 'error',
                duration: 1500
            })
            // 路由跳转到登录页面
            router.push({
                name: 'login'
            })
        }

        // ==================== 修改点 3: 移除 404 清除 token ====================
        // 404 只是接口地址错误，不应清除登录状态
        if (response.status === 404) {
            // window.localStorage.removeItem('token')  // ❌ 已删除
            ElNotification({
                message: '接口不存在：' + response.config.url,
                type: 'warning',
                duration: 2000
            })
            // 可选: 跳转到 404 页面
            // router.push({ name: '404' })
        }

        // 500 服务器错误
        if (response.status === 500) {
            ElNotification({
                message: '服务器崩溃了',
                type: 'error',
                duration: 1500
            })
            // 路由跳转到500错误页面
            router.push({
                name: '500'
            })
        }
        return response
    },
    function (error) {
        // ==================== 修改点 4: 优化错误拦截器 ====================
        // 处理 4xx、5xx 错误（主要是其他模块的错误）

        // 网络错误处理
        if (error.code === 'ERR_NETWORK' || error.message.includes('Network Error')) {
            ElNotification({
                title: '网络错误',
                message: '网络错误，请检查网络是否正常，检查后端服务状态！',
                type: 'error',
                duration: 1500
            })
            return Promise.reject(error)
        }

        // ==================== 🔥 兼容点 2: 其他模块的错误格式 ====================
        // Bug/User/Project 等模块在错误时返回: { detail: "错误信息" }
        // 需要提取 detail 字段并显示给用户
        const status = error.response?.status
        const detail = error.response?.data?.detail

        if (status === 400 && detail) {
            // 参数错误 (其他模块)
            ElNotification({
                title: '请求失败',
                message: detail,
                type: 'error',
                duration: 2000
            })
        } else if (status === 500 && detail) {
            // 服务器错误 (其他模块)
            ElNotification({
                title: '服务器错误',
                message: detail || '服务器崩溃了',
                type: 'error',
                duration: 2000
            })
        }

        return Promise.reject(error)
    }
)

export default request

