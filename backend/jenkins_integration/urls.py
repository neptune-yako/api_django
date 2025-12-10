"""
Jenkins URL 路由
"""
from django.urls import path
from . import views

urlpatterns = [
    # 测试 Jenkins 连接
    path('api/jenkins/test/', views.JenkinsTestView.as_view(), name='jenkins-test'),
    
    # 获取所有 Jobs
    path('api/jenkins/jobs/', views.JenkinsJobsView.as_view(), name='jenkins-jobs'),
]
