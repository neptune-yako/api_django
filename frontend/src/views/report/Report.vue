<template>
  <el-row v-if="state.report">
    <el-col :span="12">
      <el-scrollbar>
        <el-card v-if='state.record'>
          <div class="report_title">
            <img src="@/assets/icons/report.png" alt="plan" width="20">
            接口自动化测试报告
          </div>
          <el-descriptions :column="6" title="执行信息" direction="vertical">
            <el-descriptions-item label="计划名称" align="center">{{ state.record.plan }}</el-descriptions-item>
            <el-descriptions-item label="环境名称" align="center">{{ state.record.env }}</el-descriptions-item>
            <el-descriptions-item label="套件通过率" align="center">{{ state.record.pass_rate + '%' }}
            </el-descriptions-item>
            <el-descriptions-item label="执行人" align="center">{{ state.record.tester }}</el-descriptions-item>
            <el-descriptions-item label="执行状态" align="center">
              <el-tag v-if="state.record.status === '执行完毕'" type="success">执行完毕</el-tag>
              <el-tag v-else-if="state.record.status === '执行中'" type="info">执行中</el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="执行时间" align="center">{{
                tools.rTime(state.record.create_time)
              }}
            </el-descriptions-item>
          </el-descriptions>
        </el-card>
        <el-card body-style="padding:5px">
          <div class="title" style="padding: 15px">
            图表信息
          </div>
          <el-row :gutter="5">
            <!-- 用例信息图表 -->
            <el-col :span="14">
              <div class="chartBox" id="chart1"></div>
            </el-col>
            <!-- 通过率图表 -->
            <el-col :span="10">
              <div class="chartBox" id="chart2"></div>
            </el-col>
          </el-row>
        </el-card>
        <el-card v-if="state.report">
          <el-descriptions :column="4" title="套件统计" direction="vertical">
            <el-descriptions-item label="测试套件总数" align="center">{{
                state.report.results.length
              }}
            </el-descriptions-item>
            <el-descriptions-item label="通过测试套件" align="center">{{ successscent.length }}</el-descriptions-item>
            <el-descriptions-item label="失败测试套件" align="center">{{ failscent.length }}</el-descriptions-item>
            <el-descriptions-item label="错误测试套件" align="center">{{ errorscent.length }}</el-descriptions-item>
          </el-descriptions>
          <p style="line-height: 30px;">未通过测试套件</p>
          <div style="margin-left: 20px">
            <el-button plain size="small" @click="state.showScentDatas = errorscent" type="danger"
                       v-for="su in errorscent" :key="su.name">{{ su.name }}
            </el-button>
            <el-button plain size="small" @click="state.showScentDatas = failscent" type="warning"
                       v-for="su in failscent" :key="su.name">{{ su.name }}
            </el-button>
          </div>
          <p style="line-height: 30px;">已通过测试套件</p>
          <div style="margin-left: 20px">
            <el-button plain size="small" @click="state.showScentDatas = successscent" type="success"
                       v-for="su in successscent" :key="su.name">{{ su.name }}
            </el-button>
          </div>
        </el-card>
      </el-scrollbar>
    </el-col>

    <el-col :span="12">
      <div>
        <el-card>
          <el-button size="small" type="primary" plain @click="state.showScentDatas = state.report.results">
            所有套件
          </el-button>
          <el-button size="small" type="success" plain @click="state.showScentDatas = successscent">成功套件</el-button>
          <el-button size="small" type="warning" plain @click="state.showScentDatas = failscent">失败套件</el-button>
          <el-button size="small" type="danger" plain @click="state.showScentDatas = errorscent">错误套件</el-button>
          <el-scrollbar height="calc(100vh - 197px)">
            <template v-if="state.showScentDatas && state.showScentDatas.length > 0">
              <div class="right_box" v-for="(scent, index) in state.showScentDatas" :key="index"
                   style="margin-top: 10px;">
                <div class="title" v-if="scent.state === 'success'" style="color: #1ab43a;">
                  {{ '测试套件 : ' + scent.name + '【通过】' }}
                </div>
                <div class="title" v-else-if="scent.state === 'fail'" style="color: #f8bb08;">
                  {{ '测试套件 : ' + scent.name + '【失败】' }}
                </div>
                <div class="title" v-else style="color: #f6051e;">
                  {{ '测试套件 : ' + scent.name + '【错误】' }}
                </div>
                <el-table :data="scent.cases" style="width: 100%;margin-top: 10px;" class="result" :show-header="false"
                          stripe>
                  <el-table-column type="expand">
                    <template #default="scope">
                      <Result :result="scope.row" :hideBtn="true"></Result>
                    </template>
                  </el-table-column>
                  <el-table-column label="序号" type="index" width="80px"></el-table-column>
                  <el-table-column :show-overflow-tooltip="true" label="用例名称" prop="name"
                                   min-width="100px"></el-table-column>
                  <el-table-column label="请求方法" prop="method" min-width="40px"></el-table-column>
                  <el-table-column label="状态码" prop="status_code" min-width="40px"></el-table-column>
                  <el-table-column label="耗时" prop="run_time" min-width="40px"></el-table-column>
                  <el-table-column label="断言结果" prop="state" min-width="40px">
                    <template #default="scope">
                      <span v-if="scope.row.state === '成功'" style="color: #1ab43a;">成功</span>
                      <span v-else-if="scope.row.state === '失败'" style="color: #f8bb08">失败</span>
                      <span v-else style="color: #f6051e">错误</span>
                    </template>
                  </el-table-column>
                </el-table>
              </div>
            </template>
            <template v-else>
              <div class="table-empty" style="text-align: center; padding: 200px 0;">
                <img src="@/assets/images/none.png" alt="notData" />
                <div>暂无数据</div>
              </div>
            </template>
          </el-scrollbar>
        </el-card>
      </div>
    </el-col>
  </el-row>
</template>

<script setup>
import chart from '@/utils/chart'
import Result from '@/components/Result.vue'
import tools from '@/utils/dateTools'
import http from '@/api/index.js'
import {onMounted, reactive, computed, onUpdated} from 'vue'
import {useRoute} from 'vue-router'
import {useDark} from '@vueuse/core'

// 注入暗黑模式状态
const isDark = useDark()
const route = useRoute()

const state = reactive({
  // record运行记录信息
  record: null,
  // 报告信息
  report: null,
  // 显示的测试套件数据
  showScentDatas: []
})

// 获取报告信息
async function getReportInfo(id) {
  const response = await http.reportApi.getReport(id)
  // 判断http响应状态码
  if (response.status === 200) {
    state.report = response.data.info
    state.showScentDatas = state.report.results
  }
}

// 获取运行记录信息
async function getRecordInfo(id) {
  const response = await http.recordApi.getRecordInfo(id)
  if (response.status === 200) {
    state.record = response.data
  }
}

// 执行信息图表
function chart1() {
  const value = [state.report.all, state.report.success, state.report.fail, state.report.error]
  const label = ['用例总数', '通过用例', '失败用例', '错误用例']
  const ele = document.querySelector('#chart1')
  chart.chart1(ele, value, label, isDark.value)
}

// 通过率图表
function chart2() {
  const datas = [{value: state.report.success, name: '通过'}, {value: state.report.fail, name: '失败'},
    {value: state.report.error, name: '错误'}]
  const ele = document.querySelector('#chart2')
  chart.chart2(ele, datas, isDark.value)
}

const successscent = computed(() => {
  return state.report.results.filter(function (val, index, array) {
    return val.state === 'success'
  })
})
const failscent = computed(() => {
  return state.report.results.filter(function (val, index, array) {
    return val.state === 'fail'
  })
})
const errorscent = computed(() => {
  return state.report.results.filter(function (val, index, array) {
    return val.state === 'error'
  })
})

// 页面加载时执行
onMounted(() => {
  const id = route.params.id
  getReportInfo(id)
  getRecordInfo(id)
})

// 页面更新时执行
onUpdated(() => {
  if (document.querySelector('#chart1')) chart1()
  if (document.querySelector('#chart2')) chart2()
})
</script>

<style lang="scss" scoped>
@use './report.scss';
</style>