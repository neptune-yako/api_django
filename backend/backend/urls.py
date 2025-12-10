"""backend URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.contrib import admin
from django.urls import path, include, re_path
from django.views import static
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView, TokenObtainPairView
from scene.views import SceneView, StepOrder
from interface.views import CaseView
from plan.views import PlanView
from user.views import RegisterView, LoginView, LogoutView
from django.views.generic.base import RedirectView

urlpatterns = [
    # 后台路由地址
    path("admin/", admin.site.urls),
    # 后台图标
    path('favicon.ico', RedirectView.as_view(url='/static/media/favicon.ico')),
    # 后台静态文件路由
    re_path(r'static/(?P<path>.*)$', static.serve, {'document_root': settings.STATIC_ROOT}, name='static'),
    # 接口文档
    path('openapi.json', SpectacularAPIView.as_view(), name='schema'),
    # swagger接口文档
    path('swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    # redoc接口文档
    path('redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    # 登录接口的访问路径
    # path('login/', TokenObtainPairView.as_view(), name='login'),
    # 使用自定义的登录
    path('login/', LoginView.as_view(), name='login'),
    # 刷新token
    path('refresh/', TokenRefreshView.as_view(), name='refresh'),
    # 校验token有效
    path('verify/', TokenVerifyView.as_view(), name='verify'),
    # 退出登录
    path('logout/', LogoutView.as_view(), name='logout'),
    # 注册用户
    path('register/', RegisterView.as_view({"post": "register"}), name='register'),
    # 修改测试套件中的用例步骤顺序
    path('step/order/', StepOrder.as_view(), name='update_order'),
    # 运行单个测试用例的路由
    path('case/run/', CaseView.as_view({"post": "run_case"}), name='run_case'),
    # 运行测试套件的路由
    path('scene/run/', SceneView.as_view({"post": "run_scene"}), name='run_scene'),
    # 运行测试计划的路由
    path('plan/run/', PlanView.as_view({"post": "run_plan"}), name='run_plan'),
    # 项目应用的路由
    path('', include('project.urls')),
    path('', include('interface.urls')),
    path('', include('cronjob.urls')),
    path('', include('scene.urls')),
    path('', include('plan.urls')),
    path('', include('bug.urls')),
    path('', include('user.urls')),

    path('', include('jenkins_integration.urls')),  # 添加jenkins路由
]
