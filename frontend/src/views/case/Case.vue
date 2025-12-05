<template>
  <div class=" main_box">
    <div class="card left_box">
      <!-- 标题 -->
      <div class="title_box">
        <img src="@/assets/icons/case.png" width="25" alt="">
        <div class="name">接口用例</div>
        <el-button plain @click='pstore.getAllInterFaceList' type="success" icon="Refresh" size="small">刷新</el-button>
      </div>
      <el-tooltip class="box-item" effect="dark" content="跳转到接口管理菜单" placement="bottom">
        <el-button @click="router.push({ name: 'interface' })" type="primary" plain style="width: 100%;margin-top: 5px">
          接口管理
        </el-button>
      </el-tooltip>
      <!-- 层级菜单 -->
      <el-menu :default-active="activeCase" style="--el-menu-active-color:#1471ea">
        <!-- 接口 -->
        <el-sub-menu :index="inter.id.toString()" v-for='inter in pstore.interfaces' :key='inter.id'>
          <template #title>
            <img src="@/assets/icons/interface.png" width="20" alt="">
            <el-tag v-if='inter.method==="GET"' size="small" type="info">GET</el-tag>
            <el-tag v-else-if='inter.method==="POST"' size="small" type="success">POST</el-tag>
            <el-tag v-else-if='inter.method==="PATCH"' size="small" type="warning">PATCH</el-tag>
            <el-tag v-else-if='inter.method==="PUT"' size="small" type="primary">PUT</el-tag>
            <el-tag v-else-if='inter.method==="DELETE"' size="small" type="danger">DELETE</el-tag>
            <span v-if='inter.name.length < 12' style="margin: 0 5px;">{{ inter.name }}</span>
            <span v-else>{{ inter.name.slice(0, 12) }}...</span>
          </template>
          <!-- 测试用例 -->
          <el-menu-item @click='selectCase(_case.id)' :index="_case.id+ ''" v-for='_case in inter.cases' key='_case.id'>
            <img src="@/assets/icons/case.png" width="20" alt="">
            <span style="margin: 0 5px;" v-if='_case.title.length < 15'>{{ _case.title }}</span>
            <span style='margin: 0 5px' v-else>{{ _case.title.slice(0, 15) }}...</span>
          </el-menu-item>
          <!-- 添加用例 -->
          <el-menu-item @click='clickAddCase(inter.id)' :index="inter.id+'add'">
            <img src="@/assets/icons/add.png" width="20" alt="">
            <span style="margin: 0 5px;color: #1471ea;">用例</span>
          </el-menu-item>
        </el-sub-menu>
      </el-menu>
    </div>

    <div class="card right_box">
      <CaseEditor :case_id='activeCase'></CaseEditor>
    </div>
  </div>

  <!-- 添加用例的弹框 -->
  <el-drawer v-model="isShowDrawer" size="30%" direction="rtl" :with-header="false">
    <div class="title">添加用例</div>
    <el-form :model="newCase" label-width="auto" :rules="formDataRules" ref="formDataRef">
      <!-- 添加的表单 -->
      <el-form-item label="用例名称：" prop="title">
        <el-input v-model="newCase.title" placeholder="请输入用例名称" clearable/>
      </el-form-item>
      <el-form-item label="所属接口：" prop="interface">
        <el-select v-model="newCase.interface" placeholder="请选择所属接口" disabled>
          <el-option v-for="inter in pstore.interfaces" :key="inter.id" :label="inter.name" :value="inter.id">
          </el-option>
        </el-select>
      </el-form-item>
      <el-form-item label="创建人：" prop="username">
        <el-input v-model="newCase.username" placeholder="请输入创建人" disabled/>
      </el-form-item>
    </el-form>
    <template #footer>
      <div style="text-align: center;">
        <el-button @click='addCase(formDataRef)' type="primary" plain>确定</el-button>
        <el-button @click="isShowDrawer=false" plain>取消</el-button>
      </div>
    </template>
  </el-drawer>
</template>

<script setup>
import {ProjectStore} from '@/stores/module/ProStore'
import CaseEditor from '@/components/CaseEditor.vue'
import {ElNotification} from 'element-plus'
import http from '@/api/index'
import {ref, reactive} from 'vue'
import {UserStore} from "@/stores/module/UserStore.js"
import {useRouter} from 'vue-router'

const router = useRouter()
const pstore = ProjectStore()
const userStore = UserStore()

// 页面选中的用例id
let activeCase = ref()

// 选中的用例
function selectCase(id) {
  activeCase.value = id
}

let isShowDrawer = ref(false)
let newCase = reactive({
  title: "",
  interface: null,
  username: userStore.userInfo.username
})

// 点击添加用例
function clickAddCase(interId) {
  // 显示窗口
  isShowDrawer.value = true
  newCase.interface = interId
}

// 校验用例名称
const formDataRules = reactive({
  title: [{required: true, message: '用例名称不能为空！', trigger: 'blur'}],
})
// 表单引用对象
const formDataRef = ref()

// 发送添加用例的请求
async function addCase(elForm) {
  elForm.validate(async function (res) {
    if (!res) return
    const response = await http.caseApi.createCase(newCase)
    if (response.status === 201) {
      // 弹出提示
      ElNotification({
        title: '测试用例添加成功！',
        type: 'success',
        duration: 1500
      })
      // 更新页面数据
      await pstore.getAllInterFaceList()
      // 选中新的用例
      selectCase(response.data.id)
      // 关闭窗口
      isShowDrawer.value = false
    } else
      ElNotification({
        title: '测试用例添加失败！',
        message: response.data.detail,
        type: 'error',
        duration: 1500
      })
  })
}
</script>

<style lang="scss" scoped>
@use './case.scss';
</style>