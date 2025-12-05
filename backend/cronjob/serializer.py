from rest_framework import serializers
from .models import Cronjob


class CronjobSerializer(serializers.ModelSerializer):
    """定时任务序列化器"""
    plan_name = serializers.StringRelatedField(read_only=True, source='plan.name')
    env_name = serializers.StringRelatedField(read_only=True, source='env.name')
    pro_name = serializers.StringRelatedField(read_only=True, source='project.name')

    class Meta:
        model = Cronjob
        fields = '__all__'
