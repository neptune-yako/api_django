<template>
  <div class="charts-container">
    <el-row :gutter="20">
      <!-- 状态分布饼图 -->
      <el-col :span="12">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <span>状态分布</span>
            </div>
          </template>
          <div ref="statusPieRef" style="width: 100%; height: 500px"></div>
        </el-card>
      </el-col>

      <!-- 套件通过率柱状图 -->
      <el-col :span="12">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <span>套件通过率</span>
            </div>
          </template>
          <div ref="suiteBarRef" style="width: 100%; height: 500px"></div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, onBeforeUnmount } from 'vue'
import * as echarts from 'echarts'

const props = defineProps({
  execution: {
    type: Object,
    default: () => ({})
  },
  suites: {
    type: Array,
    default: () => []
  }
})

const statusPieRef = ref(null)
const suiteBarRef = ref(null)
let statusPieChart = null
let suiteBarChart = null

// 初始化状态分布饼图
const initStatusPieChart = () => {
  if (!statusPieRef.value) return
  
  statusPieChart = echarts.init(statusPieRef.value)
  
  const option = {
    tooltip: {
      trigger: 'item',
      formatter: '{a} <br/>{b}: {c} ({d}%)'
    },
    legend: {
      orient: 'horizontal',
      bottom: '5%',
      left: 'center'
    },
    series: [
      {
        name: '用例状态',
        type: 'pie',
        radius: ['40%', '70%'], // 环形图
        center: ['50%', '45%'],
        data: [
          { 
            value: props.execution.passed_cases || 0, 
            name: '通过',
            itemStyle: { color: '#67c23a' }
          },
          { 
            value: props.execution.failed_cases || 0, 
            name: '失败',
            itemStyle: { color: '#f56c6c' }
          },
          { 
            value: props.execution.skipped_cases || 0, 
            name: '跳过',
            itemStyle: { color: '#e6a23c' }
          },
          { 
            value: props.execution.broken_cases || 0, 
            name: '中断',
            itemStyle: { color: '#f56c6c' }
          },
          { 
            value: props.execution.unknown_cases || 0, 
            name: '未知',
            itemStyle: { color: '#909399' }
          }
        ].filter(item => item.value > 0), // 过滤掉值为0的项
        emphasis: {
          itemStyle: {
            shadowBlur: 10,
            shadowOffsetX: 0,
            shadowColor: 'rgba(0, 0, 0, 0.5)'
          }
        },
        label: {
          fontSize: 14,
          formatter: '{b}\n{c} ({d}%)'
        }
      }
    ]
  }
  
  statusPieChart.setOption(option)
}

// 初始化套件通过率柱状图
const initSuiteBarChart = () => {
  if (!suiteBarRef.value) return
  
  suiteBarChart = echarts.init(suiteBarRef.value)
  
  const suiteNames = props.suites.map(s => s.suite_name)
  const passRates = props.suites.map(s => parseFloat(s.pass_rate))
  
  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      },
      formatter: '{b}<br/>通过率: {c}%'
    },
    grid: {
      left: '5%',
      right: '5%',
      bottom: '15%',
      top: '10%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: suiteNames,
      axisLabel: {
        interval: 0,
        rotate: 30,
        fontSize: 12,
        formatter: (value) => {
          // 如果名称太长,截断并添加省略号
          return value.length > 15 ? value.substring(0, 15) + '...' : value
        }
      }
    },
    yAxis: {
      type: 'value',
      name: '通过率 (%)',
      min: 0,
      max: 100,
      axisLabel: {
        formatter: '{value}%'
      }
    },
    series: [
      {
        name: '通过率',
        type: 'bar',
        data: passRates,
        barWidth: '50%',
        itemStyle: {
          color: (params) => {
            const rate = params.value
            if (rate >= 90) return '#67c23a' // 绿色
            if (rate >= 70) return '#e6a23c' // 黄色
            return '#f56c6c' // 红色
          }
        },
        label: {
          show: true,
          position: 'top',
          fontSize: 12,
          formatter: '{c}%'
        }
      }
    ]
  }
  
  suiteBarChart.setOption(option)
}

// 监听数据变化,重新渲染图表
watch(() => [props.execution, props.suites], () => {
  if (statusPieChart) {
    initStatusPieChart()
  }
  if (suiteBarChart) {
    initSuiteBarChart()
  }
}, { deep: true })

// 窗口大小改变时,自适应图表
const handleResize = () => {
  statusPieChart?.resize()
  suiteBarChart?.resize()
}

onMounted(() => {
  initStatusPieChart()
  initSuiteBarChart()
  window.addEventListener('resize', handleResize)
})

onBeforeUnmount(() => {
  statusPieChart?.dispose()
  suiteBarChart?.dispose()
  window.removeEventListener('resize', handleResize)
})
</script>

<style scoped>
.charts-container {
  padding: 20px 0;
}

.card-header {
  font-weight: bold;
  font-size: 16px;
}
</style>
