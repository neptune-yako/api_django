import userApi from './module/userApi.js'
import roleApi from './module/roleApi.js'
import projectApi from './module/projectApi.js'
import environmentApi from '@/api/module/environmentApi.js'
import interfaceApi from '@/api/module/interfaceApi.js'
import caseApi from "@/api/module/caseApi.js"
import suiteApi from '@/api/module/suiteApi'
import planApi from "@/api/module/planApi.js"
import recordApi from "@/api/module/recordApi.js"
import cronjobApi from '@/api/module/cronjobApi.js'
import bugApi from '@/api/module/bugApi.js'
import fileApi from "@/api/module/fileApi.js"
import reportApi from "@/api/module/reportApi.js"
import jenkinsApi from '@/api/jenkins'

export default {
    // 用户相关的接口
    userApi: userApi,
    // 角色相关的接口
    roleApi: roleApi,
    // 项目相关的接口
    projectApi: projectApi,
    // 环境相关的接口
    environmentApi: environmentApi,
    // 接口相关的接口
    interfaceApi: interfaceApi,
    // 用例相关的接口
    caseApi: caseApi,
    // 套件相关接口
    suiteApi: suiteApi,
    // 测试计划相关接口
    planApi: planApi,
    // 运行记录相关的接口
    recordApi: recordApi,
    // 测试报告相关接口
    reportApi: reportApi,
    // 定时任务相关接口
    cronjobApi: cronjobApi,
    // bug相关的接口
    bugApi: bugApi,
    // 文件上传接口
    fileApi: fileApi,
    // Jenkins相关接口
    jenkinsApi: jenkinsApi
}