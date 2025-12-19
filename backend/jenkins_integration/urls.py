"""
Jenkins URL 路由配置
"""
from django.urls import path, re_path
from . import views
from . import views

urlpatterns = [
    # 测试 Jenkins 连接
    path('api/jenkins/test/', views.JenkinsTestView.as_view(), name='jenkins-test'),
    
    # Job 管理 API
    path('api/jenkins/jobs/', views.JenkinsJobsView.as_view(), name='jenkins_jobs'),
    path('api/jenkins/job/manage/', views.JenkinsJobManageView.as_view(), name='jenkins_job_manage'),
    path('api/jenkins/job/build/', views.JenkinsJobBuildView.as_view(), name='jenkins_job_build'),
    path('api/jenkins/job/validate/', views.JenkinsJobValidateView.as_view(), name='jenkins_job_validate'),
    
    # 构建结果同步 (新)
    path('api/jenkins/build/sync/', views.SyncBuildResultView.as_view(), name='sync_build_result'),
    
    # Job 批量同步 (新)
    path('api/jenkins/jobs/sync/', views.SyncJenkinsJobsView.as_view(), name='sync_jenkins_jobs'),
    
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
         views.AllureProxyView.as_view(), 
         name='allure-proxy-index'),
    
    # Allure 报告代理 - 带文件路径（匹配任意路径，包括多级目录）
    re_path(r'^api/jenkins/allure-proxy/(?P<job_name>[^/]+)/(?P<build_number>\d+)/(?P<file_path>.+)$',
            views.AllureProxyView.as_view(), 
            name='allure-proxy-file'),
]

# 注册 ViewSets
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'api/jenkins/server', views.JenkinsServerViewSet)
router.register(r'api/jenkins/pipeline', views.JenkinsJobViewSet)

urlpatterns += router.urls
