<template>
  <div class="card page_box" style="padding: 10px;">
    <el-button plain @click='clickAdd' type="primary" icon="CirclePlus" size="small">用户</el-button>
    <el-button plain @click='getUserList' type="success" icon="Refresh" size="small">刷新</el-button>
    <el-table :data="userList" style="width: 100%" stripe :header-cell-style="{'text-align':'center'}"
              :cell-style="{'text-align':'center'}" v-loading="loading" element-loading-text="加载中...">
      <template #empty>
        <div class="table-empty">
          <img src="@/assets/images/none.png" alt="notData"/>
          <div>暂无数据</div>
        </div>
      </template>
      <el-table-column label="序号" type="index" width="90"/>
      <el-table-column prop="username" label="登录名"/>
      <el-table-column prop="nickname" label="用户昵称"/>
      <el-table-column prop="email" label="用户邮箱" min-width="130"/>
      <el-table-column prop="mobile" label="手机号" min-width="100"/>
      <el-table-column prop="is_superuser" label="管理员" width="100px">
        <template #default="scope">
          <el-tag v-if="scope.row.is_superuser === true" type="primary">是</el-tag>
          <el-tag v-else-if="scope.row.is_superuser === false" type="info">否</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="is_staff" label="后台权限" width="100px">
        <template #default="scope">
          <el-tag v-if="scope.row.is_staff === true" type="primary">是</el-tag>
          <el-tag v-else-if="scope.row.is_staff === false" type="info">否</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="关联角色" width="150">
        <template #default="scope">
          <template v-if="scope.row.roles.length">
            <el-tag v-for="role in scope.row.roles" :key="role.id" type="primary">{{ role.name }}</el-tag>
          </template>
          <span v-else>-</span>
        </template>
      </el-table-column>
      <el-table-column label="状态" width="80px">
        <template #default="scope">
          <el-tag v-if="scope.row.is_active === true" type="primary">启用</el-tag>
          <el-tag v-else-if="scope.row.is_active === false" type="danger">禁用</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="last_login" label="最后登录时间" min-width="120">
        <template #default="scope">
          {{ scope.row.last_login ? tools.rTime(scope.row.last_login) : '-' }}
        </template>
      </el-table-column>
      <el-table-column prop="date_joined" label="创建时间" min-width="120">
        <template #default="scope">
          {{ tools.rTime(scope.row.date_joined) }}
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
          <el-button @click="deleteUser(scope.row.id)" icon="Delete" type="danger" plain>删除</el-button>
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
          @current-change="getUserList"
          @size-change="getUserList"
      />
    </div>
  </div>

  <!--新建用户信息-->
  <el-dialog v-model="createDialog" title="添加用户" width="600" center>
    <el-form :model="register" :rules="formDataRules" ref="formDataRef" label-width="auto">
      <el-form-item label="登录名：" prop="username">
        <el-input v-model="register.username" placeholder="请输入登录名" clearable/>
      </el-form-item>
      <el-form-item label="用户昵称：" prop="nickname">
        <el-input v-model="register.nickname" placeholder="请输入用户昵称" clearable/>
      </el-form-item>
      <el-form-item label="登录密码：" prop="password">
        <el-input v-model="register.password" :type="showPassword1 ? 'text' : 'password'" placeholder="请输入登录密码"
                  clearable>
          <template #suffix>
            <el-icon @click="showPassword1 = !showPassword1" style="cursor: pointer;">
              <component :is="showPassword1 ? 'View':'Hide' "/>
            </el-icon>
          </template>
        </el-input>
      </el-form-item>
      <el-form-item label="确认密码：" prop="check_password">
        <el-input v-model="register.check_password" :type="showPassword2 ? 'text' : 'password'"
                  placeholder="请输入确认密码" clearable>
          <template #suffix>
            <el-icon @click="showPassword2 = !showPassword2" style="cursor: pointer;">
              <component :is="showPassword2 ? 'View':'Hide' "/>
            </el-icon>
          </template>
        </el-input>
      </el-form-item>
      <el-form-item label="用户邮箱：" prop="email">
        <el-input v-model="register.email" placeholder="请输入用户邮箱" clearable/>
      </el-form-item>
      <el-form-item label="手机号：" prop="mobile">
        <el-input v-model="register.mobile" placeholder="请输入手机号" clearable/>
      </el-form-item>
      <el-form-item label="关联角色：" prop="role">
        <el-select v-model="register.role" multiple placeholder="请选择角色">
          <el-option
              v-for="role in roleOptions"
              :key="role.id"
              :label="role.name"
              :value="role.id"
          />
        </el-select>
      </el-form-item>
      <el-form-item label="是否管理员：" prop="is_superuser">
        <el-switch v-model="register.is_superuser"/>
      </el-form-item>
      <el-form-item label="后台权限：" prop="is_staff">
        <el-switch v-model="register.is_staff"/>
      </el-form-item>
      <div style="text-align: center">
        <el-button type="primary" @click="createUser(formDataRef)" plain>保存</el-button>
        <el-button @click="createDialog=false" plain>取消</el-button>
      </div>
    </el-form>
  </el-dialog>
  <!--修改用户信息-->
  <el-dialog v-model="updateDialog" title="编辑用户" width="600" center>
    <el-form :model="update" :rules="formUpdateRules" ref="formUpdateRef" label-width="auto">
      <el-form-item label="登录名：" prop="username">
        <el-input v-model="update.username" placeholder="请输入登录名" clearable/>
      </el-form-item>
      <el-form-item label="用户昵称：" prop="nickname">
        <el-input v-model="update.nickname" placeholder="请输入用户昵称" clearable/>
      </el-form-item>
      <el-form-item label="用户邮箱：" prop="email">
        <el-input v-model="update.email" placeholder="请输入用户邮箱" clearable/>
      </el-form-item>
      <el-form-item label="手机号：" prop="mobile">
        <el-input v-model="update.mobile" placeholder="请输入手机号" clearable/>
      </el-form-item>
      <el-form-item label="关联角色：" prop="role">
        <el-select v-model="update.role" multiple placeholder="请选择角色">
          <el-option
              v-for="role in roleOptions"
              :key="role.id"
              :label="role.name"
              :value="role.id"
          />
        </el-select>
      </el-form-item>
      <el-form-item label="是否管理员：" prop="is_superuser">
        <el-switch v-model="update.is_superuser"/>
      </el-form-item>
      <el-form-item label="后台权限：" prop="is_staff">
        <el-switch v-model="update.is_staff"/>
      </el-form-item>
      <div style="text-align: center">
        <el-button type="primary" @click="updateUser(formUpdateRef)" plain>保存</el-button>
        <el-button @click="updateDialog=false" plain>取消</el-button>
      </div>
    </el-form>
  </el-dialog>
</template>

<script setup>
import {reactive, ref, onMounted} from "vue"
import http from '@/api/index'
import {ElNotification, ElMessageBox, ElMessage} from "element-plus"
import tools from '@/utils/dateTools'

// 定义用户列表
const userList = ref([])
// 角色选项
const roleOptions = ref([])
// 定义密码是否显示
const showPassword1 = ref(false)
const showPassword2 = ref(false)
// 定义用户注册数据
let register = reactive({
  id: 0,
  username: "",
  email: "",
  nickname: "",
  password: "",
  check_password: "",
  mobile: "",
  is_superuser: false,
  is_active: true,
  is_staff: false,
  role: []
})
// 定义用户修改数据
let update = reactive({
  id: 0,
  username: "",
  email: "",
  nickname: "",
  mobile: "",
  is_active: true,
  is_superuser: '',
  is_staff: '',
  role: []
})
// 挂载数据
onMounted(() => {
  getRoleOptions()
  getUserList()
})
// 分页配置
const pageConfig = reactive({
  page: 1,
  size: 10,
  count: 0
})
// 加载中
const loading = ref(false)
// 获取用户列表数据
async function getUserList() {
  loading.value = true
  const params = {
    page: pageConfig.page,
    size: pageConfig.size
  }
  const response = await http.userApi.getUser(params)
  if (response.status === 200) {
    userList.value = response.data.results
    pageConfig.count = response.data.count
    loading.value = false
  }
}

// 用户注册表单验证
const formDataRules = reactive({
  username: [
    {required: true, message: '请输入登录名', trigger: 'blur'},
    {max: 20, message: '登录名不得超过20个字符', trigger: 'blur'},
  ],
  nickname: [
    {required: true, message: '请输入用户昵称', trigger: 'blur'},
    {max: 20, message: '用户昵称不得超过20个字符', trigger: 'blur'},
  ],
  password: [
    {required: true, message: '请输入密码', trigger: 'blur'},
    {max: 128, message: '密码不得超过128个字符', trigger: 'blur'},
  ],
  check_password: [
    {required: true, message: '请输入确认密码', trigger: 'blur'},
    {max: 128, message: '密码不得超过128个字符', trigger: 'blur'},
  ],
  mobile: [
    {required: true, message: '请输入手机号', trigger: 'blur'},
    {max: 11, message: '手机号不得超过11个字符', trigger: 'blur'},
  ],
  email: [
    {required: true, message: '请输入用户邮箱', trigger: 'blur'},
    {max: 50, message: '用户邮箱不得超过50个字符', trigger: 'blur'},
  ]
})

let createDialog = ref(false)
const formDataRef = ref()

// 点击添加按钮
function clickAdd() {
  createDialog.value = true
}

// 新建用户
async function createUser() {
  const valid = await formDataRef.value.validate().catch(() => false)
  if (!valid) return
  // 编辑模式下调用新建接口
  const response = await http.userApi.register({
    ...register,
    role_ids: register.role
  })
  if (response.status === 200) {
    ElNotification({
      type: 'success',
      title: '已成功新建用户！',
      duration: 1500,
      message: `用户账号为：${register.username}`
    })
    await getUserList()
    createDialog.value = false
  } else {
    ElNotification({
      type: 'error',
      title: '新建用户失败！',
      duration: 1500,
      message: response.data.detail
    })
  }
}

let updateDialog = ref(false)

// 编辑用户
function EditDialog(row) {
  updateDialog.value = true
  update.id = row.id
  update.username = row.username
  update.email = row.email
  update.nickname = row.nickname
  update.mobile = row.mobile
  update.is_active = row.is_active
  update.is_superuser = row.is_superuser
  update.is_staff = row.is_staff
  update.role = row.roles ? row.roles.map(item => item.id) : []
}

// 用户修改表单验证
const formUpdateRules = reactive({
  username: [
    {required: true, message: '请输入登录名', trigger: 'blur'},
    {max: 20, message: '登录名不得超过20个字符', trigger: 'blur'},
  ],
  email: [
    {required: true, message: '请输入用户邮箱', trigger: 'blur'},
    {max: 50, message: '用户邮箱不得超过50个字符', trigger: 'blur'},
  ],
  nickname: [
    {required: true, message: '请输入用户昵称', trigger: 'blur'},
    {max: 20, message: '用户昵称不得超过20个字符', trigger: 'blur'},
  ],
  mobile: [
    {required: true, message: '请输入手机号', trigger: 'blur'},
    {max: 11, message: '手机号不得超过11个字符', trigger: 'blur'},
  ],
})

// 表单引用对象
const formUpdateRef = ref()

// 修改用户信息
async function updateUser() {
  // 表单预校验
  const valid = await formUpdateRef.value.validate().catch(() => false)
  if (!valid) return
  // 编辑模式下调用编辑接口
  const res = await http.userApi.updateUser(update.id, {
    ...update,
    role_ids: update.role
  })
  if (res.status === 200) {
    ElNotification({
      type: 'success',
      title: '已成功修改用户！',
      duration: 1500
    })
    // 加载用户列表
    await getUserList()
    // 关闭窗口
    updateDialog.value = false
  } else {
    ElNotification({
      title: '用户修改失败！',
      message: res.data.detail,
      type: 'error',
      duration: 1500
    })
  }
}

// 删除用户
async function deleteUser(id) {
  ElMessageBox.confirm(
      '此操作不可恢复，确认删除该用户吗？',
      '警告', {
        confirmButtonText: '确认',
        cancelButtonText: '取消',
        type: 'warning',
        center: true
      })
      .then(async () => {
        const response = await http.userApi.deleteUser(id)
        if (response.status === 204) {
          await getUserList()
          ElNotification({
            type: 'success',
            title: '用户删除成功！',
            duration: 1500
          })
        } else {
          ElNotification({
            title: '用户删除失败！',
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

// 获取角色列表
async function getRoleOptions() {
  const response = await http.roleApi.getRole()
  if (response.status === 200) {
    roleOptions.value = response.data.results
  }
}
</script>

<style scoped>
</style>
