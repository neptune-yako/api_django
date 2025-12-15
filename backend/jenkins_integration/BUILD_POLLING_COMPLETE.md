# 构建状态查询和 Allure 报告接口实现完成

## ✅ 已实现的两个新接口

### 1. 查询最新构建状态（轮询用）

**接口**: `GET /api/jenkins/build/latest/`

**参数**:
- `job_name`: Job 名称（必需）

**返回示例**:
```json
{
    "code": 200,
    "message": "最新构建 #45 - 构建成功",
    "data": {
        "build_number": 45,
        "result": "SUCCESS",
        "building": false,
        "duration": 120000,
        "duration_text": "120.00秒",
        "status_text": "构建成功",
        "url": "http://jenkins/job/xxx/45/",
        "timestamp": 1702615200000
    }
}
```

**状态说明**:
- `building`: `true` 表示正在构建，`false` 表示已完成
- `result`: `SUCCESS`, `FAILURE`, `ABORTED`, `UNSTABLE`, `null`(构建中)
- `status_text`: 中文状态描述

---

### 2. 获取 Allure 报告 URL

**接口**: `GET /api/jenkins/build/allure/`

**参数**:
- `job_name`: Job 名称（必需）
- `build_number`: 构建编号（必需）

**返回示例（有报告）**:
```json
{
    "code": 200,
    "message": "找到 Allure 报告",
    "data": {
        "has_allure": true,
        "allure_url": "http://jenkins/job/test-job/123/allure/",
        "job_name": "test-job",
        "build_number": 123
    }
}
```

**返回示例（无报告）**:
```json
{
    "code": 200,
    "message": "该构建没有 Allure 报告",
    "data": {
        "has_allure": false,
        "allure_url": null,
        "job_name": "test-job",
        "build_number": 123
    }
}
```

---

## 📝 修改的文件

### 1. `views.py`
- ✅ 新增 `JenkinsBuildLatestView` 类
- ✅ 新增 `JenkinsBuildAllureView` 类

### 2. `jenkins_client.py`
- ✅ 新增 `get_allure_report_url()` 函数

### 3. `urls.py`
- ✅ 新增 `/api/jenkins/build/latest/` 路由
- ✅ 新增 `/api/jenkins/build/allure/` 路由

---

## 🔄 前端轮询示例

```javascript
// 1. 触发构建
const response = await fetch('/api/jenkins/job/build/', {
    method: 'POST',
    body: JSON.stringify({job_name: 'a-test-Pipeline'})
});

// 2. 开始轮询
const pollInterval = setInterval(async () => {
    const res = await fetch(`/api/jenkins/build/latest/?job_name=a-test-Pipeline`);
    const {data} = await res.json();
    
    if (!data.building) {
        // 构建完成
        clearInterval(pollInterval);
        
        if (data.result === 'SUCCESS') {
            // 获取 Allure 报告
            const allureRes = await fetch(
                `/api/jenkins/build/allure/?job_name=a-test-Pipeline&build_number=${data.build_number}`
            );
            const {data: allureData} = await allureRes.json();
            
            if (allureData.has_allure) {
                window.open(allureData.allure_url, '_blank');
            }
        }
    }
}, 3000); // 每3秒轮询一次
```

---

## ✅ 功能测试

### 测试1: 查询最新构建状态
```bash
curl "http://localhost:8000/api/jenkins/build/latest/?job_name=a-test-Pipeline"
```

### 测试2: 获取 Allure 报告
```bash
curl "http://localhost:8000/api/jenkins/build/allure/?job_name=a-test-Pipeline&build_number=45"
```

---

## 🧪 **Apifox 完整测试案例**

### 场景：完整的构建监控流程

基于实际数据演示如何使用这两个接口。

#### 📝 **前置条件**
- Job 名称: `a-test-Pipeline`
- 已触发构建，获得 `queue_id: 57`

---

### 步骤 1️⃣: 触发构建

**请求**:
```http
POST http://localhost:8000/api/jenkins/job/build/
Content-Type: application/json

{
    "job_name": "a-test-Pipeline"
}
```

**响应**:
```json
{
    "code": 200,
    "message": "构建已触发",
    "data": {
        "queue_id": 57
    }
}
```

✅ **记录**: `queue_id = 57`，`job_name = "a-test-Pipeline"`

---

### 步骤 2️⃣: 查询最新构建状态（构建中）

**等待 3-5 秒后**

**请求**:
```http
GET http://localhost:8000/api/jenkins/build/latest/?job_name=a-test-Pipeline
```

**预期响应（构建中）**:
```json
{
    "code": 200,
    "message": "最新构建 #8 - 正在构建中",
    "data": {
        "build_number": 8,
        "result": null,
        "building": true,
        "duration": 0,
        "duration_text": null,
        "status_text": "正在构建中",
        "url": "http://mg.morry.online/job/a-test-Pipeline/8/",
        "timestamp": 1734248123000
    }
}
```

📊 **关键字段**:
- `building: true` - 正在构建中
- `result: null` - 还没有结果
- `build_number: 8` - 记录这个编号，后续查询 Allure 用

---

### 步骤 3️⃣: 继续轮询（每3秒一次）

**10秒后再次请求**:
```http
GET http://localhost:8000/api/jenkins/build/latest/?job_name=a-test-Pipeline
```

**预期响应（仍在构建）**:
```json
{
    "code": 200,
    "message": "最新构建 #8 - 正在构建中",
    "data": {
        "build_number": 8,
        "result": null,
        "building": true,
        "duration": 10234,
        "duration_text": "10.23秒",
        "status_text": "正在构建中",
        "url": "http://mg.morry.online/job/a-test-Pipeline/8/",
        "timestamp": 1734248123000
    }
}
```

📊 **注意**: `duration` 在增加，说明构建正在进行中

---

### 步骤 4️⃣: 构建完成

**30秒后再次请求**:
```http
GET http://localhost:8000/api/jenkins/build/latest/?job_name=a-test-Pipeline
```

**预期响应（构建成功）**:
```json
{
    "code": 200,
    "message": "最新构建 #8 - 构建成功",
    "data": {
        "build_number": 8,
        "result": "SUCCESS",
        "building": false,
        "duration": 31234,
        "duration_text": "31.23秒",
        "status_text": "构建成功",
        "url": "http://mg.morry.online/job/a-test-Pipeline/8/",
        "timestamp": 1734248123000
    }
}
```

✅ **关键变化**:
- `building: false` - 构建已完成
- `result: "SUCCESS"` - 构建成功
- `duration: 31234` - 最终耗时31秒

---

### 步骤 5️⃣: 获取 Allure 报告

**使用 build_number = 8**

**请求**:
```http
GET http://localhost:8000/api/jenkins/build/allure/?job_name=a-test-Pipeline&build_number=8
```

**预期响应（有 Allure）**:
```json
{
    "code": 200,
    "message": "找到 Allure 报告",
    "data": {
        "has_allure": true,
        "allure_url": "http://mg.morry.online/job/a-test-Pipeline/8/allure/",
        "job_name": "a-test-Pipeline",
        "build_number": 8
    }
}
```

🎉 **成功**: 点击 `allure_url` 查看报告

---

## 📋 **Apifox 测试检查清单**

### ✅ 接口 1: `/build/latest/`

- [ ] Job 存在且有构建：返回最新构建信息
- [ ] Job 存在但无构建：返回 `data: null`
- [ ] Job 不存在：返回 `code: 5002`
- [ ] 缺少 job_name：返回 `code: 400`
- [ ] 构建中的状态：`building: true`
- [ ] 构建完成的状态：`building: false`

### ✅ 接口 2: `/build/allure/`

- [ ] 有 Allure 的构建：返回 `has_allure: true` 和 URL
- [ ] 无 Allure 的构建：返回 `has_allure: false`
- [ ] 缺少参数：返回 `code: 400`
- [ ] build_number 非数字：返回参数错误

---

## 🎯 **快速测试命令（cURL）**

```bash
# 1. 触发构建
curl -X POST http://localhost:8000/api/jenkins/job/build/ \
  -H "Content-Type: application/json" \
  -d '{"job_name": "a-test-Pipeline"}'

# 2. 查询状态
curl "http://localhost:8000/api/jenkins/build/latest/?job_name=a-test-Pipeline"

# 3. 获取 Allure（替换 build_number）
curl "http://localhost:8000/api/jenkins/build/allure/?job_name=a-test-Pipeline&build_number=8"
```

---

**所有接口已实现完成！可以开始前端集成了！** 🎉
