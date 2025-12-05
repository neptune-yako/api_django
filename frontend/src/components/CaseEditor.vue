<template>
  <div class="title">编辑用例</div>
  <el-divider content-position="center"><b>用例信息</b></el-divider>
  <el-collapse :model-value='["1","2","3","4","5","6","7"]' accordion>
    <el-collapse-item name="1">
      <template #title>
        <img src="@/assets/icons/interface.png" width="20" alt="" style="margin: 0 5px -5px;">
        <b>接口信息</b>
      </template>
      <el-input v-model="caseData.interface.url" readonly>
        <template #prepend>
          <el-select v-model="caseData.interface.method" style="width: 100px">
            <el-option label="GET" value="get"/>
            <el-option label="POST" value="post"/>
            <el-option label="PUT" value="put"/>
            <el-option label="PATCH" value="patch"/>
            <el-option label="DELETE" value="delete"/>
          </el-select>
        </template>
      </el-input>
    </el-collapse-item>
    <el-collapse-item name="2">
      <template #title>
        <img src="@/assets/icons/case.png" width="20" alt="" style="margin: 0 5px -5px;">
        <b>用例名称</b>
      </template>
      <el-input v-model="caseData.title" placeholder="请输入用例名称" clearable>
        <template #prepend>
          <span>用例名称</span>
        </template>
      </el-input>
    </el-collapse-item>

    <el-collapse-item name="3">
      <template #title>
        <img src="@/assets/icons/headers.png" width="20" alt="" style="margin: 0 5px -5px;">
        <b>请求头</b>
      </template>
      <Editor lang="json" v-model="caseData.headers"></Editor>
    </el-collapse-item>
    <el-collapse-item name="4">
      <template #title>
        <img src="@/assets/icons/search.png" width="20" alt="" style="margin: 0 5px -5px;">
        <b>查询参数</b>
      </template>
      <Editor lang="json" v-model="caseData.request.params"></Editor>
    </el-collapse-item>
    <el-collapse-item name="5">
      <template #title>
        <img src="@/assets/icons/body.png" width="20" alt="" style="margin: 0 5px -5px;">
        <b>请求体</b>
      </template>
      <el-radio-group v-model="bodyType" style="margin-bottom: 5px;">
        <el-radio value="json">json</el-radio>
        <el-radio value="data">x-www-form-urlencoded</el-radio>
        <el-radio value="form-data">form-data</el-radio>
      </el-radio-group>
      <!-- json参数 -->
      <div v-if='bodyType==="json"'>
        <Editor lang="json" v-model="caseData.request.json"></Editor>
      </div>
      <div v-else-if='bodyType==="data"'>
        <Editor lang="json" v-model="caseData.request.data"></Editor>
      </div>
      <div v-else>
        <FromData v-model="caseData.file" :project-id="pstore.proList.id"></FromData>
      </div>
    </el-collapse-item>
    <el-collapse-item name="6">
      <template #title>
        <img src="@/assets/icons/instruction.png" width="20" alt="" style="margin: 0 5px -5px;">
        <b>前置脚本</b>
      </template>
      <div class='script_code'>
        <div class="code">
          <Editor v-model="caseData.setup_script" lang="python" height='300px'></Editor>
        </div>
        <div class='mod'>
          <el-divider content-position="center">前置脚本模板</el-divider>
          <div class="add_code" style="margin-top:10px;">
            <el-button @click='addSetupScript("func")' plain size="small" type="primary">全局工具函数</el-button>
          </div>
          <div class="add_code" style="margin-top:10px;">
            <el-button @click='addSetupScript("global")' plain size="small" type="primary">设置全局变量</el-button>
          </div>
          <div class="add_code" style="margin-top:10px;">
            <el-button @click='addSetupScript("env")' plain size="small" type="primary">设置临时变量</el-button>
          </div>
          <div class="add_code" style="margin-top:10px;">
            <el-button @click='addSetupScript("sql")' plain size="small" type="primary">执行sql查询</el-button>
          </div>
        </div>
      </div>
    </el-collapse-item>
    <el-collapse-item name="7">
      <template #title>
        <img src="@/assets/icons/inspection.png" width="20" alt="" style="margin: 0 5px -5px;">
        <b>断言脚本</b>
      </template>
      <div class='script_code'>
        <div class="code">
          <Editor v-model="caseData.teardown_script" lang="python" height='400px'></Editor>
        </div>
        <div class='mod'>
          <el-scrollbar height="400px">
            <el-divider content-position="center">断言脚本模板</el-divider>
            <div class="add_code" style="margin-top:10px;">
              <el-button @click="addTearDownCodeMod('func')" plain size="small" type="primary">
                全局工具函数
              </el-button>
            </div>
            <div class="add_code" style="margin-top:10px;">
              <el-button @click="addTearDownCodeMod('getBody')" plain size="small" type="primary">
                获取响应体
              </el-button>
            </div>
            <div class="add_code" style="margin-top:10px;">
              <el-button @click="addTearDownCodeMod('global')" plain size="small" type="primary">
                设置全局变量
              </el-button>
            </div>
            <div class="add_code" style="margin-top:10px;">
              <el-button @click="addTearDownCodeMod('env')" plain size="small" type="primary">
                设置临时变量
              </el-button>
            </div>
            <div class="add_code" style="margin-top:10px;">
              <el-button @click="addTearDownCodeMod('sql')" plain size="small" type="primary">
                执行sql查询
              </el-button>
            </div>
            <div class="add_code" style="margin-top:10px;">
              <el-button @click="addTearDownCodeMod('JSextract')" plain size="small" type="primary">
                jsonpath提取数据
              </el-button>
            </div>
            <div class="add_code" style="margin-top:10px;">
              <el-button @click="addTearDownCodeMod('REextract')" plain size="small" type="primary">
                正则表达式提取数据
              </el-button>
            </div>
            <div class="add_code" style="margin-top:10px;">
              <el-button @click="addTearDownCodeMod('http')" plain size="small" type="primary">
                http状态码
              </el-button>
            </div>
            <div class="add_code" style="margin-top:10px;">
              <el-button @click="addTearDownCodeMod('eq')" plain size="small" type="primary">
                相等
              </el-button>
            </div>
            <div class="add_code" style="margin-top:10px;">
              <el-button @click="addTearDownCodeMod('uneq')" plain size="small" type="primary">
                不相等
              </el-button>
            </div>
            <div class="add_code" style="margin-top:10px;">
              <el-button @click="addTearDownCodeMod('contain')" plain size="small" type="primary">
                包含
              </el-button>
            </div>
            <div class="add_code" style="margin-top:10px;">
              <el-button @click="addTearDownCodeMod('uncontain')" plain size="small" type="primary">
                不包含
              </el-button>
            </div>
          </el-scrollbar>
        </div>
      </div>
    </el-collapse-item>
  </el-collapse>
  <el-affix :offset="40" position="bottom">
    <div class="btns">
      <el-button @click='runCase' type="success" plain icon='Promotion'>运行</el-button>
      <el-button @click='copyCase' type="primary" plain icon='DocumentCopy'>复制</el-button>
      <el-button @click='saveCase' type="primary" plain icon='FolderChecked'>保存</el-button>
      <el-button @click='clickDelete' type="danger" plain icon='Delete'>删除</el-button>
    </div>
  </el-affix>

  <!-- 测试用例运行的结果 -->
  <el-drawer v-model="isShowDrawer" size="40%" direction="rtl" :with-header="false">
    <div class="title">用例运行结果</div>
    <Result :result='responseData' @close="isShowDrawer = false"></Result>
  </el-drawer>
</template>

<script setup>
import FromData from '@/components/FormData.vue'
import {ElNotification, ElMessageBox, ElMessage} from 'element-plus'
import {ref, reactive, watch, onMounted} from 'vue'
import Editor from '@/components/Editor.vue'
import http from '@/api/index'
import {ProjectStore} from '@/stores/module/ProStore'
import Result from '@/components/Result.vue'
import {UserStore} from "@/stores/module/UserStore.js"

const pstore = ProjectStore()
const userStore = UserStore()
const prop = defineProps({
  case_id: ""
})
let bodyType = ref('json')
// 页面绑定的用例编辑数据
const caseData = reactive({
  title: "",
  interface: {
    method: "GET",
    url: ""
  },
  headers: "{}",
  request: {
    json: '{}',
    data: '{}',
    params: '{}'
  },
  file: [],
  setup_script: '',
  teardown_script: ''
})

// 保存用例详情对象
let caseObj = {}

// 侦听case_id的变化
watch(() => prop.case_id, (val) => {
  if (val !== '') {
    getCaseInfo(val)
  }
})

// 打开页面，数据挂载完毕之后执行
onMounted(() => {
  if (prop.case_id) {
    getCaseInfo(prop.case_id)
  }
})

// 调用获取详情的接口
async function getCaseInfo(id) {
  const response = await http.caseApi.getCaseInfo(id)
  if (response.status === 200) {
    // 保存用例对象
    caseObj = response.data
    // 把用例数据绑定到编辑页面
    caseData.title = caseObj.title
    caseData.interface = caseObj.interface
    caseData.setup_script = caseObj.setup_script
    caseData.file = caseObj.file
    caseData.teardown_script = caseObj.teardown_script
    caseData.headers = caseObj.headers
    caseData.request.json = caseObj.request.json
    caseData.request.data = caseObj.request.data
    caseData.request.params = caseObj.request.params
    caseData.file = caseObj.file
  }else {
    ElNotification({
      title: '测试用例详情获取失败！',
      type: 'error',
      message: response.data,
      duration: 1500
    })
  }
}

// 删除测试用例的方法
function clickDelete() {
  ElMessageBox.confirm(
      '此操作不可恢复，请确认是否要删除该测试用例?',
      '警告', {
        confirmButtonText: '确认',
        cancelButtonText: '取消',
        type: 'warning',
        center: true
      })
      .then(async () => {
        // 调用后端接口进行删除
        const response = await http.caseApi.deleteCase(prop.case_id)
        if (response.status === 204) {
          ElNotification({
            title: '测试用例删除成功！',
            type: 'success',
            duration: 1500
          })
          // 刷新页面数据
          await pstore.getInterFaceList()
          resetData()
        } else {
          ElNotification({
            title: '测试用例删除失败！',
            type: 'error',
            message: response.data,
            duration: 1500
          })
        }
      })
      .catch(() => {
        ElMessage({
          type: 'info',
          message: '已取消测试用例删除操作。',
          duration: 1500
        })
      })
}

function resetData() {
  // 清空页面编辑的数据
  caseData.title = ''
  caseData.interface = {
    method: "get",
    url: ""
  }
  caseData.setup_script = ''
  caseData.file = []
  caseData.teardown_script = ''
  caseData.headers = "{}"
  caseData.request.json = "{}"
  caseData.request.data = "{}"
  caseData.request.params = "{}"
  caseObj = {}
}

// 复制用例
async function copyCase() {
  const response = await http.caseApi.createCase({
    title: caseObj.title + '-复制',
    interface: caseObj.interface.id,
    username: userStore.userInfo.username
  })
  if (response.status === 201) {
    ElNotification({
      title: '测试用例复制成功！',
      type: 'success',
      duration: 1500
    })
    // 刷新页面数据
    await pstore.getInterFaceList()
  } else {
    ElNotification({
      title: '测试用例复制失败！',
      type: 'error',
      message: response.data,
      duration: 1500
    })
  }
}

// 保存用例
async function saveCase() {
  // 准备参数
  const params = {
    title: caseData.title,
    headers: caseData.headers,
    request: {
      params: caseData.request.params,
    },
    setup_script: caseData.setup_script,
    teardown_script: caseData.teardown_script,
  }
  if (bodyType.value === 'json') {
    params.request.json = caseData.request.json
  } else if (bodyType.value === 'data') {
    params.request.data = caseData.request.data
  } else {
    params.file = caseData.file
  }
  // 调用修改用例的接口
  const response = await http.caseApi.updateCase(prop.case_id, params)
  if (response.status === 200 && response.data.code !== 300) {
    ElNotification({
      title: '测试用例保存成功！',
      type: 'success',
      duration: 1500
    })
    // 刷新页面数据
    await pstore.getInterFaceList()
  } else {
    ElNotification({
      title: '测试用例保存失败！',
      type: 'error',
      message: response.data,
      duration: 1500
    })
  }
}

// 保存用例运行的结果
let responseData = ref({})
// 是否显示结果的窗口
let isShowDrawer = ref(false)

async function runCase() {
  // 准备参数
  const params = {
    env: pstore.env,
    cases: {
      title: caseData.title,
      interface: caseData.interface,
      headers: caseData.headers,
      request: {
        params: caseData.request.params,
      },
      setup_script: caseData.setup_script,
      teardown_script: caseData.teardown_script,
    }
  }
  if (bodyType.value === 'json') {
    params.cases.request.json = caseData.request.json
  } else if (bodyType.value === 'data') {
    params.cases.request.data = caseData.request.data
  } else {
    params.cases.file = caseData.file
  }
  // 调用运行用例的接口
  const response = await http.caseApi.runCase(params)
  if (response.status === 200) {
    ElNotification({
      title: '测试用例运行成功！',
      type: 'success',
      duration: 1500
    })
    // 保存用例运行的结果
    responseData.value = response.data
    // 展示执行结果
    isShowDrawer.value = true
  } else {
    ElNotification({
      title: '测试用例运行失败！',
      type: 'error',
      message: response.data.detail,
      duration: 1500
    })
  }
}

// 生成前置脚本
function addSetupScript(item) {
  if (item === "func") {
    caseData.setup_script += '\n# 调用全局工具函数mobile随机生成一个手机号码\nmobile = global_func.mobile()\n'
  } else if (item === "global") {
    caseData.setup_script += '\n# 设置全局变量\ntest.save_global_variable("变量名",变量值)\n'
  } else if (item === "env") {
    caseData.setup_script += '\n# 设置临时变量\ntest.save_env_variable("变量名",变量值)\n'
  } else if (item === "sql") {
    caseData.setup_script += '\n# 执行sql语句，格式：db.连接名.execute_all(sql语句)\nsql = "SELECT * FROM "\nres = db.aliyun.execute_all(sql)\n'
  }
}

// 生成后置脚本
function addTearDownCodeMod(item) {
  if (item === "getBody") {
    caseData.teardown_script += '\n# 获取响应体(json)\nbody = response.json()\n';
    caseData.teardown_script += '\n# 获取响应体(字符串)\nbody = response.text\n';
  } else if (item === "JSextract") {
    caseData.teardown_script += '\n# 使用jsonpath提取response中的msg字段\nmsg = test.json_extract(response.json(),"$..msg")\n';
  } else if (item === "REextract") {
    caseData.teardown_script += '\n# 正则表达式提取响应体中的数据\nres = test.re_extract(response.text,"正则表达式")\n';
  } else if (item === "sql") {
    caseData.teardown_script += '\n# 执行sql语句，格式：db.连接名.execute_all(sql语句)\nsql = "SELECT * FROM "\nres = db.aliyun.execute_all(sql)\n'
  } else if (item === "global") {
    caseData.teardown_script += '\n# 设置全局变量\ntest.save_global_variable("变量名",变量值)\n'
  } else if (item === "env") {
    caseData.teardown_script += '\n# 设置临时变量\ntest.save_env_variable("变量名",变量值)\n'
  } else if (item === "func") {
    caseData.teardown_script += '\n# 调用全局工具函数mobile随机生成一个手机号码\nmobile = global_func.mobile()\n'
  } else if (item === "http") {
    caseData.teardown_script += '\n# http状态码是否为200\ntest.assertion("相等",200,response.status_code)\n';
  } else if (item === "eq") {
    caseData.teardown_script += '\n# 相等：预期结果中与实际结果的内容完全相等\ntest.assertion("相等","预期结果","实际结果")\n';
  } else if (item === "uneq") {
    caseData.teardown_script += '\n# 不相等：预期结果中与实际结果的内容不完全相等\ntest.assertion("不相等","预期结果","实际结果")\n';
  } else if (item === "contain") {
    caseData.teardown_script += '\n# 包含：预期结果中的内容在实际结果中是否存在\ntest.assertion("包含","预期结果","实际结果")\n';
  } else if (item === "uncontain") {
    caseData.teardown_script += '\n# 不包含：预期结果中的内容在实际结果中是否存在\ntest.assertion("不包含","预期结果","实际结果")\n';
  }
}
</script>

<style lang="scss" scoped>
@use './caseEditor.scss';
</style>