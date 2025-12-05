<template>
  <div class="main_box">
    <div class="card left_box">
      <!-- 顶部标题 -->
      <div class="title_box">
        <img src="@/assets/icons/scene.png" width="25" alt="scene">
        <div class="name">测试套件</div>
        <el-button @click='clickAddScene' size="small" icon='CirclePlus' plain type="primary">套件</el-button>
        <el-button plain @click='pstore.getSceneList' type="success" icon="Refresh" size="small">刷新</el-button>
      </div>
      <!-- 套件列表 -->
      <el-menu :default-active="activeScene.id+''">
        <el-menu-item @click='selectScene(item)' :index="item.id.toString()" v-for='item in pstore.sceneList'
                      key="item.id">
          <img src="@/assets/icons/scene.png" width="20" style="margin-right: 10px;" alt="scene">
          <span v-if='item.name.length < 15'>{{ item.name }}</span>
          <span v-else>{{ item.name.slice(0, 15) }}...</span>
        </el-menu-item>
      </el-menu>
    </div>

    <div class="card right_box">
      <!-- 右侧顶部 -->
      <div style="background: none;">
        <el-divider content-position="center"><b>基本信息</b></el-divider>
        <div class="name_edit">
          <el-form :model="activeScene" :rules="formDataRules" ref="formDataRef" style="flex: 1; margin-right: 10px;">
            <el-form-item label="测试套件：" prop="name">
              <el-input v-model="activeScene.name" placeholder="请输入测试套件名称" clearable/>
            </el-form-item>
          </el-form>
          <div class="btns">
            <el-button @click="saveScene" icon="CircleCheck" plain type="primary">保存</el-button>
            <el-button @click='RunScene' type="success" icon='Promotion' plain>运行</el-button>
            <el-tooltip class="box-item" effect="dark" content="删除测试套件，将删除该套件下的所有用例步骤和计划中的套件"
                        placement="top">
              <el-button @click='clickScene' type="danger" icon="Delete" plain>删除</el-button>
            </el-tooltip>
          </div>
        </div>
      </div>

      <!-- 右侧下面部分 -->
      <div style="background: none;margin-top: 5px;" id='scene_table'>
        <el-divider content-position="center"><b>用例步骤（可拖拽测试用例，控制执行用例的顺序）</b></el-divider>
        <el-button @click="clickAddScent" plain type="primary" icon='CirclePlus' size="small">用例</el-button>
        <el-button plain @click='getSceneCase' type="success" icon="Refresh" size="small">刷新</el-button>
        <el-table :data="SceneCaseList" style="width: 100%;margin-top: 5px" :show-header='false' stripe v-loading="loading" element-loading-text="加载中...">
          <template #empty>
            <div class="table-empty">
              <img src="@/assets/images/select.png" alt="select" style="height: calc(100vh - 700px)"/>
            </div>
          </template>
          <el-table-column label="名称">
            <template #default="scope">
              <div style="display: flex;align-items: center;">
                <img src="@/assets/icons/case.png" width="20" style="margin-right: 5px;" alt="case">
                <span style="color: #00aaff;font-weight: bold;">步骤{{ scope.row.sort }}：</span>
                <span>{{ scope.row.icase.title }}</span>
              </div>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="200">
            <template #default="scope">
              <el-button @click='clickEditCase(scope.row.icase.id)' size="small" type="primary" icon="Edit" plain>编辑
              </el-button>
              <el-button @click='deleteSceneCase(scope.row.id)' size="small" type="danger" icon="Remove" plain>移除
              </el-button>
            </template>
          </el-table-column>
        </el-table>
        <div class="pagination" style="margin: 5px 5px 0">
          <el-pagination
              :hide-on-single-page="true"
              v-model:current-page="pageConfig.page"
              v-model:page-size="pageConfig.size"
              :page-sizes="[10, 20, 30, 40]"
              layout="total, sizes, prev, pager, next, jumper"
              :total="pageConfig.count"
              @current-change="getSceneCase"
              @size-change="getSceneCase"
          />
        </div>
      </div>
    </div>
  </div>

  <!-- 显示测试结果的抽屉组件 -->
  <el-drawer v-model="isShowRunResult" size="40%" direction="rtl" :with-header="false">
    <div class="title">套件运行结果</div>
    <RunSceneResult :results='runResult' @close="isShowRunResult = false"></RunSceneResult>
  </el-drawer>

  <!--显示用例编辑的组件  -->
  <el-drawer v-model="isShowEditCase" direction="rtl" :with-header="false" size="50%">
    <CaseEditor :case_id="editCaseId"></CaseEditor>
  </el-drawer>

  <!-- 新增测试步骤组件 -->
  <el-drawer v-model="addStepDlg" direction="rtl" :with-header="false" size="25%">
    <AddScene :scene='activeScene' :cases="SceneCaseList" @refresh='getSceneCase(activeScene.id)'></AddScene>
  </el-drawer>
</template>

<script setup>
import {ProjectStore} from '@/stores/module/ProStore'
import {ElNotification, ElMessageBox, ElMessage} from 'element-plus'
import RunSceneResult from './components/SceneResult.vue'
import AddScene from './components/AddScene.vue'
import CaseEditor from '@/components/CaseEditor.vue'
import http from '@/api/index'
import {ref, reactive, onMounted} from 'vue'
import Sortable from 'sortablejs'
import {UserStore} from '@/stores/module/UserStore'

const uStore = UserStore()
const pstore = ProjectStore()
// 分页配置
const pageConfig = reactive({
  page: 1,
  size: 10,
  count: 0
})

// 选择的测试套件id
let activeScene = ref({
  id: "",
  name: ""
})
// 选中用例中的测试套件列表
let SceneCaseList = ref([])

// 生命周期函数（数据挂载之后执行），默认选中第一个套件
onMounted(async () => {
  await pstore.getSceneList()
  if (pstore.sceneList.length > 0) {
    selectScene(pstore.sceneList[0])
  }
})

// 选择某个测试套件
function selectScene(item) {
  activeScene.value = item
  getSceneCase(item.id)
}

// 添加测试套件
async function clickAddScene() {
  const response = await http.suiteApi.createScene({
    project: pstore.proList.id,
    name: "测试套件",
    username: uStore.userInfo.username
  })
  if (response.status === 201) {
    // 提示成功
    ElNotification({
      title: '测试套件创建成功！',
      type: 'success',
      duration: 1500
    })
    // 刷新页面数据
    await pstore.getSceneList()
    // 选中新建的测试套件
    activeScene.value = response.data
  } else {
    ElNotification({
      title: '测试套件创建失败！',
      message: response.data.detail,
      type: 'error',
      duration: 1500
    })
  }
}
// 加载中
const loading = ref(false)
// 获取测试套件中的测试用例
async function getSceneCase() {
  loading.value = true
  const params = {
    page: pageConfig.page,
    size: pageConfig.size
  }
  const response = await http.suiteApi.getStep(activeScene.value.id, params)
  if (activeScene.value.id && response.status === 200) {
    SceneCaseList.value = response.data.results
    pageConfig.count = response.data.count
    loading.value = false
  }
  // 获取数据后，重新初始化拖拽排序
  initSort()
}

// 删除测试套件
function clickScene() {
  ElMessageBox.confirm(
      '此操作不可恢复，确认要删除该测试套件?',
      '警告', {
        confirmButtonText: '确认',
        cancelButtonText: '取消',
        type: 'warning',
        center: true
      })
      .then(async () => {
        const response = await http.suiteApi.deleteScene(activeScene.value.id)
        if (response.status === 204) {
          ElNotification({
            title: '测试套件删除成功！',
            type: 'success',
            duration: 1500
          })
          // 刷新页面数据
          await pstore.getSceneList()
          // 从新选中一个激活的测试套件
          if (pstore.sceneList.length > 0) {
            selectScene(pstore.sceneList[0])
          }
        } else {
          ElNotification({
            title: '测试套件删除失败！',
            message: response.data.detail,
            type: 'error',
            duration: 1500
          })
        }
      })
      .catch(() => {
        ElMessage({
          type: 'info',
          message: '已取消删除测试套件。',
          duration: 1500
        })
      })
}

// 表单验证
const formDataRules = reactive({
  name: [
    {required: true, message: '请输入测试套件名称', trigger: 'blur'},
    {max: 20, message: '测试套件名称不得超过20个字符', trigger: 'blur'},
  ]
})
// 表单引用对象
const formDataRef = ref()
// 保存测试套件
async function saveScene() {
  const valid = await formDataRef.value.validate().catch(() => false)
  if (!valid) return
  const response = await http.suiteApi.updateScene(activeScene.value.id, activeScene.value)
  if (response.status === 200 && response.data.code !== 300) {
    ElNotification({
      type: 'success',
      title: '测试套件保存成功！',
      duration: 1500
    })
    await pstore.getSceneList()
  } else {
    ElNotification({
      title: '测试套件保存失败！',
      message: response.data.detail,
      type: 'error',
      duration: 1500
    })
  }
}

// 保存测试套件运行的结果
const runResult = ref([])
// 是否显示测试运行结果的组件
const isShowRunResult = ref(false)

// 运行测试套件
async function RunScene() {
  if (SceneCaseList.value.length > 0) {
    const params = {
      env: pstore.env,
      scene: activeScene.value.id
    }
    const response = await http.suiteApi.runScene(params)
    if (response.status === 200) {
      ElNotification({
        title: '测试套件执行成功！',
        message: '测试套件已提交，请稍后查看执行结果！',
        type: 'success',
        duration: 1500
      })
      // 获取测试套件运行结果
      runResult.value = response.data
      // 显示测试运行结果组件
      isShowRunResult.value = true
    }
    if (response.status === 400) {
      ElNotification({
        title: '测试套件运行失败！',
        message: response.data.detail,
        type: 'error',
        duration: 1500
      })
    }
  } else {
    ElNotification({
      type: 'warning',
      title: '测试套件运行失败！',
      message: '当前测试套件中未添加测试步骤！',
      duration: 1500
    })
  }
}

// 编辑测试套件中的用例
let isShowEditCase = ref(false)
let editCaseId = ref(null)

function clickEditCase(id) {
  editCaseId.value = id
  isShowEditCase.value = true
}

// 删除测试套件中的用例
async function deleteSceneCase(id) {
  const response = await http.suiteApi.deleteStep(id)
  if (response.status === 204) {
    ElNotification({
      title: '测试套件删除成功！',
      type: 'success',
      duration: 1500
    })
    // 刷新页面数据
    await getSceneCase()
  } else {
    ElNotification({
      title: '测试套件删除失败！',
      message: response.data.detail,
      type: 'error',
      duration: 1500
    })
  }
}

// 新增步骤到测试流程的窗口是否可见
let addStepDlg = ref(false)

// 新增测试步骤
function clickAddScent() {
  addStepDlg.value = true
}

// 测试步骤拖拽排序
function initSort() {
  // 选择表格
  const tbody = document.querySelector('#scene_table .el-table__body-wrapper tbody')
  Sortable.create(tbody, {
    onEnd({newIndex, oldIndex}) {
      let currRow = SceneCaseList.value.splice(oldIndex, 1)[0]
      SceneCaseList.value.splice(newIndex, 0, currRow)
      // 修改后端用例数据的顺序
      updateScentOrder()
    }
  })
}

// 调用接口修改后端顺序
async function updateScentOrder() {
  // 修改caseList中的order字段
  let params = []
  SceneCaseList.value.forEach((item, index, array) => {
    params.push({
      id: item.id,
      sort: index + 1
    })
  })
  // 修改用例顺序
  const response = await http.suiteApi.updateStepOrder(params)
  if (response.status === 200) {
    ElNotification({
      type: 'success',
      title: '步骤调整排序成功！',
      duration: 1500
    })
  } else {
    ElNotification({
      title: '步骤调整排序失败！',
      message: response.data.detail,
      type: 'error',
      duration: 1500
    })
  }
  SceneCaseList.value = []
  await getSceneCase()
}

// 初始化排序组件
onMounted(() => {
  initSort()
})
</script>

<style lang="scss" scoped>
@use './scene.scss';
</style>