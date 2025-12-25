<template>
  <el-tag :type="tagType">
    {{ tagLabel }}
  </el-tag>
</template>

<script setup>
import { computed } from 'vue'
import { CONNECTION_STATUS_MAP, BUILD_STATUS_MAP } from '../utils/constants'

const props = defineProps({
  status: {
    type: String,
    required: true
  },
  type: {
    type: String,
    default: 'connection', // 'connection' or 'build'
    validator: (value) => ['connection', 'build'].includes(value)
  }
})

const tagType = computed(() => {
  const map = props.type === 'connection' ? CONNECTION_STATUS_MAP : BUILD_STATUS_MAP
  // 处理空字符串和null，统一转换为空字符串进行映射
  const status = props.status || ''
  const item = map[status] || map.unknown || { type: 'info' }
  return item.type
})

const tagLabel = computed(() => {
  const map = props.type === 'connection' ? CONNECTION_STATUS_MAP : BUILD_STATUS_MAP
  // 处理空字符串和null，统一转换为空字符串进行映射
  const status = props.status || ''
  const item = map[status] || map.unknown || { label: '未知' }
  return item.label
})
</script>
