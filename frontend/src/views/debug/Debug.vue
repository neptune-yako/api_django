<template>
  <div class="main_box">
    <div class="card box">
      <el-divider content-position="center"><b>请求信息</b></el-divider>
      <!-- url地址 -->
      <div class="name_edit">
        <el-input v-model="caseData.interface.url" placeholder="请输入接口地址（可以带ip+端口，不带时取测试环境）" clearable
                   style="width: calc(100% - 100px); margin-right: 10px;">
          <template #prepend>
            <el-select v-model="caseData.interface.method" placeholder="请选择请求方法" style="width: 100px">
              <el-option label="GET" value="get"/>
              <el-option label="POST" value="post"/>
              <el-option label="PUT" value="put"/>
              <el-option label="PATCH" value="patch"/>
              <el-option label="DELETE" value="delete"/>
            </el-select>
          </template>
        </el-input>
        <el-button @click='runInterFaseCase' icon="Promotion" plain type="success">运行</el-button>
      </div>

      <!-- 请求信息 -->
      <el-tabs type="border-card" class="demo-tabs" stretch style="margin-top: 10px;">
        <el-tab-pane>
          <template #label>
            <img src="@/assets/icons/headers.png" width="20" alt="" style="margin: 0 5px;">
            <span>请求头</span>
          </template>
          <Editor lang="json" v-model="caseData.headers"></Editor>
        </el-tab-pane>
        <el-tab-pane>
          <template #label>
            <img src="@/assets/icons/search.png" width="20" alt="" style="margin: 0 5px;">
            <span>查询参数</span>
          </template>
          <Editor lang="json" v-model="caseData.request.params"></Editor>
        </el-tab-pane>
        <el-tab-pane>
          <template #label>
            <img src="@/assets/icons/body.png" width="20" alt="" style="margin: 0 5px;">
            <span>请求体</span>
          </template>
          <el-radio-group v-model="bodyType">
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
            <FromData v-model="caseData.file"></FromData>
          </div>
        </el-tab-pane>
        <el-tab-pane>
          <template #label>
            <img src="@/assets/icons/instruction.png" width="20" alt="" style="margin: 0 5px;">
            <span>前置脚本</span>
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
        </el-tab-pane>
        <el-tab-pane>
          <template #label>
            <img src="@/assets/icons/inspection.png" width="20" alt="" style="margin: 0 5px;">
            <span>断言脚本</span>
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
        </el-tab-pane>
      </el-tabs>

      <!-- 响应信息 -->
      <el-divider content-position="center"><b>响应信息</b></el-divider>
      <Result :result='responseData' :hideBtn="true"></Result>
    </div>
  </div>
</template>

<script setup>
import FromData from '@/components/FormData.vue'
import {ref, reactive} from 'vue'
import Editor from '@/components/Editor.vue'
import Result from '@/components/Result.vue'
import http from '@/api/index'
import {ProjectStore} from '@/stores/module/ProStore'
import {ElNotification} from 'element-plus'

const pstore = ProjectStore()
const caseData = reactive({
  interface: {
    method: "get",
    url: ""
  },
  headers: {},
  request: {
    json: {},
    data: {},
    params: {}
  },
  file: [],
  setup_script: '# 前置脚本(python)\n# global_func：全局工具函数\n# data：用例数据 \n# env：临时环境\n# ENV：全局环境\n' +
      '# db：数据库操作对象\n',
  teardown_script: '# 断言脚本(python)\n# global_func：全局工具函数\n# data：用例数据 \n# response：响应对象 \n' +
      '# env：临时环境\n# ENV：全局环境\n# db：数据库操作对象\n'
})
let bodyType = ref('json')
// ===============运行接口用例===========
let responseData = ref({})

async function runInterFaseCase() {
  // URL必填校验
  if (!caseData.interface.url) {
    ElNotification({
      title: '运行失败',
      message: '接口地址url不能为空！',
      type: 'error',
      duration: 1500
    })
    return
  }
  // 接口用例的参数
  const params = {
    env: pstore.env,
    cases: {
      title: "调试运行",
      interface: caseData.interface,
      headers: caseData.headers,
      setup_script: caseData.setup_script,
      teardown_script: caseData.teardown_script,
      request: {
        params: caseData.request.params
      },
    }
  }
  // 判断请求体参数类型
  if (bodyType.value === 'json') {
    params.cases.request.json = caseData.request.json
  } else if (bodyType.value === 'data') {
    params.cases.request.data = caseData.request.data
  } else if (bodyType.value === 'form-data') {
    params.cases.file = caseData.request.file
  }
  const response = await http.caseApi.runCase(params)
  if (response.status === 200) {
    responseData.value = response.data
  }
}

// 生成前置脚本
function addSetupScript(item) {
  if (item === "func") {
    caseData.setup_script += '\n# 调用全局工具函数mobile随机生成一个手机号码\nmobile = global_func.mobile()\n'
  } else if (item === "global") {
    caseData.setup_script += '\n# 设置临时变量\ntest.save_global_variable("变量名","变量值")\n'
  } else if (item === "env") {
    caseData.setup_script += '\n# 设置临时变量\ntest.save_env_variable("变量名","变量值")\n'
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
    caseData.teardown_script += '\n# 设置临时变量\ntest.save_global_variable("变量名","变量值")\n'
  } else if (item === "env") {
    caseData.teardown_script += '\n# 设置临时变量\ntest.save_env_variable("变量名","变量值")\n'
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
@use './debug.scss';
</style>