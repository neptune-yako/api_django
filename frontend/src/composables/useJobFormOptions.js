import { ref } from 'vue'
import { getJenkinsServers } from '@/api/jenkins'
import http from '@/api/index'
import { parseList } from '@/views/jenkins/utils/response-parser'

/**
 * Job 表单选项数据管理
 * 用于获取创建/编辑 Job 时需要的下拉选项
 */
export function useJobFormOptions() {
    const serverList = ref([])
    const projectList = ref([])
    const environmentList = ref([])
    const planList = ref([])
    const loading = ref(false)

    /**
     * 加载所有选项数据
     */
    const loadAllOptions = async () => {
        loading.value = true
        try {
            await Promise.all([
                loadServers(),
                loadProjects(),
                loadEnvironments(),
                loadPlans()
            ])
        } catch (error) {
            console.error('加载表单选项失败:', error)
        } finally {
            loading.value = false
        }
    }

    /**
     * 加载服务器列表
     */
    const loadServers = async () => {
        try {
            const res = await getJenkinsServers({ page: 1, size: 100 })
            serverList.value = parseList(res)
        } catch (error) {
            console.error('加载服务器列表失败:', error)
            serverList.value = []
        }
    }

    /**
     * 加载项目列表
     */
    const loadProjects = async () => {
        try {
            const res = await http.projectApi.getProject({ page: 1, size: 100 })
            // DRF 分页返回 results，自定义可能返回 list
            projectList.value = res.data.results || res.data.list || res.data || []
            console.log('项目列表加载成功:', projectList.value)
        } catch (error) {
            console.error('加载项目列表失败:', error)
            projectList.value = []
        }
    }

    /**
     * 加载环境列表
     * @param {number} projectId - 可选，按项目过滤
     */
    const loadEnvironments = async (projectId = null) => {
        try {
            if (projectId) {
                const res = await http.environmentApi.getEnvironment(projectId)
                environmentList.value = res.data || []
            } else {
                // 如果没有指定项目，尝试从 store 获取当前项目
                try {
                    const { ProjectStore } = await import('@/stores/module/ProStore')
                    const pstore = ProjectStore()
                    if (pstore.proList && pstore.proList.id) {
                        const res = await http.environmentApi.getEnvironment(pstore.proList.id)
                        environmentList.value = res.data || []
                    } else {
                        environmentList.value = []
                    }
                } catch (e) {
                    console.warn('无法获取当前项目，环境列表为空')
                    environmentList.value = []
                }
            }
            console.log('环境列表加载成功:', environmentList.value)
        } catch (error) {
            console.error('加载环境列表失败:', error)
            environmentList.value = []
        }
    }

    /**
     * 加载计划列表
     * @param {number} projectId - 可选，按项目过滤
     */
    const loadPlans = async (projectId = null) => {
        try {
            const params = { page: 1, size: 100 }
            if (projectId) {
                params.project = projectId
            }
            const res = await http.planApi.getPlan(params)
            // DRF 分页返回 results，自定义可能返回 list
            planList.value = res.data.results || res.data.list || res.data || []
            console.log('计划列表加载成功:', planList.value)
        } catch (error) {
            console.error('加载计划列表失败:', error)
            planList.value = []
        }
    }

    return {
        // 数据
        serverList,
        projectList,
        environmentList,
        planList,
        loading,

        // 方法
        loadAllOptions,
        loadServers,
        loadProjects,
        loadEnvironments,
        loadPlans
    }
}
