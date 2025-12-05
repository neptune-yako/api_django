<template>
  <!-- 顶部的logo图标 -->
  <div class="logo">
    <img src="@/assets/images/icon.png" alt="logo">
    <div class="title" v-if="!uStore.isCollapse">接口测试平台</div>
  </div>
  <!-- 菜单 -->
  <el-menu :default-active="activeMenu" :collapse="uStore.isCollapse" collapse-transition size="large">
    <el-menu-item :index="item.path" v-for='item in MenuList' key="item.path" :disabled="proStore.isDisabled"
                  @click="MenuClick(item)">
      <img :src="item.iconImg" width="20" style="margin-right: 10px;" alt="">
      <span>{{ item.name }}</span>
    </el-menu-item>
  </el-menu>
</template>

<script setup>
import {UserStore} from '@/stores/module/UserStore'
import {MenuList} from '@/datas/menu'
import {ProjectStore} from "@/stores/module/ProStore"
import {useRoute, useRouter} from 'vue-router'
import {computed} from 'vue'

// 定义路由
const router = useRouter()
const uStore = UserStore()
// 获取当前路由信息
const route = useRoute()
const proStore = ProjectStore()

// 点击菜单项
const MenuClick = (item) => {
  if (item.external) {
    // 处理外部链接
    window.open(item.path)
  } else {
    // 处理内部路由
    router.push(item.path)
  }
}

// 计算当前激活的菜单项
const activeMenu = computed(() => {
  // 如果当前路由是测试报告页面，则激活"测试报告"菜单项
  if (route.name === 'report') {
    return '/record'
  }
  return route.path
})
</script>

<style lang="scss" scoped>
@use "./menu.scss";
</style>