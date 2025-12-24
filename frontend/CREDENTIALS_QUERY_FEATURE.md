# SSH 凭证 ID 查询功能

## 📋 功能说明

在创建 Jenkins 节点时，SSH凭证ID字段现在可以通过下拉选择框查询和选择Jenkins中已配置的凭证，无需手动输入。

## ✨ 功能特点

### 1. **智能下拉选择**
- 🔍 可查询Jenkins中的所有凭证
- 🎯 支持搜索过滤
- ✍️ 支持手动输入自定义凭证ID
- 🏷️ 显示凭证类型标签（SSH、Username/Password等）
- 📝 显示凭证描述信息

### 2. **UI 设计**
```
SSH凭证ID:  [下拉选择框 ▼]
            ┌──────────────────────────────┐
            │ [刷新凭证列表] 按钮           │
            ├──────────────────────────────┤
            │ ✓ aliyun-ssh-key             │
            │   SSH Username with private key
            │   Aliyun server SSH key      │
            ├──────────────────────────────┤
            │ ✓ build-server-key           │
            │   SSH Username with private key
            │   Build server access        │
            └──────────────────────────────┘
```

### 3. **凭证信息展示**

每个凭证选项包含：
- **凭证ID** - 主要标识
- **类型标签** - 彩色标签显示凭证类型
  - 🟢 绿色 - SSH类型凭证
  - ⚪ 灰色 - 其他类型凭证
- **描述** - 凭证的用途说明

## 🔧 技术实现

### 后端 API

#### 1. 新增接口
**GET** `/api/jenkins/credentials/`

**响应示例**:
```json
{
  "code": 200,
  "message": "成功获取 5 个凭证",
  "data": [
    {
      "id": "aliyun-ssh-key",
      "description": "Aliyun server SSH key",
      "displayName": "",
      "typeName": "SSH Username with private key",
      "className": "com.cloudbees.jenkins.plugins.sshcredentials.impl.BasicSSHUserPrivateKey",
      "scope": "GLOBAL"
    },
    {
      "id": "build-server",
      "description": "Build server credentials",
      "displayName": "",
      "typeName": "Username with password",
      "className": "com.cloudbees.plugins.credentials.impl.UsernamePasswordCredentialsImpl",
      "scope": "GLOBAL"
    }
  ]
}
```

#### 2. 实现文件

**`backend/jenkins_integration/jenkins_client.py`**:
- `get_credentials_list()` - 获取凭证列表
- 参考 `list_credentials.py` 实现
- 支持多个API端点自动failover
- 自动识别凭证类型

**`backend/jenkins_integration/views/node_views.py`**:
- `JenkinsCredentialsListView` - API视图
- OpenAPI文档完整

**`backend/jenkins_integration/urls.py`**:
- 新增路由配置

### 前端实现

#### 1.API调用
**`frontend/src/api/jenkins.js`**:
```javascript
export function getCredentialsList() {
  return http({ url: '/api/jenkins/credentials/', method: 'get' })
}
```

#### 2. UI组件
**`frontend/src/views/environment/Environment.vue`**:

**下拉选择框**:
```vue
<el-select 
  v-model="createNodeForm.credential_id" 
  placeholder="请选择或输入SSH凭证ID" 
  filterable 
  allow-create
  clearable
  :loading="isLoadingCredentials"
>
  <template #header>
    <el-button @click="loadCredentials" :loading="isLoadingCredentials">
      刷新凭证列表
    </el-button>
  </template>
  <el-option v-for="cred in credentialsList" ...>
    <!-- 凭证选项显示 -->
  </el-option>
</el-select>
```

**状态管理**:
```javascript
const credentialsList = ref([])           // 凭证列表
const isLoadingCredentials = ref(false)   // 加载状态

async function loadCredentials() {
  // 调用API获取凭证列表
}
```

## 🚀 使用流程

### 步骤 1: 打开创建对话框
```
1. 点击 [新增] 按钮
2. 切换到 "Jenkins节点" 选项卡
3. 填写节点名称和主机IP
4. 展开 "高级选项"
```

### 步骤 2: 选择SSH凭证
```
方式A - 从列表选择:
  1. 点击 SSH凭证ID 下拉框
  2. 点击 "刷新凭证列表" 按钮
  3. 等待加载 (1-2秒)
  4. 从列表中选择凭证

方式B - 手动输入:
  1. 点击 SSH凭证ID 下拉框
  2. 直接输入凭证ID
  3. 回车确认

方式C - 搜索过滤:
  1. 点击 SSH凭证ID 下拉框
  2. 输入关键词搜索
  3. 选择匹配的凭证
```

### 步骤 3: 完成创建
```
5. (可选) 配置其他参数
6. 点击 [创建节点]
```

## 📊 示例场景

### 场景 1: SSH凭证选择

```
用户操作:
1. 创建节点: build-node-01
2. 主机IP: 192.168.1.100
3. 点击"刷新凭证列表"
4. 选择: aliyun-ssh-key
5. 创建完成

凭证列表显示:
┌────────────────────────────────────┐
│ [刷新凭证列表]                      │
├────────────────────────────────────┤
│ ✓ aliyun-ssh-key         [SSH Key] │
│   Aliyun server SSH key            │
│ ✓ tencent-cloud-key      [SSH Key] │
│   Tencent Cloud server access      │
│ ✓ github-token           [Secret]  │
│   GitHub Personal Access Token     │
└────────────────────────────────────┘
```

### 场景 2: 手动输入新凭证

```
用户操作:
1. 在下拉框中输入: new-custom-credential
2. 回车确认（会创建新条目）
3. 继续创建节点

说明:
- allow-create 选项允许输入不在列表中的凭证ID
- 适用于临时凭证或尚未加载的凭证
```

### 场景 3: 搜索现有凭证

```
用户操作:
1. 点击下拉框
2. 输入搜索词: "aliyun"
3. 列表自动过滤
4. 选择匹配的凭证
```

## ⚙️ 技术特性

### 1. **多端点容错**
后端尝试多个Jenkins API端点:
```python
endpoints = [
    "/credentials/store/system/domain/_/api/json?depth=2",
    "/credentials/store/system/domain/_/api/json",
    "/credentials/api/json",
]
```

### 2. **类型自动识别**
根据className推断凭证类型:
```python
if 'SSH' in class_name:
    typeName = 'SSH Username with private key'
elif 'UsernamePassword' in class_name:
    typeName = 'Username with password'
elif 'Secret' in class_name:
    typeName = 'Secret text'
```

### 3. **智能选择框**
- `filterable` - 支持搜索
- `allow-create` - 允许自定义输入
- `clearable` - 可清空选择

## ⚠️ 注意事项

1. **权限要求**
   - Jenkins用户需要有 Credentials → View 权限
   - 如果无权限，列表将为空

2. **首次使用**
   - 需要手动点击"刷新凭证列表"按钮
   - 不会自动加载（避免不必要的API调用）

3. **凭证管理**
   - 凭证需要在 Jenkins → 凭据管理 中预先创建
   - 支持系统域(System Domain)中的凭证

4. **推荐做法**
   - 创建节点前先在Jenkins中配置好SSH凭证
   - 为凭证添加清晰的描述便于识别

## 📚 相关文档

- 后端凭证查询: `backend/docs/Jenkins_node_list/list_credentials.py`
- API文档: `backend/jenkins_integration/API_JENKINS_NODES.md`
- Jenkins凭证管理: https://www.jenkins.io/doc/book/using/using-credentials/

---

## 总结

现在创建Jenkins节点时，可以方便地查询和选择已配置的SSH凭证，大大提升了用户体验！🎉
