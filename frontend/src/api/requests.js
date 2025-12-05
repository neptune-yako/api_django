import axios from 'axios'
import {UserStore} from '@/stores/module/UserStore'
import {ElNotification} from 'element-plus'
import router from "@/router/index.js"

// 创建一个axios实例对象
const request = axios.create({
    // 后端接口的域名设置
    baseURL: import.meta.env.VITE_BASE_API,
    // 请求成功还是失败的状态码范围
    validateStatus: function (status) {
        return true
    },
    // 跨域请求时是否需要使用凭证
    withCredentials: false,
    // 是否允许跨域
    crossDomain: true,
    // 设置请求头
    headers: {'Content-Type': 'application/json;charset=utf-8'},
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

// 添加响应拦截器
request.interceptors.response.use(
    function (response) {
        //响应状态码正常不做处理
        if (response.status === 200) return response
        if (response.status === 201) return response
        if (response.status === 204) return response
        // 判断响应状态码是否为401、不是登录和注册接口
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
        if (response.status === 404) {
            window.localStorage.removeItem('token')
            ElNotification({
                message: '当前路由地址错误，您访问的接口不存在：' + response.config.url,
                type: 'error',
                duration: 1500
            })
            // 路由跳转到404错误页面
            router.push({
                name: '404'
            })
        }
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
    }
)

export default request
