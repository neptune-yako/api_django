<template>
  <div class="page">
    <div class="right">
      <img src="@/assets/images/500.png" alt=""/>
    </div>
    <p class="page_title">500 服务器崩溃了！</p>
    <el-button type="primary" plain ass="d2-mt" @click="router.replace({ path: '/project' })">
      返回项目
    </el-button>
  </div>
</template>

<script setup>
import {useRouter} from 'vue-router'

const router = useRouter()
</script>

<style scoped lang="scss">
.page {
  background: #131313;
  background-blend-mode: multiply, multiply;
  height: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
  flex-direction: column;

  .page_title {
    font-size: 20px;
    color: #ffffff;
  }
}
</style>