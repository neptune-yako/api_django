from .models import Plan, Record, Report
from rest_framework import serializers
from scene.serializer import SceneSerializer


class PlanSerializer(serializers.ModelSerializer):
    """测试任务的序列化器"""
    project_name = serializers.CharField(source='project.name', read_only=True)

    class Meta:
        model = Plan
        fields = '__all__'
        extra_kwargs = {
            'project': {'required': False},  # 允许更新时不传project
            'username': {'required': False},  # 允许更新时不传username
            'scene': {'required': False, 'allow_empty': True},  # 允许更新时不传scene，可以为空
            'script_file': {'required': False, 'allow_null': True},
            'script_name': {'required': False, 'allow_null': True},
            'script_type': {'required': False, 'allow_null': True},
            'script_bind_time': {'required': False, 'allow_null': True},
        }


class PlanGetSerializer(serializers.ModelSerializer):
    """单个测试任务的序列化器"""
    scene = SceneSerializer(many=True)
    script_info = serializers.SerializerMethodField()

    def get_script_info(self, obj):
        """获取绑定的Python脚本信息"""
        if obj.script_file:
            return {
                'file_name': obj.script_name or obj.script_file.name,
                'file_url': obj.script_file.url if obj.script_file else None,
                'script_type': obj.script_type,
                'bind_time': obj.script_bind_time,
            }
        return None

    class Meta:
        model = Plan
        fields = '__all__'


class RecordSerializer(serializers.ModelSerializer):
    """测试运行记录"""
    env = serializers.StringRelatedField(read_only=True, source='env.name')
    plan = serializers.StringRelatedField(read_only=True, source='plan.name')

    class Meta:
        model = Record
        fields = '__all__'


class ReportSerializer(serializers.ModelSerializer):
    """测试报告"""

    class Meta:
        model = Report
        fields = '__all__'
