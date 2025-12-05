<template>
  <el-row :gutter="40">
    <el-col :span="16">
      <el-row v-for="(item, index) in params" :key="index" :gutter="5" style="margin-top: 5px;">
        <el-col :span="5">
          <el-input size="small" v-model="item[0]" placeholder="请输入参数名" clearable/>
        </el-col>
        <el-col :span="2">
          <el-select @change="selectType($event, index)" v-model="paramsType[index]" placeholder="请选择参数类型"
                     clearable size="small" style="width: 100%;">
            <el-option label="Text" value="text"/>
            <el-option label="File" value="file"/>
          </el-select>
        </el-col>
        <el-col :span="11">
          <!-- 文字输入框 -->
          <el-input v-if="paramsType[index] === 'text'" v-model="item[1]" placeholder="请输入参数值" size="small"
                    clearable/>
          <el-select v-else @change="selectFile($event, index)" v-model="item[1][0]" size="small"
                     placeholder="请选择已有文件" style="width: 100%;">
            <el-option v-for="file in files" :key="file.info[0]" :label="file.info[0]" :value="file.info[0]"/>
          </el-select>
        </el-col>
        <el-col :span="1">
          <el-button icon="Delete" @click="removeParam(index)" size="small" type="danger" plain>删除</el-button>
        </el-col>
      </el-row>
      <el-button style="margin-top: 10px;" icon="CirclePlus" @click="addParam" size="small" type="primary" plain>添加
      </el-button>
    </el-col>
    <el-col :span="24" style="margin-top: 5px;">
      <el-card>
        <el-upload class="uploadFile" :action="http.fileApi.uploadFile.url" :data="{ project_id: proStore.proList.id }"
                   :headers="updateHead()" :show-file-list="false" multiple
                   :on-success="uploadSuccess" :on-error="uploadError" name="file"
                   accept=".jpg,.jpeg,.png,.doc,.docx,.xls,.xlsx,.ppt,.pptx,.pdf,.zip,.rar,.txt">
          <el-button type="primary" plain size="small" icon="Upload">上传文件</el-button>
          <template #tip>
            <div class="el-upload__tip">
              仅支持上传图片、pdf、word、excel、zip、文本等文件且大小不能超过1024kb，文件名称请勿带有特殊符号！
            </div>
          </template>
        </el-upload>
        <el-table :data="files" style="width: 100%" size="small" height="250px" stripe
                  :header-cell-style="{'text-align':'center'}" :cell-style="{'text-align':'center'}">
          <template #empty>
            <div class="table-empty">
              <img src="@/assets/images/none.png" alt="notData" width="85"/>
              <div>暂无文件</div>
            </div>
          </template>
          <el-table-column label="文件名称" width="300">
            <template #default="scope">
              <el-tag type="primary">{{ scope.row.info[0] }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="文件类型">
            <template #default="scope">
              <el-tag type="info">{{ scope.row.info[2] }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="创建时间" prop="create_time">
            <template #default="scope">
              {{ tools.rTime(scope.row.create_time) }}
            </template>
          </el-table-column>
          <el-table-column label="操作" width="90">
            <template #default="scope">
              <el-button size="small" icon="Delete" type="danger" plain @click="deleteFile(scope.row.id)">
                {{ scope.row.info[3] }}删除
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-card>
    </el-col>
  </el-row>
</template>

<script setup>
import tools from '@/utils/dateTools'
import {ref, onMounted, watch} from 'vue'
import {ElNotification, ElMessage, ElMessageBox} from 'element-plus'
import http from "@/api/index"
import {UserStore} from '@/stores/module/UserStore'
import {ProjectStore} from '@/stores/module/ProStore'

const uStore = UserStore()
const proStore = ProjectStore()
const params = ref([])
const files = ref([])
const paramsType = ref([])

const props = defineProps({
  modelValue: {
    type: Array,
    default: () => [['', '']],
  },
  project_id: Number
})

const emit = defineEmits(['update:modelValue'])

const updateHead = () => ({
  Authorization: 'Bearer ' + uStore.userInfo.token,
})

// 选择参数类型
const selectType = (val, index) => {
  if (val === 'file') {
    params.value[index][1] = ['', '', '']
  } else {
    params.value[index][1] = ''
  }
}

// 选择已有文件
const selectFile = (val, index) => {
  const sFile = files.value.find(item => item.info[0] === val)
  if (sFile) {
    params.value[index][1] = [...sFile.info]
  }
}

// 文件上传成功
const uploadSuccess = (response) => {
  ElNotification({
    type: 'success',
    title: '文件上传成功！',
    duration: 1500,
  })
  getFile()
}

// 文件上传失败
const uploadError = (error) => {
  ElNotification({
    title: '文件上传失败！',
    type: 'error',
    message: error.message,
    duration: 1500,
  })
}

// 获取文件列表
const getFile = async () => {
  const response = await http.fileApi.getFile({
    project: proStore.proList.id
  })
  if (response.status === 200) {
    files.value = response.data
  }
}

// 删除文件
function deleteFile(id) {
  ElMessageBox.confirm(
      '此操作不可恢复，确认要删除该文件?',
      '警告', {
        confirmButtonText: '确认',
        cancelButtonText: '取消',
        type: 'warning',
        center: true
      })
      .then(async () => {
        const response = await http.fileApi.deleteFile(id)
        if (response.status === 204) {
          files.value = response.data
          ElNotification({
            type: 'success',
            title: '文件删除成功！',
            duration: 1500,
          })
          await getFile()
        } else {
          ElNotification({
            type: 'error',
            title: '文件删除失败！',
            duration: 1500,
            message: response.data.detail,
          })
        }
      })
      .catch(() => {
        ElMessage({
          type: 'info',
          message: '已取消删除操作。',
          duration: 1500
        })
      })
}

// 添加参数行
const addParam = () => {
  params.value.push(['', ''])
}
// 删除参数行
const removeParam = (index) => {
  params.value.splice(index, 1)
}

// 获取参数类型
const getParamsType = () => {
  paramsType.value = params.value.map(item => (typeof item[1] === 'string' ? 'text' : 'file'))
}

// 监听参数变化
onMounted(() => {
  if (props.modelValue.length > 0) {
    params.value = props.modelValue
  } else {
    params.value = [['', '']]
  }
  getFile()
  getParamsType()
})
</script>

<style scoped>
</style>
