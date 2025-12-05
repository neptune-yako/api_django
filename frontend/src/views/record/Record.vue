<template>
  <div class="main">
    <!-- 渲染图标的元素 -->
    <div class="card chart">
      <div id="chart_record" class="box1" style="height: 250px"></div>
    </div>
    <div class="card table" style="padding: 10px;">
      <el-button plain @click='getRecords' type="success" icon="Refresh" size="small">刷新</el-button>
      <!-- 渲染表格的组价 -->
      <el-table :data="recordList" style="width: 100%;" stripe :header-cell-style="{'text-align':'center'}"
                :cell-style="{'text-align':'center'}" v-loading="loading" element-loading-text="加载中...">
        <template #empty>
          <div class="table-empty">
            <img src="@/assets/images/none.png" alt="notData"/>
            <div>暂无数据</div>
          </div>
        </template>
        <el-table-column label="序号" type="index" width="90"></el-table-column>
        <el-table-column prop="plan" label="计划名称"></el-table-column>
        <el-table-column prop="env" label="环境名称"></el-table-column>
        <el-table-column prop="all" label="总用例数">
          <template #default="scope">
            <span v-if="scope.row.statue !== '执行中'">{{ scope.row.all }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="success" label="通过用例数">
          <template #default="scope">
            <span v-if="scope.row.statue !== '执行中'">{{ scope.row.success }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="pass_rate" label="通过率">
          <template #default="scope">
            <span v-if="scope.row.statue !== '执行中'">{{ scope.row.pass_rate + '%' }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="执行状态">
          <template #default="scope">
            <el-tag v-if="scope.row.status === '执行完毕'" type="success">执行完毕</el-tag>
            <el-tag v-else-if="scope.row.status === '执行中'" type="info">执行中</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="tester" label="执行人"></el-table-column>
        <el-table-column label="执行时间" min-width="110">
          <template #default="scope">
            {{ dateTools.rTime(scope.row.create_time) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200">
          <template #default="scope">
            <span v-if="scope.row.statue === '执行中'">
						  <el-tag>{{ scope.row.statue }}...</el-tag>
					  </span>
            <span v-else>
              <el-button @click="showReport(scope.row)" icon="View" type="success" plain>查看</el-button>
              <el-button @click="deleteRecord(scope.row.id)" icon="Delete" type="danger" plain>删除</el-button>
            </span>
          </template>
        </el-table-column>
      </el-table>
      <div class="pagination" style="margin: 5px 5px 0">
        <el-pagination
            v-model:current-page="pageConfig.page"
            v-model:page-size="pageConfig.size"
            :page-sizes="[10, 20, 30, 40]"
            layout="total, sizes, prev, pager, next, jumper"
            :total="pageConfig.count"
            @current-change="getRecords"
            @size-change="getRecords"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import {ProjectStore} from '@/stores/module/ProStore'
import mychat from '@/utils/chart.js'
import dateTools from '@/utils/dateTools.js'
import http from '@/api/index.js'
import {ref, onMounted, reactive} from 'vue'
import {useRouter} from 'vue-router'
import {ElMessage, ElMessageBox, ElNotification} from 'element-plus'
import {useDark} from '@vueuse/core'

// 注入暗黑模式状态
const isDark = useDark()

const router = useRouter()
// 存储项目的执行记录
let recordList = ref([])

const proStore = ProjectStore()
// 分页配置
const pageConfig = reactive({
  page: 1,
  size: 10,
  count: 0
})
// 加载中
const loading = ref(false)
// 获取项目的所有测试执行记录
async function getRecords() {
  loading.value = true
  const response = await http.recordApi.getRecord({
    project: proStore.proList.id,
    page: pageConfig.page,
    size: pageConfig.size
  })
  recordList.value = response.data.results
  pageConfig.count = response.data.count
  showChat()
  loading.value = false
}

// showChart函数开始时清空pass_rate和times数组
let chartInstance = ''
let pass_rate = []
let times = []
const showChat = function () {
  pass_rate = []
  times = []
  recordList.value.forEach((item) => {
    pass_rate.push(item.pass_rate)
    times.push(dateTools.rDate(item.create_time))
  })
  const dom = document.getElementById('chart_record')
  if (chartInstance) {
    // 使用ECharts，dispose方法用于销毁实例
    chartInstance.dispose()
  }
  mychat.chart3(dom, pass_rate, times, isDark.value)
}

function showReport(record) {
  router.push({
    name: "report",
    params: {
      id: record.id
    }
  })
}

function deleteRecord(id) {
  ElMessageBox.confirm(
      '此操作将永久删除该测试执行记录，是否继续？',
      '警告', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
        center: true
      })
      .then(async () => {
        const response = await http.recordApi.deleteRecord(id)
        if (response.status === 204) {
          ElNotification({
            type: 'success',
            title: '执行记录删除成功！',
            duration: 1500
          })
          await getRecords()
        } else {
          ElNotification({
            title: '执行记录删除失败！',
            message: response.data.detail,
            type: 'error',
            duration: 1500
          })
        }
      })
      .catch(() => {
        ElMessage({
          type: 'info',
          message: '已取消删除执行记录。',
          duration: 1500
        })
      })
}

// 数据挂载完之后渲染图标
onMounted(async () => {
  // 保存通过率的数组
  await getRecords()
})
</script>

<style scoped>
</style>