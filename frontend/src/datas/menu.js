export const MenuList = [
    {
        name: '测试项目',
        path: '/project',
        iconImg: new URL('@/assets/icons/project.png', import.meta.url).href
    },
    {
        name: '测试环境',
        path: '/environment',
        iconImg: new URL("@/assets/icons/environment.png", import.meta.url).href
    },
    {
        name: '接口调试',
        path: '/debug',
        iconImg: new URL("@/assets/icons/debug.png", import.meta.url).href
    },
    {
        name: '接口管理',
        path: '/interface',
        iconImg: new URL("@/assets/icons/interface.png", import.meta.url).href
    },
    {
        name: '接口用例',
        path: '/case',
        iconImg: new URL("@/assets/icons/case.png", import.meta.url).href
    },
    {
        name: '测试套件',
        path: '/scene',
        iconImg: new URL("@/assets/icons/scene.png", import.meta.url).href
    },
    {
        name: '测试计划',
        path: '/plan',
        iconImg: new URL("@/assets/icons/plan.png", import.meta.url).href
    },
    {
        name: '定时任务',
        path: '/cronjob',
        iconImg: new URL("@/assets/icons/cronjob.png", import.meta.url).href
    },
    {
        name: '缺陷管理',
        path: '/bug',
        iconImg: new URL("@/assets/icons/bug.png", import.meta.url).href
    },
    {
        name: '测试报告',
        path: '/record',
        iconImg: new URL("@/assets/icons/analysis.png", import.meta.url).href
    },
    {
        name: '角色管理',
        path: '/role',
        iconImg: new URL("@/assets/icons/role.png", import.meta.url).href
    },
    {
        name: '用户管理',
        path: '/user',
        iconImg: new URL("@/assets/icons/user.png", import.meta.url).href
    },
    {
        name: '任务监控',
        path: import.meta.env.VITE_FLOWER_URL,
        iconImg: new URL("@/assets/icons/monitor.png", import.meta.url).href,
        external: true
    },
    {
        name: '帮助文档',
        path: import.meta.env.VITE_HELP_URL,
        iconImg: new URL("@/assets/icons/help.png", import.meta.url).href,
        external: true
    },
    {
        name: '接口文档',
        path: import.meta.env.VITE_SWAGGER_URL,
        iconImg: new URL("@/assets/icons/swagger.png", import.meta.url).href,
        external: true
    }
]