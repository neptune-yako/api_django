from django.urls import path
from .views import (
    SyncAllureReportView,
    SyncJobBuildsView,
    TaskStatusView,
    TestExecutionListView,
    TestExecutionDetailView
)

urlpatterns = [
    # 单次同步
    path('sync/', SyncAllureReportView.as_view(), name='sync_report'),
    
    # 批量同步
    path('sync-job/', SyncJobBuildsView.as_view(), name='sync_job_builds'),
    
    # 任务状态查询
    path('task-status/<str:task_id>/', TaskStatusView.as_view(), name='task_status'),
    
    # 测试执行记录查询
    path('executions/', TestExecutionListView.as_view(), name='execution_list'),
    path('executions/<int:execution_id>/', TestExecutionDetailView.as_view(), name='execution_detail'),
]
