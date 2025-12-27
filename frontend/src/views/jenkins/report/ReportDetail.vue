<template>
  <div class="app-container">
    <el-card v-loading="loading">
      <template #header>
        <div class="card-header">
          <el-button type="text" @click="handleBack">
            <el-icon><ArrowLeft /></el-icon> 返回列表
          </el-button>
          <span class="card-title">{{ execution.report_title }}</span>
        </div>
      </template>

      <!-- 概览信息 -->
      <OverviewSection :execution="execution" />

      <!-- Tab 页 -->
      <el-tabs v-model="activeTab" style="margin-top: 30px">
        <!-- 测试套件 -->
        <el-tab-pane label="测试套件" name="suites">
          <SuiteTable :suites="suites" @view-cases="handleViewCases" />
          
          <!-- 用例列表 -->
          <CaseList 
            v-if="caseList.length > 0"
            :cases="caseList"
            :suite-name="currentSuite"
            :loading="caseLoading"
            @view-detail="handleViewCaseDetail"
          />
        </el-tab-pane>

        <!-- 图表 -->
        <el-tab-pane label="图表" name="charts">
          <ChartsView :execution="execution" :suites="suites" />
        </el-tab-pane>

        <!-- 缺陷类别 -->
        <el-tab-pane label="缺陷类别" name="categories">
          <CategoryTable :categories="categories" />
        </el-tab-pane>

        <!-- 特性场景 -->
        <el-tab-pane label="特性场景" name="scenarios">
          <ScenarioTable :scenarios="scenarios" />
        </el-tab-pane>
      </el-tabs>
    </el-card>
    
    <!-- 用例详情抽屉 -->
    <CaseDetailDrawer 
      v-model:visible="drawerVisible"
      :case-data="currentCase"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ArrowLeft } from '@element-plus/icons-vue'
import { getExecutionDetail, getCaseList } from '@/api/testReport'
import { ElMessage } from 'element-plus'

// 导入子组件
import OverviewSection from './components/OverviewSection.vue'
import SuiteTable from './components/SuiteTable.vue'
import CaseList from './components/CaseList.vue'
import CaseDetailDrawer from './components/CaseDetailDrawer.vue'
import CategoryTable from './components/CategoryTable.vue'
import ScenarioTable from './components/ScenarioTable.vue'
import ChartsView from './components/ChartsView.vue'

const route = useRoute()
const router = useRouter()

// 数据
const loading = ref(false)
const activeTab = ref('suites')
const execution = ref({})
const suites = ref([])
const categories = ref([])
const scenarios = ref([])

// P0 功能：用例列表下钻
const caseList = ref([])
const caseLoading = ref(false)
const currentSuite = ref('')

// P0 功能：用例详情抽屉
const drawerVisible = ref(false)
const currentCase = ref({})

// 加载详情
const fetchDetail = async () => {
  loading.value = true
  try {
    const res = await getExecutionDetail(route.params.id)
    const data = res.data.data
    
    // DRF Serializer 返回的是扁平结构，不再有 execution 嵌套
    execution.value = data
    suites.value = data.suites || []
    categories.value = data.categories || []
    scenarios.value = data.scenarios || []
  } catch (error) {
    console.error(error)
  } finally {
    loading.value = false
  }
}

// 返回列表
const handleBack = () => {
  router.back()
}

// P0 功能：查看套件下的用例
const handleViewCases = async (suite) => {
  currentSuite.value = suite.suite_name
  caseLoading.value = true
  try {
    const res = await getCaseList(route.params.id, { parent_suite: suite.suite_name })
    caseList.value = res.data.data.cases || []
    if (caseList.value.length === 0) {
      ElMessage.warning('该套件下暂无用例数据')
    }
  } catch (error) {
    console.error(error)
    ElMessage.error('获取用例列表失败')
  } finally {
    caseLoading.value = false
  }
}

// P0 功能：查看用例详情
const handleViewCaseDetail = (caseItem) => {
  currentCase.value = caseItem
  drawerVisible.value = true
}

onMounted(() => {
  fetchDetail()
})
</script>

<style scoped>
.card-header {
  display: flex;
  align-items: center;
  gap: 20px;
}

.card-title {
  font-size: 18px;
  font-weight: bold;
}
</style>
