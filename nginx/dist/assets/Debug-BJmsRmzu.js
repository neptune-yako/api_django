import{_ as U,a as T,b as R,c as S,d as D,e as B}from"./FormData-CJACffRn.js";import{_ as m}from"./Editor-CMLAlzEc.js";import{R as N}from"./Result-DvMrgyyD.js";import{E as P,h as F}from"./index-Bqsb1G-Q.js";import{P as M}from"./ProStore-981bTmq_.js";import{_ as L}from"./_plugin-vue_export-helper-DlAUqK2U.js";import{v as O,a as w,D as g,F as o,U as t,M as s,u as b,ao as p,E as x,R as i,q as A}from"./vue-CXALzJrr.js";import"./none-CwC0Lq_I.js";import"./dateTools-APCdG_Ih.js";const I={class:"main_box"},J={class:"card box"},G={class:"name_edit"},H={key:0},K={key:1},Q={key:2},W={class:"script_code"},X={class:"code"},Y={class:"mod"},Z={class:"add_code",style:{"margin-top":"10px"}},h={class:"add_code",style:{"margin-top":"10px"}},ee={class:"add_code",style:{"margin-top":"10px"}},te={class:"add_code",style:{"margin-top":"10px"}},le={class:"script_code"},se={class:"code"},ne={class:"mod"},oe={class:"add_code",style:{"margin-top":"10px"}},ae={class:"add_code",style:{"margin-top":"10px"}},ie={class:"add_code",style:{"margin-top":"10px"}},de={class:"add_code",style:{"margin-top":"10px"}},re={class:"add_code",style:{"margin-top":"10px"}},pe={class:"add_code",style:{"margin-top":"10px"}},ue={class:"add_code",style:{"margin-top":"10px"}},me={class:"add_code",style:{"margin-top":"10px"}},_e={class:"add_code",style:{"margin-top":"10px"}},fe={class:"add_code",style:{"margin-top":"10px"}},ve={class:"add_code",style:{"margin-top":"10px"}},ye={class:"add_code",style:{"margin-top":"10px"}},ge={__name:"Debug",setup(be){const C=M(),l=O({interface:{method:"get",url:""},headers:"{}",request:{json:"{}",data:"{}",params:"{}"},file:[],setup_script:`# 前置脚本(python)
# global_func：全局工具函数
# data：用例数据 
# env：临时环境
# ENV：全局环境
# db：数据库操作对象
`,teardown_script:`# 断言脚本(python)
# global_func：全局工具函数
# data：用例数据 
# response：响应对象 
# env：临时环境
# ENV：全局环境
# db：数据库操作对象
`});let u=w("json"),q=w({});async function k(){if(!l.interface.url){P({title:"运行失败",message:"接口地址url不能为空！",type:"error",duration:1500});return}const a={env:C.env,cases:{title:"调试运行",interface:l.interface,headers:l.headers,setup_script:l.setup_script,teardown_script:l.teardown_script,request:{params:l.request.params}}};u.value==="json"?a.cases.request.json=l.request.json:u.value==="data"?a.cases.request.data=l.request.data:u.value==="form-data"&&(a.cases.file=l.request.file);const e=await F.caseApi.runCase(a);e.status===200&&(q.value=e.data)}function v(a){a==="func"?l.setup_script+=`
# 调用全局工具函数mobile随机生成一个手机号码
mobile = global_func.mobile()
`:a==="global"?l.setup_script+=`
# 设置临时变量
test.save_global_variable("变量名","变量值")
`:a==="env"?l.setup_script+=`
# 设置临时变量
test.save_env_variable("变量名","变量值")
`:a==="sql"&&(l.setup_script+=`
# 执行sql语句，格式：db.连接名.execute_all(sql语句)
sql = "SELECT * FROM "
res = db.aliyun.execute_all(sql)
`)}function r(a){a==="getBody"?(l.teardown_script+=`
# 获取响应体(json)
body = response.json()
`,l.teardown_script+=`
# 获取响应体(字符串)
body = response.text
`):a==="JSextract"?l.teardown_script+=`
# 使用jsonpath提取response中的msg字段
msg = test.json_extract(response.json(),"$..msg")
`:a==="REextract"?l.teardown_script+=`
# 正则表达式提取响应体中的数据
res = test.re_extract(response.text,"正则表达式")
`:a==="sql"?l.teardown_script+=`
# 执行sql语句，格式：db.连接名.execute_all(sql语句)
sql = "SELECT * FROM "
res = db.aliyun.execute_all(sql)
`:a==="global"?l.teardown_script+=`
# 设置临时变量
test.save_global_variable("变量名","变量值")
`:a==="env"?l.teardown_script+=`
# 设置临时变量
test.save_env_variable("变量名","变量值")
`:a==="func"?l.teardown_script+=`
# 调用全局工具函数mobile随机生成一个手机号码
mobile = global_func.mobile()
`:a==="http"?l.teardown_script+=`
# http状态码是否为200
test.assertion("相等",200,response.status_code)
`:a==="eq"?l.teardown_script+=`
# 相等：预期结果中与实际结果的内容完全相等
test.assertion("相等","预期结果","实际结果")
`:a==="uneq"?l.teardown_script+=`
# 不相等：预期结果中与实际结果的内容不完全相等
test.assertion("不相等","预期结果","实际结果")
`:a==="contain"?l.teardown_script+=`
# 包含：预期结果中的内容在实际结果中是否存在
test.assertion("包含","预期结果","实际结果")
`:a==="uncontain"&&(l.teardown_script+=`
# 不包含：预期结果中的内容在实际结果中是否存在
test.assertion("不包含","预期结果","实际结果")
`)}return(a,e)=>{const y=p("el-divider"),_=p("el-option"),j=p("el-select"),$=p("el-input"),d=p("el-button"),f=p("el-tab-pane"),V=p("el-radio"),c=p("el-radio-group"),z=p("el-scrollbar"),E=p("el-tabs");return x(),g("div",I,[o("div",J,[t(y,{"content-position":"center"},{default:s(()=>[...e[26]||(e[26]=[o("b",null,"请求信息",-1)])]),_:1}),o("div",G,[t($,{modelValue:l.interface.url,"onUpdate:modelValue":e[1]||(e[1]=n=>l.interface.url=n),placeholder:"请输入接口地址（可以带ip+端口，不带时取测试环境）",clearable:"",style:{width:"calc(100% - 100px)","margin-right":"10px"}},{prepend:s(()=>[t(j,{modelValue:l.interface.method,"onUpdate:modelValue":e[0]||(e[0]=n=>l.interface.method=n),placeholder:"请选择请求方法",style:{width:"100px"}},{default:s(()=>[t(_,{label:"GET",value:"get"}),t(_,{label:"POST",value:"post"}),t(_,{label:"PUT",value:"put"}),t(_,{label:"PATCH",value:"patch"}),t(_,{label:"DELETE",value:"delete"})]),_:1},8,["modelValue"])]),_:1},8,["modelValue"]),t(d,{onClick:k,icon:"Promotion",plain:"",type:"success"},{default:s(()=>[...e[27]||(e[27]=[i("运行",-1)])]),_:1})]),t(E,{type:"border-card",class:"demo-tabs",stretch:"",style:{"margin-top":"10px"}},{default:s(()=>[t(f,null,{label:s(()=>[...e[28]||(e[28]=[o("img",{src:U,width:"20",alt:"",style:{margin:"0 5px"}},null,-1),o("span",null,"请求头",-1)])]),default:s(()=>[t(m,{lang:"json",modelValue:l.headers,"onUpdate:modelValue":e[2]||(e[2]=n=>l.headers=n)},null,8,["modelValue"])]),_:1}),t(f,null,{label:s(()=>[...e[29]||(e[29]=[o("img",{src:T,width:"20",alt:"",style:{margin:"0 5px"}},null,-1),o("span",null,"查询参数",-1)])]),default:s(()=>[t(m,{lang:"json",modelValue:l.request.params,"onUpdate:modelValue":e[3]||(e[3]=n=>l.request.params=n)},null,8,["modelValue"])]),_:1}),t(f,null,{label:s(()=>[...e[30]||(e[30]=[o("img",{src:S,width:"20",alt:"",style:{margin:"0 5px"}},null,-1),o("span",null,"请求体",-1)])]),default:s(()=>[t(c,{modelValue:b(u),"onUpdate:modelValue":e[4]||(e[4]=n=>A(u)?u.value=n:u=n)},{default:s(()=>[t(V,{value:"json"},{default:s(()=>[...e[31]||(e[31]=[i("json",-1)])]),_:1}),t(V,{value:"data"},{default:s(()=>[...e[32]||(e[32]=[i("x-www-form-urlencoded",-1)])]),_:1}),t(V,{value:"form-data"},{default:s(()=>[...e[33]||(e[33]=[i("form-data",-1)])]),_:1})]),_:1},8,["modelValue"]),b(u)==="json"?(x(),g("div",H,[t(m,{lang:"json",modelValue:l.request.json,"onUpdate:modelValue":e[5]||(e[5]=n=>l.request.json=n)},null,8,["modelValue"])])):b(u)==="data"?(x(),g("div",K,[t(m,{lang:"json",modelValue:l.request.data,"onUpdate:modelValue":e[6]||(e[6]=n=>l.request.data=n)},null,8,["modelValue"])])):(x(),g("div",Q,[t(R,{modelValue:l.file,"onUpdate:modelValue":e[7]||(e[7]=n=>l.file=n)},null,8,["modelValue"])]))]),_:1}),t(f,null,{label:s(()=>[...e[34]||(e[34]=[o("img",{src:D,width:"20",alt:"",style:{margin:"0 5px"}},null,-1),o("span",null,"前置脚本",-1)])]),default:s(()=>[o("div",W,[o("div",X,[t(m,{modelValue:l.setup_script,"onUpdate:modelValue":e[8]||(e[8]=n=>l.setup_script=n),lang:"python",height:"300px"},null,8,["modelValue"])]),o("div",Y,[t(y,{"content-position":"center"},{default:s(()=>[...e[35]||(e[35]=[i("前置脚本模板",-1)])]),_:1}),o("div",Z,[t(d,{onClick:e[9]||(e[9]=n=>v("func")),plain:"",size:"small",type:"primary"},{default:s(()=>[...e[36]||(e[36]=[i("全局工具函数",-1)])]),_:1})]),o("div",h,[t(d,{onClick:e[10]||(e[10]=n=>v("global")),plain:"",size:"small",type:"primary"},{default:s(()=>[...e[37]||(e[37]=[i("设置全局变量",-1)])]),_:1})]),o("div",ee,[t(d,{onClick:e[11]||(e[11]=n=>v("env")),plain:"",size:"small",type:"primary"},{default:s(()=>[...e[38]||(e[38]=[i("设置临时变量",-1)])]),_:1})]),o("div",te,[t(d,{onClick:e[12]||(e[12]=n=>v("sql")),plain:"",size:"small",type:"primary"},{default:s(()=>[...e[39]||(e[39]=[i("执行sql查询",-1)])]),_:1})])])])]),_:1}),t(f,null,{label:s(()=>[...e[40]||(e[40]=[o("img",{src:B,width:"20",alt:"",style:{margin:"0 5px"}},null,-1),o("span",null,"断言脚本",-1)])]),default:s(()=>[o("div",le,[o("div",se,[t(m,{modelValue:l.teardown_script,"onUpdate:modelValue":e[13]||(e[13]=n=>l.teardown_script=n),lang:"python",height:"400px"},null,8,["modelValue"])]),o("div",ne,[t(z,{height:"400px"},{default:s(()=>[t(y,{"content-position":"center"},{default:s(()=>[...e[41]||(e[41]=[i("断言脚本模板",-1)])]),_:1}),o("div",oe,[t(d,{onClick:e[14]||(e[14]=n=>r("func")),plain:"",size:"small",type:"primary"},{default:s(()=>[...e[42]||(e[42]=[i(" 全局工具函数 ",-1)])]),_:1})]),o("div",ae,[t(d,{onClick:e[15]||(e[15]=n=>r("getBody")),plain:"",size:"small",type:"primary"},{default:s(()=>[...e[43]||(e[43]=[i(" 获取响应体 ",-1)])]),_:1})]),o("div",ie,[t(d,{onClick:e[16]||(e[16]=n=>r("global")),plain:"",size:"small",type:"primary"},{default:s(()=>[...e[44]||(e[44]=[i(" 设置全局变量 ",-1)])]),_:1})]),o("div",de,[t(d,{onClick:e[17]||(e[17]=n=>r("env")),plain:"",size:"small",type:"primary"},{default:s(()=>[...e[45]||(e[45]=[i(" 设置临时变量 ",-1)])]),_:1})]),o("div",re,[t(d,{onClick:e[18]||(e[18]=n=>r("sql")),plain:"",size:"small",type:"primary"},{default:s(()=>[...e[46]||(e[46]=[i(" 执行sql查询 ",-1)])]),_:1})]),o("div",pe,[t(d,{onClick:e[19]||(e[19]=n=>r("JSextract")),plain:"",size:"small",type:"primary"},{default:s(()=>[...e[47]||(e[47]=[i(" jsonpath提取数据 ",-1)])]),_:1})]),o("div",ue,[t(d,{onClick:e[20]||(e[20]=n=>r("REextract")),plain:"",size:"small",type:"primary"},{default:s(()=>[...e[48]||(e[48]=[i(" 正则表达式提取数据 ",-1)])]),_:1})]),o("div",me,[t(d,{onClick:e[21]||(e[21]=n=>r("http")),plain:"",size:"small",type:"primary"},{default:s(()=>[...e[49]||(e[49]=[i(" http状态码 ",-1)])]),_:1})]),o("div",_e,[t(d,{onClick:e[22]||(e[22]=n=>r("eq")),plain:"",size:"small",type:"primary"},{default:s(()=>[...e[50]||(e[50]=[i(" 相等 ",-1)])]),_:1})]),o("div",fe,[t(d,{onClick:e[23]||(e[23]=n=>r("uneq")),plain:"",size:"small",type:"primary"},{default:s(()=>[...e[51]||(e[51]=[i(" 不相等 ",-1)])]),_:1})]),o("div",ve,[t(d,{onClick:e[24]||(e[24]=n=>r("contain")),plain:"",size:"small",type:"primary"},{default:s(()=>[...e[52]||(e[52]=[i(" 包含 ",-1)])]),_:1})]),o("div",ye,[t(d,{onClick:e[25]||(e[25]=n=>r("uncontain")),plain:"",size:"small",type:"primary"},{default:s(()=>[...e[53]||(e[53]=[i(" 不包含 ",-1)])]),_:1})])]),_:1})])])]),_:1})]),_:1}),t(y,{"content-position":"center"},{default:s(()=>[...e[54]||(e[54]=[o("b",null,"响应信息",-1)])]),_:1}),t(N,{result:b(q),hideBtn:!0},null,8,["result"])])])}}},ze=L(ge,[["__scopeId","data-v-7824719a"]]);export{ze as default};
