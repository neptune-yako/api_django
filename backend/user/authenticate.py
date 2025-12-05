from django.contrib.auth.backends import ModelBackend
from django.db.models import Q
from .models import User
from rest_framework import serializers


class MyBackend(ModelBackend):
    """自定义的登录认证类"""

    def authenticate(self, request, username=None, password=None, **kwargs):
        """重写认证方法，实现账号、手机号、邮箱登录"""
        try:
            # 获取用户信息，账号、手机号、邮箱均可登录
            user = User.objects.get(Q(username=username) | Q(mobile=username) | Q(email=username))
        except User.DoesNotExist:
            raise serializers.ValidationError({'detail': "未找到该用户，请检查登录名！"})
        else:
            # 验证密码是否正确
            if user.check_password(password):
                return user
            else:
                raise serializers.ValidationError({'detail': "用户密码错误，请检查登录密码！"})
