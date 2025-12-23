import { defineStore } from 'pinia'
import http from '@/api/index'
import jenkinsApi from '@/api/jenkins.js'

export const ProjectStore = defineStore('proStore', {
    // 数据
    state: () => {
        return {
            // 项目列表
            proList: {},
            // 测试环境列表
            envList: [],
            // Jenkins节点列表
            jenkinsNodes: [],
            // 顶部选中的测试环境
            env: {},
            // 保存接口列表
            interfaces: [],
            // 测试套件列表
            sceneList: [],
            // 测试计划列表
            planList: [],
            //是否禁用菜单
            isDisabled: true,
            // 分页配置
            pageConfig: {
                page: 1,
                size: 10,
                count: 0
            }
        }
    },
    // 方法
    actions: {
        // 获取项目下面所有的环境
        async getEnvironmentList() {
            const response = await http.environmentApi.getEnvironment({ project: this.proList.id })
            if (response.status === 200) {
                this.envList = response.data
            }
        },
        // 设置足够大的分页尺寸，获取全部接口
        async getAllInterFaceList() {
            const response = await http.interfaceApi.getInterface({
                project: this.proList.id,
                page: this.pageConfig.page,
                size: this.pageConfig.size * 100
            })
            if (response.status === 200) {
                this.interfaces = response.data.results
            }
        },
        // 获取项目下面分页的接口
        async getInterFaceList() {
            const response = await http.interfaceApi.getInterface({
                project: this.proList.id,
                page: this.pageConfig.page,
                size: this.pageConfig.size
            })
            if (response.status === 200) {
                this.interfaces = response.data.results
                this.pageConfig.count = response.data.count
            }
        },
        // 获取项目下面所有的测试套件
        async getSceneList() {
            const response = await http.suiteApi.getScene({ project: this.proList.id })
            if (response.status === 200) {
                this.sceneList = response.data
            }
        },
        // 获取项目下所有的测试计划
        async getPlanList() {
            const response = await http.planApi.getPlan({ project: this.proList.id })
            if (response.status === 200) {
                this.planList = response.data
            }
        },
        // 获取Jenkins节点列表（支持自动同步到项目环境）
        async getJenkinsNodes(autoSync = false) {
            try {
                const params = autoSync && this.proList.id ? { project_id: this.proList.id } : {}
                const response = await jenkinsApi.getNodesList(params)
                if (response.status === 200 && response.data.code === 200) {
                    this.jenkinsNodes = response.data.data
                }
            } catch (error) {
                console.error('获取Jenkins节点失败:', error)
            }
        },
    },
    persist: {
        // 是否开启持久化
        enabled: true,
        // 用户状态信息持久化配置
        strategies: [
            {
                key: 'projectStore',
                storage: localStorage
            }
        ]
    }
})