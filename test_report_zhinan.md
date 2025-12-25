# 测试报告模块实施总结与异步任务指南

## 📋 项目背景

本文档总结了 `test_report` 模块的创建过程，以及未完成的**批量异步同步**功能的实施指导。

---

## ✅ 已完成的工作

### 1. test_report 模块基础架构

#### 1.1 数据库模型（基于甲方 SQL 设计）
- **TestExecution** - 测试执行总览表
- **TestSuite** - 测试套件表
- **Category** - 缺陷类别表
- **FeatureScenario** - 特性场景表

#### 1.2 核心工具类
```
backend/test_report/
├── models.py          # 数据模型
├── views.py           # API 视图（单次同步）
├── services.py        # 业务逻辑
├── urls.py            # 路由配置
└── utils/
    ├── allure_client.py   # Allure 报告解析客户端
    ├── codes.py           # 响应码定义（6xxx 系列）
    ├── exceptions.py      # 自定义异常类
    └── __init__.py        # 统一导出
```

#### 1.3 已实现的 API
- **POST /api/test-report/sync/** - 同步单次构建的 Allure 报告

**请求示例**:
```json
{
  "job_name": "a-test-Pipeline",
  "build_number": 5
}
```

**特点**:
- ✅ 同步执行（阻塞式）
- ✅ 适用于单次构建
- ❌ 不适合批量历史数据同步（会超时）

---

## 🚧 待实施功能：批量异步同步

### 需求描述

当用户需要同步某个 Job 的**全部历史构建**（如 1-100 次构建）时，使用同步 API 会导致：
- 请求超时（可能需要数分钟）
- 用户体验差（长时间等待无反馈）
- 服务器资源占用

**解决方案**: 使用 Celery 异步任务 + 前端轮询状态

---

## 📐 技术方案设计

### 方案架构图

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
         GET /task-status/xxx    │ 批量执行    │
                                 │ 更新进度    │
                                 └─────────────┘
                                        │
                                        ▼
                                  数据库入库
```

### API 设计

#### API 1: 启动批量同步任务

**端点**: `POST /api/test-report/sync-all/`

**请求参数**:
```json
{
  "job_name": "a-test-Pipeline",
  "start_build": 1,    // 可选，默认 1
  "end_build": 100     // 可选，默认最新
}
```

**响应示例**（立即返回，不等待完成）:
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

#### API 2: 查询任务状态

**端点**: `GET /api/test-report/task-status/{task_id}/`

**响应示例（进行中）**:
```json
{
  "code": 200,
  "data": {
    "task_id": "550e8400-...",
    "status": "PROGRESS",     // PENDING/PROGRESS/SUCCESS/FAILURE
    "current": 45,
    "total": 100,
    "success_count": 42,
    "failed_count": 3,
    "failed_builds": [5, 12, 38]
  }
}
```

**响应示例（已完成）**:
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

## 🛠️ 实施步骤

### 步骤 1: 创建 Celery Task

**文件**: `backend/test_report/tasks.py`

```python
from celery import shared_task
import logging
from .models import JenkinsJob
from .services import TestReportService

logger = logging.getLogger('django')

@shared_task(bind=True)
def sync_job_history_task(self, job_id, start_build, end_build):
    """
    批量同步 Job 历史构建报告
    
    Args:
        self: Celery task 实例（支持 update_state）
        job_id: Jenkins Job ID
        start_build: 起始构建号
        end_build: 结束构建号
    """
    try:
        job = JenkinsJob.objects.get(id=job_id)
        build_range = range(start_build, end_build + 1)
        total = len(build_range)
        
        results = {
            'success': [],
            'failed': [],
            'execution_ids': []
        }
        
        for i, build_num in enumerate(build_range):
            try:
                # 调用单次同步逻辑
                execution = TestReportService.save_report_from_jenkins(
                    job, build_num
                )
                
                if execution:
                    results['success'].append(build_num)
                    results['execution_ids'].append(execution.id)
                else:
                    results['failed'].append({
                        'build': build_num,
                        'error': '报告获取失败'
                    })
                    
            except Exception as e:
                logger.error(f"同步 Build #{build_num} 失败: {str(e)}")
                results['failed'].append({
                    'build': build_num,
                    'error': str(e)
                })
            
            # 更新进度（重要！）
            self.update_state(
                state='PROGRESS',
                meta={
                    'current': i + 1,
                    'total': total,
                    'success_count': len(results['success']),
                    'failed_count': len(results['failed']),
                    'failed_builds': [f['build'] for f in results['failed']]
                }
            )
        
        # 返回最终结果
        return {
            'status': 'SUCCESS',
            'total': total,
            'success_count': len(results['success']),
            'failed_count': len(results['failed']),
            'failed_builds': [f['build'] for f in results['failed']],
            'execution_ids': results['execution_ids']
        }
        
    except Exception as e:
        logger.error(f"批量同步任务异常: {str(e)}")
        return {
            'status': 'FAILURE',
            'error': str(e)
        }
```

### 步骤 2: 创建 View

**文件**: `backend/test_report/views.py`（追加）

```python
from rest_framework.views import APIView
from jenkins_integration.utils import R
from jenkins_integration.models import JenkinsJob
from .tasks import sync_job_history_task
import logging

logger = logging.getLogger('django')

class SyncAllBuildsView(APIView):
    """批量同步 Job 历史报告"""
    
    def post(self, request):
        job_name = request.data.get('job_name')
        start_build = request.data.get('start_build', 1)
        end_build = request.data.get('end_build')
        
        if not job_name:
            return R.bad_request("缺少 job_name 参数")
        
        try:
            job = JenkinsJob.objects.filter(name=job_name).first()
            if not job:
                return R.error(message=f"Job '{job_name}' 不存在")
            
            # 如果未指定 end_build，获取最新构建号
            if not end_build:
                # TODO: 调用 Jenkins API 获取 lastBuild.number
                end_build = start_build + 99  # 临时方案
            
            # 启动异步任务
            task = sync_job_history_task.delay(
                job.id, int(start_build), int(end_build)
            )
            
            return R.success(
                message="批量同步任务已启动",
                data={
                    'task_id': task.id,
                    'job_name': job_name,
                    'total_builds': end_build - start_build + 1,
                    'status': 'PENDING'
                }
            )
            
        except Exception as e:
            logger.error(f"启动批量同步任务失败: {str(e)}")
            return R.internal_error(str(e))


class TaskStatusView(APIView):
    """查询任务状态"""
    
    def get(self, request, task_id):
        from celery.result import AsyncResult
        
        try:
            task = AsyncResult(task_id)
            
            response_data = {
                'task_id': task_id,
                'status': task.state,
            }
            
            if task.state == 'PROGRESS':
                # 任务进行中，返回进度信息
                meta = task.info or {}
                response_data.update(meta)
                
            elif task.state == 'SUCCESS':
                # 任务完成，返回结果
                result = task.result or {}
                response_data.update(result)
                
            elif task.state == 'FAILURE':
                # 任务失败，返回错误
                response_data['error'] = str(task.info)
            
            return R.success(data=response_data)
            
        except Exception as e:
            logger.error(f"查询任务状态失败: {str(e)}")
            return R.internal_error(str(e))
```

### 步骤 3: 注册路由

**文件**: `backend/test_report/urls.py`（修改）

```python
from django.urls import path
from .views import SyncAllureReportView, SyncAllBuildsView, TaskStatusView

urlpatterns = [
    path('sync/', SyncAllureReportView.as_view(), name='sync_report'),
    path('sync-all/', SyncAllBuildsView.as_view(), name='sync_all_builds'),  # 新增
    path('task-status/<str:task_id>/', TaskStatusView.as_view(), name='task_status'),  # 新增
]
```

### 步骤 4: 前端实现

**伪代码**:

```javascript
// 1. 启动批量同步
async function startBatchSync(jobName, startBuild, endBuild) {
  const res = await axios.post('/api/test-report/sync-all/', {
    job_name: jobName,
    start_build: startBuild,
    end_build: endBuild
  })
  
  const taskId = res.data.data.task_id
  
  // 2. 开始轮询状态
  pollTaskStatus(taskId)
}

// 轮询任务状态
function pollTaskStatus(taskId) {
  const interval = setInterval(async () => {
    const res = await axios.get(`/api/test-report/task-status/${taskId}/`)
    const data = res.data.data
    
    // 更新进度条
    const progress = (data.current / data.total) * 100
    updateProgressBar(progress)
    updateStatusText(`正在同步: ${data.current}/${data.total}`)
    
    // 任务完成
    if (data.status === 'SUCCESS') {
      clearInterval(interval)
      ElMessage.success(
        `同步完成！成功 ${data.success_count} 条，失败 ${data.failed_count} 条`
      )
    }
    
    // 任务失败
    if (data.status === 'FAILURE') {
      clearInterval(interval)
      ElMessage.error(`同步失败: ${data.error}`)
    }
  }, 2000)  // 每 2 秒查询一次
}
```

---

## 🎯 继续开发的 Prompt 指导

如果需要 AI 继续完成这个功能，可以使用以下 prompt：

```
请基于 test_report 模块，实现批量异步同步功能：

1. 创建 backend/test_report/tasks.py，实现 sync_job_history_task Celery 任务
   - 接收参数：job_id, start_build, end_build
   - 使用 self.update_state() 更新进度
   - 返回详细的成功/失败统计

2. 在 backend/test_report/views.py 中新增两个 View：
   - SyncAllBuildsView: 启动批量同步任务
   - TaskStatusView: 查询任务状态（已有参考实现在 jenkins_integration/views/task_views.py）

3. 更新 backend/test_report/urls.py 添加新路由

4. 前端创建批量同步 UI（可选）：
   - 显示进度条
   - 实时更新状态
   - 显示成功/失败统计

参考文件：
- backend/jenkins_integration/tasks.py（Celery 任务示例）
- backend/jenkins_integration/views/task_views.py（任务状态查询示例）
- backend/test_report/services.py（单次同步逻辑）
```

---

## ⚠️ 注意事项

### 1. 防御性编程（已实施）

在 `backend/test_report/utils/allure_client.py` 中已添加类型检查：

```python
# 在遍历 children 时检查类型
for child in children:
    if not isinstance(child, dict):
        continue  # 跳过非字典项（如 UID 字符串）
    # 处理逻辑...
```

这避免了 `'str' object has no attribute 'get'` 错误。

### 2. 错误处理

批量同步时，**单个构建失败不应中断整体任务**：

```python
for build_num in build_range:
    try:
        # 同步逻辑
    except Exception as e:
        # 记录错误，继续下一个
        results['failed'].append({'build': build_num, 'error': str(e)})
```

### 3. 性能优化

- 使用 `bulk_create` 批量插入数据
- 避免在循环中频繁查询数据库
- 考虑添加重试机制（Celery 自带 `retry` 装饰器）

### 4. 数据清理

批量同步前，建议添加"去重检查"：

```python
# 检查是否已存在
timestamp = f"{job_id}_{build_num}"
if TestExecution.objects.filter(timestamp=timestamp).exists():
    # 跳过或更新
```

---

## 📚 相关文档

- [Celery 官方文档](https://docs.celeryproject.org/)
- [Django Celery 集成指南](https://docs.celeryproject.org/en/stable/django/)
- 项目已有参考实现：`backend/jenkins_integration/tasks.py`

---

## 🔗 关键文件清单

**后端**:
- `backend/test_report/models.py` - 数据模型 ✅
- `backend/test_report/utils/allure_client.py` - Allure 解析器 ✅
- `backend/test_report/services.py` - 业务逻辑 ✅
- `backend/test_report/views.py` - API 视图（单次同步 ✅，批量同步 ⏳）
- `backend/test_report/tasks.py` - Celery 任务 ⏳
- `backend/test_report/urls.py` - 路由配置（部分 ✅）

**前端**（如需实现）:
- 批量同步 UI 组件 ⏳
- 进度显示逻辑 ⏳

---

**文档版本**: v1.0  
**最后更新**: 2024-12-24  
**状态**: 基础功能已完成，批量异步功能待实施
