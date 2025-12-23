import { createApp } from 'vue'
import App from './App.vue'
import router from '@/router/index'
// element-plus相关的库导入
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import zhCn from 'element-plus/dist/locale/zh-cn.mjs'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'
// 导入暗黑模式主题
import 'element-plus/theme-chalk/dark/css-vars.css'
// 导入项目的全局css样式文件
import '@/style/global.css'
import pinia from '@/stores/index'
// 引入进度条
import 'nprogress/nprogress.css'
import { useDark } from '@vueuse/core'

// 解决element-plus表格组件引发的异常
const debounce = (fn, delay) => {
  let timer = null
  return function () {
    let context = this
    let args = arguments
    clearTimeout(timer)
    timer = setTimeout(function () {
      fn.apply(context, args)
    }, delay)
  }
}
const _ResizeObserver = window.ResizeObserver
window.ResizeObserver = class ResizeObserver extends _ResizeObserver {
  constructor(callback) {
    callback = debounce(callback, 16)
    super(callback)
  }
}

// 创建应用
const app = createApp(App)
// 注册路由、pinia
app.use(router)
// 注册pinia
app.use(pinia)

// 注册element-plus
app.use(ElementPlus, { zIndex: 3000, locale: zhCn })
// 注册element-plus的图标
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}
// 添加暗黑模式全局状态
app.provide('dark-mode', useDark())

// 清可能存在的残留 Service Worker (解决 sw.js 报错)
if ('serviceWorker' in navigator) {
  navigator.serviceWorker.getRegistrations().then((registrations) => {
    for (const registration of registrations) {
      registration.unregister()
    }
  })
}

app.mount('#app')
