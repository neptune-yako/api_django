<template>
  <router-view/>
</template>

<script setup>
import http from '@/api/index'
import {UserStore} from '@/stores/module/UserStore'
import {watch} from 'vue'
import {RouterView} from 'vue-router'

const uStore = UserStore()

// 监听暗黑模式状态变化
watch(() => uStore.darkMode, (newVal) => {
  const htmlEl = document.documentElement
  newVal ? htmlEl.classList.add('dark') : htmlEl.classList.remove('dark')}, {immediate: true}
)

// 定时校验token是否有效
setInterval(async () => {
  // 每隔半小时校验用户的token是否有效
  const response = await http.userApi.verifyToken({
    'token': uStore.userInfo.token
  })
  uStore.isAuthenticated = response.status === 200
}, 1000 * 60 * 30)
</script>

<style scoped>
</style>
