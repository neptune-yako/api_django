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
    
    # 新增: Jenkins 节点信息字段
    jenkins_node = serializers.SerializerMethodField()
    
    class Meta:
        model = Environment
        # 环境自动返回所有字段
        fields = "__all__"
    
    @extend_schema_field(serializers.DictField(allow_null=True))
    def get_jenkins_node(self, obj):
        """
        获取与环境关联的 Jenkins 节点信息
        
        匹配规则:
        - 节点名称 == 环境名称
        - 节点显示名称 == 环境名称
        
        Returns:
            dict or None: Jenkins 节点信息字典，如果没有匹配返回 None
        """
        try:
            from django.db.models import Q
            from jenkins_integration.models import JenkinsNode
            
            # 尝试通过名称或显示名称匹配节点
            node = JenkinsNode.objects.filter(
                Q(name=obj.name) | Q(display_name=obj.name)
            ).first()
            
            if node:
                return {
                    'id': node.id,
                    'name': node.name,
                    'display_name': node.display_name,
                    'host_ip': node.host_ip,
                    'is_online': node.is_online,
                    'is_busy': node.is_busy,
                    'is_idle': node.is_idle,
                    'num_executors': node.num_executors,
                    'labels': node.labels,
                    'description': node.description,
                }
            
            return None
            
        except Exception:
            # 如果 Jenkins 集成模块不可用或查询失败，返回 None
            return None


class FileSerializer(serializers.ModelSerializer):
    """测试文件的序列化器"""

    class Meta:
        model = File
        fields = "__all__"
