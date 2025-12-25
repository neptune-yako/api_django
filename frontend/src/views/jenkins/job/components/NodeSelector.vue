<template>
  <div class="node-selector">
    <el-form-item label="执行节点" prop="target_nodes">
      <el-select
        v-model="selectedNodes"
        multiple
        placeholder="选择执行节点（可多选）"
        style="width: 100%"
        @change="handleNodeChange"
      >
        <el-option
          v-for="node in nodeList"
          :key="node.id"
          :label="node.display_name || node.name"
          :value="node.id"
        >
          <div class="node-option">
            <span>{{ node.display_name || node.name }}</span>
            <el-tag v-if="!node.is_online" type="danger" size="small" style="margin-left: 10px">
              离线
            </el-tag>
            <el-tag v-else type="success" size="small" style="margin-left: 10px">
              在线
            </el-tag>
            <span v-if="node.ip_address" style="color: #909399; font-size: 12px; margin-left: 10px">
              {{ node.ip_address }}
            </span>
          </div>
        </el-option>
      </el-select>

      <div v-if="selectedNodes.length > 1" class="multi-node-hint">
        <el-alert type="info" :closable="false">
          <template #title>
            已选择 {{ selectedNodes.length }} 个节点，将创建多节点并行 Pipeline
          </template>
        </el-alert>
      </div>
    </el-form-item>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import http from '@/api/index'

const props = defineProps({
  modelValue: Array  // v-model 绑定
})

const emit = defineEmits(['update:modelValue', 'change'])

const selectedNodes = ref(props.modelValue || [])
const nodeList = ref([])

// 加载节点列表
const loadNodes = async () => {
  try {
    const res = await http.get('/api/jenkins/nodes/')
    if (res.code === 200) {
      nodeList.value = res.data || []
    }
  } catch (error) {
    console.error('加载节点列表失败:', error)
  }
}

const handleNodeChange = (value) => {
  emit('update:modelValue', value)
  emit('change', {
    nodes: value,
    count: value.length,
    isMultiNode: value.length > 1
  })
}

onMounted(() => {
  loadNodes()
})
</script>

<style scoped>
.node-option {
  display: flex;
  align-items: center;
  width: 100%;
}

.multi-node-hint {
  margin-top: 10px;
}
</style>
