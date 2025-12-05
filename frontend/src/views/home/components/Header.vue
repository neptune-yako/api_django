<template>
  <div class="head_box">
    <!-- 左侧内容 -->
    <div class="left_box">
      <!-- 图标 -->
      <el-icon size="28" @click="switchCollapse">
        <el-tooltip class="box-item" effect="dark" content="展开/收起左侧菜单栏" placement="bottom">
          <img src="@/assets/icons/indent-right.png" alt="indent-right" v-if='useStore.isCollapse' width="25"/>
          <img src="@/assets/icons/indent-left.png" alt="indent-left" v-else width="25"/>
        </el-tooltip>
      </el-icon>

      <!-- 选择框 -->
      <el-select v-model="env" placeholder="请选择测试环境" clearable style="width: 250px">
        <el-option v-for='item in evnList' :key="item.id" :label="item.name" :value="item.id"/>
      </el-select>
      <el-tooltip class="box-item" effect="dark" content="查看当前项目的环境变量" placement="bottom">
        <el-button v-if="env" @click="clickShowEnv" icon="View" type="primary" plain>查看</el-button>
      </el-tooltip>
    </div>

    <!-- 中间内容 -->
    <div class="center_box">
      <div v-if='proStore.proList.name'>当前项目：{{ proStore.proList.name }}</div>
      <div v-else>项目管理</div>
    </div>

    <!-- 右侧内容 -->
    <div class="right_box">
      <!--显示通知-->
      <el-badge :value="1" class="notice">
        <el-dropdown trigger="click">
          <div class="avatar">
            <el-icon style="vertical-align: middle" :size="25">
              <Bell/>
            </el-icon>
          </div>
          <template #dropdown>
            <el-dropdown-item>
              <img src="@/assets/images/qq.jpg" alt="qq">
            </el-dropdown-item>
          </template>
        </el-dropdown>
      </el-badge>
      <!-- 显示时间 -->
      <div class="time_info">
        {{ nTime }}
      </div>
      <!-- 页面全屏展示 -->
      <div class="fullscreen">
        <div @click='handleFullScreen'>
          <el-tooltip class="box-item" effect="dark" content="开启/退出全屏模式" placement="bottom">
            <img src="@/assets/icons/full-screen.png" alt="full-screen" v-if='!isFullscreen' width="25"/>
            <img src="@/assets/icons/off-screen.png" alt="off-screen" v-else width="25"/>
          </el-tooltip>
        </div>
      </div>
      <!-- 头像展示 -->
      <el-dropdown trigger="click">
        <div class="avatar">
          <img src="@/assets/images/avatar.gif" alt="avatar">
        </div>
        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item @click='User' icon="User">个人中心</el-dropdown-item>
            <el-dropdown-item @click='backend' icon="Setting">管理后台</el-dropdown-item>
            <el-dropdown-item @click='Logout' icon="SwitchButton">退出登录</el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
      <!-- 当前用户 -->
      <div class="nickname">
        <span>{{ useStore.userInfo.nickname }}</span>
      </div>
    </div>
  </div>
  <!-- 显示环境详情 -->
  <el-dialog v-model="showEnv" title="环境变量" center>
    <el-descriptions border :column="1" style="overflow-y: auto">
      <el-descriptions-item :label="key" v-for="(value, key) in EnvInfo.debug_global_variable">
        <template #label>
          <el-tag type="warning">调试</el-tag>
          {{ key }}
        </template>
        {{ value }}
      </el-descriptions-item>
      <el-descriptions-item :label="key" v-for="(value, key) in EnvInfo.global_variable">
        <template #label>
          <el-tag type="primary">全局</el-tag>
          {{ key }}
        </template>
        {{ value }}
      </el-descriptions-item>
    </el-descriptions>
    <template #footer>
			<span class="dialog-footer">
				<el-button @click="editEnv" type="primary" plain>编辑</el-button>
				<el-button @click="showEnv = false" type="danger" plain>关闭</el-button>
			</span>
    </template>
  </el-dialog>
  <!-- 用户信息-->
  <el-dialog v-model="Userdialog" title="个人信息" width="600px" center>
    <el-descriptions :column="1" border style="overflow-y: auto">
      <el-descriptions-item label="登录名" width="50px" align="center">
        {{ useStore.userInfo.username }}
      </el-descriptions-item>
      <el-descriptions-item label="用户昵称" width="50px" align="center">
        {{ useStore.userInfo.nickname }}
      </el-descriptions-item>
      <el-descriptions-item label="手机号" width="50px" align="center">
        {{ useStore.userInfo.mobile }}
      </el-descriptions-item>
      <el-descriptions-item label="用户邮箱" width="50px" align="center">
        {{ useStore.userInfo.email }}
      </el-descriptions-item>
      <el-descriptions-item label="是否管理员" width="50px" align="center">
        <el-tag v-if="useStore.userInfo.is_superuser === true" type="primary">是</el-tag>
        <el-tag v-else-if="useStore.userInfo.is_superuser === false" type="info">否</el-tag>
      </el-descriptions-item>
      <el-descriptions-item label="后台权限" width="50px" align="center">
        <el-tag v-if="useStore.userInfo.is_staff === true" type="primary">是</el-tag>
        <el-tag v-else-if="useStore.userInfo.is_staff === false" type="info">否</el-tag>
      </el-descriptions-item>
      <el-descriptions-item label="最后登录时间" width="50px" align="center">
        {{ tools.rTime(useStore.userInfo.last_login) }}
      </el-descriptions-item>
      <el-descriptions-item label="创建时间" width="50px" align="center">
        {{ tools.rTime(useStore.userInfo.date_joined) }}
      </el-descriptions-item>
      <el-descriptions-item label="更新时间" width="50px" align="center">
        {{ tools.rTime(useStore.userInfo.update_time) }}
      </el-descriptions-item>
    </el-descriptions>
    <template #footer>
      <span class="dialog-footer">
        <el-button type="primary" @click="Userdialog = false" plain>确认</el-button>
      </span>
    </template>
  </el-dialog>
</template>

<script setup>
import {useRouter} from 'vue-router'
import {UserStore} from '@/stores/module/UserStore'
import {ElMessage, ElMessageBox, ElNotification} from 'element-plus'
import {ref, onMounted} from 'vue'
import {ProjectStore} from '@/stores/module/ProStore'
import {storeToRefs} from 'pinia'
import screenfull from "screenfull"
import http from "@/api/index"
import tools from '@/utils/dateTools'

const useStore = UserStore()
const proStore = ProjectStore()
const router = useRouter()

// 修改菜单折叠的值
function switchCollapse() {
  useStore.isCollapse = !useStore.isCollapse
}

// 顶部实时时间的显示
let nTime = ref()

// 获取当前时间
function getNowTime() {
  let nowTime = new Date()
  let y = nowTime.getFullYear()
  let m = nowTime.getMonth() + 1
  let d = nowTime.getDate()
  let H = nowTime.getHours()
  let M = nowTime.getMinutes()
  if (H < 10) {
    H = '0' + H
  }
  if (M < 10) {
    M = '0' + M
  }
  return `${y}年${m}月${d}日${H}:${M}`
}

// 获取实时时间
setInterval(() => {
  nTime.value = getNowTime()
}, 1000)

// 测试环境的管理
const pstore = ProjectStore()
const pstoreRef = storeToRefs(pstore)
const evnList = pstoreRef.envList
let env = pstoreRef.env

// 退出登录
function Logout() {
  ElMessageBox.confirm(
      "您是否确认退出登录?",
      "警告", {
        confirmButtonText: "确定",
        cancelButtonText: "取消",
        type: "warning",
        center: true
      })
      .then(async () => {
        // 调用后端接口进行退出登录
        const response = await http.userApi.logout()
        if (response.status === 200) {
          // 跳转到登录页面，清空登录的用户信息和pinia的数据
          await router.push({
            name: "login"
          })
          ElNotification({
            title: '用户已注销登录！',
            type: 'success',
            duration: 1500
          })
          // 清除token
          useStore.userInfo.token = ''
          // 修改登录的状态
          useStore.isAuthenticated = false
          window.sessionStorage.removeItem('token')
        }
      })
      .catch(() => {
        ElMessage({
          type: 'info',
          message: '已取消退出登录操作。',
          duration: 1500
        })
      })
}

// 测试环境窗口是否可见
let showEnv = ref(false)
let EnvInfo = ref({})

// 显示测试环境信息
async function clickShowEnv() {
  const params = proStore.env
  // 获取单个环境信息
  const response = await http.environmentApi.getEnvironmentInfo(params)
  if (response.status === 200) {
    EnvInfo = response.data
    showEnv.value = true
  } else {
    ElNotification({
      title: '获取环境信息失败！',
      message: response.data.detail,
      type: 'error',
      duration: 1500
    })
  }
}

// 编辑测试环境
function editEnv() {
  showEnv.value = false
  router.push({name: 'environment'})
}

// 全屏
const isFullscreen = ref(screenfull.isFullscreen)
onMounted(() => {
  screenfull.on("change", () => {
    isFullscreen.value = !!screenfull.isFullscreen
  })
})
// 全屏切换
const handleFullScreen = () => {
  if (!screenfull.isEnabled) {
    ElNotification.error("当前的浏览器不支持全屏！")
  } else {
    screenfull.toggle()
  }
}

// 用户信息对话框
let Userdialog = ref(false)

// 用户信息
function User() {
  Userdialog.value = true
}

// 跳转django管理后台
function backend() {
  window.open(import.meta.env.VITE_ADMIN_URL)
}
</script>

<style scoped lang="scss">
@use './header.scss';
</style>