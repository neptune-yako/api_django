<template>
  <div class="main_box">
    <div class="card left_box">
      <!-- 顶部标题 -->
      <div class="title_box">
        <img src="@/assets/icons/plan.png" width="25" alt="">
        <div class="name">测试计划</div>
        <el-button @click='addPlan' size="small" icon='CirclePlus' type="primary" plain>计划</el-button>
        <el-button plain @click='pstore.getPlanList' type="success" icon="Refresh" size="small">刷新</el-button>
      </div>

      <!-- 计划列表 -->
      <el-menu :default-active="activePlan.id.toString()" v-if='pstore.planList.length>0'>
        <el-menu-item @click='selectPlan(item)' :index="item.id.toString()" v-for='item in pstore.planList'
                      key="item.id">
          <img src="@/assets/icons/plan.png" width="20" style="margin-right: 10px;" alt="">
          <span v-if='item.name.length < 15'>{{ item.name }}</span>
          <span v-else>{{ item.name.slice(0, 15) }}...</span>
        </el-menu-item>
      </el-menu>
    </div>

    <div class="card right_box">
      <!-- 测试计划基本信息 -->
      <div style="background: none;">
        <!-- 右侧内容 -->
        <el-divider content-position="center"><b>基本信息</b></el-divider>
        <div class="name_edit">
          <el-form :model="activePlan" :rules="formDataRules" ref="formDataRef" style="flex: 1; margin-right: 10px;">
            <el-form-item label="测试计划：" prop="name" >
              <el-input v-model="activePlan.name" placeholder="请输入测试计划名称" clearable/>
            </el-form-item>
          </el-form>
          <div class="btns">
            <el-button @click="savePlan(formDataRef)" icon="CircleCheck" plain type="primary">保存</el-button>
            <el-button @click="runPlan" plain type="success" icon="Promotion">运行</el-button>
            <el-tooltip class="box-item" effect="dark" content="删除测试计划，将删除计划下的套件、测试报告"
                        placement="top">
              <el-button @click="deletePlan" plain icon="Delete" type="danger">删除</el-button>
            </el-tooltip>
          </div>
        </div>
      </div>

      <!-- 测试套件列表 -->
      <div style="background: none;margin-top: 5px;">
        <el-divider content-position="center"><b>测试套件</b></el-divider>
        <el-button @click="drawer = true" plain icon="CirclePlus" size="small" type="primary">套件</el-button>
        <el-button plain @click='getPlanScene' type="success" icon="Refresh" size="small">刷新</el-button>
        <el-table :data="scene" row-key="id" style="width: 100%;margin-top: 10px;" :show-header="false" stripe  v-loading="loading" element-loading-text="加载中...">
          <template #empty>
            <div class="table-empty">
              <img src="@/assets/images/none.png" alt="notData" width="75"/>
              <div>暂无数据</div>
            </div>
          </template>
          <el-table-column>
            <template #default="scope">
              <div style="display: flex;align-items: center;">
                <img src="@/assets/icons/scene.png" width="20" style="margin-right: 5px;" alt="scene">
                <span class="el-icon-s-help" style="color: #00aaff;font-weight: bold;">
                  {{ '测试套件' + (scope.$index + 1) + '：' }}
                </span>
                <span>{{ scope.row.name }}</span>
              </div>
            </template>
          </el-table-column>
          <el-table-column width="90px">
            <template #default="scope">
              <el-button plain size="small" type="danger" @click='deleteScene(scope.row.id)' icon="Remove">移除</el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </div>
  </div>

  <!-- 添加测试套件到测试计划中 -->
  <el-drawer v-model="drawer" :with-header="false" direction="rtl" size="20%">
    <div class="title">添加测试套件</div>
    <div class="select_content">
      <el-table @selection-change="selectTable" :data="Scene2()" tooltip-effect="dark" style="width: 100%">
        <el-table-column type="selection"></el-table-column>
        <el-table-column prop="name" label="全选"></el-table-column>
      </el-table>
    </div>
    <template #footer>
      <div style="text-align: center;">
        <el-button @click="addScene" plain type="primary">确认</el-button>
      </div>
    </template>
  </el-drawer>
</template>

<script setup>
import {ProjectStore} from '@/stores/module/ProStore'
import {ElMessage, ElMessageBox, ElNotification} from 'element-plus'
import http from '@/api/index'
import {onMounted, ref, reactive} from 'vue'
import {UserStore} from '@/stores/module/UserStore'

const uStore = UserStore()
const pstore = ProjectStore()
// 已选择的测试计划
let activePlan = ref({
  id: "",
  name: ""
})

// 测试计划中的测试套件
let scene = ref([])

// 选择某个测试计划
function selectPlan(item) {
  activePlan.value = item
  getPlanScene(item.id)
}

// 生命周期函数（数据挂载之后执行），默认选中第一个测试计划
onMounted(() => {
  if (pstore.planList.length > 0) {
    selectPlan(pstore.planList[0])
  }
})

// 添加测试计划
async function addPlan() {
  const params = {
    project: pstore.proList.id,
    name: "测试计划",
    username: uStore.userInfo.username
  }
  const response = await http.planApi.createPlan(params)
  if (response.status === 201) {
    ElNotification({
      type: 'success',
      title: '测试计划添加成功！',
      duration: 1500
    })
    // 更新页面数据
    await pstore.getPlanList()
    // 选中新创建的测试计划
    selectPlan(response.data)
  } else {
    ElNotification({
      title: '测试计划添加失败！',
      type: 'error',
      message: response.data.detail,
      duration: 1500
    })
  }
}
// 加载中
const loading = ref(false)
// 获取测试计划中的套件
async function getPlanScene() {
  loading.value = true
  const response = await http.planApi.getPlanInfo(activePlan.value.id)
  if (response.status === 200) {
    scene.value = response.data.scene
    loading.value = false
  }
}

// 删除测试计划
async function deletePlan() {
  ElMessageBox.confirm(
      '此操作不可恢复，确认要删除该计划?',
      '警告', {
        confirmButtonText: '确认',
        cancelButtonText: '取消',
        type: 'warning',
        center: true
      })
      .then(async () => {
        const response = await http.planApi.deletePlan(activePlan.value.id)
        if (response.status === 204) {
          ElNotification({
            type: 'success',
            title: '测试计划删除成功！',
            duration: 1500
          })
          await pstore.getPlanList()
          if (pstore.planList.length > 0) {
            selectPlan(pstore.planList[0])
          }
        } else {
          ElNotification({
            title: '测试计划删除失败！',
            type: 'error',
            message: response.data.detail,
            duration: 1500
          })
        }
      })
      .catch(() => {
        ElMessage({
          type: 'info',
          message: '已取消删除测试计划。',
          duration: 1500
        })
      })
}

// 表单验证
const formDataRules = reactive({
  name: [
    {required: true, message: '请输入测试计划名称', trigger: 'blur'},
    {max: 20, message: '测试计划名称不得超过20个字符', trigger: 'blur'},
  ]
})
// 表单引用对象
const formDataRef = ref()
// 保存测试计划
async function savePlan() {
  const valid = await formDataRef.value.validate().catch(() => false)
  if (!valid) return
  const params = {
    ...activePlan.value,
    scene: scene.value.map(item => item.id)
  }
  const response = await http.planApi.updatePlan(activePlan.value.id, params)
  if (response.status === 200 && response.data.code !== 300) {
    ElNotification({
      type: 'success',
      title: '测试计划保存成功！',
      duration: 1500
    })
    // 更新页面数据
    selectPlan(response.data)
  } else {
    ElNotification({
      title: '测试计划保存失败！',
      type: 'error',
      message: response.data.detail,
      duration: 1500
    })
  }
}

// 运行测试计划
async function runPlan() {
  // 校验测试计划下的套件是否为空
  if (scene.value.length > 0) {
    const params = {
      env: pstore.env,
      plan: activePlan.value.id
    }
    // 调用后端运行测试计划接口，发送请求
    const response = await http.planApi.runPlan(params)
    if (response.status === 200) {
      ElNotification({
        type: 'success',
        title: '测试计划执行成功！',
        message: '测试计划已提交，请稍后查看执行结果！',
        duration: 1500
      })
    }
    if (response.status === 400) {
      ElNotification({
        title: '测试计划执行错误！',
        type: 'error',
        message: response.data.detail,
        duration: 1500
      })
    }
  } else {
    ElNotification({
      title: '测试计划执行错误！',
      type: 'warning',
      message: '当前测试计划中无测试套件！',
      duration: 1500
    })
  }
}

// 删除测试计划中的测试套件
async function deleteScene(id) {
  let scenes = []
  scene.value.forEach((item) => {
    if (item.id !== id) {
      scenes.push(item.id)
    }
  })
  let params = {...activePlan.value}
  params.scene = scenes
  const response = await http.planApi.updatePlan(params.id, params)
  if (response.status === 200 && response.data.code !== 300) {
    ElNotification({
      type: 'success',
      title: '测试套件移除成功！',
      duration: 1500
    })
    // 更新页面数据
    await getPlanScene()
  }
  if (response.status === 200 && response.data.code === 300) {
    ElNotification({
      title: '测试套件移除失败！',
      type: 'error',
      message: response.data.detail,
      duration: 1500
    })
  }
}

// 添加的测试套件弹框是否显示
let drawer = ref(false)
// 添加选中的测试套件
let SceneList = ref([])

// 可以添加到任务中的测试套件
function Scene2() {
  // 获取任务中没有添加的所有测试套件
  return pstore.sceneList.filter((item, index) => {
    return !scene.value.find(item2 => {
      return item2.id === item.id
    })
  })
}

function selectTable(val) {
  // 将选中的测试套件id保存到SceneList中
  val.forEach((item) => {
    SceneList.value.push(item.id)
  })
}

// 添加选中的测试套件到测试计划中
async function addScene() {
  // 判断是否选了测试套件
  if (SceneList.value.length === 0) {
    ElNotification({
      type: 'warning',
      title: '请选择至少一个测试套件！',
      duration: 1500
    })
    return
  }
  let params = {...activePlan.value}
  params.scene.push(...SceneList.value)
  // 发送请求
  const response = await http.planApi.updatePlan(params.id, params)
  if (response.status === 200 && response.data.code !== 300) {
    ElNotification({
      type: 'success',
      title: '测试套件添加成功！',
      duration: 1500
    })
    // 更新页面数据
    await getPlanScene()
  } else {
    ElNotification({
      title: '测试套件添加失败！',
      type: 'error',
      message: response.data.detail,
      duration: 1500
    })
  }
}
</script>

<style lang="scss" scoped>
@use './plan.scss';
</style>