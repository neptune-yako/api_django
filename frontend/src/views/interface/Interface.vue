<template>
  <div class="card page-box" style="padding: 10px;">
    <el-button @click='clickAdd' size="small" type="primary" plain icon="CirclePlus">接口</el-button>
    <el-button plain @click='pstore.getInterFaceList' type="success" icon="Refresh" size="small">刷新</el-button>
    <el-table :data="pstore.interfaces" style="width: 100%" stripe :header-cell-style="{'text-align':'center'}"
              :cell-style="{'text-align':'center'}">
      <template #empty>
        <div class="table-empty">
          <img src="@/assets/images/none.png" alt="notData"/>
          <div>暂无数据</div>
        </div>
      </template>
      <el-table-column label="序号" type="index" width="90"/>
      <el-table-column prop="project" label="项目名称" width="100"></el-table-column>
      <el-table-column prop="name" show-overflow-tooltip min-width="150" label="接口名称"/>
      <el-table-column show-overflow-tooltip prop="url" label="接口地址" min-width="250"/>
      <el-table-column prop="method" label="请求方法" width="100">
        <template #default="scope">
          <el-tag v-if='scope.row.method==="GET"' type="info">GET</el-tag>
          <el-tag v-else-if='scope.row.method==="POST"' type="success">POST</el-tag>
          <el-tag v-else-if='scope.row.method==="PATCH"' type="warning">PATCH</el-tag>
          <el-tag v-else-if='scope.row.method==="PUT"' type="primary">PUT</el-tag>
          <el-tag v-else-if='scope.row.method==="DELETE"' type="danger">DELETE</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="username" label="创建人" width="80"/>
      <el-table-column prop="create_time" label="创建时间" min-width="120">
        <template #default="scope">
          {{ tools.rTime(scope.row.create_time) }}
        </template>
      </el-table-column>
      <el-table-column label="更新时间" min-width="120">
        <template #default="scope">
          {{ tools.rTime(scope.row.update_time) }}
        </template>
      </el-table-column>
      <el-table-column label="操作" width="200">
        <template #default="scope">
          <el-button @click='clickEdit(scope.row)' icon='Edit' type="primary" plain>编辑</el-button>
          <el-tooltip class="box-item" effect="dark" content="删除测试接口，将删除该接口下的所有用例" placement="top">
            <el-button @click='deleteInterFace(scope.row.id)' icon='Delete' type="danger" plain>删除</el-button>
          </el-tooltip>
        </template>
      </el-table-column>
    </el-table>
    <div class="pagination" style="margin: 5px 5px 0">
      <el-pagination
          v-model:current-page="pstore.pageConfig.page"
          v-model:page-size="pstore.pageConfig.size"
          :page-sizes="[10, 20, 30, 40]"
          layout="total, sizes, prev, pager, next, jumper"
          :total="pstore.pageConfig.count"
          @current-change="pstore.getInterFaceList()"
          @size-change="pstore.getInterFaceList()"
      />
    </div>
  </div>

  <!-- 添加抽屉弹框 -->
  <el-drawer v-model="isShowDrawer" :with-header="false">
    <div class="title" >{{ dlgTitle }}</div>
    <!-- 添加的表单 -->
    <el-form :model="formData" :rules="formDataRules" ref="formDataRef" label-width="auto">
      <el-form-item label="接口名称：" prop="name">
        <el-input v-model="formData.name" autocomplete="off" placeholder="请输入接口名称" clearable/>
      </el-form-item>
      <el-form-item label="接口地址：" prop="url">
        <el-input v-model="formData.url" autocomplete="off" placeholder="请输入接口地址" clearable/>
      </el-form-item>
      <el-form-item label="请求方法：" prop="method">
        <el-select style="width: 100%;" v-model="formData.method" clearable>
          <el-option label="GET" value="GET"/>
          <el-option label="POST" value="POST"/>
          <el-option label="PUT" value="PUT"/>
          <el-option label="PATCH" value="PATCH"/>
          <el-option label="DELETE" value="DELETE"/>
        </el-select>
      </el-form-item>
      <el-form-item label="创建人：" prop="username">
        <el-input v-model="formData.username" autocomplete="off" placeholder="请输入接口创建人" disabled/>
      </el-form-item>
    </el-form>
    <template #footer>
      <div style="text-align: center;">
        <el-button v-if='dlgTitle==="添加接口"' type="primary" @click='addInterface(formDataRef)' plain>确定</el-button>
        <el-button v-else type="primary" @click='updateInterFace(formDataRef)' plain>确定</el-button>
        <el-button @click="isShowDrawer=false" plain>取消</el-button>
      </div>
    </template>
  </el-drawer>
</template>

<script setup>
import http from '@/api/index';
import {ref, reactive, onMounted} from 'vue'
import {ElNotification, ElMessageBox, ElMessage} from 'element-plus'
import {ProjectStore} from '@/stores/module/ProStore'
import tools from "@/utils/dateTools"
import {UserStore} from "@/stores/module/UserStore.js"

const uStore = UserStore()
const pstore = ProjectStore()

// 是否显示添加接口的窗口
let isShowDrawer = ref(false)
let dlgTitle = ref('添加接口')
let formData = reactive({
  name: "",
  url: "",
  method: "GET",
  project: pstore.proList.id,
  username: uStore.userInfo.username
})

// 点击添加按钮执行
function clickAdd() {
  dlgTitle.value = '添加接口'
  isShowDrawer.value = true
  formData.name = ''
  formData.url = ''
  formData.method = 'GET'
}

// 点击确认添加执行
async function addInterface() {
  const response = await http.interfaceApi.createInterface(formData)
  if (response.status === 201) {
    ElNotification({
      title: '接口添加成功！',
      type: 'success',
      duration: 1500
    })
    // 关闭窗口
    isShowDrawer.value = false
    // 刷新页面数据
    await pstore.getInterFaceList()
  } else {
    ElNotification({
      title: '接口添加失败！',
      message: response.data.detail,
      type: 'error',
      duration: 1500
    })
  }
}

// 校验项目名称
const formDataRules = reactive({
  name: [
    {required: true, message: '接口名称不能为空！', trigger: 'blur'},
    {max: 20, message: '接口名称长度不超过20个字符！', trigger: 'blur'}
  ],
  url: [
    {required: true, message: '接口地址不能为空！', trigger: 'blur'},
    {max: 255, message: '接口地址长度不超过255个字符！', trigger: 'blur'}
  ],
  method: [{required: true, message: '请求方法不能为空！', trigger: 'blur'}]
})
// 表单引用对象
const formDataRef = ref()

// 保存当前编辑接口的ID
let editInterId = null

// 点击编辑接口
function clickEdit(item) {
  // 显示编辑框
  dlgTitle.value = '编辑接口'
  isShowDrawer.value = true
  formData.name = item.name
  formData.url = item.url
  formData.method = item.method
  formData.username = item.username
  // 保存当前编辑接口的ID
  editInterId = item.id
}

// 调用后端修改接口信息的方法
async function updateInterFace() {
  const response = await http.interfaceApi.updateInterface(editInterId, formData)
  if (response.status === 200 && response.data.code !== 300) {
    // 关闭窗口
    isShowDrawer.value = false
    ElNotification({
      title: '接口修改成功！',
      type: 'success',
      duration: 1500
    })
    // 刷新页面数据
    await pstore.getInterFaceList()
  } else {
    ElNotification({
      title: '接口修改失败！',
      message: response.data.detail,
      type: 'error',
      duration: 1500
    })
  }
}

// 删除接口的方法
function deleteInterFace(id) {
  ElMessageBox.confirm(
      '此操作不可恢复，请确认是否要删除该接口?',
      '警告', {
        confirmButtonText: '确认',
        cancelButtonText: '取消',
        type: 'warning',
        center: true
      })
      .then(async () => {
        // 调用后端接口进行删除
        const response = await http.interfaceApi.deleteInterface(id)
        if (response.status === 204) {
          ElNotification({
            title: '接口删除成功！',
            type: 'success',
            duration: 1500
          })
          // 刷新页面数据
          await pstore.getInterFaceList()
        } else {
          ElNotification({
            title: '接口删除失败！',
            message: response.data.detail,
            type: 'error',
            duration: 1500
          })
        }
      })
      .catch(() => {
        ElMessage({
          type: 'info',
          message: '已取消删除接口操作。',
          duration: 1500
        })
      })
}

// 刷新页面数据
onMounted(() => {
  pstore.getInterFaceList()
})
</script>

<style lang="scss" scoped>
@use './interface.scss';
</style>