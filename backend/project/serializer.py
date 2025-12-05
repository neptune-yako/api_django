from drf_spectacular.utils import extend_schema_field
from .models import Project, Environment, File
from rest_framework import serializers


class ProjectSerializer(serializers.ModelSerializer):
    """测试项目的序列化器"""
    # 明确指定info、bug字段的类型
    info = serializers.SerializerMethodField()
    bug = serializers.SerializerMethodField()

    @extend_schema_field(serializers.ListField(child=serializers.DictField()))
    def get_info(self, obj):
        return obj.info()

    @extend_schema_field(serializers.ListField(child=serializers.DictField()))
    def get_bug(self, obj):
        return obj.bug()

    class Meta:
        model = Project
        # 接口返回指定字段，外加方法统计结果
        fields = ['id', 'name', 'username', 'info', 'bug', 'create_time', 'update_time']


class EnvironmentSerializer(serializers.ModelSerializer):
    """测试环境的序列化器"""

    class Meta:
        model = Environment
        # 环境自动返回所有字段
        fields = "__all__"


class FileSerializer(serializers.ModelSerializer):
    """测试文件的序列化器"""

    class Meta:
        model = File
        fields = "__all__"
