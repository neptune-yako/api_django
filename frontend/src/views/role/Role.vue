<template>
  <div class="card page_box" style="padding: 10px;">
    <el-button plain @click='clickAdd' type="primary" icon="CirclePlus" size="small">角色</el-button>
    <el-button plain @click='getRoleList' type="success" icon="Refresh" size="small">刷新</el-button>
    <el-table :data="roleList" style="width: 100%" stripe :header-cell-style="{'text-align':'center'}"
              :cell-style="{'text-align':'center'}" v-loading="loading" element-loading-text="加载中...">
      <template #empty>
        <div class="table-empty">
          <img src="@/assets/images/none.png" alt="notData"/>
          <div>暂无数据</div>
        </div>
      </template>
      <el-table-column label="序号" type="index" width="90"/>
      <el-table-column label="角色名称" prop="name"></el-table-column>
      <el-table-column label="角色描述" prop="description"></el-table-column>
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
          <el-button type="primary" icon="Edit" @click="EditDialog(scope.row)" plain>编辑</el-button>
          <el-button @click="deleteRole(scope.row.id)" icon="Delete" type="danger" plain>删除</el-button>
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
          @current-change="getRoleList"
          @size-change="getRoleList"
      />
    </div>

    <!-- 新增角色对话框 -->
    <el-dialog v-model="createDialog" title="添加角色" width="600" center>
      <el-form :model="create" :rules="createRules" ref="createRef" label-width="80px">
        <el-form-item label="角色名称" prop="name">
          <el-input v-model="create.name" placeholder="请输入角色名称"></el-input>
        </el-form-item>
        <el-form-item label="角色描述" prop="description">
          <el-input v-model="create.description" placeholder="请输入角色描述"></el-input>
        </el-form-item>
        <div style="text-align: center">
          <el-button type="primary" @click="createRole(createRef)" plain>保存</el-button>
          <el-button @click="createDialog=false" plain>取消</el-button>
        </div>
      </el-form>
    </el-dialog>
    <!-- 编辑角色对话框 -->
    <el-dialog v-model="updateDialog" title="编辑角色" width="600" center>
      <el-form :model="update" :rules="updateRules" ref="updateRef" label-width="80px">
        <el-form-item label="角色名称" prop="name">
          <el-input v-model="update.name" placeholder="请输入角色名称"></el-input>
        </el-form-item>
        <el-form-item label="角色描述" prop="description">
          <el-input v-model="update.description" placeholder="请输入角色描述"></el-input>
        </el-form-item>
        <div style="text-align: center">
          <el-button type="primary" @click="updateRole(updateRef)" plain>保存</el-button>
          <el-button @click="updateDialog=false" plain>取消</el-button>
        </div>
      </el-form>
    </el-dialog>
  </div>
</template>

<script setup>
import http from '@/api/index'
import {ref, reactive, onMounted} from 'vue'
import {ElNotification, ElMessageBox, ElMessage} from "element-plus"
import roleApi from '@/api/module/roleApi'
import tools from "@/utils/dateTools.js"

// 角色列表数据
const roleList = ref([])
// 对话框控制
const createDialog = ref(false)
// 表单数据
const create = reactive({
  id: 0,
  name: "",
  description: ""
})
// 表单引用
const createRef = ref()
// 表单验证规则
const createRules = reactive({
  name: [
    {required: true, message: '请输入角色名称', trigger: 'blur'},
    {max: 20, message: '角色名称不得超过20个字符', trigger: 'blur'}
  ],
  description: [
    {max: 255, message: '描述不得超过255个字符', trigger: 'blur'}
  ]
})
// 分页配置
const pageConfig = reactive({
  page: 1,
  size: 10,
  count: 0
})
// 加载中
const loading = ref(false)
// 挂载时获取角色列表
onMounted(() => {
  getRoleList()
})

// 获取角色列表
async function getRoleList() {
  loading.value = true
  const params = {
    page: pageConfig.page,
    size: pageConfig.size
  }
  const response = await roleApi.getRole(params)
  if (response.status === 200) {
    roleList.value = response.data.results
    pageConfig.count = response.data.count
    loading.value = false
  }
}

// 点击新增按钮
function clickAdd() {
  createDialog.value = true
}

// 创建用户角色
async function createRole() {
  const valid = await createRef.value.validate().catch(() => false)
  if (!valid) return
  const response = await http.roleApi.createRole(create)
  if (response.status === 201) {
    ElNotification({
      type: 'success',
      title: '已成功创建角色！',
      duration: 1500
    })
    await getRoleList()
    createDialog.value = false
  } else {
    ElNotification({
      type: 'error',
      title: '创建角色失败！',
      duration: 1500,
      message: response.data.detail
    })
  }
}

// 对话框控制
const updateDialog = ref(false)
// 表单数据
const update = reactive({
  id: 0,
  name: "",
  description: ""
})
// 表单引用
const updateRef = ref()
// 表单验证规则
const updateRules = reactive({
  name: [
    {required: true, message: '请输入角色名称', trigger: 'blur'},
    {max: 20, message: '角色名称不得超过20个字符', trigger: 'blur'}
  ],
  description: [
    {max: 255, message: '描述不得超过255个字符', trigger: 'blur'}
  ]
})

// 编辑角色
function EditDialog(row) {
  updateDialog.value = true
  update.id = row.id
  update.name = row.name
  update.description = row.description
}

// 更新角色
async function updateRole() {
  const valid = await updateRef.value.validate().catch(() => false)
  if (!valid) return
  const res = await http.roleApi.updateRole(update.id, update)
  if (res.status === 200) {
    ElNotification({
      type: 'success',
      title: '已成功更新角色！',
      duration: 1500
    })
    await getRoleList()
    updateDialog.value = false
  }else {
    ElNotification({
      title: '用户角色修改失败！',
      message: res.data.detail,
      type: 'error',
      duration: 1500
    })
  }
}

// 删除角色
async function deleteRole(id) {
  ElMessageBox.confirm(
      '此操作不可恢复，确认删除该角色吗？',
      '警告', {
        confirmButtonText: '确认',
        cancelButtonText: '取消',
        type: 'warning',
        center: true
      })
      .then(async () => {
        const response = await http.roleApi.deleteRole(id)
        if (response.status === 204) {
          await getRoleList()
          ElNotification({
            type: 'success',
            title: '用户角色删除成功！',
            duration: 1500
          })
        } else {
          ElNotification({
            title: '用户角色删除失败！',
            message: response.data.detail,
            type: 'error',
            duration: 1500
          })
        }
      })
      .catch(() => {
        ElMessage({
          type: 'info',
          message: '已取消删除操作。',
          duration: 1500,
        })
      })
}
</script>

<style scoped>
</style>
