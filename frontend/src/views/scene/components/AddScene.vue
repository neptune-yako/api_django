<template>
  <div class="title">添加测试用例</div>
  <div class="container">
    <el-scrollbar class="tree-container">
      <el-tree ref="treeM" :data="interfaces" show-checkbox :props="addTreeProps" node-key="id"
               default-expand-all highlight-current>
        <template #default="{ node, data }">
          <b class="custom-tree-node">
            <div v-if="data.name">
              <img src="@/assets/icons/interface.png" height="13" alt="" style="margin: 0 5px;">
              <b style="color:#00aaff;">接口：{{ data.name }}</b>
            </div>
            <div v-if="data.title">
              <b>
                <img src="@/assets/icons/case.png" height="13" alt="">
                用例：{{ data.title }}
              </b>
            </div>
          </b>
        </template>
      </el-tree>
    </el-scrollbar>
  </div>
  <div class="button">
    <el-button type="success" @click="selectAll" plain>全选</el-button>
    <el-button type="primary" @click="addScene('add')" plain>确定</el-button>
  </div>
</template>

<script setup>
import http from '@/api/index'
import {ref} from 'vue'
import {ProjectStore} from '@/stores/module/ProStore'
import {storeToRefs} from 'pinia'
import {ElNotification} from 'element-plus'

const proStore = ProjectStore()
const proStoreRef = storeToRefs(proStore)
const interfaces = proStoreRef.interfaces
// 定义props
const prop = defineProps(['cases', 'scene'])
// 定义事件
const emit = defineEmits('refresh')
// 树形数据子元素的字段
const addTreeProps = {
  children: 'cases'
}
// 树形控件的应用
const treeM = ref({})

function getCheckedCase() {
  const Node = treeM.value.getCheckedNodes()
  const Nodes = [...Node]
  // 过滤出选中的用例
  return Nodes.filter(function (item, index) {
    return item.title
  })
}

// 添加接口用例到测试套件中
async function addScene() {
  const checkedCase = getCheckedCase()
  // 校验是否选择了用例
  if (checkedCase.length === 0) {
    ElNotification({
      type: 'warning',
      title: '请选择至少一个测试用例！',
      duration: 1500
    })
    return
  }
  let order_s = prop.cases.length
  for (let value of checkedCase) {
    let item = {...value}
    order_s += 1
    const response = await http.suiteApi.createStep({icase: item.id, scene: prop.scene.id, sort: order_s})
    if (response.status === 201) {
      ElNotification({
        type: 'success',
        title: '添加成功！',
        message: `测试用例：${item.title}添加成功！`,
        duration: 1500
      })
      emit('refresh')
    } else {
      ElNotification({
        title: '添加失败！',
        message: `测试用例：${item.title}添加失败！`,
        type: 'warning',
        duration: 1500
      })
    }
  }
  await proStore.getAllInterFaceList()
}

// 全选方法
function selectAll() {
  const allNodes = getAllNodes(interfaces.value)
  // 第二个参数为false表示不只选叶子节点
  treeM.value.setCheckedNodes(allNodes, false)
}

// 递归获取所有节点中的叶子节点（即测试用例）
function getAllNodes(nodes) {
  let leafNodes = []

  function traverse(nodeList) {
    for (let node of nodeList) {
      if (node.cases && node.cases.length > 0) {
        traverse(node.cases)
      } else if (node.title) {
        leafNodes.push(node)
      }
    }
  }
  traverse(nodes)
  return leafNodes
}
</script>

<style scoped lang="scss">
@use "./addscene.scss";
</style>