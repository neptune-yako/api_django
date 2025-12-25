# 测试报告批量同步功能实施计划

## 📋 项目概述

**功能名称**：测试报告批量异步同步  
**模块**：`test_report`  
**版本**：v1.0  
**创建日期**：2024-12-24

---

## 🎯 需求定义

### 业务需求

实现 Jenkins Job 的 Allure 测试报告批量同步功能，支持：
1. **同步单个构建（指定范围）**：同步某个 Job 的 Build #X 到 Build #Y
2. **同步单个 Job 的全部构建**：同步某个 Job 的所有历史构建

### 技术需求

- 使用 **Celery 异步任务**，避免请求超时
- 支持**实时进度查询**，前端可轮询任务状态
- **容错处理**：单个构建失败不中断整体任务
- **数据去重**：避免重复导入相同构建

---

## 🏗️ 技术方案

### 架构设计

```
┌─────────────┐      POST      ┌──────────────┐
│   前端 UI   │ ─────────────> │  Django View │
│             │                 │              │
│  进度显示   │ <─────────────  │ 返回 task_id │
└─────────────┘   立即返回      └──────────────┘
       │                               │
       │ 轮询状态                      │ task.delay()
       │ (每 2 秒)                    ▼
       │                        ┌─────────────┐
       └─────────────────────>  │ Celery Task │
                                │             │
         GET /task-status/xxx   │ 批量执行    │
                                │ 更新进度    │
                                └─────────────┘
                                       │
                                       ▼
                                 数据库入库
```

### 数据展示方案

**选择**：方案 A - 不新增汇总表

**理由**：
- 数据量可控，查询性能足够
- 降低系统复杂度
- 保持数据一致性
- 可通过索引、缓存优化性能

---

## 📐 API 设计

### API 1: 启动批量同步任务

**端点**：`POST /api/test-report/sync-job/`

**请求参数**：
```json
{
  "job_name": "a-test-Pipeline",
  "start_build": 1,        // 可选，默认 1
  "end_build": 100         // 可选，默认为最新构建号
}
```

**响应示例**（立即返回）：
```json
{
  "code": 200,
  "message": "批量同步任务已启动",
  "data": {
    "task_id": "550e8400-e29b-41d4-a716-446655440000",
    "job_name": "a-test-Pipeline",
    "total_builds": 100,
    "status": "PENDING"
  }
}
```

---

### API 2: 查询任务状态

**端点**：`GET /api/test-report/task-status/{task_id}/`

**响应示例（进行中）**：
```json
{
  "code": 200,
  "data": {
    "task_id": "550e8400-...",
    "status": "PROGRESS",
    "current": 45,
    "total": 100,
    "success_count": 42,
    "failed_count": 3,
    "failed_builds": [5, 12, 38]
  }
}
```

**响应示例（已完成）**：
```json
{
  "code": 200,
  "data": {
    "task_id": "550e8400-...",
    "status": "SUCCESS",
    "current": 100,
    "total": 100,
    "success_count": 95,
    "failed_count": 5,
    "failed_builds": [5, 12, 38, 67, 89],
    "execution_ids": [101, 102, 103, ...]
  }
}
```

---

### API 3: 查询测试执行列表

**端点**：`GET /api/test-report/executions/`

**请求参数**：
```json
{
  "job_id": 123,           // 可选
  "page": 1,
  "size": 20,
  "start_date": "2024-01-01",  // 可选
  "end_date": "2024-12-31"
}
```

**响应示例**：
```json
{
  "code": 200,
  "data": {
    "total": 150,
    "items": [
      {
        "id": 1,
        "timestamp": "123_5",
        "report_title": "a-test-Pipeline #5",
        "job_name": "a-test-Pipeline",
        "total_cases": 100,
        "passed_cases": 95,
        "pass_rate": 95.00,
        "execution_time": "2h 30m 15s",
        "status": "success",
        "created_at": "2024-12-24T10:00:00Z"
      }
    ]
  }
}
```

---

### API 4: 查询测试执行详情

**端点**：`GET /api/test-report/executions/{id}/`

**响应示例**：
```json
{
  "code": 200,
  "data": {
    "execution": { /* TestExecution 数据 */ },
    "suites": [ /* TestSuite 列表 */ ],
    "categories": [ /* Category 列表 */ ],
    "scenarios": [ /* FeatureScenario 列表 */ ]
  }
}
```

---

## 🛠️ 实施步骤

### 阶段 1: 后端核心功能

#### 步骤 1.1: 创建 Celery Task

**文件**：`backend/test_report/tasks.py`（新建）

**核心逻辑**：
```python
@shared_task(bind=True)
def sync_job_builds_task(self, job_id, start_build, end_build):
    """
    批量同步 Job 构建报告
    
    Args:
        self: Celery task 实例
        job_id: Jenkins Job ID
        start_build: 起始构建号
        end_build: 结束构建号
    """
    # 1. 获取 Job 对象
    # 2. 循环遍历构建号范围
    # 3. 调用 TestReportService.save_report_from_jenkins()
    # 4. 使用 self.update_state() 更新进度
    # 5. 返回成功/失败统计
```

**关键点**：
- 使用 `bind=True` 支持 `self.update_state()`
- 单个构建失败不中断整体任务
- 记录失败的构建号和错误信息

---

#### 步骤 1.2: 创建 API 视图

**文件**：`backend/test_report/views.py`（修改）

**新增内容**：

1. **SyncJobBuildsView** - 启动批量同步
```python
class SyncJobBuildsView(APIView):
    def post(self, request):
        # 1. 参数校验
        # 2. 查询 JenkinsJob
        # 3. 如果 end_build 为空，获取最新构建号
        # 4. 启动 Celery 任务
        # 5. 返回 task_id
```

2. **TaskStatusView** - 查询任务状态
```python
class TaskStatusView(APIView):
    def get(self, request, task_id):
        # 1. 使用 AsyncResult 查询任务
        # 2. 返回状态和进度信息
```

3. **TestExecutionListView** - 查询执行列表
```python
class TestExecutionListView(APIView):
    def get(self, request):
        # 1. 支持分页、筛选
        # 2. 返回 TestExecution 列表
```

4. **TestExecutionDetailView** - 查询执行详情
```python
class TestExecutionDetailView(APIView):
    def get(self, request, execution_id):
        # 1. 查询 TestExecution
        # 2. 预加载关联数据（suites/categories/scenarios）
        # 3. 返回完整数据
```

---

#### 步骤 1.3: 注册路由

**文件**：`backend/test_report/urls.py`（修改）

**新增路由**：
```python
urlpatterns = [
    path('sync/', SyncAllureReportView.as_view()),                    # 已有
    path('sync-job/', SyncJobBuildsView.as_view()),                   # 新增
    path('task-status/<str:task_id>/', TaskStatusView.as_view()),    # 新增
    path('executions/', TestExecutionListView.as_view()),             # 新增
    path('executions/<int:execution_id>/', TestExecutionDetailView.as_view()),  # 新增
]
```

---

#### 步骤 1.4: 辅助功能（可选）

**文件**：`backend/jenkins_integration/jenkins_client.py`（修改）

**新增方法**（如果不存在）：
```python
def get_job_info(job_name, server):
    """获取 Job 信息，包括最新构建号"""
    # 调用 Jenkins API: /job/{job_name}/api/json
    # 返回 lastBuild.number
```

---

### 阶段 2: 数据库优化

#### 步骤 2.1: 添加索引

**文件**：`backend/test_report/models.py`（修改）

**优化点**：
```python
class TestExecution(models.Model):
    # ...
    class Meta:
        db_table = 'test_execution'
        indexes = [
            models.Index(fields=['job', 'created_at']),  # 查询优化
            models.Index(fields=['timestamp']),          # 唯一性查询
        ]
```

---

### 阶段 3: 前端实施（可选）

#### 步骤 3.1: 创建 API 定义

**文件**：`frontend/src/api/testReport.js`（新建）

```javascript
export function syncJobBuilds(data) {
  return http({ url: '/api/test-report/sync-job/', method: 'post', data })
}

export function getTaskStatus(taskId) {
  return http({ url: `/api/test-report/task-status/${taskId}/`, method: 'get' })
}

export function getExecutionList(params) {
  return http({ url: '/api/test-report/executions/', method: 'get', params })
}

export function getExecutionDetail(id) {
  return http({ url: `/api/test-report/executions/${id}/`, method: 'get' })
}
```

---

#### 步骤 3.2: 创建 UI 组件（可选）

**文件**：`frontend/src/views/test-report/ExecutionList.vue`（新建）

**功能**：
- 显示测试执行记录列表
- 支持按 Job、时间筛选
- 点击查看详情

**文件**：`frontend/src/views/test-report/ExecutionDetail.vue`（新建）

**功能**：
- 显示单次执行的完整数据
- Tab 页展示：概览、测试套件、缺陷类别、特性场景

---

## 📁 文件变更清单

### 后端（必须）
| 文件 | 操作 | 优先级 |
|------|------|--------|
| `backend/test_report/tasks.py` | 新建 | P0 |
| `backend/test_report/views.py` | 修改（新增 4 个 View） | P0 |
| `backend/test_report/urls.py` | 修改（新增 4 个路由） | P0 |
| `backend/test_report/models.py` | 修改（添加索引） | P1 |
| `backend/jenkins_integration/jenkins_client.py` | 修改（新增 get_job_info） | P1 |

### 前端（可选）
| 文件 | 操作 | 优先级 |
|------|------|--------|
| `frontend/src/api/testReport.js` | 新建 | P1 |
| `frontend/src/views/test-report/ExecutionList.vue` | 新建 | P2 |
| `frontend/src/views/test-report/ExecutionDetail.vue` | 新建 | P2 |

---

## ⚠️ 注意事项

### 1. 防御性编程

- 单个构建失败不中断整体任务
- 记录详细的错误信息
- 避免重复导入（检查 `timestamp` 唯一性）

### 2. 性能优化

- 使用 `bulk_create` 批量插入
- 添加数据库索引
- 使用 `prefetch_related` 优化查询
- 考虑添加 Redis 缓存（如需要）

### 3. 错误处理

```python
for build_num in range(start_build, end_build + 1):
    try:
        execution = TestReportService.save_report_from_jenkins(job, build_num)
        results['success'].append(build_num)
    except Exception as e:
        logger.error(f"同步 Build #{build_num} 失败: {str(e)}")
        results['failed'].append({
            'build': build_num,
            'error': str(e)
        })
```

### 4. 进度更新

```python
self.update_state(
    state='PROGRESS',
    meta={
        'current': i + 1,
        'total': total,
        'success_count': len(results['success']),
        'failed_count': len(results['failed'])
    }
)
```

---

## 🧪 测试计划

### 单元测试
- Celery 任务执行逻辑
- API 参数校验
- 错误处理机制

### 集成测试
1. 同步单个构建（start=1, end=1）
2. 同步小范围（start=1, end=10）
3. 同步大范围（start=1, end=100）
4. 测试 `end_build=None` 的情况
5. 测试某个构建失败的容错性
6. 测试重复同步的去重机制

### 性能测试
- 同步 100 个构建的耗时
- 查询列表的响应时间
- 查询详情的响应时间

---

## 📊 开发排期

| 阶段 | 任务 | 预计工时 |
|------|------|---------|
| 阶段 1 | 后端 Celery Task | 4h |
| 阶段 1 | 后端 API View | 4h |
| 阶段 1 | 路由注册 | 0.5h |
| 阶段 2 | 数据库优化 | 1h |
| 阶段 3 | 前端 API 定义 | 1h |
| 阶段 3 | 前端 UI 组件 | 6h |
| 测试 | 单元测试 + 集成测试 | 4h |
| **总计** | | **20.5h** |

---

## 📚 参考文档

- [Celery 官方文档](https://docs.celeryproject.org/)
- [Django Celery 集成指南](https://docs.celeryproject.org/en/stable/django/)
- 项目已有参考：`backend/jenkins_integration/tasks.py`
- 项目已有参考：`backend/jenkins_integration/views/task_views.py`

---

**文档版本**：v1.0  
**最后更新**：2024-12-24  
**状态**：待实施
