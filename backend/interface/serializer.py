from rest_framework import serializers
from .models import Interface, Case


class InterfaceSerializer(serializers.ModelSerializer):
    """接口管理的模型序列化器"""

    class Meta:
        model = Interface
        fields = '__all__'


class CaseSerializer(serializers.ModelSerializer):
    """接口用例管理模型序列化器"""

    class Meta:
        model = Case
        fields = '__all__'


class CaseListSerializer(serializers.ModelSerializer):
    """返回接口用例列表的序列化器"""

    class Meta:
        model = Case
        # 自定义接口返回字段
        fields = ['id', 'title']


class CaseGetSerializer(serializers.ModelSerializer):
    """获取单接口用例详情的模型序列化器"""
    interface = InterfaceSerializer(read_only=True)

    class Meta:
        model = Case
        fields = '__all__'


class InterfaceGetSerializer(serializers.ModelSerializer):
    """接口列表获取的模型序列化器"""
    # 外键关联的字段序列化，数据源是Case，只读，获取字段格式是case_set，重命名为cases
    cases = CaseListSerializer(many=True, read_only=True, source='case_set')
    project = serializers.StringRelatedField(read_only=True, source='project.name')

    class Meta:
        model = Interface
        fields = '__all__'
