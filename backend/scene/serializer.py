from rest_framework import serializers
from .models import Scene, Step
from interface.serializer import CaseListSerializer, CaseGetSerializer


class SceneSerializer(serializers.ModelSerializer):
    """测试套件的序列器"""

    class Meta:
        model = Scene
        fields = '__all__'
        extra_kwargs = {
            'project': {'required': False},  # 允许更新时不传project
            'username': {'required': False}  # 允许更新时不传username
        }


class StepSerializer(serializers.ModelSerializer):
    """测试套件中的测试用例执行步骤"""

    class Meta:
        model = Step
        fields = '__all__'


class StepListSerializer(serializers.ModelSerializer):
    """测试套件中所有的测试用例执行步骤序列化器"""
    icase = CaseListSerializer(read_only=True)

    class Meta:
        model = Step
        fields = '__all__'


class SceneRunSerializer(serializers.ModelSerializer):
    """测试套件中的测试用例执行步骤"""
    icase = CaseGetSerializer()

    class Meta:
        model = Step
        fields = '__all__'
