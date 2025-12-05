<template>
  <div class="card page-box" style="padding: 10px;">
    <el-button plain @click='showDlg' type="primary" icon="CirclePlus" size="small">项目</el-button>
    <el-button plain @click='getProList' type="success" icon="Refresh" size="small">刷新</el-button>
    <el-table :data="proList" style="width: 100%" stripe :header-cell-style="{'text-align':'center'}"
              :cell-style="{'text-align':'center'}" v-loading="loading" element-loading-text="加载中...">
      <template #empty>
        <div class="table-empty">
          <img src="@/assets/images/none.png" alt="notData"/>
          <div>暂无数据，请先创建项目才可以使用项目下的菜单！</div>
        </div>
      </template>
      <el-table-column label="序号" type="index" width="90"></el-table-column>
      <el-table-column prop="name" label="项目名称" min-width="140"></el-table-column>
      <el-table-column prop="username" label="创建人" min-width="140"></el-table-column>
      <el-table-column label="创建时间" min-width="180">
        <template #default="scope">
          {{ tools.rTime(scope.row.create_time) }}
        </template>
      </el-table-column>
      <el-table-column label="更新时间" min-width="120">
        <template #default="scope">
          {{ tools.rTime(scope.row.update_time) }}
        </template>
      </el-table-column>
      <el-table-column label="操作" min-width="250">
        <template #default="scope">
          <!--判断是否为当前选中的项目，选中的项目禁用操作-->
          <div v-if="scope.row.id===proStore.proList.id">
            <el-button disabled type="success" icon="Switch" plain>切换项目</el-button>
            <el-button disabled plain type="success" icon="View">查看</el-button>
            <el-button disabled plain type="primary" icon="Edit">编辑</el-button>
            <el-button disabled plain type="danger" icon="Delete">删除</el-button>
          </div>
          <div v-else>
            <el-tooltip class="box-item" effect="dark" content="切换测试项目，将获取该项目环境、接口、用例、计划、报告"
                        placement="top">
              <el-button @click="enterProject(scope.row)" type="success" icon="Switch" plain>切换项目</el-button>
            </el-tooltip>
            <el-button @click="clickView(scope.row)" type="success" icon="View" plain>查看</el-button>
            <el-button @click='clickEdit(scope.row)' type="primary" icon='Edit' plain>编辑</el-button>
            <el-tooltip class="box-item" effect="dark"
                        content="删除测试项目，将删除该项目下的所有环境、接口、用例、计划、报告" placement="top">
              <el-button @click='clickDelete(scope.row.id)' type="danger" icon='Delete' plain>删除</el-button>
            </el-tooltip>
          </div>
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
          @current-change="getProList"
          @size-change="getProList"
      />
    </div>
  </div>

  <!-- 添加项目的弹框 -->
  <el-dialog v-model="isDlgShow" title="添加项目" width="600" center>
    <el-form :model="formData" label-width="90" :rules="formDataRules" ref="formDataRef">
      <el-form-item label="项目名称：" prop="name" label-width="100px">
        <el-input v-model="formData.name" autocomplete="off" placeholder="请输入项目名称"/>
      </el-form-item>
      <el-form-item label="创建人：" prop="username" label-width="100px">
        <el-input v-model="formData.username" autocomplete="off" placeholder="请输入创建人" disabled/>
      </el-form-item>
    </el-form>
    <template #footer>
			<span class="dialog-footer">
        <el-button type="primary" @click="creatPro(formDataRef)" plain>确认</el-button>
				<el-button @click="isDlgShow = false" plain>取消</el-button>
			</span>
    </template>
  </el-dialog>

  <!-- 修改项目的弹框 -->
  <el-dialog v-model="isUpdateDlgShow" title="编辑项目" width="600" center>
    <el-form :model="formUpdateData" label-width="90" :rules="formUpdateDataRules" ref="formUpdateDataRef">
      <el-form-item label="项目名称：" prop="name" label-width="100px">
        <el-input v-model="formUpdateData.name" autocomplete="off" placeholder="请输入项目名称"/>
      </el-form-item>
      <el-form-item label="创建人：" prop="username" label-width="100px">
        <el-input v-model="formUpdateData.username" autocomplete="off" placeholder="请输入创建人" disabled/>
      </el-form-item>
    </el-form>
    <template #footer>
			<span class="dialog-footer">
				<el-button type="primary" @click="updatePro(formUpdateDataRef)" plain>确认</el-button>
        <el-button @click="isUpdateDlgShow = false" plain>取消</el-button>
			</span>
    </template>
  </el-dialog>

  <!-- 项目详情抽屉 -->
  <el-drawer v-model="drawerVisible" :with-header="false" direction="rtl" size="50%">
    <div class="title">项目详情</div>
    <div class="project-detail" v-if="currentProject">
      <el-descriptions :column="1" border>
        <el-descriptions-item label="项目名称" align="center">{{ currentProject.name }}</el-descriptions-item>
        <el-descriptions-item label="创建人" align="center">{{ currentProject.username }}</el-descriptions-item>
        <el-descriptions-item label="创建时间" align="center">{{
            tools.rTime(currentProject.create_time)
          }}
        </el-descriptions-item>
        <el-descriptions-item label="更新时间" align="center">{{
            tools.rTime(currentProject.update_time)
          }}
        </el-descriptions-item>
      </el-descriptions>
      <el-divider content-position="center">项目统计信息</el-divider>
      <el-row :gutter="20">
        <el-col :span="8" v-for="item in currentProject.info" :key="item.name">
          <el-card class="stat-card">
            <div class="stat-item">
              <div class="stat-name">{{ item.name }}</div>
              <div class="stat-value">{{ item.value }}个</div>
            </div>
          </el-card>
        </el-col>
      </el-row>
      <el-divider content-position="center">Bug统计信息</el-divider>
      <el-row :gutter="20">
        <el-col :span="6" v-for="item in currentProject.bug" :key="item.name">
          <el-card class="bug-stat-card">
            <div class="bug-stat-item">
              <div class="bug-stat-name">{{ item.name }}</div>
              <div class="bug-stat-value">{{ item.value }}个</div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>
    <template #footer>
      <div style="text-align: center;">
        <el-button @click="drawerVisible=false" plain type="primary">确定</el-button>
      </div>
    </template>
  </el-drawer>
</template>

<script setup>
import http from '@/api/index'
import {ref, reactive, onMounted} from 'vue'
import {ElMessage, ElMessageBox, ElNotification} from 'element-plus'
import {useRouter} from 'vue-router'
import {ProjectStore} from '@/stores/module/ProStore'
import {UserStore} from "@/stores/module/UserStore"
import tools from "@/utils/dateTools"

const proStore = ProjectStore()
const useStore = UserStore()
// 创建路由对象
const router = useRouter()
// 分页配置
const pageConfig = reactive({
  page: 1,
  size: 10,
  count: 0
})
// 抽屉相关
const drawerVisible = ref(false)
const currentProject = ref(null)

// 加载中
const loading = ref(false)
// 挂载数据
onMounted(() => {
  getProList()
})
// 获取项目列表
let proList = ref([])

// 获取项目列表
async function getProList() {
  loading.value = true
  const params = {
    page: pageConfig.page,
    size: pageConfig.size
  }
  const response = await http.projectApi.getProject(params)
  if (response.status === 200) {
    proList.value = response.data.results
    pageConfig.count = response.data.count
    // 加载完成
    loading.value = false
  }
}

// 查看项目详情
async function clickView(project) {
  // 获取当前的项目信息
  const response = await http.projectApi.getProjectDetail(project.id)
  if (response.status === 200) {
    currentProject.value = response.data
    drawerVisible.value = true
  } else {
    ElNotification({
      title: '获取项目详情失败',
      type: 'error',
      message: response.data.detail,
      duration: 1500
    })
  }
}

// 项目添加
let isDlgShow = ref(false)
let formData = reactive({
  name: "",
  username: useStore.userInfo.username
})

// 显示添加窗口
function showDlg() {
  isDlgShow.value = true
}

// 校验项目名称
const formDataRules = reactive({
  name: [
    {required: true, message: '项目名称不能为空！', trigger: 'blur'},
    {max: 20, message: '项目名称长度在不能超过20个字符', trigger: 'blur'}
  ]
})
// 表单引用对象
const formDataRef = ref()

// 发生请求添加项目
async function creatPro(elForm) {
  elForm.validate(async function (res) {
    if (!res) return
    const response = await http.projectApi.createProject(formData)
    if (response.status === 201) {
      // 弹出提示
      ElNotification({
        title: '项目创建成功！',
        type: 'success',
        duration: 1500
      })
      // 关闭窗口
      isDlgShow.value = false
      // 刷新页面数据
      await getProList()
    } else {
      // 创建错误提示
      ElNotification({
        title: '项目创建失败！',
        message: response.data.detail,
        type: 'error',
        duration: 1500
      })
    }
  })
}

// 项目修改
let isUpdateDlgShow = ref(false)
let formUpdateData = ref({
  name: "",
  username: ""
})
// 校验项目名称
const formUpdateDataRules = reactive({
  name: [
    {required: true, message: '项目名称不能为空！', trigger: 'blur'},
    {max: 20, message: '项目名称长度在不能超过20个字符', trigger: 'blur'}
  ]
})
// 表单引用对象
const formUpdateDataRef = ref()

// 点击编辑按钮时调用的方法
function clickEdit(pro) {
  isUpdateDlgShow.value = true
  formUpdateData.value = {...pro}
}

// 发送请求修改项目信息
async function updatePro(elForm) {
  elForm.validate(async function (res) {
    if (!res) return
    let pro_id = formUpdateData.value.id
    const response = await http.projectApi.updateProject(pro_id, formUpdateData.value)
    if (response.status === 200 && response.data.code !== 300) {
      ElNotification({
        title: '项目修改成功！',
        message: `新项目名称为：${formUpdateData.value.name}`,
        type: 'success',
        duration: 1500
      })
      // 关闭窗口
      isUpdateDlgShow.value = false
      // 刷新页面上的数据
      await getProList()
    } else {
      // 修改错误提示
      ElNotification({
        title: '项目修改失败！',
        message: response.data.detail,
        type: 'error',
        duration: 1500
      })
    }
  })
}

// 项目删除
function clickDelete(pro_id) {
  // 调用后端的接口进行删除
  ElMessageBox.confirm(
      '此操作不可恢复，请确认是否要删除该项目?',
      '警告', {
        confirmButtonText: '确认',
        cancelButtonText: '取消',
        type: 'warning',
        center: true
      })
      .then(async () => {
        // 调用后端接口进行删除
        const response = await http.projectApi.deleteProject(pro_id)
        if (response.status === 204) {
          ElNotification({
            type: 'success',
            title: '已成功删除该项目！',
            duration: 1500
          })
          // 刷新页面数据
          await getProList()
        } else {
          ElNotification({
            title: '项目删除失败！',
            type: 'warning',
            message: response.data.detail,
            duration: 1500
          })
        }
      })
      .catch(() => {
        ElMessage({
          type: 'info',
          message: '已取消删除操作。',
          duration: 1500
        })
      })
}

// 进入项目
function enterProject(pro) {
  // 清空项目信息
  proStore.$reset()
  // 保存项目信息
  proStore.proList = {
    id: pro.id,
    name: pro.name
  }
  // 启动菜单
  proStore.isDisabled = false
  // 获取环境列表
  proStore.getEnvironmentList()
  // 获取接口列表
  proStore.getInterFaceList()
  // 获取套件列表
  proStore.getSceneList()
  // 获取计划列表
  proStore.getPlanList()
  // 提示切换项目
  ElNotification({
    title: '项目切换成功！',
    type: 'success',
    message: `当前测试项目名称为：${pro.name}`,
    duration: 1500
  })
  // 跳转到environment页面
  router.push({name: "environment"})
}
</script>

<style lang="scss" scoped>
@use './project.scss';
</style>