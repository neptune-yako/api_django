<template>
  <div class="mian">
    <div class="register_box">
      <div class="head">
        <img src="@/assets/images/register.png" alt="logo" class="logo">
        <div class="title">注册接口测试平台</div>
      </div>
      <div class="register-form">
        <el-form :model="registerFrom" :rules="registerRules" ref="registerFormRef">
          <el-form-item prop="username" style="width: 400px;">
            <el-input prefix-icon="UserFilled" v-model="registerFrom.username"
                      autocomplete="off" placeholder="请输入用户名" clearable/>
          </el-form-item>
          <el-form-item prop="password" style="width: 400px;">
            <el-input prefix-icon="Lock" :type="showPassword1 ? 'text' : 'password'" v-model="registerFrom.password"
                      autocomplete="off" placeholder="请输入密码" clearable>
              <template #suffix>
                <el-icon @click="showPassword1 = !showPassword1" style="cursor: pointer;">
                  <component :is="showPassword1 ? 'View':'Hide' "/>
                </el-icon>
              </template>
            </el-input>
          </el-form-item>
          <el-form-item prop="check_password" style="width: 400px;">
            <el-input prefix-icon="Lock" :type="showPassword2 ? 'text' : 'password'"
                      v-model="registerFrom.check_password" autocomplete="off" placeholder="再次确认密码" clearable>
              <template #suffix>
                <el-icon @click="showPassword2 = !showPassword2" style="cursor: pointer;">
                  <component :is="showPassword2 ? 'View':'Hide' "/>
                </el-icon>
              </template>
            </el-input>
          </el-form-item>
          <el-form-item prop="nickname" style="width: 400px;">
            <el-input prefix-icon="Avatar" v-model="registerFrom.nickname"
                      autocomplete="off" placeholder="请输入用户昵称" clearable/>
          </el-form-item>
          <el-form-item prop="mobile" style="width: 400px;">
            <el-input prefix-icon="Phone" v-model="registerFrom.mobile"
                      autocomplete="off" placeholder="请输入手机号" clearable/>
          </el-form-item>
          <el-form-item prop="email" style="width: 400px;">
            <el-input prefix-icon="Message" v-model="registerFrom.email"
                      autocomplete="off" placeholder="请输入邮箱" clearable/>
          </el-form-item>
          <el-form-item>
            <el-checkbox v-model="registerFrom.is_superuser">是否管理员</el-checkbox>
          </el-form-item>
          <el-form-item>
            <el-checkbox v-model="registerFrom.is_staff">后台权限</el-checkbox>
          </el-form-item>
          <el-form-item>
            <el-button @click='resetForm(registerFormRef)' icon="CircleClose" style="width: 193px;">重 置</el-button>
            <el-button :disabled='isClick' type="primary" @click="registerSubmit(registerFormRef)" style="width: 193px;"
                       icon="CircleCheck">
              注 册
            </el-button>
          </el-form-item>
          <!-- 没有账号，点击注册-->
          <el-link type="primary" @click="router.push('/login')">已有账号？点击登录</el-link>
        </el-form>
      </div>
    </div>
    <div class="login-footer">
      <div class="login-footer__content">
        <span>© 2024-2025 接口测试平台. All Rights Reserved.</span>
        <a href="https://gitee.com/pytests/api_django" class="slide" target="_blank">源码下载</a>
      </div>
    </div>
  </div>
</template>

<script setup>
import {ref, reactive, computed} from 'vue'
import http from '@/api/index'
import {ElNotification} from 'element-plus'
import {useRouter} from 'vue-router'

// 创建路由
const router = useRouter()
// 定义密码是否显示
const showPassword1 = ref(false)
const showPassword2 = ref(false)
// 注册的表单数据
const registerFrom = reactive({
  username: "",
  password: "",
  nickname: "",
  email: "",
  mobile: "",
  check_password: "",
  date_joined: "",
  is_superuser: false,
  is_active: true,
  is_staff: false
})

// 校验账号密码
const registerRules = reactive({
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

// 注册提交
function registerSubmit(elFrom) {
  // 进行表单预先校验
  elFrom.validate(async function (res) {
    if (!res) return
    // 校验通过
    const response = await http.userApi.register(registerFrom)
    if (response.status === 200) {
      // 给出提示
      ElNotification({
        title: '用户注册成功！',
        type: 'success',
        duration: 1500,
        message: `用户账号为：${registerFrom.username}`
      })
      // 跳转到登录页面
      await router.push({name: "login"})
    } else {
      ElNotification({
        title: '用户注册失败！',
        type: 'error',
        duration: 1500,
        message: response.data.detail
      })
    }
  })
}

// 表单引用对象
const registerFormRef = ref()

// 重置表单的方法
function resetForm(elForm) {
  if (!elForm) return
  elForm.resetFields()
}

// 当账号密码等为空时，禁止点击注册按钮
const isClick = computed(() => {
  return !(registerFrom.username !== '' && registerFrom.password !== '' && registerFrom.check_password !== '' && registerFrom.mobile !== '' && registerFrom.email !== '')
})
</script>

<style lang='scss' scoped>
@use './register.scss';
</style>