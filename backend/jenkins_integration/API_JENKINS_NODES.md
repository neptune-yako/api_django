# Jenkins 节点管理 API 接口说明

本文档说明了新增的 Jenkins 节点管理接口,这些接口参考了 `backend/docs/Jenkins_node_list` 目录中的示例代码实现。

## 📋 接口清单

### 1. 创建节点
- **路径**: `POST /api/jenkins/nodes/create/`
- **功能**: 创建新的 SSH 连接类型的 Jenkins 节点
- **参考**: `add_jenkins_node.py` 和 `jenkins_node_crud.py` 的 `create_ssh_node` 方法

**请求参数**:
```json
{
  "name": "build-node-01",              // 必需: 节点名称
  "host": "192.168.1.100",             // 必需: 主机 IP 或域名
  "credential_id": "ssh-key-id",       // 可选: SSH 凭证 ID
  "port": 22,                          // 可选: SSH 端口 (默认 22)
  "remote_fs": "/home/jenkins",        // 可选: 远程工作目录
  "labels": "linux docker",            // 可选: 节点标签 (空格分隔)
  "num_executors": 2,                  // 可选: 执行器数量 (默认 2)
  "description": "Build server"        // 可选: 节点描述
}
```

**响应示例**:
```json
{
  "code": 200,
  "message": "成功创建节点 [build-node-01]",
  "data": {
    "node_name": "build-node-01",
    "host": "192.168.1.100",
    "port": 22,
    "labels": "linux docker",
    "num_executors": 2,
    "remote_fs": "/home/jenkins",
    "credential_id": "ssh-key-id"
  }
}
```

---

### 2. 删除节点
- **路径**: `DELETE /api/jenkins/nodes/{node_name}/delete/`
- **功能**: 删除指定的 Jenkins 节点
- **参考**: `jenkins_node_crud.py` 的 `delete_node` 方法

**响应示例**:
```json
{
  "code": 200,
  "message": "成功删除节点 [build-node-01]",
  "data": {
    "node_name": "build-node-01",
    "deleted": true
  }
}
```

---

### 3. 获取节点详细信息
- **路径**: `GET /api/jenkins/nodes/{node_name}/info/`
- **功能**: 获取节点的详细状态和配置信息
- **参考**: `jenkins_node_crud.py` 的 `get_node_info` 方法

**响应示例**:
```json
{
  "code": 200,
  "message": "成功获取节点 [build-node-01] 信息",
  "data": {
    "name": "build-node-01",
    "displayName": "build-node-01",
    "description": "Build server",
    "numExecutors": 2,
    "labels": "linux,docker",
    "offline": false,
    "temporarilyOffline": false,
    "idle": true,
    "offlineCauseReason": "",
    "monitorData": {}
  }
}
```

---

### 4. 启用/禁用节点
- **路径**: `POST /api/jenkins/nodes/{node_name}/toggle/`
- **功能**: 启用或禁用指定节点
- **参考**: `jenkins_node_crud.py` 的 `enable_node` 和 `disable_node` 方法

**请求参数**:
```json
{
  "action": "disable",                    // 必需: enable 或 disable
  "message": "Maintenance in progress"    // 可选: 禁用原因 (仅 disable 时)
}
```

**响应示例**:
```json
{
  "code": 200,
  "message": "成功禁用节点 [build-node-01]",
  "data": {
    "node_name": "build-node-01",
    "disabled": true,
    "message": "Maintenance in progress"
  }
}
```

---

### 5. 重新连接节点
- **路径**: `POST /api/jenkins/nodes/{node_name}/reconnect/`
- **功能**: 重新连接离线的节点
- **参考**: `jenkins_node_crud.py` 的 `reconnect_node` 方法

**响应示例**:
```json
{
  "code": 200,
  "message": "节点 [build-node-01] 重新连接成功",
  "data": {
    "node_name": "build-node-01",
    "is_online": true,
    "reconnected": true
  }
}
```

---

### 6. 更新节点标签
- **路径**: `PATCH /api/jenkins/nodes/{node_name}/labels/`
- **功能**: 更新节点的标签
- **参考**: `jenkins_node_crud.py` 的 `update_node_labels` 方法

**请求参数**:
```json
{
  "labels": "linux docker java11"    // 必需: 新的标签 (空格分隔)
}
```

**响应示例**:
```json
{
  "code": 200,
  "message": "成功更新节点 [build-node-01] 标签",
  "data": {
    "node_name": "build-node-01",
    "old_labels": "linux docker",
    "new_labels": "linux docker java11",
    "updated": true
  }
}
```

---

### 7. 更新节点 IP (已有接口)
- **路径**: `PATCH /api/jenkins/nodes/{node_name}/ip/`
- **功能**: 更新节点的 IP 地址
- **参考**: 已有实现

**请求参数**:
```json
{
  "new_ip": "192.168.1.200",    // 必需: 新的 IP 地址
  "ssh_port": 22                // 可选: SSH 端口
}
```

---

### 8. 查询节点列表 (已有接口)
- **路径**: `GET /api/jenkins/nodes/`
- **功能**: 查询数据库中的节点列表
- **查询参数**:
  - `server_id`: 筛选指定服务器的节点
  - `is_online`: 筛选在线/离线节点

---

### 9. 获取节点配置 (已有接口)
- **路径**: `GET /api/jenkins/nodes/{node_name}/config/`
- **功能**: 获取节点的 XML 配置和当前 IP

---

## 🔧 核心实现文件

### 1. `jenkins_client.py`
新增的后端逻辑函数:
- `create_ssh_node()` - 创建 SSH 节点
- `delete_node()` - 删除节点
- `enable_node()` - 启用节点
- `disable_node()` - 禁用节点
- `reconnect_node()` - 重新连接节点
- `get_node_info()` - 获取节点详细信息
- `update_node_labels()` - 更新节点标签
- `node_exists()` - 检查节点是否存在

### 2. `node_views.py`
新增的 API 视图类:
- `JenkinsNodeCreateView` - 创建节点视图
- `JenkinsNodeDeleteView` - 删除节点视图
- `JenkinsNodeInfoView` - 获取节点详细信息视图
- `JenkinsNodeToggleView` - 启用/禁用节点视图
- `JenkinsNodeReconnectView` - 重新连接节点视图
- `JenkinsNodeLabelsView` - 更新节点标签视图

### 3. `urls.py`
新增的路由配置,将 URL 映射到对应的视图类。

---

## 📝 使用示例

### 示例 1: 创建一个新节点
```bash
curl -X POST http://localhost:8000/api/jenkins/nodes/create/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "test-node-01",
    "host": "192.168.1.100",
    "credential_id": "ssh-credentials",
    "labels": "linux docker",
    "num_executors": 4
  }'
```

### 示例 2: 禁用节点进行维护
```bash
curl -X POST http://localhost:8000/api/jenkins/nodes/test-node-01/toggle/ \
  -H "Content-Type: application/json" \
  -d '{
    "action": "disable",
    "message": "System maintenance"
  }'
```

### 示例 3: 重新连接离线节点
```bash
curl -X POST http://localhost:8000/api/jenkins/nodes/test-node-01/reconnect/
```

### 示例 4: 更新节点标签
```bash
curl -X PATCH http://localhost:8000/api/jenkins/nodes/test-node-01/labels/ \
  -H "Content-Type: application/json" \
  -d '{
    "labels": "linux docker java11 maven"
  }'
```

### 示例 5: 删除节点
```bash
curl -X DELETE http://localhost:8000/api/jenkins/nodes/test-node-01/delete/
```

---

## ⚠️ 注意事项

1. **创建节点前确保**:
   - 目标主机已安装 Java 运行环境
   - 已在 Jenkins 中配置相应的 SSH 凭证
   - 节点名称唯一

2. **删除节点**:
   - 删除操作不可逆
   - 建议先禁用节点,确认无影响后再删除
   - master 节点无法删除

3. **重新连接**:
   - 适用于网络暂时中断等情况
   - 需要等待几秒钟才能完成重连

4. **标签管理**:
   - 标签用于 Job 的节点选择策略
   - 多个标签用空格分隔
   - 更新操作会覆盖原有标签

---

## 📚 参考文档

- `backend/docs/Jenkins_node_list/add_jenkins_node.py` - 节点创建脚本示例
- `backend/docs/Jenkins_node_list/jenkins_node_crud.py` - 完整的 CRUD 管理模块
- `backend/docs/Jenkins_node_list/jenkins_node_cli.py` - CLI 工具示例
- `backend/docs/Jenkins_node_list/list_credentials.py` - 凭证查询工具

---

## 🎯 API 文档

所有接口都集成了 OpenAPI (Swagger) 文档,可通过以下地址访问:
- Swagger UI: `http://localhost:8000/api/schema/swagger-ui/`
- ReDoc: `http://localhost:8000/api/schema/redoc/`

接口都标记了 `Jenkins 节点管理` 标签,方便在 API 文档中查找。
