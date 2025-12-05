<template>
  <div class="card page-box">
    <el-row :gutter="10">
      <el-col :span="12">
        <div class="chartBox" id="chart1Box"></div>
      </el-col>
      <el-col :span="12">
        <div class="chartBox" id="chart2Box"></div>
      </el-col>
    </el-row>
  </div>
  <div class='card bug-list' style="padding: 10px;">
    <el-row>
      <!-- 所有bug -->
      <el-badge :value="bugs.length" :hidden="bugs.length === 0" class="item" :max="99">
        <el-button @click="showBugs = bugs" type="primary" plain size="small">所有的bug</el-button>
      </el-badge>

      <!-- 未处理bug -->
      <el-badge :value="bugs1.length" :hidden="bugs1.length === 0" class="item" :max="99" style="margin: 0 10px;">
        <el-button @click="showBugs = bugs1" type="danger" plain size="small">未处理bug</el-button>
      </el-badge>

      <!-- 处理中bug -->
      <el-badge :value="bugs2.length" :hidden="bugs2.length === 0" class="item" :max="99" style="margin-right: 10px;">
        <el-button @click="showBugs = bugs2" type="warning" plain size="small">处理中bug</el-button>
      </el-badge>

      <!-- 处理完bug -->
      <el-badge :value="bugs3.length" :hidden="bugs3.length === 0" class="item" :max="99" style="margin-right: 10px;">
        <el-button @click="showBugs = bugs3" type="success" plain size="small">处理完bug</el-button>
      </el-badge>

      <!-- 无效的bug -->
      <el-badge :value="bugs4.length" :hidden="bugs4.length === 0" class="item" :max="99" style="margin-right: 10px;">
        <el-button @click="showBugs = bugs4" type="info" plain size="small">无效的bug</el-button>
      </el-badge>

      <el-badge>
        <el-button plain @click='getAllBug' type="success" icon="Refresh" size="small">刷新</el-button>
      </el-badge>
    </el-row>
    <el-table :data="showBugs" style="width: 100%;" stripe :header-cell-style="{'text-align':'center'}"
              :cell-style="{'text-align':'center'}" v-loading="loading" element-loading-text="加载中...">
      <template #empty>
        <div class="table-empty">
          <img src="@/assets/images/none.png" alt="notData"/>
          <div>暂无数据</div>
        </div>
      </template>
      <el-table-column label="序号" type="index" width="90"></el-table-column>
      <el-table-column show-overflow-tooltip prop="pro_name" label="项目名称" width="100"></el-table-column>
      <el-table-column show-overflow-tooltip prop="interface_url" label="接口地址" min-width="100"></el-table-column>
      <el-table-column show-overflow-tooltip prop="describe" label="bug描述" min-width="100"></el-table-column>
      <el-table-column prop="status" label="bug状态" min-width="40">
        <template #default="scope">
          <el-tag v-if="scope.row.status === '1'" type="danger">未处理</el-tag>
          <el-tag v-else-if="scope.row.status === '2'" type="warning">处理中</el-tag>
          <el-tag v-else-if="scope.row.status === '3'" type="success">处理完</el-tag>
          <el-tag v-else-if="scope.row.status === '4'" type="info">无效的</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="level" label="bug等级" min-width="40">
        <template #default="scope">
          <el-tag v-if="scope.row.level === '1'" type="danger">严重</el-tag>
          <el-tag v-else-if="scope.row.level === '2'" type="warning">一般</el-tag>
          <el-tag v-else-if="scope.row.level === '3'" type="info">轻微</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="username" label="创建人" min-width="30"></el-table-column>
      <el-table-column label="提交时间" min-width="100">
        <template #default="scope">
          <span>{{ tools.rTime(scope.row.create_time) }}</span>
        </template>
      </el-table-column>
      <el-table-column prop="update_time" label="处理时间" min-width="100">
        <template #default="scope">
          <span v-if="scope.row.handle_time">
           {{ tools.rTime(scope.row.handle_time) }}
         </span>
          <span v-else>-</span>
        </template>
      </el-table-column>
      <el-table-column min-width="150" label="操作">
        <template #default="scope">
          <el-button icon="View" @click="showBugInfo(scope.row)" type="success" plain>查看</el-button>
          <el-button icon="Edit" @click="state.updateBugDlg = true; state.updateBugForm =scope.row;" type="primary"
                     plain>解决
          </el-button>
          <el-button icon="Delete" @click="deleteBug(scope.row.id)" type="danger" plain>删除</el-button>
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
          @current-change="getAllBug"
          @size-change="getAllBug"
      />
    </div>
  </div>

  <!-- 查看bug信息 -->
  <el-drawer v-model="state.showBug" :with-header="false" size='50%' direction="rtl">
    <div class="title">Bug详情</div>
    <el-scrollbar>
      <el-card>
        <b>bug信息</b>
        <el-descriptions :column="5" direction="vertical">
          <el-descriptions-item label="接口地址" align="center">
            <span v-if='state.bugInfo.interface_url.length < 70'>{{ state.bugInfo.interface_url }}</span>
            <span v-else>{{ state.bugInfo.interface_url.slice(0, 70) }}...</span>
          </el-descriptions-item>
          <el-descriptions-item label="创建人" align="center">{{ state.bugInfo.username }}</el-descriptions-item>
          <el-descriptions-item prop="status" label="bug状态" align="center">
            <el-tag v-if="state.bugInfo.status === '1'" type="danger">未处理</el-tag>
            <el-tag v-else-if="state.bugInfo.status === '2'" type="warning">处理中</el-tag>
            <el-tag v-else-if="state.bugInfo.status === '3'" type="success">处理完</el-tag>
            <el-tag v-else-if="state.bugInfo.status === '4'" type="info">无效的</el-tag>
          </el-descriptions-item>
          <el-descriptions-item prop="level" label="bug等级" align="center">
            <el-tag v-if="state.bugInfo.level === '1'" type="danger">严重</el-tag>
            <el-tag v-else-if="state.bugInfo.level === '2'" type="warning">一般</el-tag>
            <el-tag v-else-if="state.bugInfo.level === '3'" type="info">轻微</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="提交时间" align="center">
            {{ tools.rTime(state.bugInfo.create_time) }}
          </el-descriptions-item>
        </el-descriptions>
      </el-card>
      <el-card style="margin:5px 0;min-height: 400px;" v-if="state.bugLogs.info.url">
        <b>用例执行信息</b>
        <div style="margin-top: 10px;">
          <Result :result="state.bugLogs.info" :hideBtn="true"></Result>
        </div>
      </el-card>
      <el-empty v-else description="暂无数据" :image-size="150"></el-empty>
      <el-card style="min-height: 150px;" v-if="state.bugLogs">
        <b>bug处理记录</b>
        <div style="margin-top: 10px;">
          <el-timeline>
            <el-timeline-item v-for="(activity, index) in state.bugLogs.handle" :key="index"
                              :timestamp="tools.rDate(activity.update_time)" placement="top">
              <h4>{{ activity.handle.replace('【1】', '【未处理】').replace('【2】', '【处理中】').replace('【3】', '【处理完】').replace('【4】', '【无效的】') }}</h4>
              <p>{{ activity.update_user }}操作于：{{ tools.rTime(activity.update_time) }}</p>
            </el-timeline-item>
          </el-timeline>
        </div>
      </el-card>
      <el-empty v-else description="暂无数据" :image-size="150"></el-empty>
    </el-scrollbar>
    <template #footer>
      <div style="text-align: center;">
        <el-button type="primary" @click="state.showBug = false" plain>确定</el-button>
      </div>
    </template>
  </el-drawer>

  <!-- 修改状态 -->
  <el-dialog title="解决bug" v-model="state.updateBugDlg" width="30%" center>
    <el-form :model="state.updateBugForm" :rules="formDataRules" ref="formDataRef">
      <el-form-item label="bug状态：" prop="status">
        <el-select style="width: 100%;" v-model="state.updateBugForm.status" placeholder="请选择bug状态" clearable>
          <el-option label="未处理" value="1"></el-option>
          <el-option label="处理中" value="2"></el-option>
          <el-option label="处理完" value="3"></el-option>
          <el-option label="无效的" value="4"></el-option>
        </el-select>
      </el-form-item>
    </el-form>
    <template #footer>
      <div class="dialog-footer">
        <el-button type="primary" @click="updateBug(formDataRef)" plain>确定</el-button>
        <el-button @click="state.updateBugDlg = false" plain>取消</el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup>
import tools from '@/utils/dateTools'
import chart from '@/utils/chart'
import http from '@/api/index'
import {ref, onMounted, reactive, computed, watch} from 'vue'
import {ProjectStore} from '@/stores/module/ProStore'
import Result from '@/components/Result.vue'
import {ElMessage, ElMessageBox, ElNotification} from 'element-plus'
import {useDark} from '@vueuse/core'
import * as echarts from 'echarts'

const proStore = ProjectStore()
// 注入暗黑模式状态
const isDark = useDark()
// 分页配置
const pageConfig = reactive({
  page: 1,
  size: 10,
  count: 0
})
const state = reactive({
  showBug: false,
  bugInfo: null,
  bugLogs: null,
  updateBugDlg: false,
  updateBugForm: {},
})
// 加载中
const loading = ref(false)
let bugs = ref([])
let showBugs = ref([])

//获取所有的bug
async function getAllBug() {
  loading.value = true
  const response = await http.bugApi.getBug({
    project: proStore.proList.id,
    page: pageConfig.page,
    size: pageConfig.size
  })
  if (response.status === 200) {
    bugs.value = response.data.results
    pageConfig.count = response.data.count
    // 强制更新当前显示数
    showBugs.value = response.data.results
    // 渲染图表
    showTable()
    loading.value = false
  }
}

const bugs1 = computed(() => {
  return bugs.value.filter((item) => {
    return item.status === '1'
  })
})
const bugs2 = computed(() => {
  return bugs.value.filter((item) => {
    return item.status === '2'
  })
})
const bugs3 = computed(() => {
  return bugs.value.filter((item) => {
    return item.status === '3'
  })
})
const bugs4 = computed(() => {
  return bugs.value.filter((item) => {
    return item.status === '4'
  })
})

function showTable() {
  const ele = document.getElementById('chart1Box')
  const ele2 = document.getElementById('chart2Box')
  if (!ele || !ele2) return
  // 销毁旧实例（防止重复初始化）
  echarts.dispose(ele)
  echarts.dispose(ele2)
  // 渲染图表
  const data = [bugs.value.length, bugs3.value.length, bugs2.value.length, bugs1.value.length, bugs4.value.length]
  const dataLabel = ['bug的总数', '处理完bug', '处理中bug', '未处理bug', '无效的bug']
  chart.chart1(ele, data, dataLabel, isDark.value)
  chart.chart2(ele2, [
    {value: bugs3.value.length, name: '处理完bug'},
    {value: bugs2.value.length, name: '处理中bug'},
    {value: bugs1.value.length, name: '未处理bug'},
    {value: bugs4.value.length, name: '无效的bug'}
  ], isDark.value)
}

// 显示bug详情
async function showBugInfo(bug) {
  state.bugInfo = bug
  const response = await http.bugApi.getBugInfo(bug.id)
  if (response.status === 200) {
    state.bugLogs = response.data
  }
  state.showBug = true
}

// 校验bug状态
const formDataRules = reactive({
  status: [{required: true, message: 'bug状态不能为空！', trigger: 'blur'}],
})
// 表单引用对象
const formDataRef = ref()

// 修改bug状态
async function updateBug(elForm) {
  elForm.validate(async function (res) {
    if (!res) return
    const response = await http.bugApi.updateBug(state.updateBugForm.id, state.updateBugForm)
    if (response.status === 200) {
      ElNotification({
        type: 'success',
        title: 'bug状态修改成功！',
        duration: 1500
      })
      state.updateBugDlg = false
      await getAllBug()
    } else {
      ElNotification({
        title: 'bug状态修改失败！',
        type: 'error',
        message: response.data.detail,
        duration: 1500
      })
    }
  })
}

// 删除bug
async function deleteBug(id) {
  ElMessageBox.confirm(
      '此操作不可恢复，确认要删除该bug?',
      '警告', {
        confirmButtonText: '确认',
        cancelButtonText: '取消',
        type: 'warning',
        center: true
      })
      .then(async () => {
        const response = await http.bugApi.deleteBug(id)
        if (response.status === 204) {
          ElNotification({
            type: 'success',
            title: 'bug删除成功！',
            duration: 1500
          })
          await getAllBug()
          showBugs.value = bugs.value
        } else {
          ElNotification({
            title: 'bug删除失败！',
            type: 'error',
            message: response.data.detail,
            duration: 1500
          })
        }
      })
      .catch(() => {
        ElMessage({
          type: 'info',
          message: '已取消删除bug。',
          duration: 1500
        })
      })
}

onMounted(async () => {
  // 获取数据
  await getAllBug()
  showBugs.value = bugs.value
})

watch(isDark, () => {
  // 销毁所有图表实例
  echarts.dispose(document.getElementById('chart1Box'))
  echarts.dispose(document.getElementById('chart2Box'))
  // 重新渲染
  showTable()
})
</script>

<style lang="scss" scoped>
@use './bug.scss';
</style>