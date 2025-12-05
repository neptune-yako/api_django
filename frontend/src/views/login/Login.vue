<template>
  <div class="mian">
    <el-tooltip :content="userStore.darkMode ? '切换到浅色模式' : '切换到暗黑模式'" placement="bottom">
      <el-button circle @click="userStore.toggleDarkMode" :icon="userStore.darkMode ? 'Moon' : 'Sunny'"
                 class="dark-toggle" style="position: absolute; top: 40px; right: 40px;"/>
    </el-tooltip>
    <div class="login_box">
      <div class="head">
        <img src="@/assets/images/logo.png" class="logo" alt="">
        <div class="title">登录接口测试平台</div>
      </div>
      <div class="login-form">
        <el-form :model="loginForm" :rules="loginRules" ref="loginFormRef">
          <el-form-item prop="username" style="width: 400px;" @keyup.enter="loginSubmit(loginFormRef)">
            <el-input prefix-icon="UserFilled" v-model="loginForm.username" autocomplete="off"
                      placeholder="请输入账号、手机号、邮箱" clearable/>
          </el-form-item>
          <el-form-item prop="password" style="width: 400px;" @keyup.enter="loginSubmit(loginFormRef)">
            <el-input prefix-icon="Lock" :type="showPassword ? 'text' : 'password'" v-model="loginForm.password"
                      autocomplete="off" placeholder="请输入密码" clearable>
              <template #suffix>
                <el-icon @click="showPassword = !showPassword" style="cursor: pointer;">
                  <component :is="showPassword ? 'View':'Hide' "/>
                </el-icon>
              </template>
            </el-input>
          </el-form-item>
          <el-form-item>
            <el-switch v-model="loginForm.status" inactive-text="记住"/>
          </el-form-item>
          <el-form-item>
            <el-button @click='resetForm(loginFormRef)' icon="CircleClose" style="width: 193px;">重 置</el-button>
            <el-button :disabled='isClick' type="primary" @click="loginSubmit(loginFormRef)" style="width: 193px;"
                       icon="Avatar">登 录
            </el-button>
          </el-form-item>
          <el-link type="primary" @click="router.push('/register')">没有账号？点击注册</el-link>
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
import {ref, reactive, computed, onMounted} from 'vue'
import http from '@/api/index'
import {ElNotification} from 'element-plus'
import {useRouter} from 'vue-router'
import {UserStore} from '@/stores/module/UserStore'

// 登录的表单数据
const loginForm = reactive({
  username: "",
  password: "",
  status: true
})
// 定义密码是否显示
const showPassword = ref(false)
// 创建路由对象
const router = useRouter()
// 实例化用户的store对象
const userStore = UserStore()

// 提交登录的方法
function loginSubmit(elForm) {
  // 进行表单预先校验
  elForm.validate(async function (res) {
    if (!res) return
    // 校验通过
    const response = await http.userApi.login(loginForm)
    if (response.status === 200) {
      // 给出提示
      ElNotification({
        title: '登录成功！',
        message: '欢迎登录接口自动化测试平台！',
        type: 'success',
        duration: 1500
      })
      // 保存用户的token、mobile、email、nickname、date_joined，使用pinia来保到userInfo
      userStore.userInfo = response.data
      if (loginForm.status) {
        userStore.isAuthenticated = true
        // 保存本地持久化数据
        localStorage.setItem('remember', 'true')
        localStorage.setItem('username', loginForm.username)
        localStorage.setItem('password', loginForm.password)
      } else {
        userStore.isAuthenticated = true
        // 清除本地持久化数据
        localStorage.removeItem('remember')
        localStorage.removeItem('username')
        localStorage.removeItem('password')
      }
      // 跳转到项目管理页面
      await router.push({name: "project"})
    } else {
      ElNotification({
        title: '登录失败',
        message: response.data.detail[0],
        type: 'error',
        duration: 1500
      })
    }
  })
}

// 校验账号密码
const loginRules = reactive({
  username: [{required: true, message: '账号不能为空', trigger: 'blur'}],
  password: [{required: true, message: '密码不能为空', trigger: 'blur'}]
})

// 表单引用对象
const loginFormRef = ref()

// 重置表单的方法
function resetForm(elForm) {
  if (!elForm) return
  elForm.resetFields()
}

// 当账号密码为空时，禁止点击登录按钮
const isClick = computed(() => {
  return !(loginForm.username !== '' && loginForm.password !== '')
})

// 页面加载时，判断是否记住密码，如果记住密码，则自动填充账号和密码
onMounted(() => {
  if (localStorage.getItem('remember') === 'true') {
    loginForm.username = localStorage.getItem('username') || ''
    loginForm.password = localStorage.getItem('password') || ''
    loginForm.status = true
  }
})
</script>

<style lang='scss' scoped>
@use './login.scss';
</style>