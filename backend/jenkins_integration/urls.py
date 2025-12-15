"""
Jenkins URL 路由配置
"""
from django.urls import path, re_path
from . import views
from . import allure_views

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
    
    # ===== Build 状态查询 =====
    # 查询最新构建状态（轮询用）
    path('api/jenkins/build/latest/', views.JenkinsBuildLatestView.as_view(), name='jenkins-build-latest'),
    
    # 获取 Allure 报告 URL
    path('api/jenkins/build/allure/', views.JenkinsBuildAllureView.as_view(), name='jenkins-build-allure'),
    
    # ===== Job 模板相关 =====
    # 获取所有可用模板列表
    path('api/jenkins/templates/', views.JenkinsTemplateListView.as_view(), name='jenkins-template-list'),
    
    # 获取指定类型的模板内容
    path('api/jenkins/template/<str:template_type>/', views.JenkinsTemplateDetailView.as_view(), name='jenkins-template-detail'),
    
    # ===== Allure 代理 =====
    # Allure 报告代理 - 主页（无文件路径）
    path('api/jenkins/allure-proxy/<str:job_name>/<int:build_number>/',
         allure_views.AllureProxyView.as_view(), 
         name='allure-proxy-index'),
    
    # Allure 报告代理 - 带文件路径（匹配任意路径，包括多级目录）
    re_path(r'^api/jenkins/allure-proxy/(?P<job_name>[^/]+)/(?P<build_number>\d+)/(?P<file_path>.+)$',
            allure_views.AllureProxyView.as_view(), 
            name='allure-proxy-file'),
]
