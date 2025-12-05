<template>
  <div class="result">
    <el-tabs type="border-card" class="demo-tabs" v-show='result.name'>
      <el-tab-pane label="响应体">
        <Editor lang="json" v-model='result.response_body'></Editor>
      </el-tab-pane>

      <el-tab-pane label="响应头">
        <div v-for='(v,k) in result.response_header'>
          <el-tag type="info">
            <b>{{ k }}：{{ v }}</b>
          </el-tag>
        </div>
      </el-tab-pane>

      <el-tab-pane label="请求信息">
        <el-collapse>
          <el-collapse-item title="请求" name="1">
            <div>请求方法：{{ result.method }}</div>
            <div>请求地址：{{ result.url }}</div>
          </el-collapse-item>
          <el-collapse-item title="请求头" name="2">
            <div v-for='(v,k) in result.requests_header'>
              {{ k }}：{{ v }}
            </div>
          </el-collapse-item>
          <el-collapse-item title="请求参数" name="3">
            {{ result.requests_body }}
          </el-collapse-item>
        </el-collapse>
      </el-tab-pane>

      <el-tab-pane label="日志">
        <div style="overflow-x: auto;">
          <div v-for='item in result.log_data'>
            <el-tag v-if='item[0] ==="INFO"' type="info">{{ item[1] }}</el-tag>
            <el-tag v-else-if='item[0] ==="DEBUG"' type="success">{{ item[1] }}</el-tag>
            <el-tag v-else type="danger">{{ item[1] }}</el-tag>
          </div>
        </div>
      </el-tab-pane>

      <el-tab-pane disabled>
        <template #label>
          <span v-if='result.state==="成功"' style="color: #1ab43a;">断言：{{ result.state }}</span>
          <span v-else style="color: #f4b806;">断言：{{ result.state }}</span>
        </template>
      </el-tab-pane>

      <el-tab-pane disabled>
        <template #label>
          <span v-if='result.status_code < 300' style="color: #1ab43a;">状态码：{{ result.status_code }}</span>
          <span v-else style="color: #f4b806;">状态码：{{ result.status_code }}</span>
        </template>
      </el-tab-pane>
      <el-tab-pane disabled>
        <template #label>
          耗时：{{ result.run_time }}
        </template>
      </el-tab-pane>
    </el-tabs>
  </div>

  <div style="margin-top: 10px;width: 100%;text-align: center;" v-if="result.state === '失败'">
    <el-button v-show='!hideBtn' @click="addBugDlg = true" plain type="danger">提交bug</el-button>
  </div>
  <!-- 添加bug的弹框 -->
  <el-dialog title="提交bug" v-model="addBugDlg" width="40%" center>
    <el-form :model="bugForm" :rules="formDataRules" ref="formDataRef" label-width="auto">
      <el-form-item label="所属接口：" prop="interface">
        <el-select v-model="bugForm.interface" placeholder="请选择bug对应的接口" style="width: 100%;"
                   clearable :fit-input-width="true">
          <el-option :label="iter.name + '：' + iter.url" :value="iter.id" v-for="iter in interfaces" :key="iter.id"
                     :title="iter.name + '：' + iter.url"></el-option>
        </el-select>
      </el-form-item>
      <el-form-item label="bug状态：" prop="status">
        <el-select v-model="bugForm.status" placeholder="请选择bug状态" style="width: 100%;" disabled>
          <el-option :label="iter.name" :value="iter.id" v-for="iter in status" :key="iter.id"></el-option>
        </el-select>
      </el-form-item>
      <el-form-item label="bug等级：" prop="level">
        <el-select v-model="bugForm.level" placeholder="请选择bug等级" style="width: 100%;" clearable>
          <el-option :label="iter.name" :value="iter.id" v-for="iter in level" :key="iter.id"></el-option>
        </el-select>
      </el-form-item>
      <el-form-item label="bug描述：" prop="describe">
        <el-input :autosize="{ minRows: 3, maxRows: 4 }" v-model="bugForm.describe" type="textarea" autocomplete="off"
                  placeholder="请输入bug的描述信息"></el-input>
      </el-form-item>
    </el-form>
    <template #footer>
      <div class="dialog-footer">
        <el-button type="primary" plain @click="saveBug(formDataRef)">确定</el-button>
        <el-button @click="addBugDlg = false" plain>取消</el-button>
      </div>
    </template>
  </el-dialog>
  <div v-if="!hideBtn" class="button">
    <el-button type="primary" @click="isShowDrawer" plain>确定</el-button>
  </div>
</template>

<script setup>
import {ref, reactive} from 'vue'
import Editor from '@/components/Editor.vue'
import http from '@/api/index'
import {ElNotification} from 'element-plus'
import {ProjectStore} from '@/stores/module/ProStore'

const level = ref([
  {id: '3', name: '轻微'},
  {id: '2', name: '一般'},
  {id: '1', name: '严重'}
])

const status = ref([
  {id: '1', name: '未处理'},
  {id: '2', name: '处理中'},
  {id: '3', name: '处理完'},
  {id: '4', name: '无效的'}
])

const prop = defineProps({
  result: {},
  hideBtn: false
})
// 实例化store对象
const proStore = ProjectStore()
const interfaces = proStore.interfaces
const addBugDlg = ref(false)
const bugForm = reactive({
  interface: null,
  level: null,
  describe: '',
  info: '',
  status: '1'
})
// 校验bug
const formDataRules = reactive({
  interface: [{required: true, message: '所属接口不能为空！', trigger: 'blur'}],
  level: [{required: true, message: 'bug等级不能为空！', trigger: 'blur'}],
  describe: [
    {required: true, message: 'bug描述不能为空！', trigger: 'blur'},
    {max: 255, message: 'bug描述不能超过255个字符！', trigger: 'blur'}
  ]
})
// 表单引用对象
const formDataRef = ref()

// 保存bug的方法
async function saveBug(elForm) {
  elForm.validate(async function (res) {
    if (!res) return
    bugForm.project = proStore.proList.id
    bugForm.info = prop.result
    const response = await http.bugApi.createBug(bugForm)
    if (response.status === 201) {
      ElNotification({
        type: 'success',
        title: 'bug提交成功！',
        duration: 1500
      })
      addBugDlg.value = false
    } else {
      ElNotification({
        title: 'bug提交失败！',
        type: 'error',
        message: response.data.detail,
        duration: 1500
      })
    }
  })
}
// 关闭窗口
const emit = defineEmits(['close'])
function isShowDrawer() {
  emit('close')
}
</script>

<style lang="scss" scoped>
@use './result.scss';
</style>