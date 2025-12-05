from .models import Plan, Record, Report
from rest_framework import serializers
from scene.serializer import SceneSerializer


class PlanSerializer(serializers.ModelSerializer):
    """测试任务的序列化器"""

    class Meta:
        model = Plan
        fields = '__all__'
        extra_kwargs = {
            'project': {'required': False},  # 允许更新时不传project
            'username': {'required': False},  # 允许更新时不传username
            'scene': {'required': False, 'allow_empty': True}  # 允许更新时不传scene，可以为空
        }


class PlanGetSerializer(serializers.ModelSerializer):
    """单个测试任务的序列化器"""
    scene = SceneSerializer(many=True)

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
