import {defineStore} from 'pinia'
import {useDark} from '@vueuse/core'

export const UserStore = defineStore('uStore', {
    state: () => {
        return {
            // 保存用户token
            token: "",
            // 保存用户信息
            username: "",
            userInfo: null,
            isCollapse: false,
            // 表示用户是否登录
            isAuthenticated: false,
            // 保存历史访问路由的变量
            tabs: [],
            // 暗黑模式存储的变量
            darkMode: useDark().value
        }
    },
    actions: {
        // 保存路由信息到tabs中的方法
        addTabs(route) {
            // 查找该路由地方已经保存
            const res = this.tabs.find((item, index) => {
                return route.path === item.path
            })
            // 如果没有保存，则进行保存
            if (!res) {
                this.tabs.push({
                    name: route.meta.title,
                    path: route.path,
                    icon: route.meta.icon,
                    iconImg: route.meta.iconImg
                })
            }
        },
        // 删除tabs中的路由信息
        deleteTabs(path) {
            this.tabs = this.tabs.filter((item) => {
                return item.path !== path
            })
        },
        // 清空所有标签
        clearAllTabs() {
            this.tabs = []
        },
        // 切换暗黑模式方法
        toggleDarkMode() {
            const dark = useDark()
            this.darkMode = !this.darkMode
            // 同步到vueuse
            dark.value = this.darkMode
            localStorage.setItem('darkMode', this.darkMode)
            // 同步更新根节点样式
            document.documentElement.classList.toggle('dark', this.darkMode)
            document.documentElement.style.colorScheme = this.darkMode ? 'dark' : 'normal'
        }
    },
    //  持久化存储配置
    persist: {
        // 持久化存储开启
        enabled: true,
        // 用户状态信息持久化配置
        strategies: [
            {
                // 存储键名
                key: 'userInfo',
                // 使用localStorage
                storage: localStorage,
                // 指定要持久化的字段
                paths: ['token', 'username', 'userInfo', 'isAuthenticated', 'isCollapse']
            }
        ]
    }
})