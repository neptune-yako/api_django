import { createRouter, createWebHashHistory } from 'vue-router'
import { UserStore } from '@/stores/module/UserStore'
import NProgress from "nprogress"
import 'nprogress/nprogress.css'

const routes = [
    {
        path: '/',
        name: 'index',
        redirect: 'login',
        meta: {
            title: '平台登录',
            noTab: true
        },
    },
    // 登录页面的路由
    {
        path: '/login',
        name: 'login',
        component: () => import( /* webpackChunkName: "about" */ '../views/login/Login.vue'),
        meta: {
            title: '平台登录',
            noTab: true
        }
    },
    // 注册页面的路由
    {
        path: '/register',
        name: 'register',
        component: () => import( /* webpackChunkName: "about" */ '../views/register/Register.vue'),
        meta: {
            title: '平台注册',
            noTab: true
        }
    },
    // 测试项目
    {
        path: '/home',
        name: 'home',
        redirect: '/project',
        component: () => import( /* webpackChunkName: "about" */ '../views/home/Home.vue'),
        children: [
            {
                path: '/project',
                name: 'project',
                component: () => import( /* webpackChunkName: "about" */ '../views/project/Project.vue'),
                meta: {
                    title: "测试项目",
                    iconImg: new URL('@/assets/icons/project.png', import.meta.url).href
                }
            },
            {
                path: '/environment',
                name: 'environment',
                component: () => import( /* webpackChunkName: "about" */ '../views/environment/Environment.vue'),
                meta: {
                    title: "测试环境",
                    iconImg: new URL('@/assets/icons/environment.png', import.meta.url).href
                }
            },
            {
                path: '/debug',
                name: 'debug',
                component: () => import( /* webpackChunkName: "about" */ '../views/debug/Debug.vue'),
                meta: {
                    title: "接口调试",
                    iconImg: new URL('@/assets/icons/debug.png', import.meta.url).href
                }
            },
            {
                path: '/interface',
                name: 'interface',
                component: () => import( /* webpackChunkName: "about" */'../views/interface/Interface.vue'),
                meta: {
                    title: "接口管理",
                    iconImg: new URL('@/assets/icons/interface.png', import.meta.url).href
                }
            },
            {
                path: '/case',
                name: 'case',
                component: () => import( /* webpackChunkName: "about" */'../views/case/Case.vue'),
                meta: {
                    title: "接口用例",
                    iconImg: new URL('@/assets/icons/case.png', import.meta.url).href
                }
            },
            {
                path: '/scene',
                name: 'scene',
                component: () => import( /* webpackChunkName: "about" */'../views/scene/Scene.vue'),
                meta: {
                    title: "测试套件",
                    iconImg: new URL('@/assets/icons/scene.png', import.meta.url).href
                }
            },
            {
                path: '/plan',
                name: 'plan',
                component: () => import( /* webpackChunkName: "about" */ '../views/plan/Plan.vue'),
                meta: {
                    title: "测试计划",
                    iconImg: new URL('@/assets/icons/plan.png', import.meta.url).href
                }
            },
            {
                path: '/cronjob',
                name: 'cronjob',
                component: () => import( /* webpackChunkName: "about" */ '../views/cronjob/Cronjob.vue'),
                meta: {
                    title: "定时任务",
                    iconImg: new URL('@/assets/icons/cronjob.png', import.meta.url).href
                }
            },
            {
                path: '/bug',
                name: 'bug',
                component: () => import( /* webpackChunkName: "about" */ '../views/bug/Bug.vue'),
                meta: {
                    title: "缺陷管理",
                    iconImg: new URL('@/assets/icons/bug.png', import.meta.url).href
                }
            },
            {
                path: '/record',
                name: 'record',
                component: () => import( /* webpackChunkName: "about" */ '../views/record/Record.vue'),
                meta: {
                    title: "测试报告",
                    iconImg: new URL('@/assets/icons/analysis.png', import.meta.url).href
                }
            },
            {
                path: '/record/report/:id',
                name: 'report',
                component: () => import( /* webpackChunkName: "about" */ '../views/report/Report.vue'),
                meta: {
                    title: "测试报告",
                    iconImg: new URL('@/assets/icons/report.png', import.meta.url).href
                }
            },
            {
                path: '/user',
                name: 'user',
                component: () => import( /* webpackChunkName: "about" */ '../views/user/User.vue'),
                meta: {
                    title: "用户列表",
                    iconImg: new URL('@/assets/icons/user.png', import.meta.url).href
                }
            },
            {
                path: '/role',
                name: 'role',
                component: () => import('../views/role/Role.vue'),
                meta: {
                    title: "角色管理",
                    iconImg: new URL('@/assets/icons/role.png', import.meta.url).href
                }
            },
            // Jenkins CI/CD 管理
            {
                path: '/jenkins',
                name: 'jenkins',
                meta: {
                    title: "CI/CD管理",
                    iconImg: new URL('@/assets/icons/project.png', import.meta.url).href
                },
                children: [
                    {
                        path: 'server',
                        name: 'jenkins-server',
                        component: () => import('@/views/jenkins/server/ServerList.vue'),
                        meta: {
                            title: "服务器管理"
                        }
                    },
                    {
                        path: 'job',
                        name: 'jenkins-job',
                        component: () => import('@/views/jenkins/job/JobList.vue'),
                        meta: {
                            title: "任务管理"
                        }
                    },
                    {
                        path: 'report',
                        name: 'jenkins-report',
                        component: () => import('@/views/jenkins/report/ReportList.vue'),
                        meta: {
                            title: "构建报告"
                        }
                    }
                ]
            }
        ]
    },
    // 错误页面404
    {
        path: '/:path(.*)*',
        name: '404',
        component: () => import( /* webpackChunkName: "about" */ '../views/error/404.vue'),
        meta: {
            title: '404',
            noTab: true
        }
    },
    // 错误页面500
    {
        path: '/500',
        name: '500',
        component: () => import( /* webpackChunkName: "about" */ '../views/error/500.vue'),
        meta: {
            title: '500',
            noTab: true
        }
    }
]

const router = createRouter({
    history: createWebHashHistory(), routes
})

// 右上角螺旋加载提示
NProgress.configure({ showSpinner: true, trickleSpeed: 200 })
// 前置路由导航守卫
router.beforeEach(async (to, from, next) => {
    // 启动进度条动画
    NProgress.start()
    // 判断是否需要保存路由访问记录
    const uStore = UserStore()
    // 路由访问的记录title保存到pinia中，去除noTab
    if (to.meta.title && !to.meta.noTab) {
        uStore.addTabs(to)
    }
    // 获取用户是否登录的状态
    let isAuthenticated = uStore.$state.isAuthenticated
    if (!isAuthenticated && to.name !== 'login' && to.name !== 'register') {
        // 停止进度条动画
        NProgress.done()
        // 将用户重定向到登录页面
        return next({ name: 'login' })
    }
    next()
})
// 后置路由导航守卫
router.afterEach((to, from) => {
    // 关闭进度条动画
    NProgress.done()
    // 设置网页标题
    document.title = to.meta.title
})

export default router