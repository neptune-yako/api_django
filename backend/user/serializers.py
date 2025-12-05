from rest_framework import serializers
from .models import User, Role


class RoleSerializer(serializers.ModelSerializer):
    """角色模型的序列化器"""

    class Meta:
        model = Role
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    """用户模型的序列化器"""
    # 用于读取的角色字段
    roles = RoleSerializer(many=True, read_only=True)
    # 用于写入的角色ID字段
    role_ids = serializers.PrimaryKeyRelatedField(many=True, queryset=Role.objects.all(), source='roles',
                                                  write_only=True, required=False)

    class Meta:
        model = User
        # 自定义返回字段
        fields = ['id', 'username', 'email', 'mobile', 'nickname', 'last_login', 'is_superuser', 'is_active',
                  'date_joined', 'is_staff', 'update_time', 'roles', 'role_ids']


class RegisterSerializer(serializers.ModelSerializer):
    """用户注册序列化器"""
    role_ids = serializers.PrimaryKeyRelatedField(many=True, queryset=Role.objects.all(), source='roles',
                                                  write_only=True, required=False)

    class Meta:
        model = User
        fields = ['username', 'password', 'email', 'mobile', 'nickname', 'is_superuser', 'is_active', 'date_joined',
                  'role_ids']
