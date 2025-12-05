<template>
  <div class="card page-box" style="padding: 10px;">
    <el-button plain @click='clickAdd' type="primary" icon="CirclePlus" size="small">任务</el-button>
    <el-button plain @click='getCronjob' type="success" icon="Refresh" size="small">刷新</el-button>
    <el-table :data="state.cronjobList" style="width: 100%" stripe :header-cell-style="{'text-align':'center'}"
              :cell-style="{'text-align':'center'}" v-loading="loading" element-loading-text="加载中...">
      <template #empty>
        <div class="table-empty">
          <img src="@/assets/images/none.png" alt="notData"/>
          <div>暂无数据</div>
        </div>
      </template>
      <el-table-column label="序号" type="index" width="90"></el-table-column>
      <el-table-column prop="name" label="任务名称" min-width="140"></el-table-column>
      <el-table-column prop="pro_name" label="项目名称" min-width="140"></el-table-column>
      <el-table-column prop="plan_name" label="计划名称" min-width="140"></el-table-column>
      <el-table-column prop="env_name" label="环境名称" min-width="140"></el-table-column>
      <el-table-column prop="username" label="创建人" width="80"/>
      <el-table-column prop="rule" label="定时规则" min-width="140"></el-table-column>
      <el-table-column label="创建时间" min-width="180">
        <template #default="scope">
          {{ tools.rTime(scope.row.create_time) }}
        </template>
      </el-table-column>
      <el-table-column label="更新时间" min-width="180">
        <template #default="scope">
          {{ tools.rTime(scope.row.update_time) }}
        </template>
      </el-table-column>
      <el-table-column label="状态">
        <template #default="scope">
          <el-switch @change='switchCronStatus(scope.row)' v-model="scope.row.status" active-color="#13ce66"
                     inactive-color="#b1b1b1"></el-switch>
        </template>
      </el-table-column>
      <el-table-column label="操作" min-width="180">
        <template #default="scope">
          <el-button @click='showUpdateCronDlg(scope.row)' type="primary" plain icon="Edit">编辑</el-button>
          <el-button @click="deleteCronjob(scope.row.id)" type="danger" plain icon="Delete">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
    <div class="pagination" style="margin: 5px 5px 0">
      <el-pagination
          v-model:current-page="pageConfig.page"
          v-model:page-size="pageConfig.size"
          :page-sizes="[10, 20, 30, 40]"
          layout="total, sizes, prev, pager, next, jumper"
          :total="pageConfig.count"
          @current-change="getCronjob"
          @size-change="getCronjob"
      />
    </div>
  </div>

  <!-- 创建、修改定时任务的窗口 -->
  <el-drawer v-model="state.dialogCronjob" :with-header="false" direction="rtl" width="50%">
    <div class="title">
      <span v-if="state.updateBtn">修改定时任务</span>
      <span v-else>创建定时任务</span>
    </div>
    <el-form :model="state.cronjobData" :rules="formDataRules" ref="formDataRef" label-width="auto">
      <el-form-item label="任务名称：" prop="name">
        <el-input v-model="state.cronjobData.name" placeholder="请输入任务名称" clearable></el-input>
      </el-form-item>
      <el-form-item label="测试环境：" prop="env">
        <el-select v-model="state.cronjobData.env" placeholder="请选择测试环境" style="width: 100%;" clearable>
          <el-option v-for="item in proStore.envList" :key="item.id" :label="item.name" :value="item.id">
          </el-option>
        </el-select>
      </el-form-item>
      <el-form-item label="测试计划：" prop="plan">
        <el-select style="width: 100%;" v-model="state.cronjobData.plan" placeholder="请选择测试计划" clearable>
          <el-option v-for="item in proStore.planList" :key="item.id" :label="item.name" :value="item.id">
          </el-option>
        </el-select>
      </el-form-item>
      <el-form-item label="状态：">
        <el-switch v-model="state.cronjobData.status" active-color="#79d0ff" inactive-color="#c3c3c3"
                   size="small">
        </el-switch>
      </el-form-item>
      <el-form-item label="创建人：" prop="username">
        <el-input v-model="state.cronjobData.username" placeholder="请输入创建人" disabled></el-input>
      </el-form-item>
      <el-form-item label="定时规则：" prop="rule">
        <el-input v-model="state.cronjobData.rule" placeholder="请输入定时规则，格式：* * * * *" clearable></el-input>
        <el-col :span="24">
          <h4>规则说明：crontab格式，具体参考官网：https://crontab.guru</h4>
          <div style="font-size: 14px">* * * * * <span style="color:#909399">分别表示：minute、hour、day、month、week。</span>
          </div>
          <div style="font-size: 14px">minute：<span style="color:#909399">表示分钟，从0到59之间的任何整数。</span>
          </div>
          <div style="font-size: 14px">hour：<span style="color:#909399">表示小时，从0到23之间的任何整数。</span>
          </div>
          <div style="font-size: 14px">day：<span style="color:#909399">表示日期，从1到31之间的任何整数。</span>
          </div>
          <div style="font-size: 14px">month：<span style="color:#909399">表示月份，从1到12之间的任何整数。</span>
          </div>
          <div style="font-size: 14px">week：<span
              style="color:#909399">表示星期几，从0到7之间的任何整数，0或7代表星期日。</span></div>
        </el-col>
        <el-col :span="24">
          <h4>配置案例：</h4>
          <div style="font-size: 14px">5 * * * * : <span style="color:#909399">每小时的第5分钟执行一次任务。</span></div>
          <div style="font-size: 14px">30 9 * * * : <span style="color:#909399">每天上午的9:30执行一次任务。</span></div>
          <div style="font-size: 14px">30 9 8 * * : <span style="color:#909399">每月8号上午的9:30执行一次任务。</span>
          </div>
          <div style="font-size: 14px">30 9 5 3 * : <span style="color:#909399">每年的3月5日9:30执行一次任务。</span>
          </div>
          <div style="font-size: 14px">30 9 * * sun : <span style="color:#909399">每星期日的上午9:30执行一次任务。</span>
          </div>
        </el-col>
      </el-form-item>
    </el-form>
    <template #footer>
      <div slot="footer" class="dialog-footer" style="text-align: center;">
        <el-button v-if="state.updateBtn" type="primary" @click="UpdateCron(formDataRef)" plain>确定</el-button>
        <el-button v-else type="primary" @click="createCron(formDataRef)" plain>确定</el-button>
        <el-button @click="state.dialogCronjob=false" plain>取消</el-button>
      </div>
    </template>
  </el-drawer>
</template>

<script setup>
import {ProjectStore} from '@/stores/module/ProStore'
import {ElNotification, ElMessageBox, ElMessage} from 'element-plus'
import http from '@/api/index'
import {reactive, ref} from 'vue'
import tools from '@/utils/dateTools'
import {UserStore} from "@/stores/module/UserStore.js"

const userStore = UserStore()
const proStore = ProjectStore()
const state = reactive({
  // 定时任务列表
  cronjobList: null,
  dialogCronjob: false,
  updateBtn: true,
  // 添加定时任务
  cronjobData: {
    name: "定时任务",
    rule: "*/1 * * * *",
    status: false,
    plan: null,
    env: null,
    username: userStore.userInfo.username
  },
})
// 分页配置
const pageConfig = reactive({
  page: 1,
  size: 10,
  count: 0
})
// 加载中
const loading = ref(false)
// 获取所有的定时任务
async function getCronjob() {
  loading.value = true
  const params = {
    page: pageConfig.page,
    size: pageConfig.size
  }
  const response = await http.cronjobApi.getCronjob(proStore.proList.id, params)
  if (response.status === 200) {
    state.cronjobList = response.data.results
    pageConfig.count = response.data.count
    loading.value = false
  }
}
getCronjob()

// 开启和关闭定时任务
async function switchCronStatus(cronjob) {
  const response = await http.cronjobApi.updateCronjob(cronjob.id, cronjob)
  if (response.status === 200 && response.data.code !== 300) {
    if (cronjob.status === true) {
      ElNotification({
        type: 'success',
        title: '定时任务已开启！',
        duration: 1500
      })
      await getCronjob()
    } else {
      ElNotification({
        type: 'warning',
        title: '定时任务已关闭！',
        duration: 1500
      })
    }
  } else {
    ElNotification({
      title: '定时任务开启失败！',
      type: 'error',
      message: response.data.detail,
      duration: 1500
    })
  }
}

//删除定时任务
function deleteCronjob(id) {
  ElMessageBox.confirm(
      '此操作不可恢复，确认要删除该任务?',
      '警告', {
        confirmButtonText: '确认',
        cancelButtonText: '取消',
        type: 'warning',
        center: true
      })
      .then(async () => {
        // 删除定时任务
        const response = await http.cronjobApi.deleteCronjob(id)
        if (response.status === 204) {
          ElNotification({
            type: 'success',
            title: '定时任务删除成功！',
            duration: 1500
          })
          // 刷新页面定时任务
          await getCronjob()
        } else {
          ElNotification({
            title: '定时任务删除失败！',
            type: 'error',
            message: response.data.detail,
            duration: 1500
          })
        }
      })
      .catch(() => {
        ElMessage({
          type: 'info',
          message: '已取消删除定时任务。',
          duration: 1500
        })
      })
}

// 点击添加按钮
function clickAdd() {
  state.dialogCronjob = true
  state.updateBtn = false
}

// 校验定时任务
const formDataRules = reactive({
  name: [
    {required: true, message: '定时任务名称不能为空！', trigger: 'blur'},
    {max: 20, message: '定时任务名称长度b不超过20个字符！', trigger: 'blur'}
  ],
  env: [{required: true, message: '测试环境不能为空！', trigger: 'blur'}],
  rule: [{required: true, message: '定时规则不能为空！', trigger: 'blur'}],
  plan: [{required: true, message: '执行计划不能为空！', trigger: 'blur'}]
})
// 表单引用对象
const formDataRef = ref()

// 添加定时任务
async function createCron(elForm) {
  elForm.validate(async function (res) {
    if (!res) return
    const params = {
      project: proStore.proList.id,
      ...state.cronjobData
    }
    const response = await http.cronjobApi.createCronjob(params)
    if (response.status === 200 && response.data.code !== 300) {
      ElNotification({
        type: 'success',
        title: '定时任务添加成功！',
        duration: 1500
      })
      state.dialogCronjob = false
      await getCronjob()
    } else {
      ElNotification({
        title: '定时任务添加失败！',
        message: response.data.detail,
        type: 'error',
        duration: 1500
      })
    }
  })
}

//显示修改定时任务的窗口
function showUpdateCronDlg(cron) {
  state.cronjobData = {...cron}
  state.dialogCronjob = true
  // 显示修改按钮
  state.updateBtn = true
}

// 修改定时任务
async function UpdateCron() {
  const response = await http.cronjobApi.updateCronjob(state.cronjobData.id, state.cronjobData)
  if (response.status === 200 && response.data.code !== 300) {
    ElNotification({
      type: 'success',
      title: '定时任务修改成功！',
      duration: 1500
    })
    state.dialogCronjob = false
    await getCronjob()
  } else {
    ElNotification({
      title: '定时任务修改失败！',
      message: response.data.detail,
      type: 'error',
      duration: 1500
    })
  }
}
</script>

<style lang="scss" scoped>
@use './cronjob.scss';
</style>