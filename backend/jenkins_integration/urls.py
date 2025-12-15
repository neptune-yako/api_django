"""
Jenkins URL 路由配置
"""
from django.urls import path
from . import views

urlpatterns = [
    # 测试 Jenkins 连接
    path('api/jenkins/test/', views.JenkinsTestView.as_view(), name='jenkins-test'),
    
    # 获取所有 Jobs
    path('api/jenkins/jobs/', views.JenkinsJobsView.as_view(), name='jenkins-jobs'),
    
   # Job 管理 - CRUD (创建、读取、更新、删除)
    path('api/jenkins/job/', views.JenkinsJobManageView.as_view(), name='jenkins-job-manage'),
    
    # XML 校验
    path('api/jenkins/job/validate/', views.JenkinsJobValidateView.as_view(), name='jenkins-job-validate'),
    
    # 复制 Job
    path('api/jenkins/job/copy/', views.JenkinsJobCopyView.as_view(), name='jenkins-job-copy'),
    
    # 启用/禁用 Job
    path('api/jenkins/job/toggle/', views.JenkinsJobToggleView.as_view(), name='jenkins-job-toggle'),
    
    # 触发构建
    path('api/jenkins/job/build/', views.JenkinsJobBuildView.as_view(), name='jenkins-job-build'),
    
    # ===== Job 模板相关 =====
    # 获取所有可用模板列表
    path('api/jenkins/templates/', views.JenkinsTemplateListView.as_view(), name='jenkins-template-list'),
    
    # 获取指定类型的模板内容
    path('api/jenkins/template/<str:template_type>/', views.JenkinsTemplateDetailView.as_view(), name='jenkins-template-detail'),
]
