from django.urls import path
from . import views

urlpatterns = [
    # 用户管理
    path('users/', views.UserMockView.as_view()),
    path('users/<str:pk>/', views.UserMockView.as_view()),
    
    # 状态模拟
    path('status/<int:code>/', views.StatusMockView.as_view()),
    path('delay/<str:seconds>/', views.DelayMockView.as_view()),
    
    # 鉴权模拟
    path('login/', views.LoginMockView.as_view()),
    path('secure-data/', views.SecureDataMockView.as_view()),
]
